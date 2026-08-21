from rdflib import Namespace, RDF, RDFS, SH, SKOS

debug = False
show_source = False

ontology_namespace_iri = "https://www.omg.org/spec/DPROD/dprod/"
DPROD = Namespace(ontology_namespace_iri)
shapes_graph_ns_iri = "https://www.omg.org/spec/DPROD/shapes/"
DPROD_SHAPES = Namespace(shapes_graph_ns_iri)

contracts_shapes_ns_iri = "https://www.omg.org/spec/DPROD/contracts/shapes/"
DPROD_CONTRACTS_SHAPES = Namespace(contracts_shapes_ns_iri)

linkedin_ns_iri = "https://www.linkedin.com/in/"
LINKEDIN = Namespace(linkedin_ns_iri)

IGNORED_NODE_SHAPE_PREDICATES = (
    RDF.type,
    RDFS.label,
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

# The JSON-LD context published for instance documents is built in
# jsonld_context.py, from the ontology graph. There is deliberately no second
# hand-maintained context definition here (issue #246).
