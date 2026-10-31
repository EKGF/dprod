"""CI compiles a pinned generator and documents the exact DPROD revision."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]


class GrapharchCITests(unittest.TestCase):
    def test_registry_fetches_exact_revision_without_copying_source_content(self):
        path = ROOT / 'scripts/grapharch_editions.py'
        spec = importlib.util.spec_from_file_location('grapharch_editions', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        revision = '1234567890abcdef1234567890abcdef12345678'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = module.prepare_registry(root, revision)
            config = json.loads((root / 'dprod.json').read_text())
            self.assertEqual(config, {'repository': 'https://github.com/EKGF/dprod.git',
                                     'ref': revision, 'definitions': 'publication/standards.ttl'})
            graph = Graph().parse(registry)
            ga = Namespace('https://ekgf.org/ontology/grapharch#')
            self.assertEqual(str(graph.value(URIRef('urn:dprod:ci:showcase'), ga.kind)), 'dprod')
            self.assertEqual(set(p.name for p in root.iterdir()), {'showcases.ttl', 'dprod.json'})
        for invalid in ('develop', 'main', 'abc', 'x' * 40, '0' * 40):
            with self.assertRaises(ValueError):
                module.require_commit(invalid)

    def test_workflow_uploads_two_named_editions_from_pinned_grapharch(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        self.assertRegex(text, r'GRAPHARCH_COMMIT: [0-9a-f]{40}')
        self.assertIn('ref: ${{ env.GRAPHARCH_COMMIT }}', text)
        self.assertIn('--source-revision "$GITHUB_SHA"', text)
        self.assertIn('--grapharch-revision "$GRAPHARCH_COMMIT"', text)
        self.assertIn('dprod-ekgf-community-${{ github.sha }}', text)
        self.assertIn('dprod-omg-submission-preview-${{ github.sha }}', text)
        self.assertNotIn('pull_request:', text)
        self.assertNotIn('set -e', text)


if __name__ == '__main__':
    unittest.main()
