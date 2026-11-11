"""CI compiles a pinned generator and documents the exact DPROD revision."""
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest
from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / '.github/workflows'
PAGES = WORKFLOWS / 'grapharch-pages.yml'


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

    def test_github_pages_is_the_only_grapharch_deployment(self):
        # GraphArch never deploys to the production host or its preview
        # platform; those keep their own workflows until a verified cutover.
        publishers = {path.name for path in WORKFLOWS.glob('*.yml')
                      if 'scripts/central_publications.py' in path.read_text()}
        self.assertEqual(publishers, {'grapharch-pages.yml'})
        text = PAGES.read_text()
        self.assertIn('--hosting-profile publication/github-pages.json', text)
        self.assertIn('actions/deploy-pages@', text)
        self.assertNotRegex(text, r'(?i)vercel(?!/output/static/dprod)')
        self.assertNotIn('secrets.', text)
        self.assertNotIn('npx', text)

    def test_deployed_site_checks_establish_public_reader_access(self):
        text = PAGES.read_text()
        smoke = text.split('- name: Verify the public specifications and provenance', 1)[1]
        self.assertNotIn('token', smoke.lower())
        self.assertIn('https://ekgf.github.io/dprod/publication-build.json', smoke)
        self.assertIn('r["config_commit"] == sys.argv[1]', smoke)
        self.assertIn('scripts/verify_publication_site.py --base-url https://ekgf.github.io', smoke)
        verifier = (ROOT / 'scripts/verify_publication_site.py').read_text()
        self.assertIn('response.status != 200', verifier)
        self.assertIn("provenance['source_commit']", verifier)

    def test_workflow_rebuilds_with_the_pinned_generator_and_retains_evidence(self):
        text = PAGES.read_text()
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        self.assertRegex(config['generator_revision'], r'^[0-9a-f]{40}$')
        self.assertIn('ref: ${{ steps.config.outputs.generator }}', text)
        self.assertIn("python-version: '3.13'", text)
        build = text.split('  deploy:')[0]
        for evidence in ('output/grapharch-pages/publications/', 'output/grapharch-pages/website/',
                         'output/grapharch-pages/publication-build.json'):
            self.assertIn(evidence, build)
        self.assertNotIn('pages: write', build)
        self.assertNotIn('id-token: write', build)
        self.assertNotIn('pull_request:', text)
        self.assertNotIn('set -e', text)

if __name__ == '__main__':
    unittest.main()
