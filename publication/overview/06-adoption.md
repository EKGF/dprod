---
grapharch:
  subject: urn:dprod-showcase:overview:06-adoption
---

## Start with one useful product

Choose a product that already has a clear owner and a real consumer. Describe its purpose, its identity, its output service, and the dataset behind that service. This turns adoption into a concrete exchange between teams instead of an inventory exercise.

### 1. Select the publication you are implementing

Use the [specification versions](https://ekgf.org/dprod/spec-versions/) to distinguish the published baseline from the evolving development draft. Record that decision with your implementation.

### 2. Adapt a worked example

DPROD publishes JSON-LD contexts and complete examples. The simple context makes common terms readable in JSON; the prefixed context is useful when combining DPROD with other JSON-LD contexts. Follow the selected version's guidance and use its published context.

### 3. Validate the description

Run the corresponding SHACL shapes against the RDF described by your document. Use the findings to improve the description. Validation checks the requirements encoded in those shapes; operational and business checks may still be needed.

### 4. Publish and learn with a consumer

Make the description available to the intended catalog or consumer. Confirm that another team can identify the owner, discover the service, and understand the shared schema without a private explanation of every field.

## Grow the description when the need is real

Additional metadata can cover lineage, quality, rights, and observability. DPROD is designed to work with established vocabularies such as PROV and ODRL. Introduce these connections to answer actual consumer questions rather than filling every possible field at once.
