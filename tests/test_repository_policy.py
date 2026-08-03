from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RETIRED_TRACKER_NAMES = (
    "changes-plan.md",
    "recurrence-redesign.md",
)
CANONICAL_BACKLOG_POLICY = (
    "GitHub Issues is the canonical and exclusive backlog for all outstanding "
    "DPROD work and design decisions."
)


class RepositoryPolicyTest(unittest.TestCase):
    def test_retired_tracker_files_are_absent(self) -> None:
        found = sorted(
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for name in RETIRED_TRACKER_NAMES
            for path in REPOSITORY_ROOT.rglob(name)
            if ".git" not in path.parts
        )

        self.assertEqual(
            [],
            found,
            "Retired hand-maintained trackers must not be reintroduced; "
            "create or update GitHub issues instead.",
        )

    def test_contributing_declares_the_canonical_backlog(self) -> None:
        contributing = (REPOSITORY_ROOT / "CONTRIBUTING.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(CANONICAL_BACKLOG_POLICY, contributing)


if __name__ == "__main__":
    unittest.main()
