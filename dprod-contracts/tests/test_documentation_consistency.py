from pathlib import Path
import re
import unittest

from rdflib import Graph, Namespace, URIRef


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = CONTRACTS_DIR / "docs"

DCT = Namespace("http://purl.org/dc/terms/")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
SH = Namespace("http://www.w3.org/ns/shacl#")

CONTRACTS_ONTOLOGY = URIRef("https://www.omg.org/spec/DPROD/contracts/")
DPROD_PROFILE = URIRef("https://www.omg.org/spec/DPROD/")
SET_SHAPE = URIRef("https://www.omg.org/spec/DPROD/contracts/shapes/SetShape")


class DocumentationConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(CONTRACTS_DIR / "dprod-contracts.ttl")
        cls.profile = Graph().parse(CONTRACTS_DIR / "dprod-contracts-prof.ttl")
        cls.shapes = Graph().parse(CONTRACTS_DIR / "dprod-contracts-shapes.ttl")

    def read(self, relative_path: str) -> str:
        return (CONTRACTS_DIR / relative_path).read_text(encoding="utf-8")

    def test_formal_semantics_subsection_numbers_are_unique(self) -> None:
        formal_semantics = self.read("docs/formal-semantics.md")
        subsection_numbers = re.findall(r"^### (\d+\.\d+)\b", formal_semantics, re.MULTILINE)

        duplicates = sorted(
            number for number in set(subsection_numbers) if subsection_numbers.count(number) > 1
        )
        self.assertEqual([], duplicates)

    def test_accepts_offer_definition_matches_the_ontology(self) -> None:
        specification = self.read("docs/specification.md")
        definition = str(
            self.ontology.value(
                URIRef("https://www.omg.org/spec/DPROD/dprod/acceptsOffer"),
                DCT.description,
            )
        )

        self.assertIn(f"| **Definition** | {definition}", specification)

    def test_set_target_documentation_matches_optional_shape_cardinality(self) -> None:
        target_property_shapes = [
            property_shape
            for property_shape in self.shapes.objects(SET_SHAPE, SH.property)
            if self.shapes.value(property_shape, SH.path) == ODRL.target
        ]
        self.assertEqual(1, len(target_property_shapes))
        self.assertIsNone(self.shapes.value(target_property_shapes[0], SH.minCount))

        specification = self.read("docs/specification.md")
        writer_guide = self.read("docs/policy-writers-guide.md")
        self.assertIn("| `odrl:target` | ODRL | 0..* |", specification)
        self.assertIn("may declare `odrl:target`", specification)
        self.assertIn("A policy-level `odrl:target` is optional", writer_guide)

    def test_readme_uses_the_normative_evaluation_result_fields(self) -> None:
        readme = self.read("README.md")
        expected_fields = (
            "decision:",
            "grantorDuties:",
            "granteeDuties:",
            "violations:",
            "inputProvenance:",
            "explanation:",
        )

        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, readme)
        self.assertNotIn("assignerDuties:", readme)
        self.assertNotIn("assigneeDuties:", readme)
        self.assertIn(
            "Eval : Request × Set<Policy> × Σ × WorldSnapshot → Success(Result) | Failure(EvaluationError)",
            readme,
        )
        self.assertNotIn("Decision x DutySet", readme)

    def test_deleted_select_extension_is_not_advertised(self) -> None:
        readme = self.read("README.md")
        overview = self.read("docs/overview.md")

        self.assertNotIn("DataContract, path, select", readme)
        self.assertNotIn("path, select, RuntimeReference", overview)

    def test_path_examples_use_domain_namespace_terms(self) -> None:
        path_comment = str(
            self.ontology.value(
                URIRef("https://www.omg.org/spec/DPROD/dprod/path"),
                URIRef("http://www.w3.org/2000/01/rdf-schema#comment"),
            )
        )

        for stale_term in ("dprod:environment", "dprod:timeliness", "dprod:role"):
            with self.subTest(stale_term=stale_term):
                self.assertNotIn(stale_term, path_comment)
        for root_term in (
            "dprod:request",
            "dprod:state",
            "dprod:agent",
            "dprod:clock",
        ):
            with self.subTest(root_term=root_term):
                self.assertIn(root_term, path_comment)
        for domain_term in ("ex:marketOpen",):
            with self.subTest(domain_term=domain_term):
                self.assertIn(domain_term, path_comment)

    def test_profile_title_and_modified_date_match_the_contracts_ontology(self) -> None:
        self.assertEqual(
            self.ontology.value(CONTRACTS_ONTOLOGY, DCT.title),
            self.profile.value(DPROD_PROFILE, DCT.title),
        )
        self.assertEqual(
            self.ontology.value(CONTRACTS_ONTOLOGY, DCT.modified),
            self.profile.value(DPROD_PROFILE, DCT.modified),
        )

    def test_named_duty_profile_context_is_documented(self) -> None:
        contracts_guide = self.read("docs/contracts-guide.md")
        self.assertIn(
            "Named duties obtain their DPROD profile context from the containing policy",
            contracts_guide,
        )


if __name__ == "__main__":
    unittest.main()
