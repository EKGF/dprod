from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"


def section(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    return text[begin : text.index(end, begin)]


class ScheduleBoundsTest(unittest.TestCase):
    """Scheduled duty instances are finite, anchored by the schedule, and fulfilled only by their own witnesses."""

    @classmethod
    def setUpClass(cls) -> None:
        text = FORMAL_SEMANTICS_PATH.read_text(encoding="utf-8")
        cls.lifecycle = section(text, "## 5. Duty Lifecycle", "## 6. ")
        cls.schedule = section(text, "### 5.5 ", "## 6. ")
        cls.evaluation = section(text, "### 7.2 ", "### 7.3 ")
        # Prose checks ignore line wrapping
        cls.schedule_prose = " ".join(cls.schedule.split())

    def test_expansion_is_bounded_by_activation_and_clock(self) -> None:
        self.assertIn("× Time? × Time → Set<Time> | ScheduleError", self.schedule)
        self.assertIn("{ t ∈ p.occurrences(rule) | from ≤ t ≤ to }", self.schedule)
        self.assertIn(
            "expand(duty.schedule, Σ.processors, Σ.activatedAt(duty), Σ.clock)",
            self.schedule,
        )
        self.assertIn("if from = ⊥ then ∅", self.schedule)

    def test_schedule_sets_the_times_and_activation_only_the_range(self) -> None:
        self.assertIn("The expression alone fixes these times", self.schedule_prose)
        self.assertIn("it never moves them", self.schedule_prose)
        self.assertNotIn("truncate(", self.schedule)

    def test_schedule_errors_do_not_depend_on_the_range(self) -> None:
        self.assertIn("never on the range", self.schedule_prose)

    def test_condition_is_three_valued_and_uses_no_undefined_environment(self) -> None:
        self.assertNotIn("Σ.env", self.lifecycle)
        self.assertIn("A condition in error leaves the template Pending", self.schedule_prose)

    def test_witness_must_fall_in_the_duty_window(self) -> None:
        self.assertIn("from ≤ t ≤ to", self.lifecycle)
        self.assertIn("window(d, Σ) = (since(d), effectiveDeadline(d, Σ))", self.lifecycle)
        for rule, end in (("D-FULFILL", "**Rule D-VIOLATE**"), ("D-VIOLATE", "**Rule D-FREEZE**")):
            block = section(self.lifecycle, f"**Rule {rule}**", end)
            with self.subTest(rule=rule):
                self.assertIn("window(duty, Σ)", block)
                self.assertIn("duty.schedule = ⊥", block)

    def test_templates_are_replaced_by_instances_with_their_own_identity(self) -> None:
        self.assertIn("identified by (duty, t)", self.schedule)
        self.assertIn("Σ.activatedAt(instantiate(duty, t)) = t", self.schedule)
        self.assertIn("a template is neither fulfilled nor violated", self.lifecycle)
        self.assertIn("instancesOf(duties, Σ₁)", self.lifecycle)
        self.assertIn("tracked(D) = { d ∈ D | d.schedule = ⊥ } ∪ instancesOf(D, Σ')", self.evaluation)
        for name in ("violatedGrantor", "violatedGrantee", "activeGrantor", "activeGrantee"):
            with self.subTest(name=name):
                self.assertRegex(self.evaluation, rf"let {name} += \{{ d ∈ tracked\(")

    def test_stale_actions_before_the_contract_do_not_count(self) -> None:
        self.assertIn("policy(d).effectiveDate", self.lifecycle)

    def test_timely_action_evaluated_late_is_not_stuck(self) -> None:
        fulfill = section(self.lifecycle, "**Rule D-FULFILL**", "**Rule D-VIOLATE**")
        self.assertNotIn("effectiveDeadline(duty, Σ) ≥ Σ.clock", fulfill)


if __name__ == "__main__":
    unittest.main()
