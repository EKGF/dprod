# Examples

All examples reference the published DPROD JSON-LD context and use **prefixed
terms** (`dprod:outputPort`, `dct:title`) together with the JSON-LD keywords
`@id` and `@type`. The context defines no bare-term aliases and no `@vocab`, so
DPROD JSON can be combined with other JSON-LD contexts and an undefined term
stays visibly undefined instead of being silently coined in the DPROD
namespace. See issues #93 and #246.

Every example here — the standalone files, the JSON-LD and Turtle snippets in
each `README.md`, and the worked examples in the specification itself — is
validated by `tests/test_examples.py` on every build: it must parse, expand
against the generated context without dropping a term, and produce triples in
which IRI-valued properties are resources rather than literals.

## Implemented

- [SBA Pool Rates](sba-pool-rates/README.md) - Mortgage-backed securities rates served through three ports: database query, API, and Kafka topic.
- [Equity Trade](equity-trade/README.md) - Equity trades data product providing datasets for London Stock Exchange and Euronext.
- [Data Lineage](data-lineage/README.md) - Tracing lineage between data products via input/output ports and at the dataset level using PROV.
- [Data Rights](data-rights/README.md) - Describing rights and entitlements on data products and datasets using ODRL policies.
- [Data Quality](data-quality/README.md) - Measuring dataset quality using the W3C Data Quality Vocabulary (DQV).
- [Data Schema](data-schema/README.md) - Describing dataset schemas using SHACL node shapes and property shapes.
- [Observability Ports](observability-ports/README.md) - Exposing monitoring and diagnostic data through a dedicated observability port.
- [Core Data Product Extensions](core-data-product-extensions/README.md) - Extending a data product with additional metadata such as FIBO-based agreements.

## Data Contracts

Examples of the DPROD Data Contracts profile (ODRL 2.2). They render as their own
section of the specification and validate against `dprod-contracts/dprod-contracts-shapes.ttl`.

- [Data Offer and Contract](contracts/data-offer-and-contract/README.md) - A provider's offer, the consumer's contract that accepts it, and the evaluated duties.
- [Provider Duties](contracts/provider-duties/README.md) - The four service-level duty patterns: delivery, schema conformance, change notification and quality.
- [Lifecycle and Versioning](contracts/lifecycle-and-versioning/README.md) - Authored offer and contract status, evaluator-computed duty state, and offer version chains.
- [Data Use Policy](contracts/data-use-policy/README.md) - An organisational policy with no named parties: purpose, classification and environment constraints, prohibitions, and logical combination.
- [Collections and Target Inheritance](contracts/collections-and-target-inheritance/README.md) - Asset and party collections with `odrl:partOf`, multi-target offers, and rule-level target override.
- [Evaluation Context](contracts/evaluation-context/README.md) - How operands bind to the request, the world snapshot and the built-in agent and clock, and what an evaluator is given.
- [ODCS Mapping](contracts/odcs-mapping/README.md) - An Open Data Contract Standard document expressed as a DPROD data offer.

## Planned

- Apply DCAT
- Gleif
- OpenData file
