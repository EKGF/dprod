"""Central builds select exact source revisions and never use old deployments."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import publication_manifest as manifest


class CentralPublicationTests(unittest.TestCase):
    def settings(self):
        return json.loads((ROOT / 'publication/publications.json').read_text())

    def test_selection_uses_branch_heads_and_only_intentional_same_repo_prs(self):
        config = self.settings()
        heads = {'main': 'a' * 40, 'develop': 'b' * 40}
        prs = [
            {'number': 42, 'title': 'Schedule', 'head': {'ref': 'issue/schedule', 'sha': 'c' * 40,
             'repo': {'full_name': 'EKGF/dprod'}}},
            {'number': 43, 'title': 'Bot', 'head': {'ref': 'dependabot/example', 'sha': 'd' * 40,
             'repo': {'full_name': 'EKGF/dprod'}}},
            {'number': 44, 'title': 'Fork', 'head': {'ref': 'example', 'sha': 'e' * 40,
             'repo': {'full_name': 'someone/dprod'}}},
        ]
        selected = manifest.select(config, heads, prs)
        self.assertEqual([p['slug'] for p in selected], ['main', 'develop', 'pr-42'])
        self.assertEqual([p['source_commit'] for p in selected], ['a' * 40, 'b' * 40, 'c' * 40])
        self.assertEqual(selected[0]['label'], 'DPROD 1.0 beta')
        self.assertEqual(selected[2]['branch'], 'issue/schedule')
        self.assertEqual(selected[2]['status'], 'Pull request preview — not standardized')

    def test_missing_source_or_ambiguous_path_is_a_hard_error(self):
        config = self.settings()
        with self.assertRaises(ValueError):
            manifest.select(config, {'develop': 'b' * 40}, [])
        config['publications'][1]['slug'] = 'main'
        with self.assertRaises(ValueError):
            manifest.validate(config)
        config = self.settings()
        config['publications'][0]['definitions'] = '../outside.ttl'
        with self.assertRaises(ValueError):
            manifest.validate(config)

    def test_inventory_has_local_links_exact_revisions_and_no_vercel_discovery(self):
        config = self.settings()
        selected = manifest.select(config, {'main': 'a' * 40, 'develop': 'b' * 40}, [])
        ttl = manifest.inventory_turtle(config, selected, 'c' * 40, '2026-11-06T00:00:00Z')
        self.assertIn('ga:route "/dprod/spec/main/"', ttl)
        self.assertIn('DPROD 1.0 beta', ttl)
        self.assertIn('a' * 40, ttl)
        self.assertNotIn('vercel', ttl)
        self.assertNotIn('approved', ttl.lower())

    def test_failure_never_promotes_partial_assembly(self):
        import central_publications as central
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'complete'
            calls = []
            def build(publication, staging):
                calls.append(publication['slug'])
                if publication['slug'] == 'develop':
                    raise RuntimeError('deliberate source error')
            with self.assertRaises(RuntimeError):
                central.assemble_atomic(output, [{'slug': 'main'}, {'slug': 'develop'}], build,
                                        lambda staging: self.fail('must not package partial output'))
            self.assertEqual(calls, ['main', 'develop'])
            self.assertFalse(output.exists())

    def test_context_serialization_uses_each_versions_ontology_namespace(self):
        sys.path.insert(0, str(ROOT / 'spec-generator'))
        from rdflib import Graph, URIRef, RDF, OWL
        from jsonld_context import ApplicationContext, SimpleContext
        graph = Graph()
        namespace = 'https://www.omg.org/spec/DPROD/dprod/'
        graph.add((URIRef(namespace + 'outputPort'), RDF.type, OWL.ObjectProperty))
        prefixed = ApplicationContext(graph, namespace=namespace).as_dict()
        simple = SimpleContext(graph, namespace=namespace).as_dict()
        self.assertEqual(prefixed['dprod'], namespace)
        self.assertEqual(prefixed['dprod:outputPort']['@type'], '@id')
        self.assertEqual(simple['outputPort']['@id'], 'dprod:outputPort')

    def test_workflow_executes_only_leading_branch_code_and_separates_deploy_credentials(self):
        workflow = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        self.assertIn('pull_request_target:', workflow)
        self.assertIn('ref: develop', workflow)
        self.assertNotIn('pull_request.head.sha', workflow)
        self.assertNotIn('spec-generator/main.py', workflow)
        self.assertNotIn('VERCEL_TOKEN', workflow.split('  deploy:')[0])
        self.assertIn('workflow_run:', workflow)
        self.assertNotIn('set -e', workflow)


if __name__ == '__main__':
    unittest.main()
