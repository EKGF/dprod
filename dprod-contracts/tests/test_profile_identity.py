"""An ODRL profile has its own identity, independent of the DPROD vocabulary."""
from pathlib import Path
import json
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, OWL, URIRef

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
PROF = Namespace("http://www.w3.org/ns/dx/prof/")
SH = Namespace("http://www.w3.org/ns/shacl#")
DPROD_ONTOLOGY = URIRef("https://ekgf.org/dprod/spec/develop/")
CONTRACTS_PROFILE = URIRef("https://ekgf.org/dprod/spec/develop/contracts/profile/")
PROFILE_GROUP = URIRef("https://ekgf.org/dprod/spec/develop/contracts/shapes/ProfilePropertyGroup")


class ContractsProfileIdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = Graph().parse(CONTRACTS / "dprod-contracts-prof.ttl")
        cls.shapes = Graph().parse(CONTRACTS / "dprod-contracts-shapes.ttl")

    def test_profile_is_distinct_from_the_unchanged_main_ontology(self):
        ontology = Graph().parse(ROOT / "ontology/dprod/dprod-ontology.ttl")
        self.assertIn((DPROD_ONTOLOGY, RDF.type, OWL.Ontology), ontology)
        self.assertEqual([CONTRACTS_PROFILE], list(self.profile.subjects(RDF.type, PROF.Profile)))
        self.assertFalse(any(self.profile.triples((DPROD_ONTOLOGY, None, None))))

    def test_every_policy_profile_shape_requires_the_contracts_profile(self):
        properties = list(self.shapes.subjects(SH.path, ODRL.profile))
        self.assertEqual(2, len(properties))
        for shape in properties:
            with self.subTest(shape=shape):
                self.assertEqual([CONTRACTS_PROFILE], list(self.shapes.objects(shape, SH.hasValue)))

    def test_profile_recognition_accepts_the_new_identifier_and_rejects_the_ontology_identifier(self):
        shapes = Graph()
        shapes.add((URIRef("urn:profile-test"), RDF.type, SH.NodeShape))
        shapes.add((URIRef("urn:profile-test"), SH.targetNode, URIRef("urn:policy")))
        shapes.add((URIRef("urn:profile-test"), SH.property, PROFILE_GROUP))
        for triple in self.shapes.triples((PROFILE_GROUP, None, None)):
            shapes.add(triple)
        for identifier, expected in [(CONTRACTS_PROFILE, True), (DPROD_ONTOLOGY, False)]:
            with self.subTest(identifier=identifier):
                data = Graph()
                data.add((URIRef("urn:policy"), ODRL.profile, identifier))
                conforms, _, _ = validate(data, shacl_graph=shapes)
                self.assertEqual(expected, conforms)
        data = Graph()
        data.add((URIRef("urn:policy"), ODRL.profile, CONTRACTS_PROFILE))
        data.add((URIRef("urn:policy"), ODRL.profile, URIRef("urn:additional-profile")))
        self.assertTrue(validate(data, shacl_graph=shapes)[0], "multiple profile identifiers remain permitted")

    def test_profile_artifacts_reference_existing_root_publication_downloads(self):
        artifacts = set(self.profile.objects(None, PROF.hasArtifact))
        expected = {
            URIRef("https://ekgf.org/dprod/spec/develop/dprod-contracts.ttl"),
            URIRef("https://ekgf.org/dprod/spec/develop/dprod-contracts-shapes.ttl"),
        }
        self.assertEqual(expected, artifacts)
        for artifact in artifacts:
            self.assertTrue((CONTRACTS / str(artifact).rsplit("/", 1)[1]).is_file())

    def test_all_shipped_policy_examples_use_the_distinct_identifier(self):
        examples = Graph()
        for path in sorted((CONTRACTS / "examples").glob("*.ttl")):
            examples.parse(path)
        values = set(examples.objects(None, ODRL.profile))
        self.assertEqual({CONTRACTS_PROFILE}, values)
        found = 0
        def check(value):
            nonlocal found
            if isinstance(value, dict):
                if "profile" in value:
                    self.assertEqual(str(CONTRACTS_PROFILE), value["profile"])
                    found += 1
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
        for path in sorted((ROOT / "examples/contracts").rglob("*.jsonld")):
            check(json.loads(path.read_text()))
        self.assertGreater(found, 0)


if __name__ == "__main__":
    unittest.main()
