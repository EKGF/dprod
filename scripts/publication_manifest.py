"""Resolve a source-owned publication catalogue, without deployment discovery."""
import datetime
import json
import os
from pathlib import PurePosixPath
import re
import urllib.request
import urllib.parse


def require_sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value) or value == '0' * 40:
        raise ValueError('an exact nonzero lowercase Git SHA is required')
    return value


def source_path(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid source path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value:
        raise ValueError('source paths must be normalized and repository-relative')
    return value


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}', value):
        raise ValueError('invalid publication slug')
    return value


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected.split()):
        raise ValueError(f'configuration requires exactly: {expected}')


def validate(config):
    keys(config, 'version repository leading_branch generator_revision canonical_url mount inventory website publications pull_requests maximum_publications')
    if config['version'] != 1:
        raise ValueError('unsupported manifest version')
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', config['repository']):
        raise ValueError('repository must be a GitHub owner/name')
    require_sha(config['generator_revision'])
    if not config['leading_branch'] or any(c in config['leading_branch'] for c in '\n\r\x00'):
        raise ValueError('invalid leading branch')
    url = urllib.parse.urlsplit(config['canonical_url'])
    if url.scheme != 'https' or not url.netloc or url.query or url.fragment or url.username:
        raise ValueError('canonical_url must be a credential-free HTTPS URL')
    mount = config['mount']
    if not mount.startswith('/') or mount.endswith('/') or url.path != mount + '/':
        raise ValueError('canonical URL and mounted site path disagree')
    source_path(mount[1:])
    if not re.fullmatch(r'urn:[A-Za-z0-9:._-]+', config['inventory']):
        raise ValueError('inventory must be a stable URN')
    keys(config['website'], 'source definitions project target')
    for key in ('source', 'definitions'):
        source_path(config['website'][key])
    maximum = config['maximum_publications']
    if type(maximum) is not int or not 1 <= maximum <= 32:
        raise ValueError('publication budget must be 1..32')
    if not 1 <= len(config['publications']) <= maximum:
        raise ValueError('explicit publication list exceeds budget or is empty')
    seen = set()
    branches = set()
    for item in config['publications']:
        keys(item, 'branch slug label status definitions assets')
        slug(item['slug'])
        source_path(item['definitions'])
        if not isinstance(item['assets'], list) or len(item['assets']) > 32:
            raise ValueError('invalid explicit source asset list')
        for asset in item['assets']:
            source_path(asset)
            if not asset.startswith('assets/'):
                raise ValueError('native assets must remain under assets/')
        if item['slug'] in seen or item['branch'] in branches:
            raise ValueError('duplicate publication path or branch')
        for key in ('label', 'status', 'branch'):
            if not isinstance(item[key], str) or not item[key] or len(item[key]) > 512 or any(ord(c) < 32 for c in item[key]):
                raise ValueError(f'invalid publication {key}')
        seen.add(item['slug'])
        branches.add(item['branch'])
    if config['leading_branch'] not in branches:
        raise ValueError('the leading branch must be an explicit publication')
    keys(config['pull_requests'], 'enabled same_repository_only exclude_branch_prefixes definitions')
    policy = config['pull_requests']
    if type(policy['enabled']) is not bool or policy['same_repository_only'] is not True:
        raise ValueError('this publisher accepts only explicitly enabled same-repository PRs')
    source_path(policy['definitions'])
    if not isinstance(policy['exclude_branch_prefixes'], list) or len(policy['exclude_branch_prefixes']) > 16:
        raise ValueError('invalid excluded branch prefixes')
    if any(not isinstance(p, str) or not p or len(p) > 128 for p in policy['exclude_branch_prefixes']):
        raise ValueError('invalid excluded branch prefix')
    return config


def select(config, heads, pull_requests):
    validate(config)
    selected = []  # bounded: maximum_publications <= 32.
    for item in config['publications']:
        if item['branch'] not in heads:
            raise ValueError(f'missing selected branch {item["branch"]}')
        selected.append(dict(item, source_commit=require_sha(heads[item['branch']])))
    policy = config['pull_requests']
    if policy['enabled']:
        for pr in sorted(pull_requests, key=lambda pr: pr['number']):
            head = pr['head']
            if not head['repo'] or head['repo']['full_name'] != config['repository']:
                continue
            branch = head['ref']
            if any(branch.startswith(p) for p in policy['exclude_branch_prefixes']):
                continue
            if branch in heads:
                continue  # Explicitly selected branches have one canonical publication.
            if type(pr['number']) is not int or pr['number'] <= 0:
                raise ValueError('invalid pull request number')
            if len(selected) >= config['maximum_publications']:
                raise ValueError('selected publication budget exceeded')
            selected.append({'branch': branch, 'slug': f'pr-{pr["number"]}',
                             'label': f'PR #{pr["number"]}: {pr["title"]}',
                             'status': 'Pull request preview — not standardized',
                             'assets': [],
                             'definitions': policy['definitions'], 'source_commit': require_sha(head['sha']),
                             'pull_request': pr['number']})
    if len({p['slug'] for p in selected}) != len(selected):
        raise ValueError('selected publication paths collide')
    return selected


def api(path):
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
               'User-Agent': 'GraphArch-central-publications'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request('https://api.github.com/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read(2 * 1024 * 1024 + 1)
    if len(payload) > 2 * 1024 * 1024:
        raise ValueError('GitHub response exceeds publication discovery budget')
    return json.loads(payload)


def discover(config, config_revision):
    validate(config)
    heads = {}
    for item in config['publications']:
        branch = item['branch']
        # The leading branch is the immutable checkout used for this build.
        heads[branch] = (require_sha(config_revision) if branch == config['leading_branch'] else
                         api(f'repos/{config["repository"]}/commits/{urllib.parse.quote(branch, safe="")}')['sha'])
    prs = []  # bounded: 1,000 API records, then <=32 selected publications.
    if config['pull_requests']['enabled']:
        for page in range(1, 11):
            rows = api(f'repos/{config["repository"]}/pulls?state=open&per_page=100&page={page}')
            if not isinstance(rows, list):
                raise ValueError('invalid pull request response')
            prs.extend(rows)
            if len(rows) < 100:
                break
        else:
            raise ValueError('pull request discovery exceeds 1,000-record budget')
    return select(config, heads, prs)


def inventory_turtle(config, selected, config_revision, observed_at):
    require_sha(config_revision)
    datetime.datetime.fromisoformat(observed_at.replace('Z', '+00:00'))
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    lines = ['@prefix ga: <https://ekgf.org/ontology/grapharch#> .',
             '@prefix dct: <http://purl.org/dc/terms/> .',
             '@prefix doap: <http://usefulinc.com/ns/doap#> .',
             '@prefix dcat: <http://www.w3.org/ns/dcat#> .',
             '@prefix prov: <http://www.w3.org/ns/prov#> .',
             f'<{config["inventory"]}> dct:modified {quote(observed_at)} ;',
             f' prov:wasDerivedFrom <https://github.com/{config["repository"]}/commit/{config_revision}> .']
    for order, item in enumerate(selected):
        identity = config['inventory'] + ':' + slug(item['slug'])
        route = f'{config["mount"]}/spec/{item["slug"]}/'
        canonical = config['canonical_url'] + f'spec/{item["slug"]}/'
        lines.extend([f'<{config["inventory"]}> dct:hasPart <{identity}> .',
                      f'<{identity}> a doap:Version ; ga:order {order} ;',
                      f' dct:title {quote(item["label"])} ; dct:identifier {quote(item["slug"])} ;',
                      f' doap:branch {quote(item["branch"])} ; ga:advertised true ;',
                      f' ga:publicationStatus {quote(item["status"])} ; ga:route {quote(route)} ;',
                      f' dcat:accessURL <{canonical}> ;',
                      f' prov:wasDerivedFrom <https://github.com/{config["repository"]}/commit/{require_sha(item["source_commit"])}> .'])
    return '\n'.join(lines) + '\n'
