from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"
SPECIFICATION_FILE = CONTRACTS_DIR / "docs" / "specification.md"
FORMAL_SEMANTICS_FILE = CONTRACTS_DIR / "docs" / "formal-semantics.md"

REQUEST_REJECTION_MESSAGE = (
    "DPROD contracts reject odrl:Request because Offer-Request-Agreement "
    "semantics are undefined; support is deferred."
)

REQUEST_DATA = """
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

<urn:dprod:test:request> a odrl:Request .
"""


class RequestRejectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")

    def test_request_is_rejected_with_the_deferred_semantics_reason(self) -> None:
        data = Graph().parse(data=REQUEST_DATA, format="turtle")

        conforms, _, report = validate(
            data_graph=data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            advanced=True,
        )

        self.assertFalse(conforms)
        self.assertIn(REQUEST_REJECTION_MESSAGE, report)

    def test_specification_records_the_deferred_rejection(self) -> None:
        specification = SPECIFICATION_FILE.read_text(encoding="utf-8")

        self.assertIn(REQUEST_REJECTION_MESSAGE, specification)

    def test_formal_request_is_distinct_from_odrl_request(self) -> None:
        formal_semantics = FORMAL_SEMANTICS_FILE.read_text(encoding="utf-8")

        self.assertIn(
            "The formal `Request` evaluation input is not an RDF "
            "`odrl:Request` policy.",
            formal_semantics,
        )


if __name__ == "__main__":
    unittest.main()
