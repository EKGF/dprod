"""Generation of the application-facing JSON-LD context (``dprod-context.jsonld``).

This is a different artifact from the compaction context used when serialising
the ontology itself, and the two must not be conflated (issue #246):

* ``dist/dprod.jsonld`` is a serialisation of the *ontology*. A bare prefix map
  is the correct compaction context for it.
* ``dist/dprod-context.jsonld`` is consumed by *instance* documents — the files
  under ``examples/`` and anything a publisher writes. A prefix map alone is not
  enough there. Prefix expansion yields the predicate IRI but never makes the
  *value* an IRI, so without type coercion ``dprod:outputPort`` and friends
  expand to literals rather than resources.

DPROD instance documents use prefixed terms (``dprod:outputPort``) rather than
bare terms (``outputPort``), following the recommendation in issue #93. That
keeps this context small and lets DPROD JSON be combined with other JSON-LD
contexts without either side claiming generic names such as ``title``,
``format``, ``action`` or ``value``.

Two consequences of that decision are deliberate and load-bearing:

* There is no ``@vocab``. An undefined term must stay undefined so that it can
  be reported, rather than being silently coined in the DPROD namespace.
* There are no ``id`` / ``type`` aliases. Documents use the ``@id`` and ``@type``
  keywords directly.
"""

from rdflib import Graph, OWL, RDF, RDFS, SH, SKOS, XSD, DCAT, DCTERMS, PROV, URIRef
from rdflib.namespace import ODRL2

import globals

#: The vocabularies DPROD instance documents draw on. Every prefix an example
#: uses must appear here, otherwise its terms cannot be expanded.
PREFIXES: dict[str, str] = {
    "dprod": globals.ontology_namespace_iri,
    "dcat": str(DCAT),
    "dct": str(DCTERMS),
    "dqv": "http://www.w3.org/ns/dqv#",
    "odrl": str(ODRL2),
    "owl": str(OWL),
    "prov": str(PROV),
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "sh": str(SH),
    "skos": str(SKOS),
    "xsd": str(XSD),
    "linkedin": globals.linkedin_ns_iri,
}

#: IRI-valued properties DPROD reuses from DCAT and DCTERMS.
#:
#: DPROD's own coercions are derived from ``owl:ObjectProperty`` declarations in
#: the ontology and so cannot drift. These cannot be derived the same way: they
#: belong to external vocabularies whose range declarations do not distinguish
#: "IRI-valued" from "literal-valued" in a way that is safe to infer from
#: (``dct:format`` and ``dct:conformsTo`` are both ``rdfs:Range rdfs:Resource``,
#: while ``dct:title`` is not typed as a datatype property either).
#:
#: The list is deliberately short: only terms DPROD's own model and examples
#: depend on. Declaring them is safe because they are namespaced names, so they
#: cannot collide with a term another context defines.
EXTERNAL_IRI_VALUED_TERMS: tuple[str, ...] = (
    "dcat:accessService",
    "dcat:distribution",
    "dcat:endpointDescription",
    "dcat:endpointURL",
    "dcat:servesDataset",
    "dct:conformsTo",
    "dct:creator",
    "dct:format",
    "dct:license",
    "dct:publisher",
    "dct:spatial",
)


class ApplicationContext:
    """The ``@context`` published as ``dprod-context.jsonld``.

    Built from the ontology graph so that the set of type coercions is a
    function of the ontology rather than a hand-maintained list.
    """

    def __init__(self, ontology_graph: Graph) -> None:
        self._graph = ontology_graph

    def dprod_object_properties(self) -> list[str]:
        """The DPROD properties whose values are resources, not literals.

        Derived from ``owl:ObjectProperty`` declarations, so a property added to
        the ontology is coerced automatically and one that is removed stops
        being coerced.
        """
        namespace = globals.ontology_namespace_iri
        return sorted(
            f"dprod:{str(subject)[len(namespace):]}"
            for subject in self._graph.subjects(RDF.type, OWL.ObjectProperty)
            if str(subject).startswith(namespace)
        )

    def coerced_terms(self) -> list[str]:
        """Every term that must carry ``"@type": "@id"``, in a stable order."""
        return self.dprod_object_properties() + list(EXTERNAL_IRI_VALUED_TERMS)

    def as_dict(self) -> dict:
        """The context object, ready to be serialised."""
        context: dict = {"@version": 1.1}
        context.update(PREFIXES)
        for term in self.coerced_terms():
            context[term] = {"@id": term, "@type": "@id"}
        return context

    def as_document(self) -> dict:
        """The full JSON-LD document written to ``dprod-context.jsonld``."""
        return {"@context": self.as_dict()}
