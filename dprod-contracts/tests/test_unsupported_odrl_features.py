from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"

CONTRACT_TEMPLATE = """
@prefix dprod: <https://ekgf.org/dprod/spec/develop/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

<urn:dprod:test:contract> a dprod:DataContract ;
  odrl:{predicate} <urn:dprod:test:value> .
"""

UNSUPPORTED_FEATURES = {
    "xone": "DPROD contracts do not support xone operator.",
    "remedy": "DPROD contracts do not support odrl:remedy.",
    "consequence": "DPROD contracts do not support odrl:consequence.",
    "inheritAllowed": "DPROD contracts do not support odrl:inheritAllowed.",
    "inheritFrom": "DPROD contracts do not support odrl:inheritFrom.",
}


class UnsupportedOdrlFeatureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")

    def test_each_unsupported_feature_is_rejected_with_its_message(self) -> None:
        for predicate, message in UNSUPPORTED_FEATURES.items():
            with self.subTest(predicate=predicate):
                data = Graph().parse(
                    data=CONTRACT_TEMPLATE.format(predicate=predicate),
                    format="turtle",
                )

                conforms, _, report = validate(
                    data_graph=data,
                    shacl_graph=self.shapes,
                    ont_graph=self.ontology,
                    inference="rdfs",
                    advanced=True,
                )

                self.assertFalse(conforms)
                self.assertIn(message, report)


if __name__ == "__main__":
    unittest.main()
