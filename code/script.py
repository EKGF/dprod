import os
import re
from dataclasses import dataclass, field, asdict
from typing import List

import jinja2
import markdown
import rdflib
from rdflib import Graph, URIRef, DCTERMS, SH, DC
from rdflib.namespace import OWL, RDF, RDFS, XSD, DCAT
import json

# Load the OWL ontology into an RDFlib graph
g = Graph()
g.parse('../ontology/dprod/dprod-ontology.ttl', format='ttl')
g.parse('../ontology/dprod/dprod-dcatprofile.ttl', format='ttl')
# g.parse('../ontology/dprod/dprod.ttl', format='ttl')

# Define the JSON-LD context
context = {
    "@vocab": str(RDF),
    "dprod": 'https://ekgf.github.io/data-product-spec/dprod/',
    "owl": str(OWL),
    "rdfs": str(RDFS),
    "xsd": str(XSD),
    "dcat": str(DCAT),
    "dcterms": str(DCTERMS),
    "sh": str(SH),
    "id": "@id",
    "type": "@type"
}


@dataclass
class RdfProperty:
    name: str
    uri: URIRef
    label: str = ''
    description: str = ''
    comment: str = ''
    range: str = ''


@dataclass
class RdfClass:
    name: str
    uri: URIRef
    label: str = ''
    description: str = ''
    inherits: list = field(default_factory=list)
    properties: List[RdfProperty] = field(default_factory=list)


@dataclass
class Example:
    name: str
    description: str = ''
    text: str = ''
    json: str = ''


def replace_backticks(markdown_text):
    # Regular expression to find code blocks and capture the type
    code_block_pattern = re.compile(r'```(\w+)\n(.*?)```', re.DOTALL)

    def replace_code_block(match):
        code_type = match.group(1)
        code_content = match.group(2)
        return f'''<pre>
                        <code>\n{code_content}\n</code>
                    </pre>'''
        # return f'<pre class="example hljs {code_type}">\n{code_content}\n</pre>'

    # Replace all code blocks
    result = code_block_pattern.sub(replace_code_block, markdown_text)
    return result

def convert_markdown_to_html(markdown_text):
    # Convert Markdown to HTML
    html = markdown.markdown(markdown_text)
    return html

def short_name(uri, split_on=r'/|#'):
    if uri is None:
        return None
    split = re.split(split_on, uri)
    return split[len(split) - 1]


def reorder_list(list_to_order, reference_list):
    name_to_object = {obj.name: obj for obj in list_to_order}
    ordered_list = [name_to_object[name] for name in reference_list if name in name_to_object]
    ordered_list += [obj for obj in list_to_order if obj.name not in reference_list]
    return ordered_list


# Define a function to add classes and properties to the context
def add_to_context(uri,classes):
    if isinstance(uri, rdflib.term.URIRef):
        name = short_name(uri)
        if name.endswith("Shape"):
            name = name[:-len("Shape")]
        types = list(g.objects(uri, RDF.type))
        if SH.NodeShape in types:
            context[name] = {"@id": str(uri)}
            class_obj = RdfClass(name=name, uri=uri)
            classes[uri] = class_obj
            fill_object(class_obj)
            for s, p, o in g.triples((None, RDFS.subClassOf, uri)):
                add_to_context(s)

            if hasattr(class_obj, 'targetClass'):
                owl_class = RdfClass(name=name, uri=class_obj.targetClass)
                context[name]["@id"] = str(owl_class.uri)
                fill_object(owl_class)
                if owl_class.description and owl_class.description != '':
                    # print(f'description: {owl_class.description}')
                    class_obj.description = owl_class.description

            for s, p, o in g.triples((uri, SH.property, None)):
                property_shape_uri = o
                path = next(g.triples((o, SH.path, None)))
                label = next(g.triples((o, RDFS.label, None)))
                description = next(g.triples((o, DC.description, None)))
                if description:
                    description = str(description[2])
                print(f"SCL  DEC {description}")
                if path is not None:
                    o = str(path[2])
                property_name = short_name(o)
                property_name = property_name.replace(f'{name}-', '')
                rdf_property = RdfProperty(name=property_name, uri=o)
                rdf_property.description = description
                class_obj.properties.append(rdf_property)
                rdf_property.__dict__["domain"] = class_obj.targetClass
                rdf_property.__dict__["domain_short"] = g.namespace_manager.normalizeUri(class_obj.targetClass)
                rdf_property.__dict__["short_uri"] = g.namespace_manager.normalizeUri(o)

                for s1, p1, o1 in g.triples((property_shape_uri, None, None)):
                    p1_name = short_name(p1)
                    if p1_name == 'class' or p1_name == 'datatype' or p1_name == 'range':
                        rdf_property.__dict__["range"] = o1
                        rdf_property.__dict__["range_short"] = g.namespace_manager.normalizeUri(o1)
                    if p1_name == 'path':
                        try:
                            label = g.value(o1, RDFS.label)
                            if label:
                                rdf_property.label = label
                            description = g.value(o1, DC.description)
                            if not rdf_property.description and description:
                                rdf_property.description = description
                            comment = g.value(o1, RDFS.comment)
                            if comment:
                                rdf_property.comment = comment
                        except:
                            pass
                    if p1_name not in rdf_property.__dict__:
                        rdf_property.__dict__[p1_name] = o1
            for p in class_obj.properties:
                if p.range and p.range != "":
                    context[p.name] = {"@id": str(p.uri), "@type": str(p.range)}
                else:
                    context[p.name] = {"@id": str(p.uri)}

    context["type"] = "@type"


def fill_object(obj):
    for s1, p1, o1 in g.triples((obj.uri, None, None)):
        obj.__dict__[short_name(p1)] = o1


def load_examples(parent_folder, white_list=None, black_list=None):
    examples = []
    # Loop through each child folder in the parent folder
    for child_folder_name in os.listdir(parent_folder):
        
        child_folder_path = os.path.join(parent_folder, child_folder_name)
        wl_ok = (white_list is None or child_folder_name in white_list)
        bl_ok = (black_list is None or child_folder_name not in black_list)
        if os.path.isdir(child_folder_path) and wl_ok and bl_ok:
            #print(f'PROCESS: {child_folder_name}')
            formatted_name = child_folder_name.replace('-', ' ').title()
            example = Example(name=formatted_name)
            examples.append(example)
            # Read the contents of README.md
            readme_path = os.path.join(child_folder_path, 'README.md')
            if os.path.isfile(readme_path):
                with open(readme_path, 'r', encoding='utf-8') as readme_file:
                    readme_content = readme_file.read()
                    example.text = convert_markdown_to_html(replace_backticks(readme_content))

            # Read the contents of example.json
            example_json_path = os.path.join(child_folder_path, 'example.json')
            if os.path.isfile(example_json_path):
                with open(example_json_path, 'r', encoding='utf-8') as json_file:
                    example_json_content = json_file.read()
                    example.json = example_json_content
    return examples


def main():
    classes = {}
    for class_uri in g.subjects():
        add_to_context(class_uri, classes)

    json_ld_context = dict(context)
    dcat_g = Graph()
    dcat_g.parse('https://www.w3.org/ns/dcat2.ttl', format='ttl')
    for uri in dcat_g.subjects():
        name = short_name(uri)
        if name not in json_ld_context:
            types = list(dcat_g.objects(uri, RDF.type))
            if OWL.ObjectProperty in types:
                for s, p, o in dcat_g.triples((uri, RDFS.range, None)):
                    json_ld_context[name] = {"@id": str(uri), "@type": str(o)}
            elif OWL.DatatypeProperty in types:
                for s, p, o in dcat_g.triples((uri, RDFS.range, None)):
                    json_ld_context[name] = {"@id": str(uri), "@type": str(o)}
    
    json_ld = {"@context": json_ld_context}
    
    examples = load_examples("../examples/")
    
    classes = reorder_list(classes.values(), ['DataProduct', 'Port', 'DataService', 'Distribution', 'Dataset'])
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../docs/respec/"))
    template = env.get_template("template.html")
    spec = template.render(classes=classes, examples=examples)
    
    with open('../docs/assets/spec.html', 'w', encoding='utf-8') as f:
        f.write(spec)
    
    with open('../docs/assets/dprod.jsonld', 'w', encoding='utf-8') as f:
        json_dump = json.dumps(json_ld, indent=4)
        # print(json_dump)
        f.write(json_dump)


if __name__ == "__main__":
    main()
