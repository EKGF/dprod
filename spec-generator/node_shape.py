from dataclasses import dataclass

from rdflib import URIRef, Graph, SH, DCTERMS, Literal, RDFS

from functions import short_name, null_html_string, cast_to_uri_ref
from globals import IGNORED_NODE_SHAPE_PREDICATES, shapes_graph_ns_iri


@dataclass(init=False)
class NodeShape:
    name: str
    shape_iri: URIRef
    axiom_iri: URIRef
    properties: dict
    label: str = None
    description: str | None = None
    comment: str | None = None
    type_name: str | None = None

    def __init__(self, g: Graph, **kwargs):
        self.properties = {}
        self.__dict__.update(kwargs)
        if self.shape_iri is None:
            raise ValueError("No IRI provided for NodeShape")
        self.axiom_iri = cast_to_uri_ref(g.value(self.shape_iri, SH.targetClass))
        if self.axiom_iri is None:
            raise ValueError("No sh:axiom_iri provided for NodeShape")
        # First load the properties of the OWL target class
        for rdf_predicate, rdf_object in g.predicate_objects(self.axiom_iri):
            self._set_prop(g, rdf_predicate, rdf_object, 'OWL')
        # Then load the properties of the SHACL shape, overriding the OWL properties
        for rdf_predicate, rdf_object in g.predicate_objects(self.shape_iri):
            self._set_prop(g, rdf_predicate, rdf_object, 'SHACL')

        self._init_name()
        self._init_description(g)

    def _set_prop(self, g, rdf_predicate, rdf_object, source):
        if rdf_predicate in IGNORED_NODE_SHAPE_PREDICATES:
            """Ignore these properties"""
            return
        if isinstance(rdf_object, Literal):
            # Only process English language literals for now
            if rdf_object.language is not None and rdf_object.language != 'en':
                return
            value = self.type_name = null_html_string(rdf_object, source)
            if value is not None:
                self.__dict__[short_name(rdf_predicate)] = value
                print(
                    f"  {g.namespace_manager.normalizeUri(self.shape_iri)}: {g.namespace_manager.normalizeUri(rdf_predicate)}: {value}")
        else:
            self.__dict__[short_name(rdf_predicate)] = rdf_object
            print(
                f"  {g.namespace_manager.normalizeUri(self.shape_iri)}: {g.namespace_manager.normalizeUri(rdf_predicate)}: {g.namespace_manager.normalizeUri(rdf_object)}")

    def _init_name(self):
        name = short_name(self.shape_iri)
        self.name = name[:-len("Shape")] if name.endswith("Shape") else name
        print(f"""Processing SHACL NodeShape "{name}" for OWL Class "{self.axiom_iri}":""")

    def _init_description(self, g: Graph):
        description = g.value(URIRef(self.shape_iri), DCTERMS.description)
        self.description = null_html_string(description)
        if self.description is not None:
            if self.description == self.comment:
                self.comment = None

    def subclass_uris(self, g):
        for s, p, o in g.triples((None, RDFS.subClassOf, self.shape_iri)):
            yield s

    def add_property(self, property_shape):
        print(f"  Adding property {property_shape.name} to class {self.name}")
        self.properties[property_shape.shape_iri] = property_shape

    def property_iris(self, g):
        """Return the URIs of the properties of this "class", 
        i.e., the properties specified by the NodeShape
        for the "targetClass"""
        for rdf_object in g.objects(subject=self.shape_iri, predicate=SH.property):
            yield rdf_object

    def html_id(self) -> str | None:
        """Return the id to be used in the generated HTML for this class"""
        if self.shape_iri.__contains__(shapes_graph_ns_iri):
            return self.shape_iri.replace(shapes_graph_ns_iri, '').lower()
        return self.name.lower()
