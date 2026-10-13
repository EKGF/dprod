"""Action refinements on duties (#275).

A duty's odrl:constraint says when the duty applies; what it requires is its
action with all refinements satisfied (ODRL 2.2 §2.6.3). A refined action is
a node whose rdf:value names the action. The profile records refinements as
agreed terms and matches on the action alone, so on a permission or a
prohibition an unevaluated refinement would change what is granted or
forbidden: those rules must not carry one.
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
@prefix dprod: <https://ekgf.org/dprod/spec/develop/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<urn:dprod:test:party> a odrl:Party .
"""

REFINEMENT = """odrl:refinement [
        a odrl:Constraint ;
        odrl:leftOperand <urn:dprod:test:completeness> ;
        odrl:operator odrl:eq ;
        odrl:rightOperand 100
    ]"""

OPERAND = """
<urn:dprod:test:completeness> a odrl:LeftOperand ;
    dprod:operandSource dprod:stateSource ;
    dprod:operandProperty <urn:dprod:test:completeness> .
"""


def rule_with_action(rule_class: str, action: str) -> str:
    return PREFIXES + OPERAND + f"""
<urn:dprod:test:rule> a {rule_class} ;
    odrl:action {action} .
"""


class ActionRefinementTest(unittest.TestCase):
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

    def test_refined_duty_action_is_valid(self) -> None:
        conforms, report = self._validate(rule_with_action(
            "odrl:Duty", f"[ rdf:value <urn:dprod:test:conformTo> ; {REFINEMENT} ]"
        ))
        self.assertTrue(conforms, report)

    def test_refinement_is_rejected_on_permissions_and_prohibitions(self) -> None:
        for rule_class in ("odrl:Permission", "odrl:Prohibition"):
            with self.subTest(rule=rule_class):
                conforms, report = self._validate(rule_with_action(
                    rule_class, f"[ rdf:value odrl:use ; {REFINEMENT} ]"
                ))
                self.assertFalse(conforms, report)
                self.assertIn("Refinements are supported on duty actions only.", report)

    def test_refined_action_must_name_its_action(self) -> None:
        conforms, report = self._validate(rule_with_action(
            "odrl:Duty", f"[ {REFINEMENT} ]"
        ))
        self.assertFalse(conforms, report)
        self.assertIn("exactly one rdf:value IRI naming the action", report)

    def test_refinement_must_be_a_constraint(self) -> None:
        conforms, report = self._validate(rule_with_action(
            "odrl:Duty", '[ rdf:value <urn:dprod:test:conformTo> ; odrl:refinement "complete" ]'
        ))
        self.assertFalse(conforms, report)
        self.assertIn("must be an odrl:Constraint or odrl:LogicalConstraint", report)


if __name__ == "__main__":
    unittest.main()
