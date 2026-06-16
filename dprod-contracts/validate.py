#!/usr/bin/env python3
"""Parse and SHACL-validate the DPROD-contracts artifacts.

Two checks, both run from the repository root or anywhere (paths are resolved
relative to this file):

1. Syntax — every ``*.ttl`` under ``dprod-contracts/`` must parse as Turtle.
2. SHACL  — every example under ``dprod-contracts/examples/`` must conform to
   ``dprod-contracts-shapes.ttl`` (with the ontology supplied as the shapes'
   ``ont_graph`` so ``sh:class`` / domain checks resolve, and RDFS inference on).

Exit code is non-zero if any file fails to parse or any example reports a
SHACL violation, so this is safe to wire into CI or a pre-commit hook.

Usage::

    python dprod-contracts/validate.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph
from pyshacl import validate

CONTRACTS_DIR: Path = Path(__file__).resolve().parent
SHAPES_FILE: Path = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
ONTOLOGY_FILE: Path = CONTRACTS_DIR / "dprod-contracts.ttl"
EXAMPLES_DIR: Path = CONTRACTS_DIR / "examples"


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single file check."""

    path: Path
    ok: bool
    detail: str = ""

    def render(self, root: Path) -> str:
        status = "OK  " if self.ok else "FAIL"
        rel = self.path.relative_to(root)
        line = f"  [{status}] {rel}"
        return line if self.ok else f"{line}\n        {self.detail.strip()}"


class ContractsValidator:
    """Runs the parse and SHACL passes over the contracts artifacts."""

    def __init__(self, contracts_dir: Path = CONTRACTS_DIR) -> None:
        self._contracts_dir = contracts_dir
        self._repo_root = contracts_dir.parent

    def _turtle_files(self) -> list[Path]:
        return sorted(self._contracts_dir.rglob("*.ttl"))

    def _examples(self) -> list[Path]:
        return sorted(EXAMPLES_DIR.glob("*.ttl"))

    def check_syntax(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for ttl in self._turtle_files():
            try:
                Graph().parse(ttl, format="turtle")
                results.append(CheckResult(ttl, True))
            except Exception as exc:  # rdflib raises a variety of parse errors
                results.append(CheckResult(ttl, False, str(exc)))
        return results

    def check_shapes(self) -> list[CheckResult]:
        shapes = Graph().parse(SHAPES_FILE, format="turtle")
        ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")
        results: list[CheckResult] = []
        for example in self._examples():
            data = Graph().parse(example, format="turtle")
            conforms, _, report = validate(
                data_graph=data,
                shacl_graph=shapes,
                ont_graph=ontology,
                inference="rdfs",
                advanced=True,
            )
            results.append(CheckResult(example, conforms, report))
        return results

    def run(self) -> bool:
        print("Syntax (Turtle parse):")
        syntax = self.check_syntax()
        for result in syntax:
            print(result.render(self._repo_root))

        print("\nSHACL (examples vs shapes):")
        shapes = self.check_shapes()
        for result in shapes:
            print(result.render(self._repo_root))

        return all(r.ok for r in syntax + shapes)


def main() -> int:
    return 0 if ContractsValidator().run() else 1


if __name__ == "__main__":
    sys.exit(main())
