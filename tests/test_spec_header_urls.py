"""The spec header must not advertise URLs that 404.

Three separate dead links shipped at once (issue #255):

* `edDraftURI` pointed at `https://ekgf.org/spec/{branch}/` — missing the
  `/dprod` basePath, and with the branch name unslugified, so a branch
  containing a slash could never resolve;
* `latestVersion` pointed at the *vocabulary namespace* IRI, which identifies
  the terms rather than a document and does not dereference;
* the frozen 1.0 archive set no `edDraftURI` at all, so ReSpec inferred one
  from the `github` config — the GitHub Pages site retired by #235.

These are cheap to reintroduce and invisible without rendering the page in a
browser, since ReSpec builds the header client-side.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPEC_TEMPLATE = REPOSITORY_ROOT / "respec" / "template.html"
ARCHIVE_SPEC = (
    REPOSITORY_ROOT / "site" / "public" / "spec" / "archive" / "1.0" / "index.html"
)

#: Hosts and paths known not to resolve.
RETIRED_URLS = (
    "ekgf.github.io/dprod",
    "https://www.omg.org/spec/DPROD/dprod.ttl",
)
SPEC_BASE = "https://ekgf.org/dprod/spec/"


class SpecHeaderUrlTest(unittest.TestCase):
    @staticmethod
    def without_comments(content: str) -> str:
        """Strip comments: a URL explained in one is not a URL that is linked."""
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        return "\n".join(
            line for line in content.splitlines() if not line.lstrip().startswith("//")
        )

    def documents(self) -> list[tuple[str, str]]:
        return [
            (
                path.relative_to(REPOSITORY_ROOT).as_posix(),
                self.without_comments(path.read_text("utf-8")),
            )
            for path in (SPEC_TEMPLATE, ARCHIVE_SPEC)
        ]

    def test_no_retired_urls_are_linked(self) -> None:
        for name, content in self.documents():
            for retired in RETIRED_URLS:
                with self.subTest(document=name, url=retired):
                    self.assertNotIn(
                        retired,
                        content,
                        f"{name} references {retired}, which does not resolve.",
                    )

    def test_both_documents_set_an_editors_draft(self) -> None:
        """Unset, ReSpec infers the retired GitHub Pages URL from `github`."""
        for name, content in self.documents():
            with self.subTest(document=name):
                self.assertIn(
                    f'edDraftURI: "{SPEC_BASE}develop/"',
                    content,
                    f"{name} must set edDraftURI explicitly to the canonical "
                    f"develop draft.",
                )

    def test_latest_version_is_the_omg_catalog(self) -> None:
        for name, content in self.documents():
            with self.subTest(document=name):
                self.assertIn(
                    'latestVersion: "https://www.omg.org/spec/DPROD/"',
                    content,
                    f"{name}: latestVersion must be the OMG catalog entry, which "
                    f"always resolves to the newest published version.",
                )

    def test_this_version_carries_the_basepath_and_a_slug(self) -> None:
        template = SPEC_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(
            f'thisVersion: "{SPEC_BASE}{{{{ branch_slug }}}}/"',
            template,
            "thisVersion must use the /dprod basePath and the slugified branch; "
            "a raw branch name containing a slash does not resolve.",
        )

        archive = ARCHIVE_SPEC.read_text(encoding="utf-8")
        self.assertIn(f'thisVersion: "{SPEC_BASE}main/"', archive)

    def test_no_href_swallows_a_trailing_full_stop(self) -> None:
        """`href="....htm."` — the sentence's full stop inside the URL."""
        for name, content in self.documents():
            with self.subTest(document=name):
                offenders = re.findall(r'href="[^"]*\.(?:htm|html|org|com)\."', content)
                self.assertEqual([], offenders, f"{name}: {offenders}")


if __name__ == "__main__":
    unittest.main()
