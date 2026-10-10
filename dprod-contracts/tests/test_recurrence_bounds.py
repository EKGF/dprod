from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"


def section(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    return text[begin : text.index(end, begin)]


class RecurrenceBoundsTest(unittest.TestCase):
    """Recurrence instances are finite, anchored, and fulfilled only by their own witnesses."""

    @classmethod
    def setUpClass(cls) -> None:
        text = FORMAL_SEMANTICS_PATH.read_text()
        cls.lifecycle = section(text, "## 5. Duty Lifecycle", "## 6. ")
        cls.recurrence = section(text, "### 5.5 ", "## 6. ")

    def test_expansion_is_bounded_by_anchor_and_clock(self) -> None:
        self.assertTrue("expand : Recurrence × Time × Time → Set<Time>" in self.recurrence)
        self.assertTrue("anchor ≤ t ≤ clock" in self.recurrence)
        self.assertTrue("Σ.activatedAt(duty) = ⊥ then ∅" in self.recurrence)

    def test_condition_guard_uses_no_undefined_environment(self) -> None:
        self.assertFalse("Σ.env" in self.lifecycle)

    def test_witness_must_fall_in_the_duty_window(self) -> None:
        self.assertTrue("from ≤ t ≤ to" in self.lifecycle)
        self.assertTrue("window(d, Σ) = (since(d), effectiveDeadline(d, Σ))" in self.lifecycle)
        for rule, end in (("D-FULFILL", "**Rule D-VIOLATE**"), ("D-VIOLATE", "**Algorithmic form**")):
            block = section(self.lifecycle, f"**Rule {rule}**", end)
            with self.subTest(rule=rule):
                self.assertTrue("window(duty, Σ)" in block)

    def test_templates_are_replaced_by_instances_with_their_own_identity(self) -> None:
        self.assertTrue("identified by (duty, t)" in self.recurrence)
        self.assertTrue("Σ.activatedAt(instantiate(duty, t)) = t" in self.recurrence)
        self.assertTrue("a template is neither fulfilled nor violated" in self.lifecycle)
        self.assertTrue("instancesOf(duties, Σ₁)" in self.lifecycle)

    def test_schedule_does_not_depend_on_the_first_evaluation_time(self) -> None:
        self.assertTrue("truncate(anchor, FREQ)" in self.recurrence)

    def test_stale_actions_before_the_contract_do_not_count(self) -> None:
        self.assertTrue("policy(d).effectiveDate" in self.lifecycle)

    def test_timely_action_evaluated_late_is_not_stuck(self) -> None:
        fulfill = section(self.lifecycle, "**Rule D-FULFILL**", "**Rule D-VIOLATE**")
        self.assertFalse("effectiveDeadline(duty, Σ) ≥ Σ.clock" in fulfill)


if __name__ == "__main__":
    unittest.main()
