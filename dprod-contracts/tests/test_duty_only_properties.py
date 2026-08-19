from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDFS


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
SPECIFICATION_FILE = CONTRACTS_DIR / "docs" / "specification.md"
DPROD = Namespace("https://www.omg.org/spec/DPROD/dprod/")

DUTY_ONLY_MESSAGE = (
    "dprod:deadline, dprod:subjectOfDuty, and dprod:objectOfDuty "
    "may be used only on odrl:Duty."
)


class DutyOnlyPropertyValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")

    def validate(self, statements: str, with_ontology: bool):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix dct: <http://purl.org/dc/terms/> .
                @prefix ex: <https://example.org/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                {statements}
            """,
            format="turtle",
        )
        if with_ontology:
            return validate(
                data_graph=data,
                shacl_graph=self.shapes,
                ont_graph=self.ontology,
                inference="rdfs",
                advanced=True,
            )
        return validate(
            data_graph=data,
            shacl_graph=self.shapes,
            advanced=True,
        )

    def assert_conforms(self, statements: str) -> None:
        for with_ontology in (True, False):
            with self.subTest(with_ontology=with_ontology):
                conforms, _, report = self.validate(statements, with_ontology)
                self.assertTrue(conforms, report)

    def assert_rejected(self, statements: str, message: str) -> None:
        for with_ontology in (True, False):
            with self.subTest(with_ontology=with_ontology):
                conforms, _, report = self.validate(statements, with_ontology)
                self.assertFalse(conforms, report)
                self.assertIn(message, report)

    def test_owl_domains_do_not_infer_duty_as_a_validation_fallback(self) -> None:
        for duty_only_property in (
            DPROD.deadline,
            DPROD.subjectOfDuty,
            DPROD.objectOfDuty,
        ):
            with self.subTest(duty_only_property=duty_only_property):
                self.assertEqual(
                    [],
                    list(self.ontology.objects(duty_only_property, RDFS.domain)),
                )

    def test_specification_documents_shacl_enforced_duty_scope(self) -> None:
        specification = SPECIFICATION_FILE.read_text(encoding="utf-8")

        self.assertGreaterEqual(
            specification.count(
                "| **Subject scope** | `odrl:Duty` (enforced by SHACL; no `rdfs:domain`) |"
            ),
            3,
        )
        self.assertIn("dprod-shapes:DutyOnlyPropertySubjectShape", specification)

    def test_duty_only_properties_are_rejected_on_other_rule_types(self) -> None:
        property_values = {
            "dprod:deadline": '"PT1H"^^xsd:duration',
            "dprod:subjectOfDuty": "ex:provider",
            "dprod:objectOfDuty": "ex:consumer",
        }
        for rule_class in ("odrl:Permission", "odrl:Prohibition"):
            for property_name, value in property_values.items():
                with self.subTest(rule_class=rule_class, property_name=property_name):
                    self.assert_rejected(
                        f"""
                        ex:rule a {rule_class} ;
                            odrl:action odrl:use ;
                            {property_name} {value} .
                        ex:provider a odrl:Party .
                        ex:consumer a odrl:Party .
                        """,
                        DUTY_ONLY_MESSAGE,
                    )

    def test_named_and_inline_duties_remain_valid(self) -> None:
        duty_properties = """
            odrl:action odrl:use ;
            dprod:deadline "PT1H"^^xsd:duration ;
            dprod:subjectOfDuty ex:provider ;
            dprod:objectOfDuty ex:consumer
        """
        self.assert_conforms(
            f"""
            ex:namedDuty a odrl:Duty ;
                {duty_properties} .
            [ a odrl:Duty ;
                {duty_properties}
            ] .
            ex:provider a odrl:Party .
            ex:consumer a odrl:Party .
            """
        )

    def test_obsolete_recurrence_is_rejected_on_every_rule_type(self) -> None:
        for rule_class in ("odrl:Duty", "odrl:Permission", "odrl:Prohibition"):
            with self.subTest(rule_class=rule_class):
                self.assert_rejected(
                    f"""
                    ex:rule a {rule_class} ;
                        odrl:action odrl:use ;
                        dprod:recurrence "FREQ=DAILY" .
                    """,
                    "dprod:recurrence is obsolete; use dprod:schedule",
                )

    def test_schedule_remains_valid_on_non_duty_resources(self) -> None:
        self.assert_conforms(
            '''
            ex:permission a odrl:Permission ;
                odrl:action odrl:use ;
                dprod:schedule ex:weekdaySchedule .

            ex:weekdaySchedule a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * 1-5" .
            '''
        )


if __name__ == "__main__":
    unittest.main()
