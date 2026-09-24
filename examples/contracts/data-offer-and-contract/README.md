A data contract in DPROD is an [ODRL 2.2](https://www.w3.org/TR/odrl-model/) policy. The provider of a data product publishes a `dprod:DataOffer` (an `odrl:Offer`) stating what it commits to deliver, what consumers may do with the data, and what they may not do. A consumer accepts that offer, and the acceptance is recorded as a `dprod:DataContract` (an `odrl:Agreement`) that names both parties and points at the offer through `dprod:acceptsOffer`.

Below, the Trading Data Team offers its market prices with two commitments of its own, a delivery every 15 minutes with a 5-minute deadline and conformance to a published schema, and one duty the consumer takes on, a monthly usage report. Consumers may display and derive from the data but may not redistribute it. The Analytics Team has accepted the offer for 2026.

Three things are worth noticing:

- **The provider's duties name their bearer.** `dprod:subjectOfDuty` says who must act. The usage report has no subject in the offer because the consumer is not yet known; it becomes the consumer's duty when the contract is made.
- **Rules inherit the offer's target.** Only the schema-conformance duty states its own `odrl:target`, because it is about the schema rather than the data.
- **The contract binds the named consumer.** It restates the rules that now apply to the Analytics Team, each with an `odrl:assignee`; a contract must carry at least one rule of its own.
- **The offer is shown nested inside the contract** so the whole agreement can be read top to bottom. In practice the provider publishes the offer once and each contract refers to it by its identifier.

ODRL terms are used directly with the `odrl:` prefix, just as DCAT terms are in a data product description. The published context says which properties take resources, so `"odrl:action": "odrl:display"` denotes an IRI without any wrapping. Only values whose datatype the context cannot know, such as a `dprod:deadline` that may be a duration or a timestamp, carry an explicit `@type`.
