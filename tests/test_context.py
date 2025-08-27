import json
import os
from pathlib import Path

import pytest
from rdflib import Dataset, Namespace
from pyld import jsonld

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GENERATOR = ROOT / "spec-generator" / "main.py"


@pytest.fixture(scope="session", autouse=True)
def build_dist():
    # Ensure dist artifacts are generated
    import subprocess, sys
    env = os.environ.copy()
    # Run using current interpreter inside .venv
    subprocess.check_call([sys.executable, str(GENERATOR)], cwd=str(ROOT), env=env)
    assert (DIST / "dprod.jsonld").exists()
    assert (DIST / "dprod-ontology.jsonld").exists()


def test_dprod_jsonld_is_context():
    # Load dprod.jsonld and ensure it's only a context document
    data = json.loads((DIST / "dprod.jsonld").read_text(encoding="utf-8"))
    # Must be a JSON object with only @context at top-level
    assert isinstance(data, dict)
    assert set(data.keys()) == {"@context"}

    ctx = data["@context"]
    assert isinstance(ctx, dict)
    # Ensure expected prefixes present
    for key in ["dprod", "rdf", "rdfs", "xsd", "dcat", "dct", "sh"]:
        assert key in ctx
    # Ensure at least one term mapping exists
    assert any(k for k, v in ctx.items() if isinstance(v, str) and v.startswith("dprod:"))


def test_ontology_is_not_context():
    # Ontology dump should contain @graph
    data = json.loads((DIST / "dprod-ontology.jsonld").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "@graph" in data


def test_context_parses_minimal_instance():
    # Compose minimal instance JSON-LD using the context
    data = json.loads((DIST / "dprod.jsonld").read_text(encoding="utf-8"))
    context = data["@context"]

    instance = {
        "@context": context,
        "@id": "https://example.org/products/demo",
        "@type": "DataProduct",
        "dataProductOwner": "https://example.org/people/alice"
    }

    # Use PyLD to convert JSON-LD to N-Quads, then load into rdflib Dataset
    nquads = jsonld.to_rdf(instance, options={"format": "application/n-quads"})

    ds = Dataset()
    ds.parse(data=nquads, format="nquads")

    dprod = Namespace("https://ekgf.github.io/dprod/")

    # Check type triple
    assert (None, None, dprod.DataProduct) in ds
    # Check property triple
    assert (None, dprod.dataProductOwner, None) in ds

    # Ensure subject is our instance IRI
    subj = next(iter(ds.subjects(predicate=dprod.dataProductOwner)))
    assert str(subj) == "https://example.org/products/demo"
