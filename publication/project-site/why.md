---
title: "Why DPROD?"
description: "Why the OMG developed the Data Product Ontology: to solve inconsistent metadata, limited discoverability, and interoperability challenges in decentralized data architectures."
permalink: /why/
nav_order: 2
grapharch:
  subject: urn:dprod:project-site:page:why
---

Motivation

# Why DPROD?

As organisations adopt Data Mesh and other decentralised data architectures, they discover the same problems over and over. DPROD exists to solve them once, as a standard.

## The problem DPROD solves

### Inconsistent metadata

Every platform, every team, every vendor describes data products differently. Without a shared schema, consumers spend more time reconciling metadata than using the data.

### Limited discoverability

Data products exist in silos. Without standard descriptions, there is no federated search, no cross-domain catalog, and no way for consumers to find what already exists.

### Interoperability friction

Data products built on incompatible descriptions cannot be composed. DPROD lets a data product produced on one platform be described, understood, and consumed on another — without rewriting metadata.

## Origins & standardisation

### Working Group Leadership

DPROD is developed in the EKGF community and edited by [Tony Seale (Chair)](https://www.linkedin.com/in/tonyseale/) together with editors including Natasa Varytimou, Pete Rivett, and Marcel Fröhlich. Setting up the DPROD working group was an initiative by [Jacobus Geluk](https://www.linkedin.com/in/jgeluk/) .

### OMG Request for Comments

OMG published the DPROD proposed specification for public comment as part of its standardisation process, focused on improving discoverability, interoperability, and reducing vendor lock-in across data marketplaces. [Read the OMG release](https://www.omg.org/news/releases/pr2024/09-24-24.htm)

## Built on W3C standards

DPROD does not reinvent the wheel. It profiles a stack of established W3C standards so data products inherit decades of work on semantics, validation, and interoperability.

[DCAT

Data Catalog Vocabulary

The W3C vocabulary DPROD extends. Provides the core building blocks for describing datasets, distributions, and data services — which DPROD profiles and specialises for data products.](https://www.w3.org/TR/vocab-dcat-3/) [RDF

Resource Description Framework

The graph data model that lets every DPROD concept be identified by a URI and linked to concepts from other vocabularies without translation layers.](https://www.w3.org/RDF/) [OWL

Web Ontology Language

The formal logic layer DPROD uses to define classes and properties with precise semantics — so tools can reason about data products, not just store records about them.](https://www.w3.org/OWL/) [SHACL

Shapes Constraint Language

The validation layer. DPROD ships SHACL shapes that let any tool verify whether a data product description conforms to the standard — no custom validators required.](https://www.w3.org/TR/shacl/) [PROV

Provenance Vocabulary

The lineage layer. PROV lets DPROD describe how data products were produced, by whom, and from which inputs — essential for trust, audit, and compliance.](https://www.w3.org/TR/prov-o/)
