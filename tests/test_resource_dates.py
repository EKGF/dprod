"""`dct:issued` and `dct:modified` are dates on data, not just annotations.

DCAT uses both as dates on `dcat:Resource`, so DPROD data products and
contracts carry them as data. Declaring them `owl:AnnotationProperty` hid them
from OWL reasoning and clashed with any graph typing them
`owl:DatatypeProperty` (issue #276). They stay plain `rdf:Property`, and SHACL
checks that their values are dates instead.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import DCTERMS, OWL, RDF, Graph

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_FILES = (
    REPOSITORY_ROOT / "ontology" / "dprod" / "dprod-ontology.ttl",
    REPOSITORY_ROOT / "dprod-contracts" / "dprod-contracts.ttl",
)
SHAPES_FILE = REPOSITORY_ROOT / "ontology" / "dprod" / "dprod-shapes.ttl"

DATA_PRODUCT = """
@prefix dprod: <https://ekgf.org/dprod/spec/develop/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<urn:dprod:test:product> a dprod:DataProduct ;
  dct:issued {issued} ;
  dct:modified {modified} .
"""


class ResourceDatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")

    def validate(self, issued: str, modified: str) -> tuple[bool, str]:
        data = Graph().parse(
            data=DATA_PRODUCT.format(issued=issued, modified=modified),
            format="turtle",
        )
        conforms, _, report = validate(data_graph=data, shacl_graph=self.shapes)
        return conforms, report

    def test_ontologies_do_not_declare_dates_as_annotation_properties(self) -> None:
        for path in ONTOLOGY_FILES:
            graph = Graph().parse(path, format="turtle")
            for prop in (DCTERMS.issued, DCTERMS.modified):
                with self.subTest(file=path.name, property=prop):
                    self.assertNotIn(
                        (prop, RDF.type, OWL.AnnotationProperty), graph
                    )

    def test_typed_dates_conform(self) -> None:
        for issued, modified in (
            ('"2026-06-01"^^xsd:date', '"2026-10-13T09:30:00Z"^^xsd:dateTime'),
            ('"2026"^^xsd:gYear', '"2026-10"^^xsd:gYearMonth'),
        ):
            with self.subTest(issued=issued, modified=modified):
                conforms, report = self.validate(issued, modified)
                self.assertTrue(conforms, report)

    def test_untyped_dates_are_rejected(self) -> None:
        for issued, modified in (
            ('"2026-06-01"', '"2026-10-13"^^xsd:date'),
            ('"2026-06-01"^^xsd:date', '"last Tuesday"@en'),
        ):
            with self.subTest(issued=issued, modified=modified):
                conforms, _ = self.validate(issued, modified)
                self.assertFalse(conforms)


if __name__ == "__main__":
    unittest.main()
