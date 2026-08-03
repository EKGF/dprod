# DPROD Contracts Technical Specification

RDF/OWL vocabulary reference for the DPROD Contracts ODRL 2.2 profile.

---

## 1. Introduction

This document is a vocabulary reference for implementers. It defines every class and property that DPROD Contracts adds to ODRL 2.2, their types, domains, ranges, and cardinalities.

**Scope**: This document covers the RDF/OWL vocabulary. For formal evaluation semantics, see [formal-semantics.md](formal-semantics.md). For practical authoring guidance, see [contracts-guide.md](contracts-guide.md) and [policy-writers-guide.md](policy-writers-guide.md).

**Source files**:

| File | Contents |
|------|----------|
| `dprod-contracts.ttl` | Core ontology (classes, properties) |
| `dprod-contracts-shapes.ttl` | SHACL validation shapes |

---

## 2. Namespace Declarations

```turtle
@prefix odrl:        <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://www.omg.org/spec/DPROD/dprod/> .
@prefix dprod-shapes: <https://www.omg.org/spec/DPROD/contracts/shapes/> .
@prefix rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:        <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:         <http://www.w3.org/2002/07/owl#> .
@prefix xsd:         <http://www.w3.org/2001/XMLSchema#> .
@prefix skos:        <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:         <http://purl.org/dc/terms/> .
@prefix prov:        <http://www.w3.org/ns/prov#> .
@prefix sh:          <http://www.w3.org/ns/shacl#> .
```

---

## 3. Class Definitions

### 3.1 Example Lifecycle Concept Scheme

DPROD ships an example `skos:ConceptScheme` — **`dprod:DataContractLifeCycleStatus`** — covering four common lifecycle states. This scheme is one ready-made vocabulary that policy authors can plug into any of the three lifecycle properties (`dprod:offerLifeCycleStatus`, `dprod:contractLifeCycleStatus`, `dprod:dutyState`). Each property's range is the open `skos:Concept` class, so implementations are free to use this scheme as-is, extend it via `skos:inScheme`, or use a different vocabulary entirely. The state machine described in [formal-semantics.md](formal-semantics.md) §5 is one possible interpretation of these concepts; it is not a requirement of the properties themselves.

| Individual | Label | Definition |
|------------|-------|------------|
| `dprod:Pending` | Pending | Condition not yet satisfied; not yet in force |
| `dprod:Active` | Active | Condition satisfied, action required; in force |
| `dprod:Fulfilled` | Fulfilled | Action performed; obligations complete |
| `dprod:Violated` | Violated | Deadline passed without performance; breached |

**Duty-state transitions** (see [formal-semantics.md](formal-semantics.md) for the formal definition):

```
Pending -> Active    (condition becomes true)
Active  -> Fulfilled (action performed)
Active  -> Violated  (deadline passed without performance)
```

For administrative offer/contract lifecycle (`dprod:offerLifeCycleStatus`, `dprod:contractLifeCycleStatus`), the same four concepts are used to represent: `Pending` (not yet in force), `Active` (in force), `Fulfilled` (obligations complete), `Violated` (breached). These transitions are administrative — they are not evaluated at request time.

### 3.2 dprod:DataOffer

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Superclass** | `odrl:Offer` |
| **Label** | Data Offer |
| **Definition** | Policy offer defining data access terms |

**Required properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:profile` | ODRL | 1..* (must include DPROD Contracts profile URI) |
| `odrl:assigner` | ODRL | 1 |

**Recommended properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:target` | ODRL | 1..* |
| `dprod:offerLifeCycleStatus` | DPROD | 0..1 |
| `dprod:effectiveDate` | DPROD | 0..1 |
| `dprod:expirationDate` | DPROD | 0..1 |

**Rule properties** (from ODRL):

| Property | Contains |
|----------|----------|
| `odrl:obligation` | Provider duties (with `dprod:subjectOfDuty`), consumer duties (without subject in Offer) |
| `odrl:permission` | Consumer permissions |
| `odrl:prohibition` | Restrictions |

**Example**:

```turtle
ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    dprod:offerLifeCycleStatus dprod:Active ;
    dprod:effectiveDate "2026-01-01T00:00:00Z"^^xsd:dateTime .
```

### 3.3 dprod:DataContract

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Superclass** | `odrl:Agreement` |
| **Label** | Data Contract |
| **Definition** | Activated data offer binding provider and consumer |

**Required properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:profile` | ODRL | 1..* |
| `odrl:assigner` | ODRL | 1 |
| `odrl:assignee` | ODRL | 1 |
| `dprod:acceptsOffer` | DPROD | 1 |

**Recommended properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `dprod:contractLifeCycleStatus` | DPROD | 0..1 |
| `dprod:effectiveDate` | DPROD | 0..1 |
| `dprod:expirationDate` | DPROD | 0..1 |

**Example**:

```turtle
ex:subscription a dprod:DataContract ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    dprod:acceptsOffer ex:contract ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:analyticsTeam ;
    dprod:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime ;
    dprod:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
```

### 3.4 dprod:RuntimeReference

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Label** | Runtime Reference |
| **Definition** | Value resolved at evaluation time |

**Individuals**:

| Individual | Types | Definition |
|------------|-------|------------|
| `dprod:currentAgent` | `dprod:RuntimeReference`, `odrl:Party` | The requesting agent (resolved at evaluation time) |
| `dprod:currentDateTime` | `odrl:LeftOperand`, `dprod:RuntimeReference` | Evaluation timestamp (canonical form; `odrl:dateTime` normalises to this) |

---

## 4. Property Definitions

### 4.1 dprod:offerLifeCycleStatus, dprod:contractLifeCycleStatus, dprod:dutyState

| Property | Domain | Range | Cardinality | Definition |
|----------|--------|-------|-------------|------------|
| `dprod:offerLifeCycleStatus` | `dprod:DataOffer` | `skos:Concept` | 0..1 | Administrative lifecycle status of a data offer (not evaluated at request time) |
| `dprod:contractLifeCycleStatus` | `dprod:DataContract` | `skos:Concept` | 0..1 | Administrative lifecycle status of a data contract (not evaluated at request time) |
| `dprod:dutyState` | `odrl:Duty` | `skos:Concept` | 0..1 | Evaluated state of a duty (set by the standard evaluation algorithm; see §5 of formal-semantics.md) |

All three properties are `owl:ObjectProperty`. The four DPROD-defined canonical concepts (`dprod:Pending`, `dprod:Active`, `dprod:Fulfilled`, `dprod:Violated`) form the default vocabulary for each; profiles MAY introduce further `skos:Concept` values.

### 4.2 dprod:deadline

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `odrl:Duty` |
| **Range** | `xsd:dateTime` | `xsd:duration` (enforced by SHACL) |
| **Cardinality** | 0..1 |
| **Definition** | Time constraint for duty fulfillment |

Two forms:

| Form | Datatype | Meaning | Example |
|------|----------|---------|---------|
| Absolute | `xsd:dateTime` | Fixed deadline | `"2026-12-31T23:59:59Z"^^xsd:dateTime` |
| Relative | `xsd:duration` | Offset from activation | `"P30D"^^xsd:duration` |

### 4.3 dprod:recurrence

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `odrl:Duty` |
| **Range** | `xsd:string` |
| **Cardinality** | 0..1 |
| **Pattern** | `^FREQ=(SECONDLY|MINUTELY|HOURLY|DAILY|WEEKLY|MONTHLY|YEARLY)` |
| **Definition** | RFC 5545 RRULE defining when duty instances are generated |

Each generated instance follows the standard duty lifecycle independently (Pending -> Active -> Fulfilled/Violated). The `deadline` property defines the per-instance fulfillment window. Any iCal-compliant library can parse the value.

### 4.4 dprod:acceptsOffer

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `dprod:DataContract` |
| **Range** | `dprod:DataOffer` |
| **Cardinality** | 1 |
| **Definition** | The contract this subscription activates |

### 4.5 dprod:effectiveDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `dprod:DataOffer` | `dprod:DataContract` |
| **Range** | `xsd:dateTime` |
| **Cardinality** | 0..1 |
| **Definition** | When the contract/subscription becomes effective |

### 4.6 dprod:expirationDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `dprod:DataOffer` | `dprod:DataContract` |
| **Range** | `xsd:dateTime` |
| **Cardinality** | 0..1 |
| **Definition** | When the contract/subscription expires |

### 4.7 dprod:partOf

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty`, `owl:TransitiveProperty` |
| **SubPropertyOf** | `odrl:partOf` |
| **Domain** | `odrl:Asset` |
| **Range** | `odrl:Asset` |
| **Cardinality** | 0..* |
| **Definition** | Asset contained in a larger asset |

Transitive: if table `partOf` schema and schema `partOf` database, then table `partOf` database. Declared `rdfs:subPropertyOf odrl:partOf` so ODRL processors with RDFS reasoning can interpret DPROD asset hierarchies.

### 4.8 dprod:memberOf

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty`, `owl:TransitiveProperty` |
| **SubPropertyOf** | `odrl:partOf` |
| **Domain** | `odrl:Party` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..* |
| **Definition** | Party member of a group or organization |

Transitive: if person `memberOf` team and team `memberOf` division, then person `memberOf` division. Declared `rdfs:subPropertyOf odrl:partOf` so ODRL processors with RDFS reasoning can interpret DPROD party hierarchies.

### 4.9 dprod:path

| Property | Value |
|----------|-------|
| **Type** | `rdf:Property` |
| **Domain** | `odrl:LeftOperand` |
| **Cardinality** | 0..1 |
| **Definition** | SPARQL-style property path from evaluation context to operand value |

Simple paths are a single property IRI; sequence paths are RDF lists:

| Path type | Syntax | Meaning | Example |
|-----------|--------|---------|---------|
| Context-rooted | `dprod:path ex:environment` | Direct property on request | `?request ex:environment ?value` |
| Asset-rooted | `dprod:path (odrl:target ex:timeliness)` | Via target | `?request odrl:target ?asset . ?asset ex:timeliness ?value` |
| Agent-rooted | `dprod:path (odrl:assignee ex:recipientType)` | Via assignee | `?request odrl:assignee ?agent . ?agent ex:recipientType ?value` |
| ODRL operand | `dprod:path odrl:purpose` | Direct property on request | `?request odrl:purpose ?value` |

### 4.10 dprod:not

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:LogicalConstraint` |
| **Range** | `odrl:Constraint` | `odrl:LogicalConstraint` |
| **Cardinality** | 0..1 (exactly one of `odrl:and`, `odrl:or`, `dprod:not` per LogicalConstraint) |
| **Definition** | Logical negation on a constraint |

ODRL defines `odrl:and` and `odrl:or` but lacks negation. DPROD Contracts adds `dprod:not` following the same pattern.

### 4.11 dprod:subjectOfDuty

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:function` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party bearing the duty (must perform the action) |

The duty bearer. Replaces `odrl:assignee` on duties to avoid role overloading -- in a bilateral agreement, the data provider is `odrl:assigner` at the policy level but would also need to be `odrl:assignee` on their own delivery duty. `dprod:subjectOfDuty` removes this confusion. Bridges to ODRL via `rdfs:subPropertyOf odrl:function` (the abstract umbrella for party-roles in a Rule), so ODRL processors retain a generic role link without inheriting the contested `odrl:assignee` semantics. Aligns with `md:subject` (W3C Market Data), which likewise scopes the property to `odrl:Duty`.

### 4.12 dprod:objectOfDuty

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:function` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party affected by the duty action |

The party affected by or receiving the result of the duty action (e.g., who is notified, who receives the report). Bridges to ODRL via `rdfs:subPropertyOf odrl:function`. Aligns with `md:object` (W3C Market Data).

**ODRL Common Vocabulary alternatives**: ODRL defines action-specific party functions that may be more semantically precise than `dprod:objectOfDuty` in certain cases:

| ODRL Function | Use when... | Example |
|---|---|---|
| `odrl:informedParty` | The duty is to inform/notify a party | Schema change notification |
| `odrl:compensatedParty` | The duty involves compensation | License fee payment |
| `odrl:trackedParty` | The duty involves tracking/monitoring | Usage tracking |
| `odrl:consentingParty` | The duty requires obtaining consent | Data processing consent |

Use `dprod:objectOfDuty` as the generic alternative when no specific ODRL function fits, or when you prefer consistency across duty types. All are sub-properties of `odrl:function`.

---

## 5. SHACL Constraints Summary

Shapes are defined in `dprod-contracts-shapes.ttl`. Key constraints:

### Policy-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:PolicyShape` | `odrl:Policy` | Must declare `odrl:profile` (for engines with RDFS inference) |
| `dprod-shapes:SetShape` | `odrl:Set` | Must declare `odrl:profile`; at least one `odrl:target`; at least one clause |
| `dprod-shapes:OfferShape` | `odrl:Offer` | Must declare `odrl:profile`; exactly one `odrl:assigner`; at least one clause |
| `dprod-shapes:AgreementShape` | `odrl:Agreement` | Must declare `odrl:profile`; exactly one `odrl:assigner` and one `odrl:assignee`; at least one clause |

### Rule-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:PermissionShape` | `odrl:Permission` | Exactly one `odrl:action`; at most one `odrl:target` (inherited from policy if absent) |
| `dprod-shapes:ProhibitionShape` | `odrl:Prohibition` | Exactly one `odrl:action`; at most one `odrl:target` (inherited from policy if absent) |
| `dprod-shapes:DutyShape` | `odrl:Duty` | Exactly one `odrl:action`; `dprod:subjectOfDuty` 0..1; `dprod:objectOfDuty` 0..1; `deadline` 0..1 (dateTime/duration); `recurrence` 0..1 (RRULE pattern); `state` 0..1 |

### Constraint-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:ConstraintShape` | `odrl:Constraint` | Exactly one `leftOperand`, `operator`, and at least one `rightOperand` |
| `dprod-shapes:LogicalConstraintShape` | `odrl:LogicalConstraint` | Exactly one of: `odrl:and`, `odrl:or`, or `dprod:not` |

### Contract-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:DataOfferShape` | `dprod:DataOffer` | Must declare `odrl:profile`; exactly one `odrl:assigner`; at least one clause; `state` 0..1; effective/expiration dates 0..1 |
| `dprod-shapes:DataContractShape` | `dprod:DataContract` | Must declare `odrl:profile`; exactly one `dprod:acceptsOffer` (must be `dprod:DataOffer`); at least one clause; `state` 0..1; effective/expiration dates 0..1 |

### Operand shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:LeftOperandShape` | `odrl:LeftOperand` | `dprod:path` 0..1 (IRI or `rdf:List` of IRIs) |

### Rejection shapes

| Shape | Rejects | Message |
|-------|---------|---------|
| `dprod-shapes:RejectXoneShape` | `odrl:xone` | Not supported in DPROD Contracts |
| `dprod-shapes:RejectRemedyShape` | `odrl:remedy` | Noted as future extension |
| `dprod-shapes:RejectConsequenceShape` | `odrl:consequence` | Noted as future extension |
| `dprod-shapes:RejectTicketShape` | `odrl:Ticket` | Not supported |
| `dprod-shapes:RejectRequestShape` | `odrl:Request` | DPROD contracts reject odrl:Request because Offer-Request-Agreement semantics are undefined; support is deferred. |
| `dprod-shapes:RejectAssetCollectionShape` | `odrl:AssetCollection` | Use `dprod:partOf` instead |
| `dprod-shapes:RejectPartyCollectionShape` | `odrl:PartyCollection` | Use `dprod:memberOf` instead |
| `dprod-shapes:RejectInheritAllowedShape` | `odrl:inheritAllowed` | Not supported |
| `dprod-shapes:RejectInheritFromShape` | `odrl:inheritFrom` | Not supported |

---

## 6. Property Usage Matrix

Which DPROD properties are valid on which classes:

| Property | Duty | DataOffer | DataContract | LeftOperand | LogicalConstraint | Asset | Party |
|----------|------|-------------|-------------|-------------|-------------------|-------|-------|
| `dprod:dutyState` | Yes | | | | | | |
| `dprod:offerLifeCycleStatus` | | Yes | | | | | |
| `dprod:contractLifeCycleStatus` | | | Yes | | | | |
| `dprod:deadline` | Yes | | | | | | |
| `dprod:recurrence` | Yes | | | | | | |
| `dprod:subjectOfDuty` | Yes | | | | | | |
| `dprod:objectOfDuty` | Yes | | | | | | |
| `dprod:acceptsOffer` | | | Yes | | | | |
| `dprod:effectiveDate` | | Yes | Yes | | | | |
| `dprod:expirationDate` | | Yes | Yes | | | | |
| `dprod:path` | | | | Yes | | | |
| `dprod:not` | | | | | Yes | | |
| `dprod:partOf` | | | | | | Yes | |
| `dprod:memberOf` | | | | | | | Yes |

---

## 7. Profile Constraints

DPROD Contracts restricts certain ODRL features:

| Feature | Status | Reason |
|---------|--------|--------|
| `odrl:conflict` | Fixed to `odrl:prohibit` at profile level | Deterministic conflict resolution; declared once in `dprod-contracts-prof.ttl` |
| `odrl:xone` | Rejected | Noted as future extension |
| `odrl:remedy` | Rejected | Noted as future extension |
| `odrl:consequence` | Rejected | Noted as future extension |
| `odrl:Ticket` | Not used | Not applicable to data governance |
| `odrl:Request` | Rejected (support deferred) | Offer-Request-Agreement semantics are undefined; accepting it would imply unsupported semantics. |
| `odrl:assignee` (on Duty) | Replaced by `dprod:subjectOfDuty` | `dprod:subjectOfDuty rdfs:subPropertyOf odrl:function` -- avoids role overloading on duties |
| `odrl:AssetCollection` | Not used | Use `dprod:partOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |
| `odrl:PartyCollection` | Not used | Use `dprod:memberOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |

DPROD contracts reject odrl:Request because Offer-Request-Agreement semantics are undefined; support is deferred. An `odrl:Request` MUST fail SHACL validation until the profile defines how it relates to `odrl:Offer` and `odrl:Agreement` and what evaluator behavior follows.

---

**Version**: 0.7 | **Date**: 2026-02-04
