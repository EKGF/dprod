---
grapharch:
  subject: urn:dprod-showcase:overview:08-standards
---

DPROD is a profile and extension of established W3C vocabularies. This is useful because each standard addresses a different part of the problem; a team can adopt a shared description without adopting one vendor's platform.

## A small map of responsibilities

| Standard | The question it helps answer |
| --- | --- |
| DCAT | What datasets, distributions, and data services are available? |
| RDF and OWL | How are the things identified, related, and defined? |
| JSON-LD | How can an ordinary JSON document carry linked-data meaning? |
| SHACL | Does this RDF description satisfy the declared constraints? |
| PROV | Where did something come from, and which activity produced it? |
| ODRL | Which permissions, prohibitions, and duties describe its use? |

These vocabularies can be used together. For example, a DPROD description can identify an output service using DCAT, point to a schema, and link to provenance or a policy where those details are needed.

## Extend deliberately

A shared vocabulary does not mean every product must carry every possible statement. Start with the information consumers need, reuse suitable terms, and document any local conventions.

> Interoperability comes from making the connections explicit, not from making every description identical.

The normative specification remains the authority for the exact terms and conformance requirements of the version you choose.
