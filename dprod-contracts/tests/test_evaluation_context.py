from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace, RDF, RDFS, OWL


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "dprod-contracts"
ONTOLOGY_PATH = CONTRACTS / "dprod-contracts.ttl"
SHAPES_PATH = CONTRACTS / "dprod-contracts-shapes.ttl"
FORMAL_SEMANTICS_PATH = CONTRACTS / "docs" / "formal-semantics.md"

DPROD = Namespace("https://www.omg.org/spec/DPROD/dprod/")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
PROV = Namespace("http://www.w3.org/ns/prov#")


class EvaluationContextOntologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(ONTOLOGY_PATH, format="turtle")
        cls.formal_semantics = FORMAL_SEMANTICS_PATH.read_text()

    def test_runtime_reference_model_is_replaced_by_one_evaluation_context(self) -> None:
        self.assertNotIn((DPROD.RuntimeReference, RDF.type, OWL.Class), self.ontology)
        self.assertNotIn((DPROD.currentDateTime, None, None), self.ontology)

        self.assertIn((DPROD.EvaluationContext, RDF.type, OWL.Class), self.ontology)
        self.assertIn(
            (DPROD.EvaluationContext, RDFS.subClassOf, PROV.Entity), self.ontology
        )

        expected_properties = {
            DPROD.request: OWL.ObjectProperty,
            DPROD.state: OWL.ObjectProperty,
            DPROD.agent: OWL.ObjectProperty,
            DPROD.clock: OWL.DatatypeProperty,
        }
        for prop, property_type in expected_properties.items():
            with self.subTest(prop=prop):
                self.assertIn((prop, RDF.type, property_type), self.ontology)
                self.assertIn(
                    (prop, RDFS.domain, DPROD.EvaluationContext), self.ontology
                )

    def test_builtins_use_the_same_path_resolver_as_profile_operands(self) -> None:
        self.assertIn((DPROD.currentAgent, RDF.type, ODRL.LeftOperand), self.ontology)
        self.assertIn((DPROD.currentAgent, DPROD.path, DPROD.agent), self.ontology)
        self.assertNotIn((DPROD.currentAgent, RDF.type, ODRL.Party), self.ontology)

        self.assertIn((ODRL.dateTime, DPROD.path, DPROD.clock), self.ontology)

    def test_formal_semantics_has_one_fail_fast_resolver(self) -> None:
        self.assertNotIn("RuntimeRef ::=", self.formal_semantics)
        self.assertNotIn("resolveRuntime", self.formal_semantics)
        self.assertNotIn("Unknown runtime reference", self.formal_semantics)
        self.assertIn("traverse(op.path, Env.node)", self.formal_semantics)
        self.assertIn("ResolutionError", self.formal_semantics)
        self.assertIn("must not be converted to `false`", self.formal_semantics)


class EvaluationContextValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shapes = Graph().parse(SHAPES_PATH, format="turtle")
        cls.ontology = Graph().parse(ONTOLOGY_PATH, format="turtle")

    def validate_operand(self, operand_definition: str):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix ex: <https://example.com/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

                ex:constraint
                  a odrl:Constraint ;
                  odrl:leftOperand ex:operand ;
                  odrl:operator odrl:eq ;
                  odrl:rightOperand true .

                ex:operand a odrl:LeftOperand ;
                  {operand_definition} .
            """,
            format="turtle",
        )
        return validate(
            data_graph=data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            advanced=True,
        )

    def validate_context(self, context_definition: str):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix ex: <https://example.com/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .
                @prefix prov: <http://www.w3.org/ns/prov#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                ex:request a prov:Entity .
                ex:snapshot a prov:Entity .
                ex:alice a odrl:Party .

                ex:context a dprod:EvaluationContext ;
                  {context_definition} .
            """,
            format="turtle",
        )
        return validate(
            data_graph=data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            advanced=True,
        )

    def test_request_and_world_state_paths_share_one_rooted_shape(self) -> None:
        for path in (
            "dprod:path (dprod:request odrl:purpose)",
            "dprod:path (dprod:state ex:marketOpen)",
            "dprod:path dprod:agent",
            "dprod:path dprod:clock",
        ):
            with self.subTest(path=path):
                conforms, _, report = self.validate_operand(path)
                self.assertTrue(conforms, str(report))

    def test_unrooted_operand_path_is_rejected(self) -> None:
        conforms, _, report = self.validate_operand("dprod:path ex:marketOpen")
        self.assertFalse(conforms, str(report))
        self.assertIn("evaluation-context root", str(report))

    def test_operand_without_path_is_rejected(self) -> None:
        conforms, _, report = self.validate_operand("rdfs:label \"missing path\"")
        self.assertFalse(conforms, str(report))
        self.assertIn("exactly one dprod:path", str(report))

    def test_complete_evaluation_context_is_accepted(self) -> None:
        conforms, _, report = self.validate_context(
            """dprod:request ex:request ;
               dprod:state ex:snapshot ;
               dprod:agent ex:alice ;
               dprod:clock \"2026-08-20T12:00:00Z\"^^xsd:dateTime"""
        )
        self.assertTrue(conforms, str(report))

    def test_evaluation_context_without_world_snapshot_is_rejected(self) -> None:
        conforms, _, report = self.validate_context(
            """dprod:request ex:request ;
               dprod:agent ex:alice ;
               dprod:clock \"2026-08-20T12:00:00Z\"^^xsd:dateTime"""
        )
        self.assertFalse(conforms, str(report))
        self.assertIn("exactly one immutable dprod:state snapshot", str(report))

    def test_obsolete_runtime_reference_type_is_rejected(self) -> None:
        data = Graph().parse(
            data="""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix ex: <https://example.com/> .

                ex:unknown a dprod:RuntimeReference .
            """,
            format="turtle",
        )
        conforms, _, report = validate(
            data_graph=data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            advanced=True,
        )
        self.assertFalse(conforms, str(report))
        self.assertIn("dprod:RuntimeReference is obsolete", str(report))


if __name__ == "__main__":
    unittest.main()
