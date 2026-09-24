"""Regression tests for #239: duty-only properties on non-Duty rules.

dprod:deadline, dprod:recurrence, dprod:subjectOfDuty and dprod:objectOfDuty
are only meaningful on odrl:Duty. Their OWL domains state that intent, but a
domain axiom infers rather than validates: under RDFS reasoning a Permission
carrying dprod:deadline silently becomes a Duty as well, which is an
ODRL-disjoint pair of rule classes. The shapes must fail fast instead.
"""

from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"

PREFIXES = """
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix dprod: <https://www.omg.org/spec/DPROD/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<urn:dprod:test:party> a odrl:Party .
"""

DUTY_ONLY_PROPERTIES = {
    "dprod:deadline": '"P1D"^^xsd:duration',
    "dprod:recurrence": '"FREQ=DAILY"',
    "dprod:subjectOfDuty": "<urn:dprod:test:party>",
    "dprod:objectOfDuty": "<urn:dprod:test:party>",
}

NON_DUTY_RULES = ("odrl:Permission", "odrl:Prohibition")


def rule_with(rule_class: str, prop: str, value: str) -> str:
    return PREFIXES + f"""
<urn:dprod:test:rule> a {rule_class} ;
    odrl:action odrl:use ;
    {prop} {value} .
"""


VALID_DUTIES = PREFIXES + """
<urn:dprod:test:namedDuty> a odrl:Duty ;
    odrl:action odrl:inform ;
    dprod:deadline "P1D"^^xsd:duration ;
    dprod:recurrence "FREQ=DAILY" ;
    dprod:subjectOfDuty <urn:dprod:test:party> ;
    dprod:objectOfDuty <urn:dprod:test:party> .

<urn:dprod:test:offer> a odrl:Offer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner <urn:dprod:test:party> ;
    odrl:obligation <urn:dprod:test:namedDuty> ;
    odrl:obligation [
        a odrl:Duty ;
        odrl:action odrl:inform ;
        dprod:deadline "2030-01-01T00:00:00Z"^^xsd:dateTime ;
        dprod:subjectOfDuty <urn:dprod:test:party>
    ] .
"""


class DutyOnlyPropertiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")

    def _validate(self, turtle: str):
        data = Graph().parse(data=turtle, format="turtle")
        conforms, _, report = validate(
            data_graph=data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            advanced=True,
        )
        return conforms, report

    def test_duty_only_properties_are_rejected_on_non_duty_rules(self) -> None:
        for rule_class in NON_DUTY_RULES:
            for prop, value in DUTY_ONLY_PROPERTIES.items():
                with self.subTest(rule=rule_class, property=prop):
                    conforms, report = self._validate(
                        rule_with(rule_class, prop, value)
                    )
                    self.assertFalse(conforms, report)
                    self.assertIn(prop, report)

    def test_named_and_inline_duties_remain_conformant(self) -> None:
        conforms, report = self._validate(VALID_DUTIES)
        self.assertTrue(conforms, report)


if __name__ == "__main__":
    unittest.main()
