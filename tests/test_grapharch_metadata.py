"""Source-owned Grapharch metadata preserves the develop specification links."""
from pathlib import Path
import json
import re
import unittest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')

class GrapharchMetadataTests(unittest.TestCase):
    def test_model_preserves_numbered_example_and_two_notes(self):
        model = (ROOT / 'publication/standards/model.md').read_text()
        self.assertIn('```json example\n', model)
        self.assertEqual(model.count('> [!NOTE]'), 2)
        self.assertNotIn('>\n> [!NOTE]', model)
        self.assertIn('> DPROD publishes two JSON-LD contexts', model)
        self.assertIn('> The following sections are driven by the Shapes', model)

    def test_publication_json_examples_declare_their_language(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        paths = sorted({str(path) for path in graph.objects(None, GA.sourcePath)
                        if str(path).endswith('.md')})
        checked = 0
        for relative in paths:
            body = (ROOT / relative).read_text()
            for match in re.finditer(r'^```([^\n]*)\n(.*?)^```[ \t]*$', body,
                                     re.MULTILINE | re.DOTALL):
                info, code = match.groups()
                try:
                    value = json.loads(code)
                except json.JSONDecodeError:
                    continue
                if not isinstance(value, (dict, list)):
                    continue
                checked += 1
                language = info.split()[0] if info.split() else ''
                self.assertIn(language, ('json', 'jsonld', 'json-ld'),
                              f'{relative}: JSON example needs an explicit language')
        self.assertGreater(checked, 1)
        contracts = (ROOT / 'publication/standards/contracts-model.md').read_text()
        self.assertIn('```json example\n', contracts)

    def test_contributors_have_explicit_family_names(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        schema = Namespace('https://schema.org/')
        people = set(graph.objects(DOC.specification, GA.editor)) | set(graph.objects(DOC.specification, GA.author))
        self.assertEqual(len(people), 15)
        for person in people:
            self.assertTrue(str(graph.value(person, schema.familyName) or '').strip(), str(person))
        self.assertEqual(str(graph.value(Namespace('urn:dprod:documentation:author:')['1'], schema.familyName)), 'Whittam Smith')

    def test_ordered_header_preserves_people_and_publication_links(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        target = DOC.specification
        self.assertEqual(len(list(graph.objects(target, GA.editor))), 6)
        self.assertEqual(len(list(graph.objects(target, GA.author))), 9)
        rows = sorted(graph.objects(target, GA.metadataRow),
                      key=lambda row: int(graph.value(row, GA.order)))
        titles = [str(graph.value(row, Namespace('http://purl.org/dc/terms/').title)) for row in rows]
        self.assertEqual(titles, ['This version:', 'Latest published version:',
            "Latest editor’s draft:", 'History:', 'Editors:', 'Authors:',
            'Feedback:', 'Download as RDF:', 'PDF editions:'])
        bodies = '\n'.join(str(graph.value(row, GA.body) or '') for row in rows)
        self.assertIn('https://github.com/EKGF/dprod/commits/develop/', bodies)
        self.assertIn('https://github.com/EKGF/dprod/pulls', bodies)
        self.assertIn('https://github.com/EKGF/dprod/issues/new', bodies)
        self.assertIn('https://github.com/EKGF/dprod/issues', bodies)
        template = (ROOT / 'respec/template.html').read_text()
        downloads = template.split('key: "Download as RDF:"', 1)[1].split('localBiblio:', 1)[0]
        for label, path in re.findall(r'value: "([^"]+)",\s*href: "([^"]+)"', downloads):
            self.assertIn(label, bodies)
            self.assertIn(f'href="../{path}"', bodies)

    def test_rows_link_artifacts_of_the_same_build_relative_to_the_publication(self):
        # Hosts are deployment configuration. A row link into the deployment
        # stays relative, so it resolves wherever the bundle is published.
        import subprocess
        import sys
        import tempfile
        sys.path.insert(0, str(ROOT / 'scripts'))
        from central_publications import DERIVED_RESOURCES
        from publication_resources import serialize
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        with tempfile.TemporaryDirectory() as temporary:
            native = serialize(ROOT, {'source_commit': revision,
                                      'definitions': 'publication/standards.ttl'}, Path(temporary))
        bundle = set(native) | set(DERIVED_RESOURCES)
        self.assertEqual(str(graph.value(DOC.specification, GA.destination)), 'specification')
        downloads = 0
        for row in graph.objects(DOC.specification, GA.metadataRow):
            for href in re.findall(r'href="([^"]+)"', str(graph.value(row, GA.body) or '')):
                self.assertNotRegex(href, r'^https://(ekgf\.org|ekgf\.github\.io)/dprod/', href)
                if href.startswith('../') and href.endswith(('.ttl', '.jsonld', '.rdf')):
                    self.assertIn(href[len('../'):], bundle, href)
                    downloads += 1
        self.assertEqual(downloads, 12)

    def test_product_logo_is_a_retained_source_asset_separate_from_authority(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        asset = DOC['product-logo']
        collector = DOC['source:product-logo']
        self.assertEqual(graph.value(DOC.specification, GA.productLogo), asset)
        self.assertEqual(str(graph.value(asset, Namespace('http://purl.org/dc/terms/').title)), 'DPROD')
        self.assertIn(collector, graph.objects(DOC.project, GA.collector))
        self.assertEqual(graph.value(collector, GA.collectorType), GA.ImageCollector)
        self.assertEqual(graph.value(collector, GA.asset), asset)
        self.assertEqual(str(graph.value(collector, GA.source)), 'assets/dprod.jpg')
        self.assertEqual(graph.value(collector, GA.source), graph.value(collector, GA.sourcePath))
        path = ROOT / str(graph.value(collector, GA.source))
        self.assertEqual(path, ROOT / 'assets/dprod.jpg')
        self.assertTrue(path.is_file())

    def test_publication_authorities_use_imported_governance_class(self):
        from rdflib import RDF, URIRef
        canonical = URIRef('https://ekgf.org/ontology/artifact-governance#Authority')
        removed = GA.Authority
        for name in ('standards.ttl', 'grapharch.ttl'):
            graph = Graph().parse(ROOT / 'publication' / name)
            publishers = list(graph.objects(None, GA.publisher))
            self.assertTrue(publishers, name)
            for publisher in publishers:
                self.assertIn((publisher, RDF.type, canonical), graph, name)
                self.assertNotIn((publisher, RDF.type, removed), graph, name)

if __name__ == '__main__':
    unittest.main()
