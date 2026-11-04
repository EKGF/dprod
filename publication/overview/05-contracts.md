---
grapharch:
  subject: urn:dprod-showcase:overview:05-contracts
---

A description makes a product discoverable and understandable. A contract addresses another question: what do provider and consumer commit to when the product is used?

## An optional layer of commitments

DPROD's developing Data Contracts profile builds on the W3C Open Digital Rights Language (ODRL). It reuses ODRL policies, permissions, prohibitions, duties, parties, and assets, adding vocabulary for the requirements described in the community specification.

For example, a provider may commit to deliver market data every fifteen minutes, with a defined fulfilment window. A consumer may be permitted to display the data and prohibited from redistributing it. An accepted offer records the agreement between the parties.

> The product description explains what is available. The contract records the terms under which it is offered and used.

## Three distinctions worth keeping

- **Offer and agreement:** an offer proposes terms; an accepted contract records the parties' agreement.
- **Lifecycle and evaluation:** an authored lifecycle status differs from a duty's evaluator-computed state.
- **Policy and enforcement:** expressing a policy does not execute it. A conforming processor must understand the profile's semantics before evaluating it.

The Data Contracts profile is optional. It is not necessary to adopt it before publishing useful DPROD product descriptions. Teams that need machine-readable commitments should consult the [current community specification](https://ekgf.org/dprod/spec/develop/) and its formal evaluation semantics.
