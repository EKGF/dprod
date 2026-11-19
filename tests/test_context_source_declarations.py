"""Derived contexts must not invent DPROD terms absent from a selected version."""
import sys
from pathlib import Path
import unittest

from rdflib import Graph, RDF, URIRef

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'spec-generator'))
from jsonld_context import ApplicationContext, SimpleContext


class ContextSourceDeclarationTests(unittest.TestCase):
    def test_supplemental_property_is_coerced_only_when_declared_in_source_namespace(self):
        historical = 'https://www.omg.org/spec/DPROD/dprod/'
        current = 'https://ekgf.org/dprod/spec/develop/'
        graph = Graph()
        graph.add((URIRef(current + 'operandProperty'), RDF.type, RDF.Property))
        for factory in (ApplicationContext, SimpleContext):
            old_context = factory(graph, namespace=historical).as_dict()
            self.assertNotIn('dprod:operandProperty', old_context)
            self.assertNotIn('operandProperty', old_context)
            current_context = factory(graph, namespace=current).as_dict()
            self.assertEqual(current_context['dprod:operandProperty'],
                             {'@id': 'dprod:operandProperty', '@type': '@id'})


if __name__ == '__main__':
    unittest.main()
