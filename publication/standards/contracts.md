---
title: "Data Contracts"
grapharch:
  subject: urn:dprod:documentation:contracts
---

A data product is only useful once someone can rely on it. The provider of a product commits to
deliver data on a schedule, to keep it conformant to a schema, and to give notice before it changes;
the consumer, in turn, agrees to use the data only in permitted ways and to meet obligations of its
own, such as reporting usage. In a Data Mesh these commitments are made between many autonomous teams,
so they need to be recorded in a form that machines can validate and evaluate, not just in prose.

DPROD Data Contracts is a profile of the W3C
[Open Digital Rights Language (ODRL) 2.2](https://www.w3.org/TR/odrl-model/) [odrl-model](https://www.w3.org/TR/odrl-model/)
for exactly this purpose. It uses ODRL's own terms for everything ODRL already defines: a policy, its
permissions, prohibitions and duties, the constraints on them, and the parties and assets they refer to.
DPROD adds vocabulary only where ODRL leaves behaviour undefined:

- **Two policy types.** A [`dprod:DataOffer`](https://ekgf.org/dprod/spec/develop/DataOffer) is an
  `odrl:Offer` published by a data provider. A
  [`dprod:DataContract`](https://ekgf.org/dprod/spec/develop/DataContract) is an `odrl:Agreement` that
  records a consumer's acceptance of exactly one offer, through
  [`dprod:acceptsOffer`](https://ekgf.org/dprod/spec/develop/acceptsOffer), and binds both parties.
- **Bilateral duties.** ODRL duties fall on the assignee. In a data contract the provider
  has duties too, so DPROD names the party that bears each duty
  ([`dprod:subjectOfDuty`](https://ekgf.org/dprod/spec/develop/subjectOfDuty)) and the party it is owed to
  ([`dprod:objectOfDuty`](https://ekgf.org/dprod/spec/develop/objectOfDuty)).
- **Schedules and deadlines.** A duty may recur on a
  reusable, identified [`dprod:Schedule`](https://ekgf.org/dprod/spec/develop/Schedule) (for example an [RFC5545](https://www.rfc-editor.org/rfc/rfc5545)
  recurrence rule with its start time and timezone), referenced through `dprod:schedule`,
  and each instance has a fulfilment window ([`dprod:deadline`](https://ekgf.org/dprod/spec/develop/deadline)).
- **Authored status and computed state.** A publisher records where an offer or contract is
  in its lifecycle. An evaluator computes, from observable facts, whether each duty is pending, active,
  fulfilled or violated ([`dprod:dutyState`](https://ekgf.org/dprod/spec/develop/dutyState)). The two are kept apart
  on purpose.
- **Deterministic evaluation.** Every operand a constraint refers to is bound to one
  property on one normalised input (the authorisation request, a state-of-the-world snapshot, or the
  evaluation context itself), prohibitions always win over permissions, and the same inputs always
  produce the same decision.

Because it is a proper ODRL profile, every DPROD data contract is a valid ODRL 2.2 policy. An ODRL
processor that knows nothing of DPROD can still read the permissions and prohibitions; a DPROD-aware
processor additionally enforces duty state, bilateral duties and the evaluation rules.

The profile is defined by three files, published alongside this document:
<dprod-contracts.ttl> (the vocabulary),
[dprod-contracts-shapes.ttl](../../dprod-contracts/dprod-contracts-shapes.ttl) (the [SHACL](https://www.w3.org/TR/shacl/) constraints an
instance document must satisfy) and
<dprod-contracts-prof.ttl> (the profile declaration).
The normative evaluation semantics, which define what a conforming evaluator must compute, are
maintained in the
[formal
semantics](https://github.com/EKGF/dprod/blob/develop/dprod-contracts/docs/formal-semantics.md) document; authoring guidance for contract writers and policy writers is in the
[contracts documentation](https://github.com/EKGF/dprod/tree/develop/dprod-contracts/docs).

The Data Contracts profile is optional. A data product description conforms to DPROD whether or not it
carries any policy; an implementation that does process contracts must satisfy the contracts shapes as
stated in the [Conformance](urn:dprod:documentation:conformance) section.
