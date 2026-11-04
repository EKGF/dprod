"""Generate DPROD specification editions and the audience overview from a pinned remote repository revision."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


PROJECT = 'urn:dprod:ci'


def require_commit(value: str) -> str:
    if not re.fullmatch(r'[0-9a-f]{40}', value) or value == '0' * 40:
        raise ValueError('an exact lowercase 40-character Git commit is required')
    return value


def prepare_registry(root: Path, revision: str) -> Path:
    revision = require_commit(revision)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'dprod.json').write_text(json.dumps({
        'repository': 'https://github.com/EKGF/dprod.git',
        'ref': revision,
        'definitions': 'publication/standards.ttl',
    }, indent=2) + '\n', encoding='utf-8')
    registry = root / 'showcases.ttl'
    registry.write_text('''@prefix ga: <https://ekgf.org/ontology/grapharch#> .
@prefix dct: <http://purl.org/dc/terms/> .
<urn:dprod:ci> ga:showcase <urn:dprod:ci:showcase> .
<urn:dprod:ci:showcase> a ga:Showcase ; ga:slug "dprod" ;
    dct:title "DPROD PDF editions" ; ga:order 1 ;
    ga:kind "dprod" ; ga:source "dprod.json" ;
    ga:previewPath "specification/index.html" ;
    ga:pdfPath "pdf/ekgf/document.pdf" .
''', encoding='utf-8')
    return registry


def retain_editions(output: Path, source: str, generator: str) -> None:
    publication = output / 'artifacts/dprod'
    manifest = {'source_repository': 'https://github.com/EKGF/dprod.git',
                'source_commit': source,
                'generator_repository': 'https://github.com/EKGF/grapharch.git',
                'generator_commit': generator,
                'editions': []}
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        manifest['ci'] = {
            'provider': 'GitHub Actions',
            'actor': os.environ.get('GITHUB_ACTOR'),
            'run_url': (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
                        f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"),
        }
    for name, source_directory in (
        ('ekgf-community', 'pdf/ekgf'),
        ('omg-submission-preview', 'pdf/omg'),
        ('overview', 'pdf/overview'),
    ):
        pdf = publication / source_directory / 'document.pdf'
        with pdf.open('rb') as stream:
            if stream.read(5) != b'%PDF-':
                raise ValueError(f'{name} is not a PDF: {pdf}')
        artifact = output / name
        artifact.mkdir()
        target = artifact / f'dprod-{name}.pdf'
        shutil.copyfile(pdf, target)
        with target.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        manifest['editions'].append({'edition': name, 'sha256': digest,
                                    'file': str(target.relative_to(output))})
    rendered_graph = publication / 'documentation.nq'
    if not rendered_graph.is_file():
        raise FileNotFoundError(f'missing retained source evidence: {rendered_graph}')
    for name in ('ekgf-community', 'omg-submission-preview', 'overview'):
        (output / name / 'build-provenance.json').write_text(
            json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (output / 'build-provenance.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grapharch', type=Path, required=True)
    parser.add_argument('--source-revision', type=require_commit, required=True)
    parser.add_argument('--grapharch-revision', type=require_commit, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--registry-root', type=Path,
                        default=Path('output/grapharch-input/registry'))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('output directory must be new or empty')
    root = args.registry_root.resolve()
    prepare_registry(root, args.source_revision)
    subprocess.run([
        str(args.grapharch.resolve()), 'publication', 'verify-gallery',
        '--source', str(root), '--project', PROJECT,
        '--output-root', str(output), '--json',
    ], check=True)
    retain_editions(output, args.source_revision, args.grapharch_revision)


if __name__ == '__main__':
    main()
