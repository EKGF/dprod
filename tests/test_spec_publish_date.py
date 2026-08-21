"""The spec's publication date must be authored, never inferred.

ReSpec runs in the reader's browser. With no `publishDate` in its config it
stamps the day the page is *viewed*, so every DPROD document — including the
frozen 1.0 archive — reported that it had been published today, and the date
changed every morning (issue #253).

Deriving the date from git history does not fix it either: a maintenance
commit that retires a URL or fixes a typo would silently republish the
standard. The date is therefore a triple, `dct:issued`, and these tests keep
it that way.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from rdflib import DCTERMS, Graph, URIRef

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_FILE = REPOSITORY_ROOT / "ontology" / "dprod" / "dprod-ontology.ttl"
SPEC_TEMPLATE = REPOSITORY_ROOT / "respec" / "template.html"
ARCHIVE_SPEC = (
    REPOSITORY_ROOT / "site" / "public" / "spec" / "archive" / "1.0" / "index.html"
)
ONTOLOGY_IRI = URIRef("https://www.omg.org/spec/DPROD/dprod/")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SpecPublishDateTest(unittest.TestCase):
    def test_ontology_carries_exactly_one_issued_date(self) -> None:
        graph = Graph()
        graph.parse(ONTOLOGY_FILE, format="ttl")

        issued = list(graph.objects(ONTOLOGY_IRI, DCTERMS.issued))

        self.assertEqual(
            1,
            len(issued),
            "The DPROD ontology must carry exactly one dct:issued; it is the "
            "single source of the spec's publication date.",
        )
        self.assertRegex(str(issued[0]), ISO_DATE)

    def test_template_pins_the_publish_date(self) -> None:
        template = SPEC_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn(
            'publishDate: "{{ publish_date }}"',
            template,
            "respec/template.html must pin publishDate. Without it ReSpec "
            "falls back to the date the page is viewed.",
        )

    def test_frozen_archive_pins_a_literal_publish_date(self) -> None:
        """The 1.0 archive is immutable, so its date is a literal, not a build value."""
        archive = ARCHIVE_SPEC.read_text(encoding="utf-8")

        match = re.search(r'publishDate:\s*"(\d{4}-\d{2}-\d{2})"', archive)

        self.assertIsNotNone(
            match,
            "The frozen 1.0 archive must pin its own publishDate, otherwise an "
            "immutable standard reports a new publication date every day.",
        )
        self.assertNotIn(
            "{{",
            match.group(0),
            "The archive is a static snapshot and must not be templated.",
        )


if __name__ == "__main__":
    unittest.main()
