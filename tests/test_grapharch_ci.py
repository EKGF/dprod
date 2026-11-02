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

    def test_static_preview_uses_the_existing_vercel_project_root(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        deploy = text.split('- name: Deploy a reviewable static preview', 1)[1].split('- name:', 1)[0]
        directory = re.search(r'working-directory: (.+)', deploy)
        deploy_root = ROOT / (directory.group(1).strip() if directory else '.')
        # The active Vercel project has rootDirectory=site. Prebuilt deployments
        # still validate that directory; deployment must preserve its source root.
        self.assertTrue((deploy_root / 'site').is_dir())
        package = text.split('- name: Package the project website', 1)[1].split('- name:', 1)[0]
        package_root = ROOT / re.search(r'--output-root (\S+)', package).group(1)
        self.assertEqual(package_root.resolve(), deploy_root.resolve())

    def test_preview_checks_establish_public_reader_access(self):
        text = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        smoke = text.split('- name: Verify the deployed preview routes', 1)[1].split('- name:', 1)[0]
        self.assertNotIn('VERCEL_TOKEN', smoke)
        self.assertNotIn('vercel@', smoke)
        self.assertIn('if curl ', smoke)
        self.assertIn('[ "$status" != 200 ]', smoke)
        evidence = text.split('- name: Retain machine-readable build evidence', 1)[1]
        self.assertIn('output/grapharch-project-site/documentation.nq', evidence)

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
