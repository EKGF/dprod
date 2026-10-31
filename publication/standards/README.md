# DPROD standards publication sources

`../standards.ttl` describes a source-owned **1.1 draft**, collected from the
`develop` branch. The community publication is
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
profile, and constraint files are collected alongside the core RDF. The
existing ReSpec generator and official publication workflow are unchanged.

The specification and PDF profiles declare required section roles and
metadata. Their placements control the order; the generated reference groups
belong under the explicit `reference` placement. The companion website has its
own content selection. Marketing README material is not implicitly included in
the formal specification.

Three draft outputs are selected by the GraphArch showcase: specification,
companion website, and PDF. A fourth target, `doc:release`, defines a stricter
release profile. It is deliberately blocked: the document identifier, release
date, authoritative version URL, and approval status must be supplied by the
publisher. Do not manufacture those values to make a build pass.

`migration-provenance.json` records the initial source revision and import
hashes, plus the Beta 2 comparison baseline. These hashes describe the import;
they do not freeze future edits. Imported fragment nodes also retain queryable
`dct:source` and `prov:wasDerivedFrom` references in the RDF configuration.
