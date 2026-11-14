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
    def test_engine_pin_is_the_dependabot_managed_action_step(self):
        text = PAGES.read_text()
        pins = re.findall(r'uses: EKGF/grapharch@([0-9a-f]{40}) # v(\d+\.\d+\.\d+)', text)
        self.assertEqual(pins, [('c3ad8918a3916df53b306b639a519254fdf082bd', '0.2.10')])
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        self.assertFalse({'generator_version', 'generator_revision'} & set(config))
        dependabot = (ROOT / '.github/dependabot.yml').read_text()
        self.assertIn('package-ecosystem: "github-actions"', dependabot)
        self.assertIn('interval: "daily"', dependabot)

    def test_every_publication_is_defined_by_controlling_definitions(self):
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        definitions = {p['branch']: p['definitions'] for p in config['publications']}
        self.assertEqual(definitions, {'main': 'publication/definitions/main.ttl',
                                       'develop': 'publication/definitions/develop.ttl'})
        self.assertEqual(config['pull_requests']['definitions'], 'publication/definitions/develop.ttl')
        for path in set(definitions.values()):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_github_pages_is_the_only_grapharch_deployment(self):
        # GraphArch never deploys to the production host or its preview
        # platform; those keep their own workflows until a verified cutover.
        publishers = {path.name for path in WORKFLOWS.glob('*.yml')
                      if 'scripts/central_publications.py' in path.read_text()}
        self.assertEqual(publishers, {'grapharch-pages.yml'})
        text = PAGES.read_text()
        self.assertIn('--hosting-profile publication/github-pages.json', text)
        self.assertIn('actions/deploy-pages@', text)
        self.assertNotRegex(text, r'(?i)vercel')
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
