"""Source-owned preview configuration leaves the standard's native RDF intact."""
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, URIRef
ROOT=Path(__file__).resolve().parents[2]
GA=Namespace("https://ekgf.org/ontology/grapharch#")
DOC=Namespace("urn:dprod-showcase:")
DCT=Namespace("http://purl.org/dc/terms/")

class PreviewTests(unittest.TestCase):
    def test_all_declared_inputs_exist_and_targets_are_independent(self):
        graph=Graph().parse(ROOT/"publication/grapharch.ttl")
        self.assertEqual(len(set(graph.objects(DOC.project,GA.target))),3)
        for collector in graph.objects(DOC.project,GA.collector):
            self.assertIn((collector,RDF.type,GA.Collector),graph)
            self.assertIsNotNone(graph.value(collector,GA.source), "collector hints must retain their source identity")
            path=str(graph.value(collector,GA.sourcePath))
            self.assertTrue((ROOT/path).is_file(),path)
        self.assertEqual(str(graph.value(DOC.specification,GA.publicationStatus)),"Documentation Preview")
        self.assertEqual(graph.value(DOC.specification,GA.publisher),URIRef("urn:uuid:6c1408aa-039c-42f9-8dee-9c3f0009d61a"))

    def test_header_metadata_is_owned_by_the_native_ontology(self):
        settings=Graph().parse(ROOT/"publication/grapharch.ttl")
        ontology=Graph().parse(ROOT/"ontology/dprod/dprod-ontology.ttl")
        subject=URIRef("https://ekgf.org/dprod/spec/develop/")
        for field in (DCT.title,DCT.description,DCT.license,DCT.issued):
            self.assertTrue(list(ontology.objects(subject,field)),str(field))
        self.assertIsNone(settings.value(DOC.specification,GA.publicationDate))
        self.assertIsNone(settings.value(DOC.specification,GA.license))
