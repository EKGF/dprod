---
title: "Why DPROD?"
description: "Why the OMG developed the Data Product Ontology: to solve inconsistent metadata, limited discoverability, and interoperability challenges in decentralized data architectures."
permalink: /why/
nav_order: 2
grapharch:
  subject: urn:dprod:project-site:page:why
  fragment: urn:dprod:content:why
  fragments:
    inconsistent-metadata: urn:dprod:content:why:inconsistent-metadata
    limited-discoverability: urn:dprod:content:why:limited-discoverability
    interoperability-friction: urn:dprod:content:why:interoperability-friction
    working-group-leadership: urn:dprod:content:why:working-group-leadership
    omg-request-for-comments: urn:dprod:content:why:omg-request-for-comments
    built-on-w3c-standards: urn:dprod:content:why:built-on-w3c-standards
    dcat: urn:dprod:content:why:dcat
    rdf: urn:dprod:content:why:rdf
    owl: urn:dprod:content:why:owl
    shacl: urn:dprod:content:why:shacl
    prov: urn:dprod:content:why:prov
  resource_sections: [origins-standardisation, built-on-w3c-standards]
  card_icons:
    inconsistent-metadata: {name: triangle-alert, tone: accent}
    limited-discoverability: {name: search, tone: primary}
    interoperability-friction: {name: plug, tone: accent}
    working-group-leadership: {name: users, tone: primary}
    omg-request-for-comments: {name: megaphone, tone: accent}
    dcat: {name: layers, tone: primary}
    rdf: {name: layers, tone: accent}
    owl: {name: layers, tone: primary}
    shacl: {name: layers, tone: accent}
    prov: {name: layers, tone: primary}
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

DPROD is the collective work of its EKGF workgroup and wider community. [Tony Seale](https://www.linkedin.com/in/tonyseale/) is the workgroup chair. [Matthias Autrata](https://www.linkedin.com/in/matthiasautrata/) has contributed especially to Data Contracts; [Josh Cornejo](https://www.linkedin.com/in/joshuacornejo/) and many others have made substantial contributions across DPROD.

The project's documented editors are [Matthias Autrata](https://www.linkedin.com/in/matthiasautrata/), [Marcel Fröhlich](https://www.linkedin.com/in/marcel-fr%C3%B6hlich-648a043/), [Jacobus Geluk](https://www.linkedin.com/in/jgeluk/), [Pete Rivett](https://www.linkedin.com/in/peterivett/), [Tony Seale](https://www.linkedin.com/in/tonyseale/), and [Natasa Varytimou](https://www.linkedin.com/in/natasavaritimou/).

Its documented authors are [Oli Bage](https://www.linkedin.com/in/olibage/), [Ben Clinch](https://www.linkedin.com/in/benclinch/), [Josh Cornejo](https://www.linkedin.com/in/joshuacornejo/), [Steve Fisher](https://www.linkedin.com/in/steve-fisher-b9463a3/), [Andrea Gioia](https://www.linkedin.com/in/andreagioia/), [Charles Ivie](https://www.linkedin.com/in/charlesivie/), [Carl Mattocks](https://www.linkedin.com/in/carlmattocks/), [Carlos Tubbax](https://www.linkedin.com/in/carlos-tubbax-975058118/), and [Ben Whittam Smith](https://www.linkedin.com/in/benedictws/). DPROD also benefits from the workgroup's reviewers, implementers, and other community contributors.

### OMG Request for Comments

OMG published the DPROD proposed specification for public comment as part of its standardisation process, focused on improving discoverability, interoperability, and reducing vendor lock-in across data marketplaces. [Read the OMG release](https://www.omg.org/news/releases/pr2024/09-24-24.htm)

## Built on W3C standards

DPROD does not reinvent the wheel. It profiles a stack of established W3C standards so data products inherit decades of work on semantics, validation, and interoperability.

### [DCAT](https://www.w3.org/TR/vocab-dcat-3/)

**Data Catalog Vocabulary**

The W3C vocabulary DPROD extends. Provides the core building blocks for describing datasets, distributions, and data services — which DPROD profiles and specialises for data products.

 ### [RDF](https://www.w3.org/RDF/)

**Resource Description Framework**

The graph data model that lets every DPROD concept be identified by a URI and linked to concepts from other vocabularies without translation layers.

 ### [OWL](https://www.w3.org/OWL/)

**Web Ontology Language**

The formal logic layer DPROD uses to define classes and properties with precise semantics — so tools can reason about data products, not just store records about them.

 ### [SHACL](https://www.w3.org/TR/shacl/)

**Shapes Constraint Language**

The validation layer. DPROD ships SHACL shapes that let any tool verify whether a data product description conforms to the standard — no custom validators required.

 ### [PROV](https://www.w3.org/TR/prov-o/)

**Provenance Vocabulary**

The lineage layer. PROV lets DPROD describe how data products were produced, by whom, and from which inputs — essential for trust, audit, and compliance.


