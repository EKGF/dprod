"""The audience overview is a distinct, source-owned publication."""
import unittest
from pathlib import Path
from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')

class OverviewPublication(unittest.TestCase):
    def test_overview_has_its_own_scope_and_no_reference_catalogue(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        target = DOC['overview-pdf']
        self.assertIn((DOC.project, GA.target, target), graph)
        profile = graph.value(target, GA.profile)
        self.assertEqual(str(graph.value(profile, GA.style)), 'overview')
        self.assertEqual(str(graph.value(target, GA.destination)), 'pdf/overview')
        placements = list(graph.objects(profile, GA.placement))
        self.assertGreaterEqual(len(placements), 7)
        for placement in placements:
            self.assertNotEqual(str(graph.value(placement, GA.sectionRole)), 'reference')
        scope = graph.value(target, GA.scope)
        self.assertNotEqual(scope, DOC.scope)
        includes = set(graph.objects(scope, GA.include))
        for name in ['home', 'why', 'concepts', 'adopt', 'roadmap']:
            self.assertIn(URIRef('urn:dprod:project-site:page:' + name), includes)
        self.assertIn((scope, GA.traverse, GA.topic), graph)
        self.assertEqual(int(graph.value(scope, GA.maxDepth)), 1)

    def test_overview_reuses_canonical_marketing_and_specification_fragments(self):
        import re
        directory = ROOT / 'publication/overview'
        self.assertEqual({p.name for p in directory.glob('*.md')}, {'01-brief.md', '09-reading.md'})
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        profile = graph.value(DOC['overview-pdf'], GA.profile)
        selected = {fragment for placement in graph.objects(profile, GA.placement)
                    for component in graph.objects(placement, GA.component)
                    for fragment in graph.objects(component, GA.fragment)}
        for path in ['publication/project-site/index.md', 'publication/project-site/why.md',
                     'publication/project-site/concepts.md', 'publication/project-site/adopt.md',
                     'publication/project-site/roadmap.md', 'publication/standards/model.md',
                     'publication/standards/contracts.md']:
            frontmatter = (ROOT / path).read_text().split('---', 2)[1]
            identities = {URIRef(v) for v in re.findall(r'^  fragment: (\S+)$', frontmatter, re.M)}
            sections = re.search(r'^  fragments:\n((?:    .*\n?)+)', frontmatter, re.M)
            if sections:
                identities.update(URIRef(v) for v in re.findall(r'^    [^:]+: (\S+)$', sections[1], re.M))
            self.assertTrue(selected & identities, path)
        self.assertIn('UK Bonds', (ROOT / 'publication/standards/model.md').read_text())
        self.assertIn('assets/dprod-overview-model.svg', (ROOT / 'publication/project-site/concepts.md').read_text())

    def test_overview_credits_the_collective_team_without_a_git_appendix(self):
        graph = Graph().parse(ROOT / 'publication/standards.ttl')
        profile = graph.value(DOC['overview-pdf'], GA.profile)
        self.assertEqual(str(graph.value(profile, GA.showProvenance)), 'false')
        self.assertIsNone(graph.value(DOC['pdf-profile'], GA.showProvenance))
        self.assertIsNone(graph.value(DOC['omg-pdf-profile'], GA.showProvenance))
        content = (ROOT / 'publication/project-site/why.md').read_text()
        for name in ['Tony Seale', 'Matthias Autrata', 'Josh Cornejo', 'Jacobus Geluk', 'Andrea Gioia', 'Ben Whittam Smith']:
            self.assertIn(name, content)
        self.assertIn('workgroup chair', content)
        self.assertIn('Data Contracts', content)
        self.assertNotIn('following provenance record', content)
        self.assertNotIn('Recent committers', content)
