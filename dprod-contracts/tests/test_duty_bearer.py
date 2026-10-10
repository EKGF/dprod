from pathlib import Path
import unittest

from rdflib import Graph, Namespace, RDFS


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"

DPROD = Namespace("https://ekgf.org/dprod/spec/develop/")


def section(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end)]


class DutyCollectionAndBearerTest(unittest.TestCase):
    """Duties are engaged by the policy that grants, and borne by its assignee by default."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = FORMAL_SEMANTICS_PATH.read_text()
        cls.evaluation = section(cls.text, "### 7.2 ", "### 7.3 ")
        cls.ontology = Graph().parse(CONTRACTS / "dprod-contracts.ttl", format="turtle")

    def test_duties_are_not_matched_against_the_request(self) -> None:
        self.assertFalse("n : Duty, matches(n, request)" in self.evaluation)
        self.assertTrue("{ d ∈ p.clauses | p ∈ granting, d : Duty }" in self.evaluation)

    def test_bearer_default_is_defined_and_used(self) -> None:
        self.assertTrue("**Default bearer**" in self.text)
        self.assertFalse("d.subject = policy(d).grantee" in self.text)
        self.assertFalse("d.subject = agreement.grantee" in self.text)

    def test_grantor_violation_does_not_deny_the_grantee(self) -> None:
        self.assertTrue("if violatedGrantee ≠ ∅ then" in self.evaluation)
        self.assertFalse("if violated ≠ ∅ then" in self.evaluation)
        self.assertTrue("violations: violatedGrantor" in self.evaluation)

    def test_default_bearer_duties_are_tracked_per_agent(self) -> None:
        self.assertTrue("one duty per agent, each tracked separately in Σ" in self.text)

    def test_ontology_bearer_default_is_the_assignee(self) -> None:
        comment = str(self.ontology.value(DPROD.subjectOfDuty, RDFS.comment))
        self.assertNotIn("dataProductOwner", comment)
        self.assertIn("odrl:assignee", comment)


if __name__ == "__main__":
    unittest.main()
