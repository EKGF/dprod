"""Each DPROD ontology file names its preferred prefix and namespace (issue #217).

Deployment and import tooling, such as eccenca's cmemc, reads
`vann:preferredNamespacePrefix` and `vann:preferredNamespaceUri` to decide which
graph an imported file belongs to (PR #170). The namespace must be the
ontology's own IRI, so that moving the namespace (to OMG, #275) cannot leave a
stale value behind.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from rdflib import OWL, RDF, Graph, Literal, Namespace, URIRef

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = REPOSITORY_ROOT / "ontology" / "dprod"
VANN = Namespace("http://purl.org/vocab/vann/")

# File, and the prefix it is meant to be known by
ONTOLOGY_FILES = (
    (ONTOLOGY_DIR / "dprod-ontology.ttl", "dprod"),
    (ONTOLOGY_DIR / "dprod-shapes.ttl", "dprod-shapes"),
)


class VannMetadataTest(unittest.TestCase):
    def test_preferred_namespace_is_the_ontology_iri(self) -> None:
        for path, prefix in ONTOLOGY_FILES:
            with self.subTest(file=path.name):
                graph = Graph().parse(path, format="turtle")
                ontologies = list(graph.subjects(RDF.type, OWL.Ontology))
                self.assertEqual(1, len(ontologies), "expected exactly one owl:Ontology")
                ontology = ontologies[0]

                self.assertEqual(
                    [Literal(prefix)],
                    list(graph.objects(ontology, VANN.preferredNamespacePrefix)),
                )
                self.assertEqual(
                    [Literal(str(ontology))],
                    list(graph.objects(ontology, VANN.preferredNamespaceUri)),
                    "vann:preferredNamespaceUri must be the ontology IRI, as a plain literal",
                )

    def test_preferred_prefix_is_declared_for_that_namespace(self) -> None:
        for path, prefix in ONTOLOGY_FILES:
            with self.subTest(file=path.name):
                graph = Graph().parse(path, format="turtle")
                ontology = next(graph.subjects(RDF.type, OWL.Ontology))
                declared = dict(graph.namespaces())

                self.assertEqual(URIRef(str(ontology)), declared.get(prefix))


if __name__ == "__main__":
    unittest.main()
