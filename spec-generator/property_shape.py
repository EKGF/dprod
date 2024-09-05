from __future__ import annotations

from dataclasses import dataclass

from rdflib import URIRef, Graph, Literal, RDFS, DCTERMS, SH

import node_shape
from globals import debug, IGNORED_PROPERTY_SHAPE_PREDICATES, ontology_namespace_iri
from functions import short_name, null_html_string, shacl_short_name, is_empty_string, cast_to_uri_ref


@dataclass(init=False)
class PropertyShape:
    name: str
    axiom_iri: URIRef
    shape_iri: URIRef
    node_shape: node_shape.NodeShape
    label: str = None
    description: str = None
    comment: str = None
    domain: URIRef = None
    range: URIRef = None
    range_short: str = None
    datatype: URIRef = None
    shacl_class: URIRef = None

    def __init__(self, g: Graph, shape_iri: URIRef, **kwargs):
        if shape_iri is None:
            raise ValueError("No shape IRI provided for PropertyShape")
        self.shape_iri = shape_iri
        self.axiom_iri = cast_to_uri_ref(g.value(self.shape_iri, SH.path))
        if self.axiom_iri is None:
            raise ValueError(f"ERROR: No sh:path found for property shape {self.shape_iri}")
        self.__dict__.update(kwargs)
        if self.axiom_iri is None:
            raise ValueError(f"No sh:path found for property shape {self.shape_iri}")
        if self.node_shape is None:
            raise ValueError(f"No NodeShape provided for PropertyShape {self.axiom_iri}")
        # First process all the triples of the OWL-defined property
        for rdf_predicate, rdf_object in g.predicate_objects(self.axiom_iri):
            self._set_prop(g, rdf_predicate, rdf_object, 'OWL')
        # Then process all the triples of the SHACL shape, overriding the OWL properties with the same local name
        for rdf_predicate, rdf_object in g.predicate_objects(self.shape_iri):
            self._set_prop(g, rdf_predicate, rdf_object, 'SHACL')

        self.axiom_iri_normalized = g.namespace_manager.normalizeUri(self.axiom_iri)
        self.shape_name = short_name(self.shape_iri)
        self._init_name()
        self._init_label(g)
        # self._init_shape_description(g)
        # self._init_description(g)
        self._init_comment(g)
        self.node_shape.add_property(self)
        self._init_range(g)
        self._init_domain(g)

    def _set_prop(self, g, rdf_predicate, rdf_object, source):
        if rdf_predicate in IGNORED_PROPERTY_SHAPE_PREDICATES:
            return
        if isinstance(rdf_object, Literal):
            # Only process English language literals for now
            if rdf_object.language is not None and rdf_object.language != 'en':
                return
            value = null_html_string(rdf_object, source)
            if value is not None:
                self.__dict__[shacl_short_name(rdf_predicate)] = value
                print(
                    f"  {g.namespace_manager.normalizeUri(self.axiom_iri)}: {g.namespace_manager.normalizeUri(rdf_predicate)}: {value}") if debug else None
        else:
            self.__dict__[shacl_short_name(rdf_predicate)] = rdf_object
            print(
                f"  {g.namespace_manager.normalizeUri(self.axiom_iri)}: {g.namespace_manager.normalizeUri(rdf_predicate)}: {g.namespace_manager.normalizeUri(rdf_object)}") if debug else None

    def _init_name(self):
        self.name = short_name(self.axiom_iri)
        self.name = null_html_string(self.name.replace(f'{self.node_shape.name}-', ''))

    def _init_label(self, g):
        """Possibly override SHACL property label with OWL property label if there is one"""
        label = g.value(self.axiom_iri, RDFS.label)
        if label:
            self.label = null_html_string(label, 'OWL')

    def _init_shape_description(self, g):
        if self.shape_iri is None:
            return
        self.description = null_html_string(g.value(self.shape_iri, DCTERMS.description), 'SHACL')

    def _init_description(self, g):
        """Shape description overrides the OWL property description"""
        if self.description is None:
            description = g.value(self.axiom_iri, DCTERMS.description)
            if description is not None:
                self.description = null_html_string(description, 'OWL')

    def _init_comment(self, g):
        comment = g.value(self.axiom_iri, RDFS.comment)
        if comment:
            self.comment = null_html_string(comment, 'OWL')

    def _init_range(self, g):
        if self.range is None and self.datatype is None and self.shacl_class is None:
            return
        if self.shacl_class is not None:
            self.range = self.shacl_class
        elif self.datatype is not None:
            self.range = self.datatype
        if self.range is not None:
            self.range_short = g.namespace_manager.normalizeUri(self.range)
            return

    def _init_domain(self, g):
        self.domain = self.node_shape.axiom_iri
        self.domain_short = g.namespace_manager.normalizeUri(self.domain)

    def html_id(self):
        """Return the id to be used in the generated HTML for this property"""
        if self.axiom_iri.__contains__(ontology_namespace_iri):
            return self.axiom_iri.replace(ontology_namespace_iri, '').lower()
        return self.shape_name.lower()

    def href(self):
        """Return the href value that provides the shortest way to reach the property's section, which
         may be on the same page if it's part of a local shape or class, 
         or on another page if it's part of a different shape or class."""
        if self.axiom_iri.__contains__(ontology_namespace_iri):
            return f"#{self.axiom_iri.replace(ontology_namespace_iri, '').lower()}"
        return self.axiom_iri

    def html_domain(self):
        if self.domain is None:
            return ''
        if self.domain.__contains__(ontology_namespace_iri):
            return f"""<a href="#{self.domain.replace(ontology_namespace_iri, '').lower()}" title="{self.domain}">{self.domain_short}</a>"""
        return f"""<a href="{self.domain}" title="{self.domain}">{self.domain_short}</a>"""

    def html_range(self):
        if is_empty_string(self.range):
            return ''
        if self.range_short is None:
            raise ValueError(
                f"Missing \"range_short\" for property \"{self.name}\" of class \"{self.node_shape.shape_iri}\" while a range has been set: {self.range}")
        if self.range.__contains__(ontology_namespace_iri):
            return f"""<a href="#{self.range.replace(ontology_namespace_iri, '').lower()}" title="{self.range}">{self.range_short}</a>"""
        return f"""<a href="{self.range}" title="{self.range}">{self.range_short}</a>"""
