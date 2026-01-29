# DPROD Data Contracts Ontology

A semantic web ontology for formalizing **Data Contracts** - bilateral agreements between data providers and consumers using W3C standards.

## Overview

DPROD Data Contracts models:
- **DataContract** - Binding agreement between provider and consumer
- **DataOffer** - Provider's proposal for data access
- **Provider Promises** - Timeliness, schema conformance, change notification
- **Consumer Promises** - Usage restrictions, retention policies

Built on: RDF, OWL, SHACL, ODRL, DCAT

## Files

| File | Purpose |
|------|---------|
| `dprod-contracts.ttl` | Core ontology (classes, properties) |
| `dprod-contracts-shapes.ttl` | SHACL validation shapes |
| `dprod-contract-examples.ttl` | Example instances |

## Quick Start

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Validate examples against shapes
pyshacl -s dprod-contracts-shapes.ttl -df turtle dprod-contract-examples.ttl
```

## Documentation

- [DATA-CONTRACTS.md](DATA-CONTRACTS.md) - Full specification and usage patterns
- [CLAUDE.md](CLAUDE.md) - Design philosophy and development guide
- [AGENTS.md](AGENTS.md) - Contribution guidelines

## Related

- [DPROD (Data Product Ontology)](https://ekgf.github.io/dprod/) - Parent ontology
- [DCAT](https://www.w3.org/TR/vocab-dcat-3/) - W3C Data Catalog Vocabulary
- [ODRL](https://www.w3.org/TR/odrl-model/) - Open Digital Rights Language

## License

MIT
