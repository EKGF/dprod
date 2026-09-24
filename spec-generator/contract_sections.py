"""Content for the Data Contracts sections of the generated specification.

The contracts SHACL file (``dprod-contracts/dprod-contracts-shapes.ttl``)
mixes three kinds of NodeShape:

* shapes that define DPROD's own contract classes (``DataOffer``,
  ``DataContract``, ``EvaluationContext``);
* shapes that constrain ODRL classes DPROD reuses (``odrl:Permission``,
  ``odrl:Duty``, ``odrl:Set`` ...) -- these are profile constraints, not
  DPROD vocabulary, and would only duplicate the ODRL specification if
  rendered as class definitions;
* ``Reject*`` shapes that forbid ODRL constructs the profile does not
  support.

Before issue #258 all of these fell through into the core "Data Product
Model" class loop, so the spec listed ``Policy``, ``Set`` and ``Offer`` as if
they were DPROD classes. The functions here split them so that the template
can render each kind in the right place.
"""

from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, RDFS, DCTERMS
from rdflib.namespace import ODRL2

from globals import ontology_namespace_iri, contracts_shapes_ns_iri
from functions import null_html_string, short_name


def is_contracts_shape(shape_iri) -> bool:
    return str(shape_iri).startswith(contracts_shapes_ns_iri)


def is_dprod_term(iri) -> bool:
    return str(iri).startswith(ontology_namespace_iri)


def is_rejection_shape(shape_iri) -> bool:
    local_name = short_name(str(shape_iri))
    return local_name.startswith("Reject") and local_name.endswith("Shape")


def split_node_shapes(node_shapes: dict) -> tuple[list, list]:
    """Partition discovered NodeShapes into core classes and contract classes.

    Returns ``(core, contracts)``. A contracts NodeShape only counts as a
    contract *class* when its target is a DPROD term; ODRL-targeted shapes
    are excluded from both lists.
    """
    core = []
    contracts = []
    for node_shape in node_shapes.values():
        if not is_contracts_shape(node_shape.shape_iri):
            core.append(node_shape)
        elif is_dprod_term(node_shape.axiom_iri) and not is_rejection_shape(node_shape.shape_iri):
            contracts.append(node_shape)
    return core, contracts


@dataclass
class ExtensionProperty:
    """A DPROD property whose domain is an ODRL class."""
    iri: str
    name: str
    label: str | None
    description: str | None
    comment: str | None
    domain: str
    domain_iri: str
    range: str | None
    range_iri: str | None

    def html_id(self) -> str:
        return self.iri.replace(ontology_namespace_iri, "").lower()


def contract_extension_properties(g: Graph) -> list[ExtensionProperty]:
    """DPROD properties that extend ODRL classes, ordered by domain then name."""
    nm = g.namespace_manager
    found = []
    for prop in set(g.subjects(RDFS.domain, None)):
        if not is_dprod_term(prop):
            continue
        for domain in g.objects(prop, RDFS.domain):
            if not str(domain).startswith(str(ODRL2)):
                continue
            rng = g.value(prop, RDFS.range)
            found.append(ExtensionProperty(
                iri=str(prop),
                name=nm.normalizeUri(prop),
                label=null_html_string(g.value(prop, RDFS.label)),
                description=null_html_string(g.value(prop, DCTERMS.description)),
                comment=null_html_string(g.value(prop, RDFS.comment)),
                domain=nm.normalizeUri(domain),
                domain_iri=str(domain),
                range=nm.normalizeUri(rng) if rng is not None else None,
                range_iri=str(rng) if rng is not None else None,
            ))
    return sorted(found, key=lambda p: (p.domain, p.name))
