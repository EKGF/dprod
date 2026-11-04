---
grapharch:
  subject: urn:dprod-showcase:overview:04-example
---

## Follow the UK Bonds product

The specification's UK Bonds example makes the model concrete. A product exposes an output port implemented as a REST API. The API supplies a JSON distribution of a dataset, and that dataset references a FIBO schema for callable bonds.

The shortened excerpt below shows the connection. It is illustrative; the complete worked examples and validation shapes remain the implementation reference.

```json example="A product points to an output service"
{
  "@context": "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
  "id": "https://y.com/products/uk-bonds",
  "type": "DataProduct",
  "title": "UK Bonds",
  "outputPort": {
    "id": "https://y.com/products/uk-bonds/ports/10-year-api",
    "type": "DataService",
    "endpointURL": "https://y.com/uk-10-year-bonds"
  }
}
```

## What a consumer learns

The product and its service have their own identifiers. A catalog can describe the product; an access tool can follow the service's endpoint. The dataset's shared schema explains what the data means, while its distribution explains the representation being delivered.

This separation also helps when delivery changes. A new representation or access port can be described alongside the existing one, without giving up the product's identity.

[Explore the complete examples](https://github.com/EKGF/dprod/tree/develop/examples) and compare them with the [normative model](https://ekgf.org/dprod/spec/develop/).
