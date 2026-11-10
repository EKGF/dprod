"""Publication adapters have RDF identities separate from configured uses."""
from pathlib import Path
import unittest
from rdflib import Graph, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
GA = Namespace('https://ekgf.org/ontology/grapharch#')


class ComponentIdentityTests(unittest.TestCase):
    def test_publication_targets_reference_shared_renderer_resources(self):
        supported = {GA.HtmlRenderer, GA.WebsiteRenderer, GA.SpecificationRenderer,
                     GA.SpecificationPagesRenderer, GA.BookshelfRenderer, GA.TypstRenderer}
        for path in sorted((ROOT / 'publication').glob('*.ttl')):
            graph = Graph().parse(path)
            for target in graph.subjects(RDF.type, GA.Target):
                with self.subTest(configuration=path.name, target=target):
                    renderers = list(graph.objects(target, GA.renderer))
                    self.assertEqual(len(renderers), 1)
                    self.assertIsInstance(renderers[0], URIRef)
                    self.assertIn(renderers[0], supported)

    def test_configured_collectors_keep_sources_on_the_use(self):
        for path in sorted((ROOT / 'publication').glob('*.ttl')):
            graph = Graph().parse(path)
            self.assertFalse(list(graph.subjects(RDF.type, GA.Collector)), path.name)
            for project in graph.subjects(RDF.type, GA.Project):
                for use in graph.objects(project, GA.collector):
                    with self.subTest(configuration=path.name, collector=use):
                        self.assertIn((use, RDF.type, GA.CollectorUse), graph)
                        definitions = list(graph.objects(use, GA.collectorType))
                        self.assertEqual(len(definitions), 1)
                        self.assertIsInstance(definitions[0], URIRef)
                        self.assertIsNone(graph.value(use, GA.kind))
                        self.assertIsNotNone(graph.value(use, GA.source))


if __name__ == '__main__':
    unittest.main()
