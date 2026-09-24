"""The Data Contracts sections of the generated specification (issue #258).

The contracts SHACL file targets ODRL classes as well as DPROD classes, and
before #258 every one of those shapes rendered as a DPROD class definition in
the "Data Product Model" section, so the spec listed ``odrl:Policy``,
``odrl:Set`` and ``odrl:Offer`` as if DPROD had defined them. These tests pin
the split the generator now makes.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "spec-generator"))

from rdflib import Graph  # noqa: E402
from rdflib.namespace import ODRL2  # noqa: E402

import globals  # noqa: E402
from contract_sections import (  # noqa: E402
    contract_extension_properties,
    split_node_shapes,
)
from main import add_to_context  # noqa: E402


def local_graph() -> Graph:
    """The ontology and shapes, without the remote DCAT fetch the build does."""
    graph = Graph()
    for path in (
        "ontology/dprod/dprod-ontology.ttl",
        "ontology/dprod/dprod-shapes.ttl",
        "dprod-contracts/dprod-contracts.ttl",
        "dprod-contracts/dprod-contracts-shapes.ttl",
    ):
        graph.parse(REPOSITORY_ROOT / path, format="ttl")
    return graph


class ContractSectionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = local_graph()
        cls.node_shapes: dict = {}
        for subject in cls.graph.subjects():
            add_to_context(cls.graph, subject, cls.node_shapes)
        cls.core, cls.contracts = split_node_shapes(cls.node_shapes)

    def test_contract_classes_are_exactly_the_dprod_contract_terms(self) -> None:
        self.assertEqual(
            {"DataOffer", "DataContract", "EvaluationContext"},
            {shape.name for shape in self.contracts},
        )

    def test_no_odrl_class_renders_as_a_dprod_class(self) -> None:
        for shape in self.core + self.contracts:
            with self.subTest(shape=shape.name):
                self.assertFalse(
                    str(shape.axiom_iri).startswith(str(ODRL2)),
                    f"{shape.name} targets an ODRL class and must not render as a DPROD class.",
                )

    def test_core_classes_contain_no_contracts_shapes(self) -> None:
        for shape in self.core:
            with self.subTest(shape=shape.name):
                self.assertFalse(
                    str(shape.shape_iri).startswith(globals.contracts_shapes_ns_iri)
                )

    def test_no_rejection_shape_renders_as_a_class(self) -> None:
        for shape in self.core + self.contracts:
            with self.subTest(shape=shape.name):
                self.assertFalse(shape.name.startswith("Reject"))

    def test_extension_properties_cover_the_duty_extensions(self) -> None:
        names = {prop.name for prop in contract_extension_properties(self.graph)}
        for expected in (
            "dprod:deadline",
            "dprod:recurrence",
            "dprod:subjectOfDuty",
            "dprod:objectOfDuty",
            "dprod:dutyState",
            "dprod:operandSource",
            "dprod:operandProperty",
            "dprod:not",
        ):
            with self.subTest(property=expected):
                self.assertIn(expected, names)


if __name__ == "__main__":
    unittest.main()
