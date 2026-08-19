from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
FORMAL_SEMANTICS_FILE = CONTRACTS_DIR / "docs" / "formal-semantics.md"

DPROD = Namespace("https://www.omg.org/spec/DPROD/dprod/")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")

MEMBERSHIP_MESSAGE = (
    "odrl:partOf must link an odrl:Asset to an odrl:AssetCollection or an "
    "odrl:Party to an odrl:PartyCollection."
)


class OdrlCollectionMembershipTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")

    def validate(self, statements: str):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix ex: <https://example.org/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .

                {statements}
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

    def assert_conforms(self, statements: str) -> None:
        conforms, _, report = self.validate(statements)
        self.assertTrue(conforms, report)

    def assert_rejected(self, statements: str, message: str) -> None:
        conforms, _, report = self.validate(statements)
        self.assertFalse(conforms)
        self.assertIn(message, report)

    def test_explicit_asset_collection_membership_is_supported(self) -> None:
        self.assert_conforms(
            """
            ex:table a odrl:Asset ;
                odrl:partOf ex:schema .
            ex:schema a odrl:AssetCollection .
            """
        )

    def test_explicit_party_collection_membership_is_supported(self) -> None:
        self.assert_conforms(
            """
            ex:analyst a odrl:Party ;
                odrl:partOf ex:analyticsTeam .
            ex:analyticsTeam a odrl:PartyCollection .
            """
        )

    def test_nested_collection_membership_is_supported(self) -> None:
        self.assert_conforms(
            """
            ex:table a odrl:Asset ;
                odrl:partOf ex:schema .
            ex:schema a odrl:AssetCollection ;
                odrl:partOf ex:dataPlatform .
            ex:dataPlatform a odrl:AssetCollection .

            ex:analyst a odrl:Party ;
                odrl:partOf ex:analyticsTeam .
            ex:analyticsTeam a odrl:PartyCollection ;
                odrl:partOf ex:dataDivision .
            ex:dataDivision a odrl:PartyCollection .
            """
        )

    def test_asset_membership_rejects_party_collection_target(self) -> None:
        self.assert_rejected(
            """
            ex:table a odrl:Asset ;
                odrl:partOf ex:analyticsTeam .
            ex:analyticsTeam a odrl:PartyCollection .
            """,
            MEMBERSHIP_MESSAGE,
        )

    def test_party_membership_rejects_asset_collection_target(self) -> None:
        self.assert_rejected(
            """
            ex:analyst a odrl:Party ;
                odrl:partOf ex:schema .
            ex:schema a odrl:AssetCollection .
            """,
            MEMBERSHIP_MESSAGE,
        )

    def test_nested_membership_rejects_cross_kind_collection_target(self) -> None:
        self.assert_rejected(
            """
            ex:schema a odrl:AssetCollection ;
                odrl:partOf ex:businessUnit .
            ex:businessUnit a odrl:PartyCollection .
            """,
            MEMBERSHIP_MESSAGE,
        )

    def test_obsolete_dprod_hierarchy_properties_fail_fast(self) -> None:
        for statement, message in (
            (
                "ex:table a odrl:Asset ; dprod:partOf ex:schema .",
                "dprod:partOf is obsolete; use odrl:partOf.",
            ),
            (
                "ex:analyst a odrl:Party ; dprod:memberOf ex:team .",
                "dprod:memberOf is obsolete; use odrl:partOf.",
            ),
        ):
            with self.subTest(statement=statement):
                self.assert_rejected(statement, message)

    def test_collection_source_is_rejected_until_resolution_is_defined(self) -> None:
        for collection_class in ("odrl:AssetCollection", "odrl:PartyCollection"):
            with self.subTest(collection_class=collection_class):
                self.assert_rejected(
                    f"""
                    ex:collection a {collection_class} ;
                        odrl:source ex:catalogQuery .
                    """,
                    "DPROD contracts support explicit collection membership only; "
                    "odrl:source collection resolution is not supported.",
                )

    def test_collection_refinement_is_rejected_until_semantics_are_defined(self) -> None:
        for collection_class in ("odrl:AssetCollection", "odrl:PartyCollection"):
            with self.subTest(collection_class=collection_class):
                self.assert_rejected(
                    f"""
                    ex:collection a {collection_class} ;
                        odrl:refinement ex:constraint .
                    """,
                    "DPROD contracts support explicit collection membership only; "
                    "collection odrl:refinement is not supported.",
                )

    def test_duplicate_dprod_properties_are_removed_from_the_ontology(self) -> None:
        for obsolete_property in (DPROD.partOf, DPROD.memberOf):
            with self.subTest(obsolete_property=obsolete_property):
                self.assertEqual(
                    [],
                    list(self.ontology.triples((obsolete_property, None, None))),
                )
                self.assertEqual(
                    [],
                    list(self.ontology.triples((None, RDFS.subPropertyOf, obsolete_property))),
                )

    def test_dprod_does_not_redeclare_odrl_part_of_as_transitive(self) -> None:
        self.assertNotIn(
            (ODRL.partOf, RDF.type, OWL.TransitiveProperty),
            self.ontology,
        )

    def test_examples_use_standard_odrl_collection_membership(self) -> None:
        for example in sorted((CONTRACTS_DIR / "examples").glob("*.ttl")):
            graph = Graph().parse(example, format="turtle")
            with self.subTest(example=example):
                self.assertFalse(any(graph.triples((None, DPROD.partOf, None))))
                self.assertFalse(any(graph.triples((None, DPROD.memberOf, None))))
                for _, _, collection in graph.triples((None, ODRL.partOf, None)):
                    self.assertTrue(
                        (collection, RDF.type, ODRL.AssetCollection) in graph
                        or (collection, RDF.type, ODRL.PartyCollection) in graph,
                        f"{collection} is not typed as an ODRL collection in {example}",
                    )

    def test_formal_semantics_uses_one_typed_transitive_relation(self) -> None:
        formal_semantics = FORMAL_SEMANTICS_FILE.read_text(encoding="utf-8")

        self.assertIn("transitive closure of `odrl:partOf`", formal_semantics)
        self.assertNotIn("`dprod:partOf`", formal_semantics)
        self.assertNotIn("`dprod:memberOf`", formal_semantics)
        self.assertNotIn("memberOf⁺", formal_semantics)


if __name__ == "__main__":
    unittest.main()
