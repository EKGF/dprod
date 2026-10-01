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

A second, convenience context, ``dprod-simple.jsonld`` (:class:`SimpleContext`),
layers bare terms and the ``id`` / ``type`` aliases over this one for documents
that use DPROD on its own. The examples are written against it. It still has no
``@vocab``.
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
    # ODRL 2.2 terms the Data Contracts profile reuses (issue #258). With
    # these coerced, a policy reads `"odrl:action": "odrl:display"` in the
    # same way a data product reads `"dcat:endpointURL": "https://..."`.
    # `odrl:rightOperand` is deliberately absent: it may be a literal.
    "odrl:action",
    "odrl:and",
    "odrl:assignee",
    "odrl:assigner",
    "odrl:constraint",
    "odrl:hasPolicy",
    "odrl:includedIn",
    "odrl:leftOperand",
    "odrl:obligation",
    "odrl:operator",
    "odrl:or",
    "odrl:partOf",
    "odrl:permission",
    "odrl:profile",
    "odrl:prohibition",
    "odrl:target",
    "prov:wasRevisionOf",
    "skos:inScheme",
)

#: DPROD properties that are IRI-valued but not declared ``owl:ObjectProperty``
#: (``dprod:operandProperty`` names a property and is typed ``rdf:Property``).
DPROD_IRI_VALUED_RDF_PROPERTIES: tuple[str, ...] = (
    "dprod:operandProperty",
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
        return (
            self.dprod_object_properties()
            + list(DPROD_IRI_VALUED_RDF_PROPERTIES)
            + list(EXTERNAL_IRI_VALUED_TERMS)
        )

    def dprod_typed_literal_properties(self) -> dict[str, str]:
        """DPROD datatype properties with an XSD range, mapped to that range.

        Lets an instance document write ``"dprod:effectiveDate": "2026-01-15T00:00:00Z"``
        and still denote an ``xsd:dateTime``. ``xsd:string`` is the default
        for a plain JSON string, so it is not listed. A property with no
        declared range (``dprod:deadline`` accepts a dateTime or a duration)
        is left alone and its values carry an explicit ``@type``.
        """
        namespace = globals.ontology_namespace_iri
        typed: dict[str, str] = {}
        for subject in self._graph.subjects(RDF.type, OWL.DatatypeProperty):
            if not str(subject).startswith(namespace):
                continue
            rng = self._graph.value(subject, RDFS.range)
            if rng is None or not str(rng).startswith(str(XSD)) or rng == XSD.string:
                continue
            typed[f"dprod:{str(subject)[len(namespace):]}"] = f"xsd:{str(rng)[len(str(XSD)):]}"
        return dict(sorted(typed.items()))

    def as_dict(self) -> dict:
        """The context object, ready to be serialised."""
        context: dict = {"@version": 1.1}
        context.update(PREFIXES)
        for term in self.coerced_terms():
            context[term] = {"@id": term, "@type": "@id"}
        for term, datatype in self.dprod_typed_literal_properties().items():
            context[term] = {"@id": term, "@type": datatype}
        return context

    def as_document(self) -> dict:
        """The full JSON-LD document written to ``dprod-context.jsonld``."""
        return {"@context": self.as_dict()}


#: Bare-term vocabularies for ``dprod-simple.jsonld``, highest priority first.
#: When two vocabularies share a local name, the earlier one owns the bare term
#: (``purpose`` is ``dprod:purpose``, not ``odrl:purpose``) and the other stays
#: reachable through its prefix. DPROD's own terms are derived from the ontology
#: and always come first.
SIMPLE_EXTERNAL_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("dcat", (
        "DataService", "Dataset", "Distribution", "accessService", "distribution",
        "endpointDescription", "endpointURL", "servesDataset",
    )),
    ("dct", (
        "conformsTo", "creator", "description", "format", "hasVersion", "identifier",
        "issued", "license", "modified", "publisher", "spatial", "temporal", "title",
    )),
    ("rdfs", ("comment", "label")),
    ("dqv", ("Metric", "QualityMeasurement", "computedOn", "isMeasurementOf", "value")),
    ("prov", ("Entity", "wasRevisionOf")),
    ("skos", ("Concept", "ConceptScheme", "inScheme", "prefLabel")),
    # rdflib cannot declare `and` and `or` as attributes, so its ODRL namespace
    # omits them; they are ODRL 2.2 logical-constraint operands all the same.
    ("odrl", tuple(ODRL2.__annotations__) + ("and", "or")),
)

#: Properties whose values are themselves vocabulary terms (an action, an
#: operator, a status). In the simple context they are coerced with ``@vocab``
#: so a document can write ``"action": "display"`` rather than
#: ``"action": "odrl:display"``. A full IRI or a prefixed name still works.
SIMPLE_VOCAB_VALUED_TERMS: frozenset[str] = frozenset({
    "odrl:action", "odrl:leftOperand", "odrl:operator",
    "dprod:contractLifecycleStatus", "dprod:offerLifecycleStatus",
    "dprod:dutyState", "dprod:operandSource", "dprod:operandProperty",
})


class SimpleContext:
    """The ``@context`` published as ``dprod-simple.jsonld``.

    A convenience layer over :class:`ApplicationContext` for documents that use
    DPROD on its own: it adds bare terms (``outputPort``, ``title``,
    ``DataProduct``) and the ``id`` / ``type`` keyword aliases, so the examples
    read as plain JSON. Every bare term maps to exactly the IRI and coercion of
    its prefixed form, so a document expands to the same graph either way.

    The prefixed context stays the one to use when DPROD is combined with other
    JSON-LD contexts: bare names such as ``title``, ``format`` and ``target``
    are generic and would collide (issue #93). There is still no ``@vocab``, so
    a misspelt term is dropped visibly rather than coined in the DPROD namespace.
    """

    def __init__(self, ontology_graph: Graph) -> None:
        self._graph = ontology_graph
        self._prefixed = ApplicationContext(ontology_graph).as_dict()

    def dprod_terms(self) -> list[str]:
        """Every class, property and individual in the DPROD namespace."""
        namespace = globals.ontology_namespace_iri
        locals_ = {
            str(subject)[len(namespace):]
            for subject in self._graph.subjects()
            if isinstance(subject, URIRef) and str(subject).startswith(namespace)
        }
        return sorted(name for name in locals_ if name and "/" not in name and "#" not in name)

    def bare_terms(self) -> dict[str, str]:
        """Bare name to prefixed name, resolved by vocabulary priority."""
        terms: dict[str, str] = {}
        for name in self.dprod_terms():
            terms[name] = f"dprod:{name}"
        for prefix, names in SIMPLE_EXTERNAL_TERMS:
            for name in names:
                terms.setdefault(name, f"{prefix}:{name}")
        return dict(sorted(terms.items()))

    def as_dict(self) -> dict:
        context: dict = dict(self._prefixed)
        context["id"] = "@id"
        context["type"] = "@type"
        for name, prefixed in self.bare_terms().items():
            definition = self._prefixed.get(prefixed)
            if prefixed in SIMPLE_VOCAB_VALUED_TERMS:
                context[name] = {"@id": prefixed, "@type": "@vocab"}
            elif isinstance(definition, dict):
                context[name] = dict(definition)
            else:
                context[name] = prefixed
        return context

    def as_document(self) -> dict:
        """The full JSON-LD document written to ``dprod-simple.jsonld``."""
        return {"@context": self.as_dict()}
