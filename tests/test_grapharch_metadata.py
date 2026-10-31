"""Source-owned Grapharch metadata preserves the develop specification links."""
from pathlib import Path
import re
import unittest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')

class GrapharchMetadataTests(unittest.TestCase):
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
            'Feedback:', 'Download as RDF:'])
        bodies = '\n'.join(str(graph.value(row, GA.body) or '') for row in rows)
        self.assertIn('https://github.com/EKGF/dprod/commits/develop/', bodies)
        self.assertIn('https://github.com/EKGF/dprod/pulls', bodies)
        self.assertIn('https://github.com/EKGF/dprod/issues/new', bodies)
        self.assertIn('https://github.com/EKGF/dprod/issues', bodies)
        template = (ROOT / 'respec/template.html').read_text()
        downloads = template.split('key: "Download as RDF:"', 1)[1].split('localBiblio:', 1)[0]
        for label, path in re.findall(r'value: "([^"]+)",\s*href: "([^"]+)"', downloads):
            self.assertIn(label, bodies)
            self.assertIn('https://ekgf.org/dprod/spec/develop/' + path, bodies)

    def test_product_logo_is_a_retained_source_asset_separate_from_authority(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        asset = DOC['product-logo']
        collector = DOC['source:product-logo']
        self.assertEqual(graph.value(DOC.specification, GA.productLogo), asset)
        self.assertEqual(str(graph.value(asset, Namespace('http://purl.org/dc/terms/').title)), 'DPROD')
        self.assertIn(collector, graph.objects(DOC.project, GA.collector))
        self.assertEqual(str(graph.value(collector, GA.kind)), 'image')
        self.assertEqual(graph.value(collector, GA.asset), asset)
        path = ROOT / str(graph.value(collector, GA.sourcePath))
        self.assertEqual(path, ROOT / 'assets/dprod.jpg')
        self.assertTrue(path.is_file())

if __name__ == '__main__':
    unittest.main()
