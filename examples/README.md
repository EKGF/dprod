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

## Planned

- Apply DCAT
- Gleif
- OpenData file
