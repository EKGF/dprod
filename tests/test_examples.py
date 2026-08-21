"""Validation of the JSON-LD examples shipped in ``examples/``.

Nothing in the build used to parse the examples, so they drifted: two files were
not valid JSON at all, and none of them expanded into the graph they were meant
to denote (issues #92, #93, #119, #246, #247). This module is the regression
test asked for in #92.

Three properties are checked for every example, including the JSON-LD blocks
embedded in the example ``README.md`` files, which are what the specification
actually renders:

1. it parses as JSON;
2. expanding it against the generated DPROD context drops no term — an
   undefined term must be a build failure rather than a silent omission, which
   is the whole reason the published context carries no ``@vocab``;
3. expansion produces triples, and IRI-valued properties produce resources
   rather than literals.
"""

from __future__ import annotations

import html
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Iterator

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "spec-generator"))

from pyld import jsonld  # noqa: E402
from rdflib import Graph, Literal, OWL, RDF  # noqa: E402

from jsonld_context import ApplicationContext  # noqa: E402

CONTEXT_IRI = "https://www.omg.org/spec/DPROD/dprod-context.jsonld"
EXAMPLES_DIR = REPOSITORY_ROOT / "examples"
SPEC_TEMPLATE = REPOSITORY_ROOT / "respec" / "template.html"
JSON_BLOCK = re.compile(r"```(?:json|jsonld|json-ld)\n(.*?)```", re.DOTALL)
TURTLE_BLOCK = re.compile(r"```turtle\n(.*?)```", re.DOTALL)
SPEC_JSON_BLOCK = re.compile(
    r'<pre id="(?P<id>[^"]+)"[^>]*class="[^"]*\bjson\b[^"]*"[^>]*>(?P<body>.*?)</pre>',
    re.DOTALL,
)

#: Terms an example may legitimately leave unexpanded. Keep empty unless there
#: is a real reason: every entry is a term that silently produces no triples.
ALLOWED_DROPPED_TERMS: frozenset[str] = frozenset()


def build_context_document() -> dict:
    """The context as the generator would publish it, built from the ontology."""
    graph = Graph()
    graph.parse(REPOSITORY_ROOT / "ontology/dprod/dprod-ontology.ttl", format="ttl")
    graph.parse(REPOSITORY_ROOT / "dprod-contracts/dprod-contracts.ttl", format="ttl")
    return ApplicationContext(graph).as_document()


class LocalDocumentLoader:
    """Resolves the DPROD context locally and refuses every other network call.

    Tests must not depend on the context being deployed (it is not yet — see
    #232), and must not silently pass because a remote fetch failed.
    """

    def __init__(self, context_document: dict) -> None:
        self._context_document = context_document

    def __call__(self, url: str, options: dict | None = None) -> dict:
        if url != CONTEXT_IRI:
            raise AssertionError(
                f"Example tried to load a remote context {url!r}. Examples must "
                f"only reference {CONTEXT_IRI} plus inline contexts."
            )
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": self._context_document,
        }


def iter_example_documents() -> Iterator[tuple[str, object]]:
    """Every JSON-LD document in ``examples/``, standalone files and README blocks."""
    for path in sorted(EXAMPLES_DIR.rglob("*.json")) + sorted(
        EXAMPLES_DIR.rglob("*.jsonld")
    ):
        yield path.relative_to(REPOSITORY_ROOT).as_posix(), path

    for readme in sorted(EXAMPLES_DIR.rglob("README.md")):
        text = readme.read_text(encoding="utf-8")
        for match in JSON_BLOCK.finditer(text):
            line = text[: match.start()].count("\n") + 2
            name = f"{readme.relative_to(REPOSITORY_ROOT).as_posix()}:{line}"
            yield name, match.group(1)

    # The spec's own worked examples. These are the most visible documents DPROD
    # publishes, and were subject to exactly the same defects (issue #246).
    spec = SPEC_TEMPLATE.read_text(encoding="utf-8")
    for match in SPEC_JSON_BLOCK.finditer(spec):
        body = html.unescape(match.group("body"))
        if '"@context"' not in body:
            continue
        yield f"respec/template.html#{match.group('id')}", body


def collect_terms(node: object, found: set[str]) -> None:
    """Every key and ``@type`` value in a document, ignoring JSON-LD keywords."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "@context":
                continue
            if not key.startswith("@"):
                found.add(key)
            if key == "@type":
                for type_name in [value] if isinstance(value, str) else value:
                    if isinstance(type_name, str):
                        found.add(type_name)
            collect_terms(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_terms(item, found)


def collect_inline_prefixes(node: object, prefixes: dict[str, str]) -> None:
    """Prefixes an example declares itself, e.g. an ``ex:`` extension namespace."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "@context":
                for entry in [value] if not isinstance(value, list) else value:
                    if isinstance(entry, dict):
                        for name, iri in entry.items():
                            if isinstance(iri, str) and not name.startswith("@"):
                                prefixes[name] = iri
            else:
                collect_inline_prefixes(value, prefixes)
    elif isinstance(node, list):
        for item in node:
            collect_inline_prefixes(item, prefixes)


def resolve_term(term: str, prefixes: dict[str, str]) -> str | None:
    """Expand a compact IRI, or return ``None`` when nothing can define it.

    A bare term (``outputPort``) resolves to nothing, which is the point: with
    no ``@vocab`` in the published context it cannot expand, and the caller
    reports it as dropped.
    """
    if term.startswith("http://") or term.startswith("https://"):
        return term
    prefix, separator, local = term.partition(":")
    if not separator or prefix not in prefixes:
        return None
    return prefixes[prefix] + local


def iter_turtle_blocks() -> Iterator[tuple[str, str]]:
    """Turtle snippets embedded in the example ``README.md`` files."""
    for readme in sorted(EXAMPLES_DIR.rglob("README.md")):
        text = readme.read_text(encoding="utf-8")
        for match in TURTLE_BLOCK.finditer(text):
            line = text[: match.start()].count("\n") + 2
            name = f"{readme.relative_to(REPOSITORY_ROOT).as_posix()}:{line}"
            yield name, match.group(1)


class ExampleValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context_document = build_context_document()
        cls.loader = LocalDocumentLoader(cls.context_document)
        cls.documents = list(iter_example_documents())
        cls.prefixes = {
            name: iri
            for name, iri in cls.context_document["@context"].items()
            if isinstance(iri, str) and not name.startswith("@")
        }

    def parse(self, source: object) -> object:
        if isinstance(source, Path):
            return json.loads(source.read_text(encoding="utf-8"))
        return json.loads(source)

    def test_embedded_turtle_snippets_parse(self) -> None:
        """A Turtle snippet must be self-contained, prefixes included."""
        for name, snippet in iter_turtle_blocks():
            with self.subTest(example=name):
                try:
                    Graph().parse(data=snippet, format="turtle")
                except Exception as error:  # rdflib raises several types here
                    self.fail(f"{name} is not valid Turtle: {error}")

    def graph_for(self, source: object) -> Graph:
        """The RDF graph an example denotes, expanded against the DPROD context."""
        nquads = jsonld.to_rdf(
            self.parse(source),
            {
                "documentLoader": self.loader,
                "format": "application/n-quads",
                "base": "",
            },
        )
        graph = Graph()
        graph.parse(data=nquads, format="nquads")
        return graph

    def test_examples_were_found(self) -> None:
        self.assertGreater(
            len(self.documents), 5, "Example discovery found suspiciously little."
        )

    def test_every_example_is_valid_json(self) -> None:
        for name, source in self.documents:
            with self.subTest(example=name):
                try:
                    self.parse(source)
                except json.JSONDecodeError as error:
                    self.fail(f"{name} is not valid JSON: {error}")

    def test_every_example_expands_without_dropping_terms(self) -> None:
        for name, source in self.documents:
            with self.subTest(example=name):
                document = self.parse(source)

                declared: set[str] = set()
                collect_terms(document, declared)

                prefixes = dict(self.prefixes)
                collect_inline_prefixes(document, prefixes)

                expanded = jsonld.expand(
                    document, {"documentLoader": self.loader, "base": ""}
                )
                surviving: set[str] = set()
                collect_terms(expanded, surviving)

                dropped = sorted(
                    term
                    for term in declared
                    if term not in ALLOWED_DROPPED_TERMS
                    and (
                        (resolved := resolve_term(term, prefixes)) is None
                        or resolved not in surviving
                    )
                )
                self.assertEqual(
                    [],
                    dropped,
                    f"{name}: terms dropped during expansion because nothing "
                    f"defines them: {dropped}",
                )

    def test_every_example_produces_triples(self) -> None:
        for name, source in self.documents:
            with self.subTest(example=name):
                graph = self.graph_for(source)
                self.assertGreater(
                    len(graph), 0, f"{name} produced no triples at all."
                )

    def test_ontology_object_properties_are_all_coerced(self) -> None:
        """Every ``owl:ObjectProperty`` must carry ``"@type": "@id"``.

        Checked against the ontology rather than against the context, so a
        property that stops being coerced is caught even though the context is
        what generated the list.
        """
        graph = Graph()
        graph.parse(
            REPOSITORY_ROOT / "ontology/dprod/dprod-ontology.ttl", format="ttl"
        )
        graph.parse(
            REPOSITORY_ROOT / "dprod-contracts/dprod-contracts.ttl", format="ttl"
        )
        context = self.context_document["@context"]

        # Queried here rather than via ApplicationContext, so that a change to
        # the generator's own derivation cannot make this test vacuous.
        namespace = self.context_document["@context"]["dprod"]
        object_properties = sorted(
            f"dprod:{str(subject)[len(namespace):]}"
            for subject in graph.subjects(RDF.type, OWL.ObjectProperty)
            if str(subject).startswith(namespace)
        )
        self.assertGreater(len(object_properties), 10)

        for term in object_properties:
            with self.subTest(term=term):
                self.assertIsInstance(
                    context.get(term),
                    dict,
                    f"{term} is an owl:ObjectProperty but the published context "
                    f"does not coerce it, so its values expand to literals.",
                )
                self.assertEqual("@id", context[term]["@type"])

    def test_no_example_yields_an_iri_shaped_literal(self) -> None:
        """A literal whose lexical form is an absolute IRI means a missed coercion.

        This is deliberately independent of the coercion list: it catches an
        IRI-valued property nobody remembered to declare, in DPROD's vocabulary
        or in any other, which is exactly how #246 went unnoticed.
        """
        iri_shaped = re.compile(r"^https?://\S+$")

        for name, source in self.documents:
            with self.subTest(example=name):
                for _, predicate, obj in self.graph_for(source):
                    if isinstance(obj, Literal) and iri_shaped.match(str(obj)):
                        self.fail(
                            f"{name}: <{predicate}> has the literal value "
                            f"{str(obj)!r}, which is an IRI. The property needs "
                            f'\'"@type": "@id"\' in the published context.'
                        )


if __name__ == "__main__":
    unittest.main()
