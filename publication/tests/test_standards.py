"""The source-owned draft is complete while the release remains gated."""
from pathlib import Path
import unittest
import re
from urllib.parse import urlsplit, unquote
from rdflib import Graph, Namespace, RDF
ROOT = Path(__file__).resolve().parents[2]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')
DCT = Namespace('http://purl.org/dc/terms/')

class StandardsTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph().parse(ROOT / 'publication/standards.ttl')

    def test_every_declared_collector_has_an_existing_source(self):
        collectors = list(self.graph.objects(DOC.project, GA.collector))
        self.assertEqual(len(collectors), 49)
        examples, code = [], []
        for collector in collectors:
            self.assertIn((collector, RDF.type, GA.Collector), self.graph)
            path = str(self.graph.value(collector, GA.sourcePath))
            self.assertTrue((ROOT / path).is_file(), path)
            kind = str(self.graph.value(collector, GA.kind))
            if kind == 'markdown' and path.startswith('examples/'):
                examples.append(path)
            if kind == 'code':
                code.append(path)
                self.assertEqual(str(self.graph.value(collector, GA["format"])), 'application/ld+json')
        self.assertEqual(len(examples), 15)
        self.assertEqual(len(code), 12)

    def test_profiles_define_roles_and_unambiguous_placements(self):
        for profile in (DOC.profile, DOC['pdf-profile'], DOC['release-profile']):
            roles = set(map(str, self.graph.objects(profile, GA.requiredSectionRole)))
            self.assertTrue({'abstract','status','scope','conformance','references','terms','symbols','namespaces','model','contracts','contracts-model','reference','acknowledgements'} <= roles)
            placements = list(self.graph.objects(profile, GA.placement))
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

    def test_model_uses_the_portable_repository_diagram(self):
        body = (ROOT / 'publication/standards/model.md').read_text()
        self.assertIn('assets/dprod-model.svg', body)
        self.assertNotIn('DPROD.drawio.svg', body)

    def test_release_does_not_claim_approval_or_invent_identity(self):
        self.assertEqual(len(set(self.graph.objects(DOC.project, GA.target))), 4)
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
