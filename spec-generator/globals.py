from rdflib import Namespace, RDF, RDFS, SH, SKOS, OWL, XSD, DCAT, DCTERMS

debug = False
show_source = False

ontology_namespace_iri = "https://ekgf.github.io/dprod/"
DPROD = Namespace(ontology_namespace_iri)
shapes_graph_ns_iri = "https://ekgf.github.io/dprod/dprod-shapes/"
DPROD_SHAPE = Namespace(shapes_graph_ns_iri)

IGNORED_NODE_SHAPE_PREDICATES = (
    RDF.type,
    RDFS.isDefinedBy,
    SKOS.altLabel,
    SKOS.changeNote,
    SKOS.editorialNote,
    SKOS.scopeNote,
    SKOS.definition,
    SH.property
)

IGNORED_PROPERTY_SHAPE_PREDICATES = (
    RDF.type,
    RDFS.isDefinedBy,
    SKOS.altLabel,
    SKOS.changeNote,
    SKOS.editorialNote,
    SKOS.scopeNote,
    SKOS.definition
)

# Define the JSON-LD context
json_ld_context = {
    "@vocab": str(RDF),
    "dprod": ontology_namespace_iri,
    "owl": str(OWL),
    "rdfs": str(RDFS),
    "xsd": str(XSD),
    "dcat": str(DCAT),
    "dct": str(DCTERMS),
    "sh": str(SH),
    "id": "@id",
    "type": "@type"
}
