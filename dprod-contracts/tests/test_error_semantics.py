from itertools import permutations, product
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"


def section(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end)]


# Reference reading of §6.1: True, False, or a frozenset of errors.
def k_and(*values):
    if False in values:
        return False
    errors = [v for v in values if isinstance(v, frozenset)]
    return frozenset().union(*errors) if errors else True


def k_or(*values):
    if True in values:
        return True
    errors = [v for v in values if isinstance(v, frozenset)]
    return frozenset().union(*errors) if errors else False


def k_not(value):
    return value if isinstance(value, frozenset) else not value


TRUTHS = (True, False, frozenset({"e1"}), frozenset({"e2"}))


class KleeneConnectivesTest(unittest.TestCase):
    """Reference check of §6.1's truth tables: order-independent, and an error
    never changes a Boolean result. It checks the definitions as transcribed
    above, not the document text."""

    def test_connectives_do_not_depend_on_operand_order(self) -> None:
        for values in product(TRUTHS, repeat=3):
            for connective in (k_and, k_or):
                results = {connective(*p) for p in permutations(values)}
                self.assertEqual(1, len(results), (connective.__name__, values))

    def test_completing_an_error_never_changes_a_boolean_result(self) -> None:
        for values in product(TRUTHS, repeat=3):
            for connective in (k_and, k_or):
                result = connective(*values)
                if isinstance(result, frozenset):
                    continue
                completions = product(
                    *[(True, False) if isinstance(v, frozenset) else (v,) for v in values]
                )
                for completion in completions:
                    self.assertEqual(result, connective(*completion), values)

    def test_negation_preserves_errors(self) -> None:
        self.assertEqual(frozenset({"e1"}), k_not(frozenset({"e1"})))
        self.assertEqual(frozenset({"e1"}), k_not(k_and(True, frozenset({"e1"}))))


class ErrorSemanticsDocumentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = FORMAL_SEMANTICS_PATH.read_text()
        cls.conditions = section(cls.text, "### 6.1 ", "### 6.2 ")
        cls.evaluation = section(cls.text, "### 7.2 ", "### 7.3 ")
        cls.readme = (CONTRACTS / "README.md").read_text()
        cls.overview = (CONTRACTS / "docs" / "overview.md").read_text()

    def test_connectives_are_not_left_to_right(self) -> None:
        for document in (self.conditions, self.readme, self.overview):
            self.assertFalse("left-to-right" in document)
        self.assertTrue("strong Kleene" in self.conditions)
        self.assertTrue("must not be converted to `false`" in self.conditions)

    def test_incomparable_operands_are_errors_not_false(self) -> None:
        self.assertNotIn("the operator returns `false`", self.text)
        self.assertIn("ResolutionError(Incomparable", self.text)
        self.assertIn("Every operator requires operands of the same type", self.text)

    def test_active_prohibition_is_checked_before_any_error_can_abort(self) -> None:
        self.assertNotIn("immediately returns Failure", self.evaluation)
        deny = self.evaluation.index("return {decision: Deny, ...}")
        self.assertLess(deny, self.evaluation.index("return Failure("))
        self.assertLess(deny, self.evaluation.index("updateDutyStates("))

    def test_order_independence_and_error_soundness_are_stated(self) -> None:
        self.assertIn("### 9.6 Order Independence", self.text)
        self.assertIn("### 9.7 Error Soundness", self.text)
        self.assertIn("EvaluationError = Set<ResolutionError>", self.text)


if __name__ == "__main__":
    unittest.main()
