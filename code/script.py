import re
from dataclasses import dataclass, field, asdict
from typing import List

import jinja2
import rdflib
from rdflib import Graph, URIRef, DCTERMS, SH
from rdflib.namespace import OWL, RDF, RDFS, XSD, DCAT
import json

# Load the OWL ontology into an RDFlib graph
g = Graph()
g.parse('../ontology/dprod/dprod-ontology.ttl', format='ttl')
g.parse('../ontology/dprod/dprod-dcatprofile.ttl', format='ttl')
#g.parse('../ontology/dprod/dprod.ttl', format='ttl')

# Define the JSON-LD context
context = {
    "@vocab": str(RDF),
    "dprod": 'https://ekgf.github.io/data-product-spec/dprod/',
    "owl": str(OWL),
    "rdfs": str(RDFS),
    "xsd": str(XSD),
    "dcat": str(DCAT),
    "dcterms": str(DCTERMS),
    "sh": str(SH)
}

@dataclass
class RdfProperty:
    name: str
    uri: URIRef
    label: str = ''
    description: str = ''

@dataclass
class RdfClass:
    name: str
    uri: URIRef
    label: str = ''
    description: str = ''
    inherits: list = field(default_factory=list)
    properties: List[RdfProperty] = field(default_factory=list)



classes = {}


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
def add_to_context(uri):
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
                fill_object(owl_class)
                if owl_class.description and owl_class.description != '':
                    #print(f'description: {owl_class.description}')
                    class_obj.description = owl_class.description
                    
            for s, p, o in g.triples((uri, SH.property, None)):
                property_name = short_name(o)
                property_name = property_name.replace(f'{name}-', '')
                rdf_property = RdfProperty(name=property_name, uri=o)
                class_obj.properties.append(rdf_property)
                rdf_property.__dict__["domain"] = class_obj.targetClass
                rdf_property.__dict__["domain_short"] = g.namespace_manager.normalizeUri(class_obj.targetClass)
                rdf_property.__dict__["short_uri"] = g.namespace_manager.normalizeUri(o)
                for s1, p1, o1 in g.triples((rdf_property.uri, None, None)):
                    p1_name = short_name(p1)
                    if p1_name == 'class' or p1_name == 'datatype':
                        rdf_property.__dict__["range"] = o1
                        rdf_property.__dict__["range_short"] = g.namespace_manager.normalizeUri(o1)
                    rdf_property.__dict__[p1_name] = o1  
        elif OWL.ObjectProperty in types:
            for s, p, o in g.triples((uri, RDFS.range, None)):
                context[name] = {"@id": str(uri), "@type": str(o)}
        elif OWL.DatatypeProperty in types:
            range_uri = next(g.objects(uri, RDFS.range))
            context[name] = {"@id": str(uri), "@type": str(range_uri)}
    # context[name] = {"@id": str(uri)}


def fill_object(obj):
    for s1, p1, o1 in g.triples((obj.uri, None, None)):
        obj.__dict__[short_name(p1)] = o1


# Add classes and properties to the context
for class_uri in g.subjects():
    add_to_context(class_uri)

json_ld = {"@context": context}

classes = reorder_list(classes.values(), ['DataProduct', 'DataService', 'Distribution', 'Dataset'])
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="../docs/respec/"))
template = env.get_template("template.html")
spec = template.render(classes=classes)

with open('../docs/assets/spec.html', 'w', encoding='utf-8') as f:
    f.write(spec)
    
with open('../docs/assets/dprod.jsonld', 'w', encoding='utf-8') as f:
    f.write(json.dumps(json_ld, indent=4))
    

