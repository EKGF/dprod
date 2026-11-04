"""The audience overview is a distinct, source-owned publication."""
import unittest
from pathlib import Path
from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')

class OverviewPublication(unittest.TestCase):
    def test_overview_has_its_own_scope_and_no_reference_catalogue(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        target = DOC['overview-pdf']
        self.assertIn((DOC.project, GA.target, target), graph)
        profile = graph.value(target, GA.profile)
        self.assertEqual(str(graph.value(profile, GA.style)), 'overview')
        self.assertEqual(str(graph.value(target, GA.destination)), 'pdf/overview')
        placements = list(graph.objects(profile, GA.placement))
        self.assertGreaterEqual(len(placements), 7)
        for placement in placements:
            self.assertNotEqual(str(graph.value(placement, GA.sectionRole)), 'reference')
        scope = graph.value(target, GA.scope)
        self.assertNotEqual(scope, DOC.scope)
        self.assertTrue(all('overview:' in str(item) for item in graph.objects(scope, GA.include)))

    def test_overview_sources_are_authored_content_with_a_worked_example(self):
        directory = ROOT / 'publication/overview'
        pages = list(directory.glob('*.md'))
        self.assertGreaterEqual(len(pages), 7)
        content = '\n'.join(page.read_text() for page in pages)
        self.assertIn('UK Bonds', content)
        self.assertIn('```json', content)
        self.assertIn('../../assets/DPROD.drawio.svg', content)
        self.assertNotIn('RDF predicate', content)
