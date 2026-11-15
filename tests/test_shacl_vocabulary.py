"""Every sh: IRI used in the DPROD shapes files must be a SHACL term.

SHACL processors ignore unknown predicates, so a misspelled term such as
sh:targetSubjectOf (instead of sh:targetSubjectsOf) silently disables a
shape. The SHACL vocabulary is the W3C shacl.ttl bundled with pyshacl.
"""

from importlib.resources import files
from pathlib import Path
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import SH


ROOT = Path(__file__).resolve().parents[1]
SHAPES_FILES = (
    ROOT / "ontology" / "dprod" / "dprod-shapes.ttl",
    ROOT / "dprod-contracts" / "dprod-contracts-shapes.ttl",
)
MISSPELLED_TARGET = URIRef(f"{SH}targetSubjectOf")
SHACL_VOCABULARY = files("pyshacl") / "assets" / "shacl.ttl"


def shacl_terms() -> frozenset[URIRef]:
    vocabulary = Graph().parse(data=SHACL_VOCABULARY.read_text(), format="turtle")
    return frozenset(
        subject
        for subject in vocabulary.subjects()
        if isinstance(subject, URIRef) and str(subject).startswith(str(SH))
    )


def used_shacl_iris(graph: Graph) -> frozenset[URIRef]:
    return frozenset(
        term
        for triple in graph
        for term in triple
        if isinstance(term, URIRef) and str(term).startswith(str(SH))
    )


class ShaclVocabularyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.terms = shacl_terms()

    def test_vocabulary_contains_known_terms(self) -> None:
        self.assertIn(SH.targetSubjectsOf, self.terms)
        self.assertNotIn(MISSPELLED_TARGET, self.terms)

    def test_shapes_files_use_only_shacl_terms(self) -> None:
        for shapes_file in SHAPES_FILES:
            with self.subTest(shapes_file=shapes_file.relative_to(ROOT)):
                graph = Graph().parse(shapes_file, format="turtle")
                unknown = sorted(used_shacl_iris(graph) - self.terms)
                self.assertEqual([], unknown)

    def test_misspelled_term_is_reported(self) -> None:
        graph = Graph().parse(
            data=(
                "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
                "<urn:x:shape> sh:targetSubjectOf <urn:x:p> ."
            ),
            format="turtle",
        )
        self.assertEqual(
            {MISSPELLED_TARGET}, used_shacl_iris(graph) - self.terms
        )


if __name__ == "__main__":
    unittest.main()
