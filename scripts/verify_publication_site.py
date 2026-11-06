"""Verify the assembled publication and its source revision identities over HTTP."""
import argparse
import json
from pathlib import Path
import urllib.request


def verify(base_url, record_path):
    record = json.loads(record_path.read_text())
    mount = record['mount']
    routes = [mount + path for path in ['/', '/why/', '/concepts/', '/adopt/', '/roadmap/', '/spec-versions/']]
    for item in record['publications']:
        root = f'{mount}/spec/{item["slug"]}'
        routes += [root + path for path in ['/', '/specification/', '/dprod.ttl', '/dprod-simple.jsonld', '/build-provenance.json']]
        with urllib.request.urlopen(base_url.rstrip('/') + root + '/build-provenance.json', timeout=60) as response:
            provenance = json.load(response)
        if provenance['source_commit'] != item['source_commit']:
            raise ValueError(f'wrong source revision at {root}')
        if provenance['generator_revision'] != record['generator_revision']:
            raise ValueError(f'wrong generator revision at {root}')
    for route in routes:
        with urllib.request.urlopen(base_url.rstrip('/') + route, timeout=60) as response:
            if response.status != 200:
                raise ValueError(f'HTTP {response.status}: {route}')
            if not response.read(1):
                raise ValueError(f'empty publication route: {route}')
        print('Verified ' + route)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--record', type=Path, required=True)
    args = parser.parse_args()
    verify(args.base_url, args.record)
