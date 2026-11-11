"""Central builds select exact source revisions and never use old deployments."""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import publication_manifest as manifest


class CentralPublicationTests(unittest.TestCase):
    def settings(self):
        return json.loads((ROOT / 'publication/publications.json').read_text())

    def test_generator_release_version_is_exact_and_binary_must_agree(self):
        from unittest.mock import patch
        import central_publications as central
        config = self.settings()
        for invalid in ('latest', 'v0.2.0', '', 2):
            with self.subTest(version=invalid), self.assertRaises(ValueError):
                manifest.validate(dict(config, generator_version=invalid))
        with patch.object(central.subprocess, 'check_output', return_value='grapharch 0.1.0\n'), \
             self.assertRaisesRegex(ValueError, 'binary version'):
            central.build_all(ROOT, config, [], Path('/unused/grapharch'), Path('/unused/output'), 'a' * 40)

    def test_published_generator_identity_must_match_version_and_revision(self):
        from unittest.mock import patch
        import central_publications as central
        config = dict(self.settings(), generator_version='0.2.4',
                      generator_revision='2a065f7603dbcee13ad7f3bbb150c72be170515d')
        release = ('grapharch 0.2.4 (build 5)\nBuild 5; producer attempt 1; source commit '
                   '2a065f7603dbcee13ad7f3bbb150c72be170515d; workflow '
                   'EKGF/grapharch/.github/workflows/automatic-release.yml@refs/heads/main; '
                   'https://github.com/EKGF/grapharch/actions/runs/42707507721/attempts/1\n')
        with patch.object(central.subprocess, 'check_output', return_value=release):
            central.verify_generator(Path('/unused/grapharch'), config)
        for output in (release.replace('2a065f76', 'ffffffff'),
                       release.replace('0.2.4 (build 5)', '0.2.5 (build 5)'),
                       'grapharch 0.2.4 (build 5)\n',
                       'grapharch 0.2.4\n'):
            with self.subTest(output=output), \
                 patch.object(central.subprocess, 'check_output', return_value=output), \
                 self.assertRaisesRegex(ValueError, 'binary'):
                central.verify_generator(Path('/unused/grapharch'), config)

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

    def test_leading_branch_must_be_selected_before_building(self):
        config = self.settings()
        config['publications'] = config['publications'][:1]
        with self.assertRaisesRegex(ValueError, 'leading branch'):
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

    def test_serializer_selects_rdf_collectors_by_their_collector_definition(self):
        from publication_resources import serialize
        revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        with tempfile.TemporaryDirectory() as temporary:
            published = serialize(ROOT, {'source_commit': revision,
                                         'definitions': 'publication/standards.ttl'}, Path(temporary))
        self.assertIn('dprod.ttl', published)
        self.assertIn('dprod-shapes.ttl', published)

    def test_false_committed_configuration_provenance_is_rejected(self):
        import central_publications as central
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            source = root / 'manifest.json'
            source.write_text('{}')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.org',
                            'commit', '-qm', 'fixture'], check=True)
            self.assertRegex(central.committed_configuration(root, source), r'^[0-9a-f]{40}$')
            source.write_text('{"changed":true}')
            with self.assertRaises(ValueError):
                central.committed_configuration(root, source)
            with self.assertRaises(ValueError):
                central.committed_configuration(root, root.parent / 'external.json')

    def test_native_svg_download_rejects_active_content_without_rewriting_source(self):
        from publication_resources import validate_asset
        safe = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Historical label</text></svg>'
        self.assertEqual(validate_asset('diagram.svg', safe), safe)
        for unsafe in [b'<svg onload="alert(1)"/>', b'<svg><script>alert(1)</script></svg>',
                       b'<svg><image href="https://tracking.example/pixel"/></svg>']:
            with self.assertRaises(ValueError):
                validate_asset('diagram.svg', unsafe)

    def test_workflow_executes_only_leading_branch_code_and_separates_deploy_credentials(self):
        workflow = (ROOT / '.github/workflows/grapharch-pdfs.yml').read_text()
        self.assertIn('pull_request_target:', workflow)
        self.assertIn('ref: develop', workflow)
        self.assertNotIn('pull_request.head.sha', workflow)
        self.assertNotIn('spec-generator/main.py', workflow)
        self.assertNotIn('VERCEL_TOKEN', workflow.split('  deploy:')[0])
        self.assertIn('workflow_run:', workflow)
        self.assertNotIn('set -e', workflow)
        self.assertNotIn('--token', workflow)


if __name__ == '__main__':
    unittest.main()
