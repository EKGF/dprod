from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS, SH, SKOS


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CORE_ONTOLOGY_FILE = REPOSITORY_ROOT / "ontology" / "dprod" / "dprod-ontology.ttl"
CORE_SHAPES_FILE = REPOSITORY_ROOT / "ontology" / "dprod" / "dprod-shapes.ttl"
CONTRACTS_DIR = REPOSITORY_ROOT / "dprod-contracts"
CONTRACTS_ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"
CONTRACTS_SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
FORMAL_SEMANTICS_FILE = CONTRACTS_DIR / "docs" / "formal-semantics.md"

DPROD = Namespace("https://www.omg.org/spec/DPROD/dprod/")
DPROD_SHAPES = Namespace("https://www.omg.org/spec/DPROD/shapes/")
DPROD_CONTRACTS_SHAPES = Namespace(
    "https://www.omg.org/spec/DPROD/contracts/shapes/"
)
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
EX = Namespace("https://example.org/")


class LifecycleStatusOntologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = Graph().parse(CORE_ONTOLOGY_FILE, format="turtle")
        cls.core_shapes = Graph().parse(CORE_SHAPES_FILE, format="turtle")
        cls.contracts = Graph().parse(CONTRACTS_ONTOLOGY_FILE, format="turtle")
        cls.contract_shapes = Graph().parse(CONTRACTS_SHAPES_FILE, format="turtle")
        cls.ontology = cls.core + cls.contracts

    def assert_property(
        self,
        graph: Graph,
        property_iri,
        *,
        domain=None,
        subproperty=None,
    ) -> None:
        self.assertIn((property_iri, RDF.type, OWL.ObjectProperty), graph)
        self.assertIn((property_iri, RDFS.range, SKOS.Concept), graph)
        if domain is None:
            self.assertEqual([], list(graph.objects(property_iri, RDFS.domain)))
        else:
            self.assertIn((property_iri, RDFS.domain, domain), graph)
        if subproperty is not None:
            self.assertIn(
                (property_iri, RDFS.subPropertyOf, subproperty),
                graph,
            )

    def assert_term_absent(self, graph: Graph, term) -> None:
        self.assertFalse(
            any(graph.triples((term, None, None)))
            or any(graph.triples((None, term, None)))
            or any(graph.triples((None, None, term))),
            f"obsolete term remains in RDF: {term}",
        )

    def test_core_owns_generic_and_data_product_status_properties(self) -> None:
        self.assert_property(self.core, DPROD.lifecycleStatus)
        self.assert_property(
            self.core,
            DPROD.dataProductLifecycleStatus,
            domain=DPROD.DataProduct,
            subproperty=DPROD.lifecycleStatus,
        )

    def test_contract_status_properties_use_the_core_hierarchy(self) -> None:
        self.assert_property(
            self.contracts,
            DPROD.offerLifecycleStatus,
            domain=DPROD.DataOffer,
            subproperty=DPROD.lifecycleStatus,
        )
        self.assert_property(
            self.contracts,
            DPROD.contractLifecycleStatus,
            domain=DPROD.DataContract,
            subproperty=DPROD.lifecycleStatus,
        )
        self.assertNotIn(
            (DPROD.dutyState, RDFS.subPropertyOf, DPROD.lifecycleStatus),
            self.contracts,
        )

    def test_supplied_vocabularies_are_open_skos_concept_schemes(self) -> None:
        self.assertIn(
            (DPROD.DataProductLifecycleStatus, RDF.type, SKOS.ConceptScheme),
            self.core,
        )
        self.assertNotIn(
            (DPROD.DataProductLifecycleStatus, RDF.type, OWL.Class),
            self.core,
        )
        self.assertIn(
            (DPROD.DataContractLifecycleStatus, RDF.type, SKOS.ConceptScheme),
            self.contracts,
        )

    def test_obsolete_mixed_capitalization_terms_are_removed(self) -> None:
        self.assert_term_absent(self.ontology, DPROD.offerLifeCycleStatus)
        self.assert_term_absent(self.ontology, DPROD.contractLifeCycleStatus)
        self.assert_term_absent(self.ontology, DPROD.DataContractLifeCycleStatus)

        expected_rejections = (
            (
                DPROD_CONTRACTS_SHAPES.RejectObsoleteOfferLifecycleStatusSpellingShape,
                DPROD.offerLifeCycleStatus,
            ),
            (
                DPROD_CONTRACTS_SHAPES.RejectObsoleteContractLifecycleStatusSpellingShape,
                DPROD.contractLifeCycleStatus,
            ),
        )
        for shape, obsolete_property in expected_rejections:
            with self.subTest(shape=shape):
                self.assertIn(
                    (shape, SH.targetSubjectsOf, obsolete_property),
                    self.contract_shapes,
                )

    def test_shapes_enforce_canonical_properties_and_skos_values(self) -> None:
        expected_paths = (
            (
                self.core_shapes,
                DPROD_SHAPES["DataProduct-dataProductLifecycleStatus"],
                DPROD.dataProductLifecycleStatus,
            ),
            (
                self.contract_shapes,
                DPROD_CONTRACTS_SHAPES.OfferLifecycleStatusPropertyGroup,
                DPROD.offerLifecycleStatus,
            ),
            (
                self.contract_shapes,
                DPROD_CONTRACTS_SHAPES.ContractLifecycleStatusPropertyGroup,
                DPROD.contractLifecycleStatus,
            ),
        )

        for graph, shape, path in expected_paths:
            with self.subTest(shape=shape):
                self.assertIn((shape, SH.path, path), graph)
                self.assertIn((shape, SH["class"], SKOS.Concept), graph)
                self.assertIn((shape, SH.maxCount, None), graph)

    def test_authored_artifacts_use_only_canonical_lifecycle_names(self) -> None:
        authored_files = [
            CORE_ONTOLOGY_FILE,
            CORE_SHAPES_FILE,
            REPOSITORY_ROOT / "examples" / "dprod-example.json",
            REPOSITORY_ROOT / "respec" / "template.html",
            CONTRACTS_ONTOLOGY_FILE,
            CONTRACTS_DIR / "README.md",
            *sorted((CONTRACTS_DIR / "docs").glob("*.md")),
            *sorted((CONTRACTS_DIR / "examples").glob("*.md")),
            *sorted((CONTRACTS_DIR / "examples").glob("*.ttl")),
        ]
        obsolete_names = (
            "offerLifeCycleStatus",
            "contractLifeCycleStatus",
            "DataContractLifeCycleStatus",
        )

        for path in authored_files:
            content = path.read_text(encoding="utf-8")
            for obsolete_name in obsolete_names:
                with self.subTest(path=path, obsolete_name=obsolete_name):
                    self.assertNotIn(obsolete_name, content)

        for path in (
            REPOSITORY_ROOT / "examples" / "dprod-example.json",
            REPOSITORY_ROOT / "respec" / "template.html",
        ):
            with self.subTest(path=path, obsolete_name="lifecycleStatus key"):
                self.assertNotIn('"lifecycleStatus"', path.read_text(encoding="utf-8"))

        model_svg = (REPOSITORY_ROOT / "assets" / "dprod-model.svg").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(">+dprod:lifecycleStatus<", model_svg)
        self.assertIn(">+dprod:dataProductLifecycleStatus<", model_svg)

    def test_formal_semantics_separates_computed_duty_state(self) -> None:
        content = FORMAL_SEMANTICS_FILE.read_text(encoding="utf-8")

        self.assertNotIn(
            "`State` is a unified lifecycle enum shared by duties, contracts, "
            "and subscriptions.",
            content,
        )
        self.assertIn(
            "The formal `State` domain contains evaluator-computed duty states only.",
            content,
        )


class LifecycleStatusValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        core = Graph().parse(CORE_ONTOLOGY_FILE, format="turtle")
        contracts = Graph().parse(CONTRACTS_ONTOLOGY_FILE, format="turtle")
        cls.ontology = core + contracts
        cls.shapes = Graph().parse(CONTRACTS_SHAPES_FILE, format="turtle")

    def validate(self, lifecycle_statement: str):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix ex: <https://example.org/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .
                @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

                ex:status a skos:Concept .
                ex:offer
                    a dprod:DataOffer ;
                    odrl:profile <https://www.omg.org/spec/DPROD/> ;
                    odrl:assigner ex:provider ;
                    odrl:permission [
                        a odrl:Permission ;
                        odrl:action odrl:use ;
                        odrl:target ex:asset
                    ] ;
                    {lifecycle_statement}
                .
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

    def test_enterprise_skos_status_is_accepted(self) -> None:
        conforms, _, report = self.validate(
            "dprod:offerLifecycleStatus ex:status"
        )

        self.assertTrue(conforms, report)

    def test_contract_status_on_offer_fails_fast(self) -> None:
        conforms, _, report = self.validate(
            "dprod:contractLifecycleStatus ex:status"
        )

        self.assertFalse(conforms)
        self.assertIn(
            "DataOffer must not use dprod:contractLifecycleStatus.",
            report,
        )

    def test_data_product_status_on_offer_fails_fast(self) -> None:
        conforms, _, report = self.validate(
            "dprod:dataProductLifecycleStatus ex:status"
        )

        self.assertFalse(conforms)
        self.assertIn(
            "DataOffer must not use dprod:dataProductLifecycleStatus.",
            report,
        )

    def test_obsolete_offer_status_fails_fast(self) -> None:
        conforms, _, report = self.validate(
            "dprod:offerLifeCycleStatus ex:status"
        )

        self.assertFalse(conforms)
        self.assertIn(
            "dprod:offerLifeCycleStatus is obsolete; use "
            "dprod:offerLifecycleStatus.",
            report,
        )


if __name__ == "__main__":
    unittest.main()
