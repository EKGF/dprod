from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
FORMAL_SEMANTICS_PATH = ROOT / "dprod-contracts" / "docs" / "formal-semantics.md"


def section(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    return text[begin : text.index(end, begin)]


def definition(text: str, name: str) -> str:
    return section(text, f"{name}(norm, request) =", "\n\n")


class NormMatchingDirectionTest(unittest.TestCase):
    """Permissions must cover the request; prohibitions apply to any overlap (§7.4)."""

    @classmethod
    def setUpClass(cls) -> None:
        text = FORMAL_SEMANTICS_PATH.read_text()
        cls.evaluation = section(text, "## 7. Policy Evaluation", "## 8.")

    def test_matches_used_in_step_one_is_defined(self) -> None:
        self.assertTrue("matches(n, request)" in self.evaluation)
        self.assertTrue("matches(norm, request) =" in self.evaluation)
        self.assertTrue("matches(norm, Env.request) ∧" in self.evaluation)

    def test_permission_is_the_broader_side(self) -> None:
        covers = definition(self.evaluation, "covers")
        for component in ("agent", "action", "asset"):
            with self.subTest(component=component):
                self.assertRegex(covers, rf"request\.{component} ⊑ norm\.")
                self.assertNotRegex(covers, rf"norm\.\w+ ⊑ request\.{component}")

    def test_prohibition_matches_in_both_directions(self) -> None:
        overlaps = definition(self.evaluation, "overlaps")
        for component in ("action", "asset"):
            with self.subTest(component=component):
                self.assertRegex(overlaps, rf"request\.{component} ⊑ norm\.")
                self.assertRegex(overlaps, rf"norm\.\w+ ⊑ request\.{component}")

    def test_no_policy_side_narrower_test_remains(self) -> None:
        self.assertFalse("norm.action matches Env.action" in self.evaluation)
        self.assertFalse("norm.asset matches Env.asset" in self.evaluation)


if __name__ == "__main__":
    unittest.main()
