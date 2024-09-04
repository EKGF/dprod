import shutil

from functions import *
from node_shape import NodeShape
from property_shape import PropertyShape
from jinja import generate_spec_page


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

    with open('dist/dprod-all.jsonld', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF JSON-LD: ./{f.name}")
        f.write(g.serialize(format='json-ld'))

    # with open('dist/dprod.jsonld', mode='x', encoding='utf-8') as f:
    #     print(f"Generating RDF JSON-LD: ./{f.name}")
    #     json_dump = json.dumps(json_ld, indent=4)
    #     f.write(json_dump)

    with open('dist/dprod.ttl', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF Turtle: ./{f.name}")
        f.write(g.serialize(format='turtle'))

    with open('dist/dprod.rdf', mode='x', encoding='utf-8') as f:
        print(f"Generating RDF/XML: ./{f.name}")
        f.write(g.serialize(format='application/rdf+xml'))

    for asset in os.listdir('assets'):
        print(f"Copying asset: {asset}")
        shutil.copy2(f'assets/{asset}', 'dist/assets')

    print("Copying dprod-shapes.ttl")
    shutil.copy2('ontology/dprod/dprod-shapes.ttl', 'dist')

    print("Specification generated successfully!")


if __name__ == "__main__":
    main()
