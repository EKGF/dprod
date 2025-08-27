import shutil

from rdflib import XSD, OWL, PROV, RDFS

from functions import *
from node_shape import NodeShape
from property_shape import PropertyShape
from jinja import generate_spec_page

from globals import ontology_namespace_iri, shapes_graph_ns_iri, LINKEDIN


# Define a function to add classes and properties to the context
def add_to_context(g, node_shape_iri, node_shapes: dict):
    if not is_node_shape(g, node_shape_iri):  # we're at this point only interested in the NodeShapes
        return
    if node_shapes.get(node_shape_iri) is not None:
        return

    node_shape = NodeShape(shape_iri=node_shape_iri, g=g)
    node_shapes[node_shape_iri] = node_shape

    for property_shape_iri in node_shape.property_iris(g):
        PropertyShape(node_shape=node_shape, shape_iri=property_shape_iri, g=g)


def main():
    print("Generating the specification...")

    g = load_ontologies()
    node_shapes = {}
    for class_uri in g.subjects():
        add_to_context(g, class_uri, node_shapes)

    examples = load_examples("./examples/")

    # TODO: Create a special annotation predicate called something like `preferredSortOrder` that has a value 
    # of type xsd:string and has values like '00001', '00002', etc. to allow for deviating from the default
    # alphabetical order of classes and properties based on the value of `rdfs:label`.
    # This would allow us to remove this DPROD specific list from the code.
    classes = reorder_list(node_shapes.values(), [
        'DataProduct',
        'Port',
        'DataService',
        'Distribution',
        'Dataset',
        'DataProductLifecycleStatus',
        'InformationSensitivityClassification',
        'Protocol',
        'SecuritySchemaType',
        'Enumeration'
    ])

    if os.path.exists('dist'):
        shutil.rmtree('dist')

    os.makedirs('dist/assets')

    # generate_class_and_property_pages(classes)

    generate_spec_page({'classes': classes, 'examples': examples})

    g_ontology = load_dprod_ontology()
    g_shapes = load_dprod_shapes()
    
    jsonld_context_ontology = {
        "@version": 1.1,
        "dprod": ontology_namespace_iri,
        "xsd": str(XSD),
        "owl": str(OWL),
        "dcat": str(DCAT),
        "dct": str(DCTERMS),
        "prov": str(PROV),
        "rdfs": str(RDFS),
        "rdf": str(RDF),
        "sh": str(SH),
        "linkedin": str(LINKEDIN)
    }

    jsonld_context_shapes = {
        "@version": 1.1,
        "dprod": ontology_namespace_iri,
        "dprod-shapes": shapes_graph_ns_iri,
        "xsd": str(XSD),
        "owl": str(OWL),
        "dcat": str(DCAT),
        "dct": str(DCTERMS),
        "prov": str(PROV),
        "rdfs": str(RDFS),
        "rdf": str(RDF),
        "sh": str(SH),
        "odrl": str(ODRL2),
        "linkedin": str(LINKEDIN),
    }

    with open('dist/dprod.jsonld', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF JSON-LD - on its own: ./{f.name}")
        f.write(g_ontology.serialize(
            format='json-ld',
            base=ontology_namespace_iri,
            indent=4,
            context=jsonld_context_ontology,
            auto_compact=True
        ))

    with open('dist/dprod-all.jsonld', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF JSON-LD - all: ./{f.name}")
        f.write(g.serialize(
            format='json-ld',
            base=ontology_namespace_iri,
            indent=4,
            context=jsonld_context_shapes,
            auto_compact=True
        ))

    # with open('dist/dprod.ttl', mode='x', encoding='utf-8') as f:
    #     print(f"Generating RDF Turtle - on its own: ./{f.name}")
    #     f.write(g_ontology.serialize(format='turtle', base=ontology_namespace_iri))

    with open('dist/dprod-all.ttl', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF Turtle - all: ./{f.name}")
        f.write(g.serialize(format='turtle', base=ontology_namespace_iri))

    with open('dist/dprod.rdf', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF/XML - on its own: ./{f.name}")
        f.write(g_ontology.serialize(format='pretty-xml', base=ontology_namespace_iri))

    with open('dist/dprod-all.rdf', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF/XML - all: ./{f.name}")
        f.write(g.serialize(format='pretty-xml', base=ontology_namespace_iri))

    with open('dist/dprod-shapes.ttl', mode='x', encoding='utf-8') as f:
        print(f"Generating SHACL Ontology Turtle - on its own: ./{f.name}")
        f.write(g_shapes.serialize(format='turtle', base=shapes_graph_ns_iri))

    with open('dist/dprod-shapes.jsonld', mode='x', encoding='utf-8') as f:
        print(f"Generating SHACL Ontology JSON-LD - on its own: ./{f.name}")
        f.write(g_shapes.serialize(format='json-ld', base=shapes_graph_ns_iri, indent=4, context=jsonld_context_shapes))

    with open('dist/dprod-shapes.rdf', mode='x', encoding='utf-8') as f:
        print(f"Generating SHACL Ontology RDF/XML - on its own: ./{f.name}")
        f.write(g_shapes.serialize(format='pretty-xml', base=shapes_graph_ns_iri))

    for asset in os.listdir('assets'):
        print(f"Copying asset: {asset}")
        shutil.copy2(f'assets/{asset}', 'dist/assets')
        
    shutil.copy2('assets/favicon.ico', 'dist')

    print("Copying dprod.ttl")
    shutil.copy2('ontology/dprod/dprod-ontology.ttl', 'dist/dprod.ttl')
    print("Copying dprod-shapes.ttl")
    shutil.copy2('ontology/dprod/dprod-shapes.ttl', 'dist/dprod-shapes.ttl')

    print("Specification generated successfully!")


if __name__ == "__main__":
    main()
