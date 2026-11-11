"""CI compiles a pinned generator and documents the exact DPROD revision."""
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]


class GrapharchCITests(unittest.TestCase):
    def test_formal_omg_profile_uses_the_verified_native_release(self):
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        self.assertEqual(config['generator_version'], '0.2.8')
        self.assertEqual(config['generator_revision'],
                         '595e55913096cb7f39633189ef67f5d916ef4dcc')

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
            self.assertEqual(graph.value(URIRef('urn:dprod:ci:showcase'), ga.showcaseRunner), ga.DprodShowcaseRunner)
            self.assertEqual(set(p.name for p in root.iterdir()), {'showcases.ttl', 'dprod.json'})
        for invalid in ('develop', 'main', 'abc', 'x' * 40, '0' * 40):
            with self.assertRaises(ValueError):
                module.require_commit(invalid)

    def test_static_preview_uses_the_existing_vercel_project_root(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        self.assertTrue((ROOT / 'site').is_dir())
        self.assertIn('path: .vercel/output', text)
        self.assertIn('needs: assemble', text)
        self.assertIn('ref: ${{ needs.assemble.outputs.config_revision }}', text)

    def test_preview_checks_establish_public_reader_access(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        smoke = text.split('- name: Verify every deployed publication', 1)[1].split('- name:', 1)[0]
        self.assertNotIn('VERCEL_TOKEN', smoke)
        self.assertNotIn('vercel@', smoke)
        self.assertIn('scripts/verify_publication_site.py', smoke)
        verifier = (ROOT / 'scripts/verify_publication_site.py').read_text()
        self.assertIn('response.status != 200', verifier)
        self.assertIn("provenance['source_commit']", verifier)

    def test_workflow_uploads_two_named_editions_from_pinned_grapharch(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        self.assertRegex(config['generator_revision'], r'^[0-9a-f]{40}$')
        self.assertIn('ref: ${{ steps.config.outputs.generator }}', text)
        self.assertIn('output/central-publications/publications/', text)
        self.assertNotIn('VERCEL_TOKEN', text.split('  deploy:')[0])
        self.assertNotIn('pull_request:', text)
        self.assertNotIn('set -e', text)


if __name__ == '__main__':
    unittest.main()
