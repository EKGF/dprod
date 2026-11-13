---
title: "Get Started"
description: "How to reference the Data Product Ontology in your own work: the JSON-LD @context, how to cite the OMG standard, and where to find worked examples."
permalink: /adopt/
nav_order: 4
grapharch:
  subject: urn:dprod:project-site:page:adopt
  fragment: urn:dprod:content:adopt
  fragments:
    1-reference-the-json-ld-context: urn:dprod:content:adopt:1-reference-the-json-ld-context
    2-study-the-worked-examples: urn:dprod:content:adopt:2-study-the-worked-examples
    3-validate-with-the-shacl-shapes: urn:dprod:content:adopt:3-validate-with-the-shacl-shapes
    4-cite-the-omg-standard: urn:dprod:content:adopt:4-cite-the-omg-standard
  card_icons:
    1-reference-the-json-ld-context: {name: file-json, tone: primary}
    2-study-the-worked-examples: {name: folder-open, tone: accent}
    3-validate-with-the-shacl-shapes: {name: rocket, tone: primary}
    4-cite-the-omg-standard: {name: quote, tone: accent}
    the-specification: {name: book-open, tone: primary}
    core-concepts: {name: network, tone: accent}
    contact-the-working-group: {name: users, tone: primary}
    the-bigger-picture: {name: book-open, tone: accent}
---

Adoption

# Getting started

Four concrete steps to start describing your data products with DPROD — from the JSON-LD context to the formal citation.

## 1. Reference the JSON-LD context

DPROD ships a stand-alone JSON-LD `@context` so you can describe data products in plain JSON and get full RDF semantics for free. Point your documents at the published context URL:

```json
{
  "@context": "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
  "type": "DataProduct",
  "id": "https://example.com/data-products/customer-360",
  "title": "Customer 360",
  "description": "A unified view of the customer across domains.",
  "outputPort": [
    {
      "type": "DataService",
      "id": "https://example.com/data-products/customer-360/api"
    }
  ]
}
```

Any JSON-LD processor will expand these terms into the full DPROD vocabulary automatically — no code generation, no schema compilation.

## 2. Study the worked examples

The specification includes worked examples covering common patterns: SBA pool rates, equity trades, core data product extensions, data lineage, data quality, data rights, data schemas, and observability ports. Each example is a complete, machine-readable JSON-LD file you can copy and adapt.

[Browse examples on GitHub](https://github.com/EKGF/dprod/tree/develop/examples)

## 3. Validate with the SHACL shapes

DPROD ships SHACL shapes that any conforming RDF tool can use to validate your data product descriptions. Use the shapes for the version you are implementing. They check the constraints encoded in those shapes; operational and business requirements may require additional checks.

[Browse the shapes in the spec](https://ekgf.org/dprod/spec-versions/) [Raw SHACL file](https://github.com/EKGF/dprod/blob/develop/ontology/dprod/dprod-shapes.ttl)

## 4. Cite the OMG standard

When you reference DPROD in papers, internal documentation, or procurement requirements, use the formal OMG citation:

```text
Object Management Group (OMG). Data Product Ontology (DPROD), Version 1.0.
OMG Document Number: dtc/2024-09-01.
https://ekgf.org/dprod/spec/develop/
```

## Go deeper

### The specification

The complete, normative DPROD specification with classes, properties, and shapes.

[Open the spec](https://ekgf.org/dprod/spec-versions/)

### Core concepts

A plain-English walkthrough of Data Products, Ports, Distributions, and Datasets.

[Read concepts](concepts.md)

### Contact the working group

Questions, feedback, or interested in contributing? Reach out to the EKGF community.

[Get in touch](https://ekgf.org/contact/)

### The bigger picture

A visual introduction to DPROD's purpose, model, worked example, and adoption path.

[Download the overview PDF](https://ekgf.github.io/grapharch/showcases/artifacts/dprod/pdf/ekgf-overview-dprod.pdf)
