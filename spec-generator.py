import inspect
import shutil
import os
import re
from dataclasses import dataclass, field
from typing import List

import jinja2
import markdown
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import NamespaceManager, OWL, RDF, RDFS, XSD, DCAT, SH, DC, DCTERMS
import json
import html

debug = True
show_source = True

ontology_namespace_iri = "https://ekgf.github.io/dprod/"
DPROD = Namespace(ontology_namespace_iri)
shapes_graph_ns_iri = "https://ekgf.github.io/dprod/dprod-shapes/"
DPROD_SHAPE = Namespace(shapes_graph_ns_iri)

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


@dataclass(init=False)
class RdfProperty:
    name: str
    uri: URIRef
    shape_iri: URIRef = None
    label: str = None
    description: str = None
    comment: str = None
    domain: URIRef = None
    range: str = None
    owl_class: 'OwlClass' = None

    def __init__(self, g: Graph, **kwargs):
        self.__dict__.update(kwargs)
        if self.uri is None:
            raise ValueError("No URI provided for class or shape")
        if self.shape_iri is None:
            raise ValueError(f"No shape IRI provided for property {self.uri}")
        # First process all the triples of the shape
        for s1, p1, o1 in g.triples((self.shape_iri, None, None)):
            self._set_prop(g, 'Shape', p1, o1)
        # Then process all the triples of the OWL property, values from the OWL property take precedence
        for s1, p1, o1 in g.triples((self.uri, None, None)):
            self._set_prop(g, 'Ontology', p1, o1)

        self.short_uri = g.namespace_manager.normalizeUri(self.uri)
        if self.shape_iri is not None:
            self.shape_name = short_name(self.shape_iri)
        self._init_name()
        self._init_label(g)
        self._init_shape_description(g)
        self._init_description(g)
        self._init_comment(g)
        if self.owl_class:
            self.owl_class.add_property(self)
            self.domain = self.owl_class.uri
            self.domain_short = g.namespace_manager.normalizeUri(self.owl_class.uri)
        
    def _set_prop(self, g, source, predicate, object):
        if predicate == RDF.type or predicate == RDFS.isDefinedBy:
            return
        if isinstance(object, Literal):
            value = null_html_string_from_shape(object) if source == 'Shape' else null_html_string_from_ontology(object)
            if value is not None:
                self.__dict__[short_name(predicate)] = value
                print(f"  {g.namespace_manager.normalizeUri(self.uri)}: {g.namespace_manager.normalizeUri(predicate)}: {value}") if debug else None
        else:
            self.__dict__[short_name(predicate)] = object
            print(f"  {g.namespace_manager.normalizeUri(self.uri)}: {g.namespace_manager.normalizeUri(predicate)}: {g.namespace_manager.normalizeUri(object)}") if debug else None
            
    def _init_name(self):
        self.name = short_name(self.uri)
        if self.owl_class is not None:
            self.name = null_html_string_from_ontology(self.name.replace(f'{self.owl_class.name}-', ''))
            
    def _init_label(self, g):
        """Possibly override SHACL property label with OWL property label if there is one"""
        label = g.value(self.uri, RDFS.label)
        if label:
            self.label = null_html_string_from_ontology(label)

    def _init_shape_description(self, g):
        if self.shape_iri is None:
            return
        self.description = null_html_string_from_shape(g.value(self.shape_iri, DC.description))
        
    def _init_description(self, g):
        """Shape description overrides the OWL property description"""
        if self.description is None:
            description = g.value(self.uri, DC.description)
            if description is not None:
                self.description = null_html_string_from_ontology(description)
                
    def _init_comment(self, g):
        comment = g.value(self.uri, RDFS.comment)
        if comment:
            self.comment = null_html_string_from_ontology(comment)

    def html_id(self):
        """Return the id to be used in the generated HTML for this property"""
        if self.uri.__contains__(ontology_namespace_iri):
            return self.uri.replace(ontology_namespace_iri, '').lower()
        return self.shape_name.lower()

    def href(self):
        """Return the href value that provides the shortest way to reach the property's section which
         may be on the same page if it's part of a local shape or class, 
         or on another page if it's part of a different shape or class."""
        if self.uri.__contains__(ontology_namespace_iri):
            return f"#{self.uri.replace(ontology_namespace_iri, '').lower()}"
        return self.uri
    
    def htmlDomain(self):
        if self.domain is None:
            return ''
        if self.domain.__contains__(ontology_namespace_iri):
            return f"""<a href="#{self.domain.replace(ontology_namespace_iri, '').lower()}" title="{self.domain}">{self.domain_short}</a>"""
        return f"""<a href="{self.domain}" title="{self.domain}">{self.domain_short}</a>"""
    
    def htmlRange(self):
        if self.range is None:
            return ''
        if self.range.__contains__(ontology_namespace_iri):
            return f"""<a href="#{self.range.replace(ontology_namespace_iri, '').lower()}" title="{self.range}">{self.range_short}</a>"""
        return f"""<a href="{self.range}" title="{self.range}">{self.range_short}</a>"""


@dataclass(init=False)
class ClassOrShape:
    name: str
    uri: URIRef
    label: str = None
    description: str = None
    inherits: list = field(default_factory=list)
    properties: List[RdfProperty] = field(default_factory=list)
    shapedBy: 'ClassOrShape' = None
    type_name: str = None

    def __init__(self, g: Graph, **kwargs):
        self.__dict__.update(kwargs)
        if self.uri is None:
            raise ValueError("No URI provided for class or shape")
        for s1, predicate, object in g.triples((self.uri, None, None)):
            self._set_prop(g, predicate, object)

        self.properties = []
        description = g.value(URIRef(self.uri), DC.description)
        if description is None:
            # If the description is not provided, use the description of the class that shapes this object
            if self.shapedBy and not self.shapedBy.description and self.description and self.description != '':
                self.description = null_html_string(self.shapedBy.description)
        else:
            self.description = null_html_string(str(description))
            
    def _set_prop(self, g, predicate, object):
        if predicate == SH.property or predicate == RDF.type or predicate == RDFS.isDefinedBy:
            """Ignore these properties"""
            return
        if isinstance(object, Literal):
            value = self.type_name = null_html_string_from_shape(object) if self.type_name == 'Shape' else null_html_string_from_ontology(object)
            if value is not None:
                self.__dict__[short_name(predicate)] = value
                print(f"  {g.namespace_manager.normalizeUri(self.uri)}: {g.namespace_manager.normalizeUri(predicate)}: {value}")
        else:
            self.__dict__[short_name(predicate)] = object
            print(f"  {g.namespace_manager.normalizeUri(self.uri)}: {g.namespace_manager.normalizeUri(predicate)}: {g.namespace_manager.normalizeUri(object)}")

    def subclass_uris(self, g):
        for s,p,o in g.triples((None, RDFS.subClassOf, self.uri)):
            yield s
    
    def add_property(self, property):
        print(f"  Adding property {property.name} to class {self.name}")
        self.properties.append(property)
        
    def property_iris(self, g):
        """Return the URIs of the properties of this "class", 
        i.e., the properties specified by the NodeShape
        for the "targetClass"""
        for s,p,o in g.triples((self.uri, SH.property, None)):
            yield o

    def html_id(self):
        """Return the id to be used in the generated HTML for this class"""
        if self.uri.__contains__(ontology_namespace_iri):
            return self.uri.replace(ontology_namespace_iri, '').lower()
        return None


class NodeShape(ClassOrShape):
    
    targetClass: URIRef = None
    
    def __init__(self,g: Graph, **kwargs):
        self.type_name = 'Shape'
        super().__init__(g, **kwargs)


class OwlClass(ClassOrShape):
    def __init__(self,g: Graph, **kwargs):
        self.type_name = 'Class'
        super().__init__(g, **kwargs)


@dataclass
class Example:
    name: str
    description: str = ''
    text: str = ''
    json: str = ''


def is_empty_string(s):
    return s is None or s.isspace()

def null_empty_string(s):
    return None if is_empty_string(s) else s.strip()

def null_html_string(s):
    return None if is_empty_string(s) else html.escape(s.strip())

def null_html_string_from_shape(s):
    if is_empty_string(s):
        return None
    if show_source:
        return "SHACL: " + html.escape(s.strip())
    return html.escape(s.strip())

def null_html_string_from_ontology(s):
    if is_empty_string(s):
        return None
    if show_source:
        return "OWL: " + html.escape(s.strip())
    return html.escape(s.strip())

def load_ontologies():
    """Load the OWL ontology into an RDFlib graph"""
    g = Graph()
    nm = NamespaceManager(g, bind_namespaces="rdflib")
    nm.bind("dprod", DPROD)
    nm.bind("dprod-shape", DPROD_SHAPE)
    nm.bind("dcat", DCAT)
    nm.bind("dct", DCTERMS)
    g.parse('./ontology/dprod/dprod-ontology.ttl', format='ttl')
    g.parse('./ontology/dprod/dprod-dcatprofile.ttl', format='ttl')
    # g.parse('./ontology/dprod/dprod.ttl', format='ttl')
    return g


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
    html = markdown.markdown(markdown_text)
    return html

def short_name(uri, split_on=r'/|#'):
    if uri is None:
        return None
    split = re.split(split_on, uri)
    return split[len(split) - 1]

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

def reorder_list(list_to_order, reference_list):
    name_to_object = {obj.name: obj for obj in list_to_order}
    ordered_list = [name_to_object[name] for name in reference_list if name in name_to_object]
    ordered_list += [obj for obj in list_to_order if obj.name not in reference_list]
    return ordered_list

def is_shape(g, subject_iri):
    return isinstance(subject_iri, rdflib.term.URIRef) and SH.NodeShape in g.objects(subject_iri, RDF.type)

# Define a function to add classes and properties to the context
def add_to_context(g, node_shape_iri, owl_classes):
    if not is_shape(g, node_shape_iri): # we're at this point only interested in the NodeShapes
        return 
    name = short_name(node_shape_iri)
    if name.endswith("Shape"):
        name = name[:-len("Shape")]
    print(f"""Processing SHACL NodeShape "{short_name(node_shape_iri)}" for OWL Class "{name}":""")
    global json_ld_context
    json_ld_context["type"] = "@type" # JG> Is this necessary Tony?
    json_ld_context[name] = {"@id": str(node_shape_iri)}
    node_shape = NodeShape(name=name, uri=node_shape_iri, g=g)
    for subclass_iri in node_shape.subclass_uris(g):
        print(f"Processing subclass {subclass_iri}")
        add_to_context(g, subclass_iri, owl_classes)
    
    if not hasattr(node_shape, 'targetClass'):
        print(f"ERROR: No targetClass found for NodeShape {node_shape_iri}")
        return
        
    owl_class = OwlClass(name=name, uri=node_shape.targetClass, g=g, classes=owl_classes, shapedBy=node_shape)
    owl_classes[name] = owl_class
    for subclass_iri in owl_class.subclass_uris(g):
        print(f"Processing subclass {subclass_iri}")
        add_to_context(g, subclass_iri, owl_classes)
    json_ld_context[name]["@id"] = str(owl_class.uri)

    for property_shape_iri in node_shape.property_iris(g):

        property_iri = g.value(property_shape_iri, SH.path)
        if property_iri is None:
            print(f"ERROR: No sh:path found for property shape {property_shape_iri}")
            continue

        rdf_property = RdfProperty(uri=property_iri, shape_iri=property_shape_iri, owl_class=owl_class, g=g)

        for s1, p1, o1 in g.triples((property_shape_iri, None, None)):
            p1_name = short_name(p1)
            if p1_name == 'class' or p1_name == 'datatype' or p1_name == 'range':
                rdf_property.__dict__["range"] = o1
                rdf_property.__dict__["range_short"] = g.namespace_manager.normalizeUri(o1) # TODO: expected type 'str', got 'Node' instead
            if p1_name == 'path':
                try:
                    comment = g.value(o1, RDFS.comment)
                    if comment:
                        rdf_property.comment = html.escape(comment)
                except:
                    pass
            if p1_name not in rdf_property.__dict__:
                rdf_property.__dict__[p1_name] = o1
    for p in node_shape.properties:
        if p.range and p.range != "":
            json_ld_context[p.name] = {"@id": str(p.uri), "@type": str(p.range)}
        else:
            json_ld_context[p.name] = {"@id": str(p.uri)}



def fill_object(g, obj):
    for s1, p1, o1 in g.triples((obj.uri, None, None)):
        obj.__dict__[short_name(p1)] = o1
        print(f"  {short_name(p1)}: {o1}")
        
        
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
            #print(f'PROCESS: {child_folder_name}')
            formatted_name = child_folder_name.replace('-', ' ').title()
            example = Example(name=formatted_name)
            examples.append(example)
            # Read the contents of README.md
            readme_path = os.path.join(child_folder_path, 'README.md')
            if os.path.isfile(readme_path):
                with open(readme_path, 'r', encoding='utf-8') as readme_file:
                    print(f"Processing {readme_path}")
                    readme_content = readme_file.read()
                    example.text = convert_markdown_to_html(replace_backticks(readme_content))

            # Read the contents of example.json
            example_json_path = os.path.join(child_folder_path, 'example.json')
            if os.path.isfile(example_json_path):
                with open(example_json_path, 'r', encoding='utf-8') as json_file:
                    print(f"Processing {example_json_path}")
                    example_json_content = json_file.read()
                    example.json = example_json_content
    return examples

def generate_spec_page(classes, examples):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./respec/"))
    template = env.get_template("template.html")
    spec = template.render(classes=classes, examples=examples)
    with open('dist/index.html', mode='x', encoding='utf-8') as f:
        print(f"Generating spec page: ./{f.name}")
        f.write(spec)

def main():
    print("Generating the specification...")
    
    g = load_ontologies()
    classes = {}
    for class_uri in g.subjects():
        add_to_context(g, class_uri, classes)

    json_ld_context = dict(classes)
    dcat_g = Graph()
    dcat_g.parse('https://www.w3.org/ns/dcat2.ttl', format='ttl')
    for dcat_subject in dcat_g.subjects():
        name = short_name(dcat_subject)
        if name not in json_ld_context:
            types = list(dcat_g.objects(dcat_subject, RDF.type))
            if OWL.ObjectProperty in types:
                for s, p, o in dcat_g.triples((dcat_subject, RDFS.range, None)):
                    json_ld_context[name] = {"@id": str(dcat_subject), "@type": str(o)}
            elif OWL.DatatypeProperty in types:
                for s, p, o in dcat_g.triples((dcat_subject, RDFS.range, None)):
                    json_ld_context[name] = {"@id": str(dcat_subject), "@type": str(o)}
    
    json_ld = {"@context": json_ld_context}
    
    examples = load_examples("./examples/")
    
    # TODO: Create a special annotation predicate called something like `preferredSortOrder` that has a value 
    # of type xsd:string and has values like '00001', '00002', etc. to allow for deviating from the default
    # alphabetical order of classes and properties based on the value of `rdfs:label`.
    # This would allow us to remove this DPROD specific list from the code.
    classes = reorder_list(classes.values(), [
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
    
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # generate_class_and_property_pages(classes)
    
    generate_spec_page(classes, examples)

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

    for img in os.listdir('./images/'):
        print(f"Copying image: {img}")
        shutil.copy2(f'./images/{img}', './dist')
        
    print("Copying dprod-dcatprofile.ttl")    
    shutil.copy2('./ontology/dprod/dprod-dcatprofile.ttl', './dist/')

    print("Specification generated successfully!")
    
if __name__ == "__main__":
    main()
