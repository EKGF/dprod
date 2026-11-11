"""Two publication editions share technical content and retain distinct front matter."""
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')
DOC = Namespace('urn:dprod-showcase:')
DCT = Namespace('http://purl.org/dc/terms/')


class GrapharchEditionTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph().parse(ROOT / 'publication/standards.ttl')

    def test_generator_installs_the_same_verified_release_without_a_compiler(self):
        workflow = (ROOT / '.github/workflows/grapharch-pages.yml').read_text()
        self.assertIn('uses: ./.grapharch-tool', workflow)
        self.assertIn('version: ${{ steps.config.outputs.version }}', workflow)
        self.assertIn('expected-revision: ${{ steps.config.outputs.generator }}', workflow)
        self.assertNotIn('cargo build', workflow)
        self.assertNotIn('setup-rust-toolchain', workflow)

    def test_active_editions_are_distinct_drafts_not_the_approved_release(self):
        graph = self.graph
        self.assertEqual(set(graph.objects(DOC.project, GA.target)),
                         {DOC.specification, DOC.website, DOC.pdf, DOC['omg-pdf'], DOC['overview-pdf']})
        for target, destination, status in (
            (DOC.pdf, 'pdf/ekgf', 'Community Draft'),
            (DOC['omg-pdf'], 'pdf/omg', 'Submission Preview'),
        ):
            self.assertEqual(str(graph.value(target, GA.destination)), destination)
            self.assertEqual(str(graph.value(target, GA.publicationStatus)), status)
            self.assertEqual(graph.value(target, GA.renderer), GA.TypstRenderer)
            self.assertEqual(graph.value(target, GA.scope), DOC.scope)
            self.assertIsNone(graph.value(target, GA.documentIdentifier))
            self.assertIsNone(graph.value(target, GA.approvalStatus))
        self.assertNotEqual(graph.value(DOC.pdf, GA.publisher),
                            graph.value(DOC['omg-pdf'], GA.publisher))

    def test_omg_edition_selects_the_formal_typst_skin(self):
        self.assertEqual(str(self.graph.value(DOC['omg-pdf-profile'], GA.style)), 'omg')
        self.assertEqual(str(self.graph.value(DOC['pdf-profile'], GA.style)), 'specification')

    def test_technical_placements_are_shared_front_matter_is_distinct(self):
        graph = self.graph
        profiles = [graph.value(target, GA.profile) for target in (DOC.pdf, DOC['omg-pdf'])]
        def placements(profile, front):
            return {placement for placement in graph.objects(profile, GA.placement)
                    if (str(graph.value(placement, GA.sectionRole)) in {'preface', 'status'}) == front}
        self.assertTrue(placements(profiles[0], False))
        self.assertEqual(placements(profiles[0], False), placements(profiles[1], False))
        self.assertTrue(placements(profiles[0], True).isdisjoint(placements(profiles[1], True)))
        for profile in profiles:
            self.assertIn(GA.preamble, graph.objects(profile, GA.requiredMetadata))
            for placement in placements(profile, True):
                component = graph.value(placement, GA.component)
                fragment = graph.value(component, GA.fragment)
                collector = next(node for node in graph.subjects(GA.fragment, fragment)
                                 if (node, RDF.type, GA.CollectorUse) in graph)
                self.assertIn(collector, graph.objects(DOC.project, GA.collector))
                text = (ROOT / str(graph.value(collector, GA.source))).read_text()
                if str(graph.value(placement, GA.sectionRole)) == 'status':
                    self.assertIn('not an approved OMG', text)
        self.assertEqual(graph.value(DOC.specification, GA.profile), DOC.profile)
        self.assertEqual(placements(DOC.profile, True), placements(profiles[0], True))

    def test_specification_links_both_pdf_editions(self):
        rows = list(self.graph.objects(DOC.specification, GA.metadataRow))
        row = next(row for row in rows if str(self.graph.value(row, DCT.title)) == 'PDF editions:')
        body = str(self.graph.value(row, GA.body))
        self.assertIn('../pdf/ekgf/document.pdf', body)
        self.assertIn('../pdf/omg/document.pdf', body)
        self.assertIn('EKGF community draft', body)
        self.assertIn('OMG submission preview', body)


if __name__ == '__main__':
    unittest.main()
