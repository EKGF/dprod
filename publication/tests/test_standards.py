"""The source-owned draft is complete while the release remains gated."""
from pathlib import Path
import unittest
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, unquote
from rdflib import Graph, Namespace, RDF
ROOT = Path(__file__).resolve().parents[2]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')
DCT = Namespace('http://purl.org/dc/terms/')

class StandardsTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph().parse(ROOT / 'publication/definitions/develop.ttl')

    def test_every_declared_collector_has_an_existing_source(self):
        collectors = list(self.graph.objects(DOC.project, GA.collector))
        self.assertTrue(collectors)
        examples, code = [], []
        for collector in collectors:
            self.assertIn((collector, RDF.type, GA.CollectorUse), self.graph)
            self.assertEqual(self.graph.value(collector, GA.source), self.graph.value(collector, GA.sourcePath))
            path = str(self.graph.value(collector, GA.source))
            self.assertTrue((ROOT / path).is_file(), path)
            kind = self.graph.value(collector, GA.collectorType)
            if kind == GA.MarkdownFileCollector and path.startswith('examples/'):
                examples.append(path)
            if kind == GA.CodeFileCollector:
                code.append(path)
                self.assertEqual(str(self.graph.value(collector, GA["format"])), 'application/ld+json')
        self.assertEqual(len(examples), 15)
        self.assertEqual(len(code), 12)

    def test_profiles_define_roles_and_unambiguous_placements(self):
        for profile in (DOC.profile, DOC['pdf-profile'], DOC['release-profile']):
            roles = set(map(str, self.graph.objects(profile, GA.requiredSectionRole)))
            self.assertTrue({'abstract','status','scope','conformance','references','terms','symbols','namespaces','model','contracts','contracts-model','reference','acknowledgements'} <= roles)
            # Generated vocabulary-reference placements carry no section role;
            # their content comes from the documentor, not an authored fragment.
            placements = [p for p in self.graph.objects(profile, GA.placement) if ':generated:' not in str(p)]
            orders = []
            for placement in placements:
                self.assertIn(str(self.graph.value(placement, GA.sectionRole)), roles)
                component = self.graph.value(placement, GA.component)
                self.assertIn((component, RDF.type, GA.Component), self.graph)
                self.assertTrue(list(self.graph.objects(component, GA.fragment)))
                orders.append(int(self.graph.value(placement, GA.order)))
            self.assertEqual(len(orders), len(set(orders)))

    def test_authored_relative_links_resolve_in_the_repository(self):
        for path in (ROOT / 'publication/standards').glob('*.md'):
            for target in re.findall(r'\]\(([^ )]+)', path.read_text()):
                link = urlsplit(target)
                if link.scheme or not link.path:
                    continue
                self.assertTrue((path.parent / unquote(link.path)).exists(), f'{path}: {target}')

    def test_normative_filenames_are_real_links(self):
        for path in (ROOT / 'publication/standards').glob('*.md'):
            self.assertNotRegex(path.read_text(), r'<[\w-]+\.ttl>')

    def test_model_uses_the_same_diagram_as_the_develop_specification(self):
        template = (ROOT / 'respec/template.html').read_text()
        published = re.search(r'<img alt="Information model for the Profile" src="\./([^"]+)"', template).group(1)
        body = (ROOT / 'publication/standards/model.md').read_text()
        selected = re.search(r'!\[Information model for the Profile\]\(([^)]+)\)', body).group(1)
        self.assertEqual((ROOT / 'publication/standards' / selected).resolve(), ROOT / published)

    def test_overview_diagram_has_complete_native_svg_labels(self):
        root = ET.parse(ROOT / 'assets/DPROD.drawio.svg').getroot()
        self.assertFalse(root.findall('.//{http://www.w3.org/2000/svg}foreignObject'))
        labels = {' '.join(''.join(node.itertext()).split()) for node in root.findall('.//{http://www.w3.org/2000/svg}text')}
        self.assertTrue({'Data Product', 'Dataset', 'DataService', 'Distribution',
            'informationSensitivityClassification', 'isDistributionOf',
            'isAccessServiceOf (inverse)', 'dataProductLifecycleStatus'} <= labels)
        self.assertFalse(any('...' in label for label in labels))

    def test_release_does_not_claim_approval_or_invent_identity(self):
        self.assertEqual(set(self.graph.objects(DOC.project, GA.target)),
                         {DOC.specification, DOC.website, DOC.pdf, DOC['omg-pdf'], DOC['overview-pdf']})
        self.assertEqual(str(self.graph.value(DOC.release, GA.publicationStatus)), 'Documentation Preview')
        self.assertEqual(str(self.graph.value(DOC['release-profile'], GA.allowedPublicationStatus)), 'Formal Specification')
        for predicate in (GA.documentNumber, GA.publicationDate, GA.thisVersion):
            self.assertIsNone(self.graph.value(DOC.release, predicate))
            self.assertIn((DOC['release-profile'], GA.requiredMetadata, predicate), self.graph)
        self.assertTrue(list(self.graph.objects(DOC.specification, GA.editor)))
        self.assertTrue(list(self.graph.objects(DOC.pdf, GA.author)))

    def test_imported_prose_is_traceable_and_contains_no_template_code(self):
        for path in (ROOT / 'publication/standards').glob('*.md'):
            if path.name == 'README.md':
                continue
            body = path.read_text()
            self.assertNotIn('{%', body)
            self.assertNotIn('{{', body)
        self.assertTrue(list(self.graph.objects(DOC['fragment:preface'], DCT.source)))
        self.assertIn('1.0 beta 2', (ROOT/'publication/standards/preface.md').read_text())
