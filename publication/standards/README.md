# DPROD standards publication sources

`../definitions/develop.ttl` describes a source-owned **1.1 draft**, collected
from the `develop` branch; `../definitions/main.ttl` describes 1.0 beta from `main`. The community publication is
<https://ekgf.org/dprod/spec/develop/>. The official baseline remains OMG
[DPROD 1.0 beta 2](https://www.omg.org/spec/DPROD/1.0/Beta2/PDF), document
ptc/26-05-40. Neither this configuration nor its generated outputs establish
OMG approval of 1.1.

The authored fragments cover the abstract, publisher preface, scope,
conformance, normative references, terms, symbols, namespaces, model,
data contracts, vocabulary reference, and acknowledgements. The preface and
bibliography carry draft review notes. Confirm the bibliographic editions and
publisher text before release. Legal notices are collected from
`respec/template.html` without rewriting their wording.

The configuration includes all eight core worked examples and seven contract
examples. Twelve examples have separate machine-readable source files; the
other three already contain their code in their README. Contract ontology,
profile, and constraint files are collected alongside the core RDF. The existing
ReSpec generator remains available. GraphArch CI separately produces both draft
PDF editions from the exact repository commit being verified.

The specification and PDF profiles declare required section roles and
metadata. Their placements control the order; the generated reference groups
belong under the explicit `reference` placement. The companion website has its
own content selection. Marketing README material is not implicitly included in
the formal specification.

Four draft outputs are selected by the GraphArch showcase: the specification,
companion website, **EKGF community PDF** (`doc:pdf`, `pdf/ekgf-spec-dprod.pdf`)
and **OMG submission preview PDF** (`doc:omg-pdf`, `pdf/omg-submission-dprod.pdf`).
Both PDFs share the same scope, technical placements, ontology, shapes and
examples. Their source-owned status, preface and publishing authority differ;
community HTML uses the EKGF front matter. Both retain the existing legal text
and the same source revision in their closing provenance section. Neither
claims OMG approval or an assigned 1.1 document number. The specification header
links both editions explicitly.

The inactive `doc:release` target defines a stricter release profile. It is
deliberately blocked: the document identifier, release date, authoritative
version URL, and approval status must be supplied by the
publisher. Do not manufacture those values to make a build pass.

`migration-provenance.json` records the initial source revision and import
hashes, plus the Beta 2 comparison baseline. These hashes describe the import;
they do not freeze future edits. Imported fragment nodes also retain queryable
`dct:source` and `prov:wasDerivedFrom` references in the RDF configuration.


## CI artifacts

The **GraphArch PDF editions** workflow runs for pushes to `develop` and can
also be dispatched manually on that branch. It builds an explicitly pinned
GraphArch source commit and gives its Git collector the exact DPROD
`GITHUB_SHA`. It does not copy ontology content into the GraphArch repository
or select a moving `develop` branch during the build.

Each successful run uploads two separately named artifacts:

- `dprod-ekgf-community-<commit>`: `dprod-ekgf-community.pdf`.
- `dprod-omg-submission-preview-<commit>`:
  `dprod-omg-submission-preview.pdf`.

Both include a `build-provenance.json` file with the exact source and generator
commits and the SHA-256 digest of each PDF. A third evidence artifact retains
the verification report and exported documentation KG. These are review
artifacts; the workflow does not promote either edition to an approved OMG
publication. The GraphArch showcase publishes the matching editions through its
normal website build.
