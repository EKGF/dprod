"""Verify the assembled publication and its source revision identities over HTTP."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.request

PRODUCTION = 'https://ekgf.org/dprod/'
WEBSITE_ROUTES = ['/', '/why/', '/concepts/', '/adopt/', '/roadmap/', '/spec-versions/']


class Links(HTMLParser):
    """Collect navigable hrefs; canonical metadata links are not navigation."""

    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'href' in attrs and not (tag == 'link' and attrs.get('rel') in ('canonical', 'alternate')):
            self.hrefs.append(attrs['href'])


def absolute_internal_links(html, mount, locations):
    """Links that name a website location or the host mount instead of being relative."""
    parser = Links()
    parser.feed(html)
    prefixes = tuple(locations) + (mount + '/',)
    return [href for href in parser.hrefs if href.startswith(prefixes)]


def verify(base_url, record_path):
    record = json.loads(record_path.read_text())
    mount = record['mount']
    routes = [mount + path for path in WEBSITE_ROUTES]
    locations = {PRODUCTION, record.get('publication_url', PRODUCTION)}
    for item in record['publications']:
        root = f'{mount}/spec/{item["slug"]}'
        routes += [root + path for path in ['/', '/specification/', '/dprod.ttl', '/dprod-simple.jsonld', '/build-provenance.json']]
        with urllib.request.urlopen(base_url.rstrip('/') + root + '/build-provenance.json', timeout=60) as response:
            provenance = json.load(response)
        # GraphArch build-revision provenance (version 2): content from the
        # designated commit, definitions from this build's controlling commit.
        if provenance.get('version') != 2:
            raise ValueError(f'unsupported build provenance at {root}')
        if provenance['content']['commit'] != item['source_commit']:
            raise ValueError(f'wrong source revision at {root}')
        if provenance['definitions']['commit'] != record['config_commit']:
            raise ValueError(f'wrong definitions revision at {root}')
        if provenance['generator']['revision'] != record['generator_revision']:
            raise ValueError(f'wrong generator revision at {root}')
    for route in routes:
        with urllib.request.urlopen(base_url.rstrip('/') + route, timeout=60) as response:
            if response.status != 200:
                raise ValueError(f'HTTP {response.status}: {route}')
            body = response.read()
            if not body:
                raise ValueError(f'empty publication route: {route}')
        if route in (mount + path for path in WEBSITE_ROUTES):
            found = absolute_internal_links(body.decode('utf-8'), mount, locations)
            if found:
                raise ValueError(f'{route} links its own site absolutely: {sorted(set(found))}')
        print('Verified ' + route)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--record', type=Path, required=True)
    args = parser.parse_args()
    verify(args.base_url, args.record)
