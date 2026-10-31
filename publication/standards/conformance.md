---
title: "Conformance"
grapharch:
  subject: urn:dprod:documentation:conformance
---

A data product is conformant with this specification if it satisfies the [SHACL](https://www.w3.org/TR/shacl/) constraints provided in the file
[dprod-shapes.ttl](../../ontology/dprod/dprod-shapes.ttl).

Support for the [Data Contracts](urn:dprod:documentation:contracts) profile is optional. A data offer, data
contract or data use policy is conformant with this specification if it satisfies the [SHACL](https://www.w3.org/TR/shacl/)
constraints provided in the file
<dprod-contracts-shapes.ttl>, and an evaluator of such policies
is conformant if it produces the results defined by the profile's formal semantics.
