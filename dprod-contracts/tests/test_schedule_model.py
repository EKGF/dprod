from pathlib import Path
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, XSD


CONTRACTS_DIR = Path(__file__).resolve().parents[1]
ONTOLOGY_FILE = CONTRACTS_DIR / "dprod-contracts.ttl"
SHAPES_FILE = CONTRACTS_DIR / "dprod-contracts-shapes.ttl"
FORMAL_SEMANTICS_FILE = CONTRACTS_DIR / "docs" / "formal-semantics.md"

DPROD = Namespace("https://www.omg.org/spec/DPROD/dprod/")
DPROD_CONTRACTS_SHAPES = Namespace(
    "https://www.omg.org/spec/DPROD/contracts/shapes/"
)
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")


class ScheduleOntologyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")

    def test_schedule_is_a_reusable_identified_resource(self) -> None:
        self.assertIn((DPROD.Schedule, RDF.type, OWL.Class), self.ontology)
        self.assertIn((DPROD.ScheduleFormat, RDF.type, OWL.Class), self.ontology)
        self.assertIn((DPROD.schedule, RDF.type, OWL.ObjectProperty), self.ontology)
        self.assertIn((DPROD.schedule, RDFS.range, DPROD.Schedule), self.ontology)
        self.assertEqual([], list(self.ontology.objects(DPROD.schedule, RDFS.domain)))

    def test_schedule_expression_is_a_single_string_property(self) -> None:
        self.assertIn(
            (DPROD.scheduleExpression, RDF.type, OWL.DatatypeProperty),
            self.ontology,
        )
        self.assertIn(
            (DPROD.scheduleExpression, RDFS.domain, DPROD.Schedule),
            self.ontology,
        )
        self.assertIn(
            (DPROD.scheduleExpression, RDFS.range, XSD.string),
            self.ontology,
        )

    def test_builtin_formats_name_exact_standards(self) -> None:
        for schedule_format in (
            DPROD.Rfc5545ScheduleFormat,
            DPROD.PosixCrontabScheduleFormat,
        ):
            with self.subTest(schedule_format=schedule_format):
                self.assertIn(
                    (schedule_format, RDF.type, DPROD.ScheduleFormat),
                    self.ontology,
                )
                self.assertIn(
                    (schedule_format, DCTERMS.conformsTo, None),
                    self.ontology,
                )

    def test_obsolete_recurrence_property_is_removed(self) -> None:
        self.assertFalse(any(self.ontology.triples((DPROD.recurrence, None, None))))
        self.assertIn(
            (
                DPROD_CONTRACTS_SHAPES.RejectObsoleteRecurrenceShape,
                SH.targetSubjectsOf,
                DPROD.recurrence,
            ),
            self.shapes,
        )
        rejection_properties = self.shapes.objects(
            DPROD_CONTRACTS_SHAPES.RejectObsoleteRecurrenceShape,
            SH.property,
        )
        self.assertTrue(
            any(
                (property_shape, SH.path, DPROD.recurrence) in self.shapes
                for property_shape in rejection_properties
            )
        )

        authored_files = [
            ONTOLOGY_FILE,
            CONTRACTS_DIR / "README.md",
            *sorted(
                path
                for path in (CONTRACTS_DIR / "docs").glob("*.md")
                if path.name != "specification.md"
            ),
            *sorted((CONTRACTS_DIR / "examples").glob("*.md")),
            *sorted((CONTRACTS_DIR / "examples").glob("*.ttl")),
        ]
        for path in authored_files:
            with self.subTest(path=path):
                self.assertNotIn("dprod:recurrence", path.read_text(encoding="utf-8"))

    def test_formal_semantics_rejects_unprocessable_schedules(self) -> None:
        semantics = FORMAL_SEMANTICS_FILE.read_text(encoding="utf-8")

        self.assertIn("UnrecognizedScheduleFormat", semantics)
        self.assertIn("InvalidScheduleExpression", semantics)
        self.assertNotIn("an invalid RRULE yields ∅", semantics)


class ScheduleValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(ONTOLOGY_FILE, format="turtle")
        cls.shapes = Graph().parse(SHAPES_FILE, format="turtle")

    def validate_schedule(self, schedule: str, reference: str = "ex:schedule"):
        data = Graph().parse(
            data=f"""
                @prefix dprod: <https://www.omg.org/spec/DPROD/dprod/> .
                @prefix dct: <http://purl.org/dc/terms/> .
                @prefix ex: <https://example.org/> .
                @prefix odrl: <http://www.w3.org/ns/odrl/2/> .

                ex:duty
                    a odrl:Duty ;
                    odrl:action odrl:use ;
                    dprod:schedule {reference} .

                {schedule}
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

    def assert_conforms(self, schedule: str) -> None:
        conforms, _, report = self.validate_schedule(schedule)
        self.assertTrue(conforms, report)

    def assert_rejected(self, schedule: str, message: str, reference="ex:schedule") -> None:
        conforms, _, report = self.validate_schedule(schedule, reference)
        self.assertFalse(conforms, report)
        self.assertIn(message, report)

    def test_rfc5545_schedule_is_accepted(self) -> None:
        self.assert_conforms(
            '''
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:Rfc5545ScheduleFormat ;
                dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260810T060000\\nRRULE:FREQ=DAILY" .
            '''
        )

    def test_posix_crontab_schedule_is_accepted(self) -> None:
        self.assert_conforms(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * *" .
            """
        )

    def test_schedule_reference_must_be_an_iri(self) -> None:
        self.assert_rejected(
            "",
            "Schedule references must be IRIs",
            reference='"FREQ=DAILY"',
        )

    def test_schedule_itself_must_have_an_iri_identifier(self) -> None:
        self.assert_rejected(
            """
            _:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * *" .
            """,
            "A Schedule must have an IRI identifier",
            reference="_:schedule",
        )

    def test_obsolete_recurrence_fails_fast(self) -> None:
        conforms, _, report = self.validate_schedule(
            "",
            reference='ex:schedule ; dprod:recurrence "FREQ=DAILY"',
        )
        self.assertFalse(conforms, report)
        self.assertIn(
            "dprod:recurrence is obsolete; use dprod:schedule",
            report,
        )

    def test_schedule_requires_one_authoritative_expression(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * *", "0 7 * * *" .
            """,
            "Schedule must have exactly one authoritative expression",
        )

    def test_schedule_requires_one_authoritative_format(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:Rfc5545ScheduleFormat,
                    dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260810T060000\\nRRULE:FREQ=DAILY" .
            """,
            "Schedule format must be an identified dprod:ScheduleFormat",
        )

    def test_unregistered_format_is_rejected(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo ex:VagueCron ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * *" .
            """,
            "Schedule format must be an identified dprod:ScheduleFormat",
        )

    def test_extension_format_can_be_plugged_in(self) -> None:
        self.assert_conforms(
            """
            ex:CustomScheduleFormat a dprod:ScheduleFormat ;
                dct:conformsTo <https://example.org/schedule-specification> .

            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo ex:CustomScheduleFormat ;
                dprod:scheduleExpression "custom schedule expression" .
            """
        )

    def test_bare_dcat_frequency_is_not_an_executable_schedule(self) -> None:
        self.assert_rejected(
            "",
            "Schedule format must be an identified dprod:ScheduleFormat",
            reference="<http://purl.org/cld/freq/daily>",
        )

    def test_rfc5545_schedule_requires_anchor_and_timezone(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:Rfc5545ScheduleFormat ;
                dprod:scheduleExpression "RRULE:FREQ=DAILY" .
            """,
            "RFC 5545 schedules must include DTSTART with TZID and RRULE",
        )

    def test_malformed_posix_crontab_is_rejected(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleTimeZone "Europe/London" ;
                dprod:scheduleExpression "0 6 * * * unexpected-command" .
            """,
            "POSIX crontab schedules must contain exactly five time fields",
        )

    def test_posix_crontab_requires_iana_timezone(self) -> None:
        self.assert_rejected(
            """
            ex:schedule
                a dprod:Schedule ;
                dct:conformsTo dprod:PosixCrontabScheduleFormat ;
                dprod:scheduleExpression "0 6 * * *" .
            """,
            "POSIX crontab schedules must declare one IANA timezone",
        )


if __name__ == "__main__":
    unittest.main()
