import re
from dataclasses import dataclass, field, asdict
from typing import List

import jinja2
import rdflib
from jinja2 import Environment, PackageLoader, select_autoescape
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD, DCAT
import json

# Load the OWL ontology into an RDFlib graph
g = Graph()
g.parse('../ontology/dprod/dprod.ttl', format='ttl')

# Define the JSON-LD context
context = {
    "@vocab": str(RDF),
    "owl": str(OWL),
    "rdfs": str(RDFS),
    "xsd": str(XSD),
    "dcat": str(DCAT)
}

@dataclass
class RdfProperty:
    name: str
    uri: URIRef
    description: str = None

@dataclass
class RdfClass:
    name: str
    uri: URIRef
    description: str = None
    inherits: list = field(default_factory=list)
    properties: List[RdfProperty] = field(default_factory=list)



classes = {}


def short_name(uri, split_on=r'/|#'):
    if uri is None:
        return None
    split = re.split(split_on, uri)
    return split[len(split) - 1]


# Define a function to add classes and properties to the context
def add_to_context(uri):
    if isinstance(uri, rdflib.term.URIRef):
        name = short_name(uri)
        types = list(g.objects(uri, RDF.type))
        if OWL.Class in g.objects(uri, RDF.type):
            context[name] = {"@id": str(uri)}
            class_obj = RdfClass(name=name, uri=uri)
            classes[uri] = class_obj
            for s1, p1, o1 in g.triples((class_obj.uri, None, None)):
                class_obj.__dict__[short_name(p1)] = o1
            for s, p, o in g.triples((None, RDFS.subClassOf, uri)):
                add_to_context(s)            
            for s, p, o in g.triples((None, RDFS.domain, uri)):
                rdf_property = RdfProperty(name=short_name(s), uri=s)
                class_obj.properties.append(rdf_property)
                for s1, p1, o1 in g.triples((rdf_property.uri, None, None)):
                    rdf_property.__dict__[short_name(p1)] = o1
                
                
        elif OWL.ObjectProperty in types:
            for s, p, o in g.triples((uri, RDFS.range, None)):
                context[name] = {"@id": str(uri), "@type": str(o)}
        elif OWL.DatatypeProperty in types:
            range_uri = next(g.objects(uri, RDFS.range))
            context[name] = {"@id": str(uri), "@type": str(range_uri)}
    # context[name] = {"@id": str(uri)}


# Add classes and properties to the context
for class_uri in g.subjects():
    add_to_context(class_uri)

json_ld = {"@context": context}
classes = classes.values()

env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../docs/respec/"))
template = env.get_template("template.html")
spec = template.render(classes=classes)
for c in classes:
    print(c.name)
with open('../docs/assets/spec.html', 'w', encoding='utf-8') as f:
    f.write(spec)
    
with open('../docs/assets/dprod.jsonld', 'w', encoding='utf-8') as f:
    f.write(json.dumps(json_ld, indent=4))
    

