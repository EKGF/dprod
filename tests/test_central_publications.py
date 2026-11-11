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

    def test_pinned_generator_accepts_the_published_release_binary(self):
        from unittest.mock import patch
        import central_publications as central
        # Exact `grapharch --version` output of the v0.2.8 release asset
        # grapharch-aarch64-apple-darwin.zip (tag commit 595e559).
        release = ('grapharch 0.2.8 (build 17)\nBuild 17; producer attempt 1; source commit '
                   '595e55913096cb7f39633189ef67f5d916ef4dcc; workflow '
                   'EKGF/grapharch/.github/workflows/automatic-release.yml@refs/heads/main; '
                   'https://github.com/EKGF/grapharch/actions/runs/43024114387/attempts/1\n')
        with patch.object(central.subprocess, 'check_output', return_value=release):
            central.verify_generator(Path('/unused/grapharch'), manifest.validate(self.settings()))

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

    def test_failed_pull_request_preview_is_reported_and_omitted(self):
        import contextlib
        import io
        import os
        from unittest.mock import patch
        import central_publications as central
        preview = {'slug': 'pr-42', 'branch': 'issue/schedule', 'source_commit': 'c' * 40,
                   'pull_request': 42}
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'complete'
            summary = Path(temp) / 'summary.md'
            def build(publication, staging):
                tree = staging / 'publications' / publication['slug']
                tree.mkdir(parents=True)
                (tree / 'partial.html').write_text('partial')
                if publication['slug'] == 'pr-42':
                    raise RuntimeError('configured DPROD collector must be typed CollectorUse')
            packaged = []
            def package(staging, published):
                self.assertFalse((staging / 'publications/pr-42').exists())
                packaged.extend(p['slug'] for p in published)
            log = io.StringIO()
            with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), \
                 contextlib.redirect_stderr(log):
                central.assemble_atomic(output, [{'slug': 'main'}, {'slug': 'develop'}, preview],
                                        build, package)
            self.assertEqual(packaged, ['main', 'develop'])
            self.assertTrue((output / 'publications/develop/partial.html').is_file())
            self.assertFalse((output / 'publications/pr-42').exists())
            for report in (log.getvalue(), summary.read_text()):
                self.assertIn('PR #42', report)
                self.assertIn('issue/schedule', report)
                self.assertIn('configured DPROD collector must be typed CollectorUse', report)

    def test_preview_report_carries_the_engines_diagnostics(self):
        import contextlib
        import io
        import os
        from unittest.mock import patch
        import central_publications as central
        with tempfile.TemporaryDirectory() as temp:
            engine = Path(temp) / 'grapharch'
            engine.write_text('#!/bin/sh\nprintf "error: configured DPROD collector must be typed CollectorUse\\n" >&2\n'
                              'exit 1\n')
            engine.chmod(0o755)
            log = io.StringIO()
            with contextlib.redirect_stderr(log), \
                 self.assertRaises(subprocess.CalledProcessError) as failure:
                central.run_engine(engine, ['build-dprod'])
            self.assertIn('must be typed CollectorUse', log.getvalue())
            summary = Path(temp) / 'summary.md'
            preview = {'slug': 'pr-42', 'branch': 'issue/schedule', 'source_commit': 'c' * 40,
                       'pull_request': 42}
            with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), \
                 contextlib.redirect_stderr(io.StringIO()):
                central.omit_preview(preview, failure.exception, Path(temp))
            self.assertIn('error: configured DPROD collector must be typed CollectorUse', summary.read_text())

    def test_release_failure_is_never_isolated_like_a_preview(self):
        import contextlib
        import io
        import central_publications as central
        preview = {'slug': 'pr-42', 'branch': 'issue/schedule', 'source_commit': 'c' * 40,
                   'pull_request': 42}
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'complete'
            def build(publication, staging):
                raise RuntimeError(f'deliberate {publication["slug"]} error')
            with contextlib.redirect_stderr(io.StringIO()), \
                 self.assertRaisesRegex(RuntimeError, 'deliberate main error'):
                central.assemble_atomic(output, [preview, {'slug': 'main'}, {'slug': 'develop'}], build,
                                        lambda staging, published: self.fail('must not package partial output'))
            self.assertFalse(output.exists())

    def test_omitted_preview_leaves_no_route_inventory_or_record_entry(self):
        import contextlib
        import io
        import os
        import shutil
        from unittest.mock import patch
        import central_publications as central
        import publication_resources
        config = manifest.validate(self.settings())
        selected = manifest.select(config, {'main': 'a' * 40, 'develop': 'b' * 40}, [
            {'number': 42, 'title': 'Schedule', 'head': {'ref': 'issue/schedule', 'sha': 'c' * 40,
             'repo': {'full_name': 'EKGF/dprod'}}}])
        self.assertEqual([p['slug'] for p in selected], ['main', 'develop', 'pr-42'])
        captured = {}
        def engine(binary, arguments):
            options = {key: value for key, value in zip(arguments[1:], arguments[2:]) if key.startswith('--')}
            if arguments[0] == 'build-dprod':
                if options['--git-ref'] == 'c' * 40:
                    raise subprocess.CalledProcessError(1, [str(binary), 'publication', 'build-dprod'])
                specification = Path(options['--output-root']) / 'specification'
                specification.mkdir(parents=True)
                (specification / 'index.html').write_text('<!doctype html>')
            elif arguments[0] == 'build-site':
                captured['inventory'] = Path(options['--definitions']).read_text()
                site = Path(options['--output-root']) / 'site'
                site.mkdir(parents=True)
                (site / 'publication-versions.json').write_text('{}')
            else:
                self.assertEqual(arguments[0], 'package-site')
                captured['hosting'] = json.loads(Path(options['--config']).read_text())
                (Path(options['--output-root']) / '.vercel/output/static/dprod').mkdir(parents=True)
        def serialize(git, item, specification):
            for name in ('dprod.jsonld', 'dprod.rdf', 'dprod-all.ttl', 'dprod-all.rdf', 'dprod-all.jsonld',
                         'dprod-shapes.jsonld', 'dprod-shapes.rdf', 'dprod-context.jsonld',
                         'dprod-simple.jsonld', 'source-resources.json'):
                (specification / name).write_text(item['source_commit'])
            return []
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            (root / 'publication').mkdir(parents=True)
            shutil.copyfile(ROOT / config['website']['definitions'], root / config['website']['definitions'])
            binary = Path(temp) / 'grapharch'
            binary.write_text('engine')
            output = Path(temp) / 'complete'
            summary = Path(temp) / 'summary.md'
            with patch.object(central, 'verify_generator'), patch.object(central, 'run_engine', engine), \
                 patch.object(central.subprocess, 'run'), \
                 patch.object(publication_resources, 'serialize', serialize), \
                 patch.object(publication_resources, 'retain_assets'), \
                 patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), \
                 contextlib.redirect_stderr(io.StringIO()):
                central.build_all(root, config, selected, binary, output, 'd' * 40)
            record = json.loads((output / 'publication-build.json').read_text())
            deployed = json.loads((output / 'deployment/.vercel/output/static/dprod/publication-build.json').read_text())
            self.assertEqual([p['slug'] for p in record['publications']], ['main', 'develop'])
            self.assertEqual(deployed, record)
            self.assertEqual([tree['destination'] for tree in captured['hosting']['static_trees']],
                             ['spec/main', 'spec/develop'])
            self.assertNotIn('pr-42', json.dumps(captured['hosting']))
            self.assertIn('ga:route "/dprod/spec/develop/"', captured['inventory'])
            self.assertNotIn('pr-42', captured['inventory'])
            self.assertNotIn('c' * 40, captured['inventory'])
            self.assertFalse((output / 'publications/pr-42').exists())
            self.assertIn('PR #42', summary.read_text())

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
