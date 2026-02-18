import json
import os
from pathlib import Path

import pytest
from rdflib import Dataset, Namespace, RDF
from pyld import jsonld

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GENERATOR = ROOT / "spec-generator" / "main.py"

DPROD_NS = "https://www.omg.org/spec/DPROD/"


@pytest.fixture(scope="session", autouse=True)
def build_dist():
    """Ensure dist artifacts are generated before tests run."""
    import subprocess, sys
    subprocess.check_call([sys.executable, str(GENERATOR)], cwd=str(ROOT))
    assert (DIST / "dprod.jsonld").exists()
    assert (DIST / "dprod-ontology.jsonld").exists()


def test_dprod_jsonld_is_context():
    """dprod.jsonld must be a pure JSON-LD context document."""
    data = json.loads((DIST / "dprod.jsonld").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert set(data.keys()) == {"@context"}

    ctx = data["@context"]
    assert isinstance(ctx, dict)
    # Expected namespace prefixes
    for key in ["dprod", "rdf", "rdfs", "xsd", "dcat", "dct", "sh"]:
        assert key in ctx, f"Missing prefix: {key}"
    # JSON-LD keyword aliases
    assert ctx.get("id") == "@id"
    assert ctx.get("type") == "@type"
    # At least one DPROD term mapping
    assert any(
        k for k, v in ctx.items()
        if isinstance(v, str) and v.startswith("dprod:")
    )


def test_ontology_jsonld_contains_graph():
    """dprod-ontology.jsonld must be an ontology dump with @graph."""
    data = json.loads((DIST / "dprod-ontology.jsonld").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "@graph" in data


def test_context_resolves_dprod_terms():
    """A minimal JSON-LD instance using the context must expand to correct triples."""
    data = json.loads((DIST / "dprod.jsonld").read_text(encoding="utf-8"))
    context = data["@context"]

    instance = {
        "@context": context,
        "@id": "https://example.org/products/demo",
        "@type": "DataProduct",
        "dataProductOwner": "https://example.org/people/alice",
    }

    nquads = jsonld.to_rdf(instance, options={"format": "application/n-quads"})

    ds = Dataset()
    ds.parse(data=nquads, format="nquads")

    dprod = Namespace(DPROD_NS)

    # rdf:type must resolve to dprod:DataProduct
    assert (None, RDF.type, dprod.DataProduct) in ds
    # dprod:dataProductOwner triple must exist
    assert (None, dprod.dataProductOwner, None) in ds

    subj = next(iter(ds.subjects(predicate=dprod.dataProductOwner)))
    assert str(subj) == "https://example.org/products/demo"


def test_context_id_type_aliases():
    """Bare 'id' and 'type' must work as aliases for @id and @type."""
    data = json.loads((DIST / "dprod.jsonld").read_text(encoding="utf-8"))
    context = data["@context"]

    instance = {
        "@context": context,
        "id": "https://example.org/products/alias-test",
        "type": "DataProduct",
    }

    nquads = jsonld.to_rdf(instance, options={"format": "application/n-quads"})

    ds = Dataset()
    ds.parse(data=nquads, format="nquads")

    dprod = Namespace(DPROD_NS)

    assert (None, RDF.type, dprod.DataProduct) in ds
    subj = next(iter(ds.subjects(predicate=RDF.type)))
    assert str(subj) == "https://example.org/products/alias-test"
