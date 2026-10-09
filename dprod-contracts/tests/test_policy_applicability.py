from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"


def section(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end)]


class PolicyApplicabilityTest(unittest.TestCase):
    """A policy's target belongs to its rules; its validity window is evaluated."""

    @classmethod
    def setUpClass(cls) -> None:
        text = FORMAL_SEMANTICS_PATH.read_text()
        cls.policies = section(text, "### 3.4 Policies", "### 3.5 ")
        cls.applicability = section(text, "### 7.3 Policy Applicability", "### 7.4 ")
        cls.specification = (CONTRACTS / "docs" / "specification.md").read_text()
        cls.guide = (CONTRACTS / "docs" / "contracts-guide.md").read_text()

    def test_policy_target_is_distributed_to_rules_not_tested_twice(self) -> None:
        self.assertTrue("target: Set<Asset>" in self.policies)
        self.assertTrue("**Effective target and assignee**" in self.policies)
        self.assertFalse("p.target" in self.applicability)

    def test_policy_has_no_unencoded_condition(self) -> None:
        grammar = section(self.policies, "Policy ::=", "```")
        self.assertFalse("condition" in grammar)
        self.assertFalse("p.condition" in self.applicability)

    def test_validity_window_is_evaluated(self) -> None:
        self.assertTrue("p.effectiveDate ≤ Env.Σ.clock" in self.applicability)
        self.assertTrue("Env.Σ.clock ≤ p.expirationDate" in self.applicability)
        self.assertIn("is not applicable (formal semantics §7.3)", self.specification)

    def test_multi_target_inheritance_is_defined(self) -> None:
        self.assertFalse("inheritance is ambiguous" in self.guide)
        self.assertTrue("one copy per target" in self.policies)
        self.assertTrue("identified by the rule and its target" in self.policies)

    def test_policy_assignee_is_distributed_to_rules(self) -> None:
        self.assertTrue("takes the policy's `grantee` as its `subject`" in self.policies)


if __name__ == "__main__":
    unittest.main()
