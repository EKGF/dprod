"""The Pages review publication is independent and keeps the project prefix once."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


class PagesPublicationTests(unittest.TestCase):
    def test_pages_profile_uses_default_repository_url_without_changing_manifest(self):
        from pages_publication import hosting_configuration
        config = json.loads((ROOT / 'publication/publications.json').read_text())
        original = config['canonical_url']
        profile = {'version': 1, 'platform': 'github-pages', 'canonical_url': 'https://ekgf.github.io/dprod/'}
        hosted = hosting_configuration(config, profile)
        self.assertEqual(hosted['canonical_url'], profile['canonical_url'])
        self.assertEqual(hosted['mount'], '/dprod')
        self.assertEqual(config['canonical_url'], original)
        profile['canonical_url'] = 'https://ekgf.org/dprod/'
        with self.assertRaises(ValueError):
            hosting_configuration(config, profile)

    def test_pages_website_uses_host_metadata_without_rewriting_normative_inputs(self):
        from pages_publication import website_definitions
        from rdflib import Graph, URIRef
        source = (ROOT / 'publication/project-site.ttl').read_text()
        result = website_definitions(source, 'urn:dprod:project-site:website', 'https://ekgf.github.io/dprod/')
        graph = Graph().parse(data=result, format='turtle')
        values = list(graph.objects(URIRef('urn:dprod:project-site:website'), URIRef('https://ekgf.org/ontology/grapharch#thisVersion')))
        self.assertEqual(values, [URIRef('https://ekgf.github.io/dprod/')])
        self.assertIn('https://ekgf.org/dprod/', source)

    def test_pages_artifact_is_mounted_contents_not_a_second_dprod_directory(self):
        from pages_publication import prepare_artifact
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary)
            root = stage / 'deployment/.vercel/output/static/dprod'
            root.mkdir(parents=True)
            (root / 'index.html').write_text('site')
            self.assertEqual(prepare_artifact(stage, '/dprod'), root)
            self.assertTrue((root / '.nojekyll').is_file())
            (root / 'CNAME').write_text('ekgf.org')
            with self.assertRaises(ValueError):
                prepare_artifact(stage, '/dprod')

    def test_pages_workflow_uses_grapharch_action_and_no_vercel_credentials(self):
        workflow = (ROOT / '.github/workflows/grapharch-pages.yml').read_text()
        self.assertIn('uses: ./.grapharch-tool', workflow)
        self.assertIn('expected-revision: ${{ steps.config.outputs.generator }}', workflow)
        self.assertIn('version: ${{ steps.config.outputs.version }}', workflow)
        self.assertNotIn('source-revision:', workflow)
        self.assertIn('actions/upload-pages-artifact@', workflow)
        self.assertIn('actions/deploy-pages@', workflow)
        self.assertIn('static/dprod', workflow)
        self.assertIn('ref: develop', workflow)
        self.assertNotIn('VERCEL', workflow)
        self.assertNotIn('set -e', workflow)


if __name__ == '__main__':
    unittest.main()
