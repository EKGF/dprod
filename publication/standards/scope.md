---
title: "Scope"
grapharch:
  subject: urn:dprod:documentation:scope
---

The [Data Product (DPROD)](dprod.ttl) specification is a
profile of the [Data Catalog (DCAT) Vocabulary](https://www.w3.org/TR/vocab-dcat-3/),
designed to describe Data Products.
This document defines the schema and provides examples of its use.

DPROD extends DCAT to enable publishers to describe Data Products and data services in a decentralized way.
By using a standard model and ontology, DPROD facilitates the consumption and aggregation of metadata
from multiple Data Marketplaces.
This approach increases the discoverability of products and services, supports decentralized data publishing,
and enables federated search across multiple sites using a uniform query mechanism and structure.

DPROD also defines an optional [Data Contracts](urn:dprod:documentation:contracts) profile of the W3C Open
Digital Rights Language [odrl-model](https://www.w3.org/TR/odrl-model/), with which the provider of a data product can publish the terms
on which it is offered, and a consumer can record the contract under which it is used.

The namespace for DPROD terms is `https://ekgf.org/dprod/spec/develop/`

The suggested prefix for the DPROD namespace is **`dprod`**

**DPROD follows two basic principles:**

- Decentralize Data Ownership: To make data integration more efficient, tasks should be shared among multiple
  teams. DCAT helps by offering a standard way to publish datasets in a decentralized manner.
- Harmonize Data Schemas: Using shared schemas helps unify different data formats.
  For instance, the [DPROD](dprod.ttl) specification provides a
  common set of rules for defining a [Data Product](https://ekgf.org/dprod/spec/develop/DataProduct).
  Users of DPROD can extend this schema as needed.

The [dprod](https://ekgf.org/dprod/spec/develop/) specification builds on DCAT [vocab-dcat-3](https://www.w3.org/TR/vocab-dcat-3/) by connecting
[DCAT Data Services](https://www.w3.org/TR/vocab-dcat-3/#Class:Data_Service) to
DPROD [Data Products](https://ekgf.org/dprod/spec/develop/DataProduct) using
[input](https://ekgf.org/dprod/spec/develop/inputPort) and
[output](https://ekgf.org/dprod/spec/develop/outputPort) ports.
These ports are used to publish and consume data from a Data Product.
DPROD treats ports as [DCAT data services](https://www.w3.org/TR/vocab-dcat-3/#Class:Data_Service),
so the data exchanged can be described using DCAT's highly expressive metadata around
[distributions](https://www.w3.org/TR/vocab-dcat-3/#Class:Distribution) and
[datasets](https://www.w3.org/TR/vocab-dcat-3/#Class:Dataset).
This approach also allows publishers to create their own descriptions for the data they are sharing.
They can use a special property called
[conformsTo](https://www.w3.org/TR/vocab-dcat-3/#Property:resource_conforms_to) from DCAT to link to
their own set of rules or guidelines for their data.

**The DPROD specification has four main aims:**

- To provide unambiguous and sharable semantics to answer the question:
  'What is a [data product](https://ekgf.org/dprod/spec/develop/DataProduct)?'
- Be simple for anyone to use, but expressive enough to power large data marketplaces
- Allow organisations to reuse their existing data catalogues and dataset infrastructure
- To share common semantics across different Data Products and promote harmonization
