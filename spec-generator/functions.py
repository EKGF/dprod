from __future__ import annotations

import html
import inspect
import os
import re

import markdown
from rdflib import Graph, DCAT, DCTERMS, SH, RDF, URIRef, ODRL2
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

import globals
import example


def load_ontologies():
    """Load the OWL ontology and the SHACL ontology and important reference ontologies into an RDFlib graph"""
    g = Graph()
    nm = NamespaceManager(g, bind_namespaces="rdflib")
    nm.bind("dprod", globals.DPROD)
    nm.bind("dprod-shape", globals.DPROD_SHAPES)
    nm.bind("dcat", DCAT)
    nm.bind("dct", DCTERMS)
    nm.bind("linkedin", globals.LINKEDIN)
    g.parse('./ontology/dprod/dprod-ontology.ttl', format='ttl')
    g.parse('./ontology/dprod/dprod-shapes.ttl', format='ttl')
    g.parse('https://www.w3.org/ns/dcat2.ttl', format='ttl')
    return g


def load_dprod_ontology():
    """Load JUST the OWL ontology into an RDFlib graph"""
    g = Graph()
    nm = NamespaceManager(g, bind_namespaces="rdflib")
    nm.bind("dprod", globals.DPROD)
    nm.bind("dcat", DCAT)
    nm.bind("dct", DCTERMS)
    nm.bind("odrl", ODRL2)
    nm.bind("linkedin", globals.LINKEDIN)
    g.parse('./ontology/dprod/dprod-ontology.ttl', format='ttl')
    return g

def load_dprod_shapes():
    """Load JUST the SHACL ontology into an RDFlib graph"""
    g = Graph()
    nm = NamespaceManager(g, bind_namespaces="rdflib")
    nm.bind("dprod", globals.DPROD)
    nm.bind("dprod-shapes", globals.DPROD_SHAPES)
    nm.bind("dcat", DCAT)
    nm.bind("dct", DCTERMS)
    nm.bind("odrl", ODRL2)
    nm.bind("linkedin", globals.LINKEDIN)
    g.parse('./ontology/dprod/dprod-shapes.ttl', format='ttl')
    return g


def is_empty_string(s):
    return s is None or s.isspace()


def null_empty_string(s):
    return None if is_empty_string(s) else s.strip()


def null_html_string(s, source=None):
    if isinstance(s, Node):
        s = str(s)
    if is_empty_string(s):
        return None
    if globals.show_source and source is not None:
        return source + ": " + html.escape(s.strip())
    return html.escape(s.strip())


def replace_backticks(markdown_text):
    # Regular expression to find code blocks and capture the type
    code_block_pattern = re.compile(r'```(\w+)\n(.*?)```', re.DOTALL)

    def replace_code_block(match):
        code_type = match.group(1)
        code_content = html.escape(match.group(2))
        if code_type == 'text':
            return f'''<pre class="ekgfexample"><code class="ekgfexample">{code_content}\n</code></pre>'''
        else:
            return f'''<pre class="nolinks hljs {code_type} ekgfexample"><code class="ekgfexample">{code_content}\n</code></pre>'''
        # return f'<pre class="example hljs {code_type}">\n{code_content}\n</pre>'

    # Replace all code blocks
    result = code_block_pattern.sub(replace_code_block, markdown_text)
    return result


def convert_markdown_to_html(markdown_text):
    # Convert Markdown to HTML
    return markdown.markdown(markdown_text)


def short_name(uri, split_on=r'/|#'):
    if uri is None:
        return None
    split = re.split(split_on, uri)
    return split[len(split) - 1]


def shacl_short_name(uri):
    if uri is None:
        raise ValueError("No URI provided for property")
    if uri == SH['class']:
        return "shacl_class"
    return short_name(uri)


def fragment_of(uri, split_on=r'/|#'):
    """Extract the fragment of a DPROD IRI that we can use as an anchor href in the generated HTML."""
    if uri is None:
        return None
    # if not uri.startswith(ontology_namespace_iri):
    #     return None
    # print(f"URI: {uri} subject_iri: {subject_iri}")
    split = re.split(split_on, uri)
    fragment = split[len(split) - 1]
    return fragment.lower()


def reorder_list(list_to_order, reference_list) -> list:
    name_to_object = {obj.name: obj for obj in list_to_order}
    ordered_list = [name_to_object[name] for name in reference_list if name in name_to_object]
    ordered_list += [obj for obj in list_to_order if obj.name not in reference_list]
    return ordered_list


def is_node_shape(g, subject_iri):
    return isinstance(subject_iri, URIRef) and SH.NodeShape in g.objects(subject_iri, RDF.type)


def cast_to_uri_ref(rdf_object: Node | None) -> URIRef | None:
    if rdf_object is None:
        return None
    if isinstance(rdf_object, URIRef):
        return rdf_object
    return URIRef(str(rdf_object))


def generate_class_page(cls):
    print(f"Class: {cls.name}")
    with open(f"dist/{cls.name}.html", mode='x', encoding='utf-8') as f:
        print(f"Generating class page: dist/{cls.name}.html")
        f.write(inspect.cleandoc(f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{cls.name}</title>
                <script>
                    window.onload = function() {{
                        window.location.href = window.location.href.substring(
                            0, window.location.href.lastIndexOf( "/" ) + 1
                        ) + "#{cls.name.lower()}";
                    }};
                </script>
            </head>
            <body>
                <h1>{cls.name}</h1>
                <p>{cls.description}</p>
            </body>
            </html>
            '''))


def generate_property_page(prop):
    print(f"  Property: {prop.name}")
    with open(f"dist/{prop.name}.html", mode='x', encoding='utf-8') as f:
        print(f"Generating property page: dist/{prop.name}.html")
        f.write(inspect.cleandoc(f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{prop.name}</title>
                <script>
                    window.onload = function() {{
                        window.location.href = window.location.href.substring(
                            0, window.location.href.lastIndexOf( "/" ) + 1
                        ) + "#{prop.name.lower()}";
                    }};
                </script>
            </head>
            <body>
                <h1>{prop.name}</h1>
                <p>{prop.description}</p>
            </body>
            </html>
            '''))


def generate_class_and_property_pages(classes):
    for cls in classes:
        generate_class_page(cls)
        for prop in cls.properties:
            generate_property_page(prop)


def load_examples(parent_folder, white_list=None, black_list=None):
    examples = []
    # Loop through each child folder in the parent folder
    for child_folder_name in os.listdir(parent_folder):

        child_folder_path = os.path.join(parent_folder, child_folder_name)
        wl_ok = (white_list is None or child_folder_name in white_list)
        bl_ok = (black_list is None or child_folder_name not in black_list)
        if os.path.isdir(child_folder_path) and wl_ok and bl_ok:
            # print(f"PROCESS: {child_folder_name}")
            formatted_name = child_folder_name.replace('-', ' ').title()
            xmpl = example.Example(name=formatted_name)
            examples.append(xmpl)
            # Read the contents of README.md
            readme_path = os.path.join(child_folder_path, 'README.md')
            if os.path.isfile(readme_path):
                with open(readme_path, 'r', encoding='utf-8') as readme_file:
                    print(f"Processing {readme_path}")
                    readme_content = readme_file.read()
                    xmpl.text = convert_markdown_to_html(replace_backticks(readme_content))

            # Read the contents of example.json
            example_json_path = os.path.join(child_folder_path, 'example.json')
            if os.path.isfile(example_json_path):
                with open(example_json_path, 'r', encoding='utf-8') as json_file:
                    print(f"Processing {example_json_path}")
                    example_json_content = json_file.read()
                    xmpl.json = example_json_content
    return examples
