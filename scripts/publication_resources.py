"""Serialize native RDF from selected commits using trusted leading-branch code.

No Python, templates, build commands, or dependencies from a selected branch are
executed. RDF imports are deliberately not fetched by this serializer.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import re
import urllib.parse
import xml.etree.ElementTree as ET

from rdflib import Graph, Namespace, OWL, RDF, URIRef

from publication_manifest import require_sha, source_path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'spec-generator'))
from jsonld_context import ApplicationContext, SimpleContext

GA = Namespace('https://ekgf.org/ontology/grapharch#')
PROJECT = URIRef('urn:dprod-showcase:project')


def validate_asset(path, data):
    suffix = Path(path).suffix
    if suffix in {'.png', '.jpg', '.ico'}:
        return data
    if suffix != '.svg':
        raise ValueError(f'unsupported native asset: {path}')
    tree = ET.fromstring(data)
    allowed = {'svg', 'defs', 'g', 'path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline',
               'line', 'text', 'tspan', 'switch', 'foreignObject', 'div', 'span', 'font', 'b', 'br', 'a',
               'marker', 'title', 'desc', 'linearGradient', 'radialGradient', 'stop', 'clipPath'}
    for node in tree.iter():
        tag = node.tag.split('}')[-1]
        if tag not in allowed:
            raise ValueError(f'active or unsupported SVG element: {tag}')
        for attribute, value in node.attrib.items():
            name = attribute.split('}')[-1].lower()
            if name.startswith('on') or name in {'src', 'srcdoc'}:
                raise ValueError('active SVG attribute')
            if name == 'href' and not (value.startswith('#') or
                                       tag == 'a' and urllib.parse.urlsplit(value).scheme == 'https'):
                raise ValueError('external SVG resource is forbidden')
            if name == 'style' and re.search(r'url\s*\(|expression\s*\(|@import|javascript:', value, re.I):
                raise ValueError('active SVG style')
    return data


def retain_assets(repository, item, destination):
    for path in item['assets']:
        target = destination / source_path(path)
        if target.exists():
            raise ValueError(f'native asset path collision: {path}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(validate_asset(path, blob(repository, item['source_commit'], path)))


def blob(repository, revision, path):
    require_sha(revision)
    source_path(path)
    kind = subprocess.check_output(['git', '-C', str(repository), 'ls-tree', revision, '--', path], text=True)
    if not kind.startswith('100644 blob ') and not kind.startswith('100755 blob '):
        raise ValueError(f'source must be a regular Git blob: {path}')
    size = int(subprocess.check_output(['git', '-C', str(repository), 'cat-file', '-s', f'{revision}:{path}']))
    if size > 16 * 1024 * 1024:
        raise ValueError(f'source blob exceeds 16 MiB budget: {path}')
    return subprocess.check_output(['git', '-C', str(repository), 'show', f'{revision}:{path}'])


def serialize(repository, item, destination):
    revision = item['source_commit']
    definitions = Graph().parse(data=blob(repository, revision, item['definitions']), format='turtle')
    ontology = Graph()
    shapes = Graph()
    evidence = []
    collectors = list(definitions.objects(PROJECT, GA.collector))  # bounded: engine limits 64 source collectors.
    if len(collectors) > 64:
        raise ValueError('too many source collectors')
    for collector in collectors:
        if definitions.value(collector, GA.collectorType) != GA.RdfFileCollector:
            continue
        path = str(definitions.value(collector, GA.sourcePath))
        data = blob(repository, revision, path)
        graph = Graph().parse(data=data, format='turtle')
        target = shapes if path.endswith('-shapes.ttl') else ontology
        target += graph
        name = Path(path).name
        if name == 'dprod-ontology.ttl':
            name = 'dprod.ttl'
        target_path = destination / name
        if target_path.exists():
            raise ValueError(f'publication resource collision: {name}')
        target_path.write_bytes(data)
        evidence.append({'path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'published': name})
    core_path = 'ontology/dprod/dprod-ontology.ttl'
    core = Graph().parse(data=blob(repository, revision, core_path), format='turtle')
    namespaces = list(core.subjects(RDF.type, OWL.Ontology))
    if len(namespaces) != 1:
        raise ValueError('core source must declare exactly one ontology identity')
    namespace = str(namespaces[0])
    prefixes = dict(ontology.namespaces())
    prefixes['dprod'] = namespace
    context = {key: str(value) for key, value in prefixes.items()}
    # These are derived representations of this source graph, not old dist/ files.
    for name, graph in [('dprod', ontology), ('dprod-shapes', shapes), ('dprod-all', ontology + shapes)]:
        for suffix, format_name in [('jsonld', 'json-ld'), ('rdf', 'xml')]:
            options = {'context': context, 'auto_compact': True, 'indent': 2} if suffix == 'jsonld' else {}
            graph.serialize(destination=destination / f'{name}.{suffix}', format=format_name, **options)
    (ontology + shapes).serialize(destination=destination / 'dprod-all.ttl', format='turtle')
    for name, factory in [('dprod-context', ApplicationContext), ('dprod-simple', SimpleContext)]:
        (destination / f'{name}.jsonld').write_text(
            json.dumps(factory(ontology, namespace=namespace).as_document(), indent=2) + '\n')
    (destination / 'source-resources.json').write_text(json.dumps({
        'source_commit': revision, 'resources': evidence,
        'serializer_config_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'imports_fetched': False,
    }, indent=2) + '\n')
    return [row['published'] for row in evidence]
