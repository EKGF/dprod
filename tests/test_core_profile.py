"""DPROD core is declared in RDF as a W3C PROF profile of DCAT 3 (#300)."""
from pathlib import Path
import unittest

from rdflib import Graph, Namespace, RDF, URIRef, XSD
from rdflib.namespace import DCTERMS

ROOT = Path(__file__).resolve().parents[1]
PROF = Namespace("http://www.w3.org/ns/dx/prof/")
ROLE = Namespace("http://www.w3.org/ns/dx/prof/role/")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
GA = Namespace("https://ekgf.org/ontology/grapharch#")
BASE = "https://ekgf.org/dprod/spec/develop/"
CORE_PROFILE = URIRef(BASE + "profile/")
CONTRACTS_PROFILE = URIRef(BASE + "contracts/profile/")
DCAT3 = URIRef("https://www.w3.org/TR/vocab-dcat-3/")


class CoreProfileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Graph().parse(ROOT / "ontology/dprod/dprod-prof.ttl")
        cls.contracts = Graph().parse(ROOT / "dprod-contracts/dprod-contracts-prof.ttl")

    def test_core_is_a_profile_of_the_dcat3_standard(self):
        self.assertEqual([CORE_PROFILE], list(self.core.subjects(RDF.type, PROF.Profile)))
        self.assertEqual([DCAT3], list(self.core.objects(CORE_PROFILE, PROF.isProfileOf)))
        self.assertIn((DCAT3, RDF.type, DCTERMS.Standard), self.core)
        for predicate in (DCTERMS.title, DCTERMS.description, DCTERMS.modified):
            with self.subTest(predicate=predicate):
                self.assertIsNotNone(self.core.value(CORE_PROFILE, predicate))

    def test_tokens_are_distinct(self):
        core = self.core.value(CORE_PROFILE, PROF.hasToken)
        contracts = self.contracts.value(CONTRACTS_PROFILE, PROF.hasToken)
        self.assertEqual(XSD.token, core.datatype)
        self.assertEqual("dprod-core", str(core))
        self.assertNotEqual(str(core), str(contracts))

    def test_resource_descriptors_name_published_artifacts_by_role(self):
        roles = {}
        for descriptor in self.core.objects(CORE_PROFILE, PROF.hasResource):
            self.assertIn((descriptor, RDF.type, PROF.ResourceDescriptor), self.core)
            roles[self.core.value(descriptor, PROF.hasRole)] = self.core.value(descriptor, PROF.hasArtifact)
            if self.core.value(descriptor, PROF.hasRole) != ROLE.specification:
                self.assertIsNotNone(self.core.value(descriptor, DCTERMS.conformsTo))
        self.assertEqual({
            ROLE.vocabulary: URIRef(BASE + "dprod.ttl"),
            ROLE.validation: URIRef(BASE + "dprod-shapes.ttl"),
            ROLE.schema: URIRef(BASE + "dprod-context.jsonld"),
            ROLE.specification: URIRef(BASE + "specification/"),
        }, roles)

    def test_contracts_profile_extends_odrl_and_dprod_core(self):
        self.assertEqual({ODRL.core, CORE_PROFILE},
                         set(self.contracts.objects(CONTRACTS_PROFILE, PROF.isProfileOf)))

    def test_develop_publication_collects_and_publishes_the_profile(self):
        definitions = Graph().parse(ROOT / "publication/definitions/develop.ttl")
        project = URIRef("urn:dprod-showcase:project")
        collectors = [use for use in definitions.objects(project, GA.collector)
                      if str(definitions.value(use, GA.sourcePath)) == "ontology/dprod/dprod-prof.ttl"]
        self.assertEqual(1, len(collectors))
        self.assertEqual(CORE_PROFILE, definitions.value(collectors[0], GA.subject))
        targets = [target for target in definitions.objects(project, GA.target)
                   if str(definitions.value(target, GA.slug)) == "dprod-prof"]
        self.assertEqual(1, len(targets))
        self.assertEqual(collectors[0], definitions.value(targets[0], GA.rdfSource))
        sections = set(definitions.subjects(GA.termType, PROF.Profile))
        self.assertEqual(1, len(sections))


if __name__ == "__main__":
    unittest.main()
