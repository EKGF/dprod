"""Build all selected Git publications with one engine, then assemble one site."""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import publication_manifest as manifest


def committed_configuration(root, path):
    root = root.resolve()
    try:
        relative = path.resolve().relative_to(root)
    except ValueError as error:
        raise ValueError('publication manifest must belong to the trusted source checkout') from error
    subprocess.run(['git', '-C', str(root), 'ls-files', '--error-unmatch', str(relative)],
                   check=True, stdout=subprocess.DEVNULL)
    dirty = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True)
    untracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard', '--',
                                        'publication', 'scripts', 'spec-generator'], text=True)
    if dirty or untracked:
        raise ValueError('central publication requires committed configuration, content and executable inputs')
    return manifest.require_sha(subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip())


def omit_preview(publication, error, staging):
    """Report a failed pull-request preview and remove anything it left in staging."""
    tree = staging / 'publications' / publication['slug']
    if tree.exists():
        shutil.rmtree(tree)
    source = f'{publication["branch"]} at {publication["source_commit"]}'
    reason = f'{type(error).__name__}: {error}'
    if getattr(error, 'stderr', None):
        reason += '\n' + error.stderr
    print(f'PR #{publication["pull_request"]} ({source}) preview omitted from the site and '
          f'version inventory: {reason}', file=sys.stderr, flush=True)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as stream:
            stream.write(f'### PR #{publication["pull_request"]} preview omitted\n\n'
                         f'`{source}` failed to build. It is not deployed and not listed in the '
                         f'version inventory; develop and release publications are unaffected.\n\n'
                         f'~~~text\n{reason}\n~~~\n\n')


def assemble_atomic(output, publications, build, package):
    if output.exists():
        raise ValueError('publication output must not already exist')
    output.parent.mkdir(parents=True, exist_ok=True)
    # The staging tree is never a deployed site. Failure leaves output absent.
    with tempfile.TemporaryDirectory(prefix='.publication-build-', dir=output.parent) as temporary:
        staging = Path(temporary)
        published = []  # bounded: maximum_publications <= 32.
        for publication in publications:
            if 'pull_request' not in publication:
                # Develop and release publications are all-or-nothing.
                build(publication, staging)
            else:
                try:
                    build(publication, staging)
                except Exception as error:
                    # A failing PR preview is reported and omitted; it never
                    # blocks the develop and release deployment.
                    omit_preview(publication, error, staging)
                    continue
            published.append(publication)
        package(staging, published)
        staging.rename(output)


def run_engine(engine, arguments):
    # Selected Git sources are data. No deployment/discovery credential enters
    # the document processor's environment, including subprocesses it launches.
    environment = {key: value for key, value in os.environ.items() if key in {
        'PATH', 'HOME', 'TMPDIR', 'TEMP', 'LANG', 'LC_ALL', 'SYSTEMROOT',
        'SSL_CERT_FILE', 'SSL_CERT_DIR', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY',
    }}
    command = [str(engine), 'publication', *arguments]
    # Diagnostics stream to the log as they arrive; the tail is kept so a
    # failure report states the engine's reason, not only its exit status.
    diagnostics = collections.deque(maxlen=20)  # bounded: last 20 lines.
    with subprocess.Popen(command, env=environment, stderr=subprocess.PIPE,
                          encoding='utf-8', errors='replace') as process:
        for line in process.stderr:
            sys.stderr.write(line)
            diagnostics.append(line.rstrip('\n'))
    sys.stderr.flush()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, stderr='\n'.join(diagnostics))


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_generator(engine, config):
    """Require the installed binary to identify the pinned release and source commit."""
    lines = subprocess.check_output([str(engine), '--version'], text=True).splitlines()
    version = re.fullmatch(r'grapharch (\d+\.\d+\.\d+)(?: \(build \d+\))?', lines[0] if lines else '')
    if version is None or version[1] != config['generator_version']:
        raise ValueError('generator binary version differs from the publication manifest')
    sources = {match for line in lines[1:] for match in re.findall(r'source commit ([0-9a-f]{40})\b', line)}
    if sources != {config['generator_revision']}:
        raise ValueError('generator binary source commit differs from the publication manifest')


def build_all(root, config, selected, engine, output, config_revision, hosting_profile=None):
    from publication_resources import retain_assets, serialize
    verify_generator(engine, config)
    repository = 'https://github.com/' + config['repository'] + '.git'
    cache = root / 'output/central-git-cache'
    cache.mkdir(parents=True, exist_ok=True)
    git = cache / 'sources.git'
    if not git.exists():
        subprocess.run(['git', 'init', '--bare', str(git)], check=True)
    observed = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

    def build(item, staging):
        # Fetch source objects only; never check out or execute another branch.
        subprocess.run(['git', '-C', str(git), 'fetch', '--no-tags', repository, item['source_commit']], check=True)
        destination = staging / 'publications' / item['slug']
        run_engine(engine, ['build-dprod', '--git-repository', repository,
                   '--git-ref', item['source_commit'], '--definitions', item['definitions'],
                   '--generator-revision', config['generator_revision'],
                   '--git-cache', str(cache / 'grapharch'), '--output-root', str(destination), '--json'])
        specification = destination / 'specification'
        if not (specification / 'index.html').is_file():
            raise ValueError(f'{item["slug"]}: no specification/index.html target')
        resources = serialize(git, item, specification)
        if 'dprod-contracts-prof.ttl' in resources:
            profile = specification / 'contracts/profile'
            profile.mkdir(parents=True)
            shutil.copyfile(specification / 'dprod-contracts-prof.ttl', profile / 'index.ttl')
        # Keep target-relative links intact. The old entry URL redirects into
        # the specification target; sibling PDFs and website pages retain their
        # original relative relationship instead of rewriting rendered HTML.
        (destination / 'index.html').write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            '<title>Open specification</title>'
            '<script>location.replace("specification/"+location.search+location.hash)</script>'
            '<noscript><meta http-equiv="refresh" content="0;url=specification/"></noscript>'
            '<a href="specification/">Open specification</a></html>\n')
        for name in resources + ['dprod.jsonld', 'dprod.rdf', 'dprod-all.ttl', 'dprod-all.rdf',
                                  'dprod-all.jsonld', 'dprod-shapes.jsonld', 'dprod-shapes.rdf',
                                  'dprod-context.jsonld', 'dprod-simple.jsonld', 'source-resources.json']:
            shutil.copyfile(specification / name, destination / name)
        if (specification / 'contracts').exists():
            shutil.copytree(specification / 'contracts', destination / 'contracts')
        retain_assets(git, item, destination)

    def package(staging, published):
        website = config['website']
        definition = staging / 'project-site.ttl'
        source_definitions = (root / website['definitions']).read_text()
        if hosting_profile is not None:
            from pages_publication import website_definitions
            source_definitions = website_definitions(source_definitions, website['target'], config['canonical_url'])
        definition.write_text(source_definitions + '\n' +
                              manifest.inventory_turtle(config, published, config_revision, observed))
        run_engine(engine, ['build-site', '--source', str(root / website['source']),
                           '--definitions', str(definition), '--project', website['project'],
                           '--target', website['target'], '--output-root', str(staging / 'website')])
        trees = [{'source': str(staging / 'publications' / p['slug']),
                  'destination': 'spec/' + p['slug']} for p in published]
        hosting = {'version': 1, 'mount': config['mount'], 'site': str(staging / 'website/site'),
                   'static_trees': trees, 'directory_aliases': [], 'file_aliases': [],
                   'inventory': str(staging / 'website/site/publication-versions.json'), 'version_path': 'spec'}
        # The longstanding /spec/ URL selects the leading branch; all versions
        # are actual local directories, never Vercel proxy routes.
        leading = next(p for p in published if p['branch'] == config['leading_branch'])
        hosting['directory_aliases'].append({'path': 'spec', 'target': 'spec/' + leading['slug']})
        if any(p['slug'] == 'main' for p in published):
            hosting['directory_aliases'].append({'path': 'spec/archive/1.0', 'target': 'spec/main'})
        for item in published:
            if (staging / 'publications' / item['slug'] / 'dprod-contracts-prof.ttl').is_file():
                hosting['file_aliases'].append({'path': f'spec/{item["slug"]}/contracts/profile/',
                    'target': f'spec/{item["slug"]}/dprod-contracts-prof.ttl', 'content_type': 'text/turtle'})
        if (staging / 'publications' / leading['slug'] / 'dprod-contracts-prof.ttl').is_file():
            hosting['file_aliases'].append({'path': 'spec/contracts/profile/',
                'target': f'spec/{leading["slug"]}/dprod-contracts-prof.ttl', 'content_type': 'text/turtle'})
        configuration = staging / 'hosting.json'
        configuration.write_text(json.dumps(hosting, indent=2) + '\n')
        run_engine(engine, ['package-site', '--config', str(configuration), '--output-root', str(staging / 'deployment')])
        record = {'version': 1, 'repository': repository, 'leading_branch': config['leading_branch'],
                  'mount': config['mount'],
                  'config_commit': config_revision, 'generator_revision': config['generator_revision'],
                  'generator_version': config['generator_version'], 'generator_sha256': sha256(engine), 'observed_at': observed, 'publications': published}
        if hosting_profile is not None:
            from pages_publication import prepare_artifact
            prepare_artifact(staging, config['mount'])
            record['hosting_profile'] = str(hosting_profile.relative_to(root))
            record['publication_url'] = config['canonical_url']
        record_path = staging / 'deployment/.vercel/output/static' / config['mount'][1:] / 'publication-build.json'
        record_path.write_text(json.dumps(record, indent=2) + '\n')
        (staging / 'publication-build.json').write_text(json.dumps(record, indent=2) + '\n')

    assemble_atomic(output, selected, build, package)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('publication/publications.json'))
    parser.add_argument('--hosting-profile', type=Path)
    parser.add_argument('--grapharch', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = committed_configuration(root, args.manifest)
    config = manifest.validate(json.loads(args.manifest.read_text()))
    if args.hosting_profile is not None:
        from pages_publication import hosting_configuration
        committed_configuration(root, args.hosting_profile)
        args.hosting_profile = args.hosting_profile.resolve()
        config = hosting_configuration(config, json.loads(args.hosting_profile.read_text()))
    selected = manifest.discover(config, revision)
    print(json.dumps({'config_commit': revision, 'selected': selected}, indent=2), flush=True)
    build_all(root, config, selected, args.grapharch.resolve(), args.output.resolve(), revision, args.hosting_profile)


if __name__ == '__main__':
    main()
