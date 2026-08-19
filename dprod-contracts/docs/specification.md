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

### 3.1 Optional Lifecycle Concept Scheme

DPROD ships an optional `skos:ConceptScheme` — **`dprod:DataContractLifecycleStatus`** — covering four common values. Policy authors may use it for `dprod:offerLifecycleStatus` and `dprod:contractLifecycleStatus`, extend it, or replace it with an enterprise taxonomy. The properties range over the open `skos:Concept` class; conformance never requires membership in the DPROD scheme.

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

The formal evaluator may also use these concept IRIs as `dprod:dutyState` values. Reusing a concept does not merge the properties: offer and contract statuses are authored administrative facts, while duty state is computed from observable facts. `dprod:dutyState` is not part of the lifecycle-status property hierarchy.

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
| `dprod:offerLifecycleStatus` | DPROD | 0..1 |
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
    dprod:offerLifecycleStatus dprod:Active ;
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
| `dprod:contractLifecycleStatus` | DPROD | 0..1 |
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

### 4.1 Lifecycle Status and Duty State

| Property | Super-property | Domain | Range | Cardinality | Definition |
|----------|----------------|--------|-------|-------------|------------|
| `dprod:lifecycleStatus` | — | — | `skos:Concept` | — | Core abstract super-property for authored lifecycle statuses |
| `dprod:dataProductLifecycleStatus` | `dprod:lifecycleStatus` | `dprod:DataProduct` | `skos:Concept` | 0..1 | Authored development lifecycle status of a data product |
| `dprod:offerLifecycleStatus` | `dprod:lifecycleStatus` | `dprod:DataOffer` | `skos:Concept` | 0..1 | Authored publication lifecycle status of a data offer |
| `dprod:contractLifecycleStatus` | `dprod:lifecycleStatus` | `dprod:DataContract` | `skos:Concept` | 0..1 | Authored administrative lifecycle status of a data contract |
| `dprod:dutyState` | — | `odrl:Duty` | `skos:Concept` | 0..1 | Evaluator-computed state of a duty; see §5 of formal-semantics.md |

The generic property and `dprod:dataProductLifecycleStatus` are defined by the core ontology. The contracts module defines only its domain-specific sub-properties. `dprod:dutyState` is deliberately outside the hierarchy because it is computed rather than authored.

All five properties are `owl:ObjectProperty`. Their values come from open SKOS taxonomies: DPROD's concept schemes are optional starting points, and profiles MAY introduce additional `skos:Concept` values. The former mixed-capitalization spellings of the offer and contract properties are obsolete and fail SHACL validation.

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

### 4.7 odrl:partOf Collection Membership

DPROD reuses `odrl:partOf` instead of defining parallel asset and party hierarchy properties. The relation is type-constrained by SHACL:

| Subject | Object |
|---------|--------|
| `odrl:Asset` | `odrl:AssetCollection` |
| `odrl:AssetCollection` | `odrl:AssetCollection` |
| `odrl:Party` | `odrl:PartyCollection` |
| `odrl:PartyCollection` | `odrl:PartyCollection` |

DPROD evaluators MUST apply the transitive closure of valid, same-kind `odrl:partOf` paths. This is profile evaluation semantics, not a redeclaration of the ODRL property as `owl:TransitiveProperty`. Cross-kind paths fail validation. Collections are explicit: `odrl:source` resolution and collection `odrl:refinement` are unsupported and fail validation.

The removed `dprod:partOf` and `dprod:memberOf` properties are breaking changes. Their use fails validation so obsolete contracts cannot silently acquire different semantics.

### 4.8 dprod:path

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

### 4.9 dprod:not

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:LogicalConstraint` |
| **Range** | `odrl:Constraint` | `odrl:LogicalConstraint` |
| **Cardinality** | 0..1 (exactly one of `odrl:and`, `odrl:or`, `dprod:not` per LogicalConstraint) |
| **Definition** | Logical negation on a constraint |

ODRL defines `odrl:and` and `odrl:or` but lacks negation. DPROD Contracts adds `dprod:not` following the same pattern.

### 4.10 dprod:subjectOfDuty

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:function` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party bearing the duty (must perform the action) |

The duty bearer. Replaces `odrl:assignee` on duties to avoid role overloading -- in a bilateral agreement, the data provider is `odrl:assigner` at the policy level but would also need to be `odrl:assignee` on their own delivery duty. `dprod:subjectOfDuty` removes this confusion. Bridges to ODRL via `rdfs:subPropertyOf odrl:function` (the abstract umbrella for party-roles in a Rule), so ODRL processors retain a generic role link without inheriting the contested `odrl:assignee` semantics. Aligns with `md:subject` (W3C Market Data), which likewise scopes the property to `odrl:Duty`.

### 4.11 dprod:objectOfDuty

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

### Collection shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:PartOfShape` | Subjects of `odrl:partOf` | Asset membership must end in an `odrl:AssetCollection`; party membership must end in an `odrl:PartyCollection`; collection nesting must remain within the same kind |
| `dprod-shapes:AssetCollectionShape` | `odrl:AssetCollection` | Explicit membership only; rejects `odrl:source` and `odrl:refinement` |
| `dprod-shapes:PartyCollectionShape` | `odrl:PartyCollection` | Explicit membership only; rejects `odrl:source` and `odrl:refinement` |

### Rejection shapes

| Shape | Rejects | Message |
|-------|---------|---------|
| `dprod-shapes:RejectXoneShape` | `odrl:xone` | Not supported in DPROD Contracts |
| `dprod-shapes:RejectRemedyShape` | `odrl:remedy` | Noted as future extension |
| `dprod-shapes:RejectConsequenceShape` | `odrl:consequence` | Noted as future extension |
| `dprod-shapes:RejectTicketShape` | `odrl:Ticket` | Not supported |
| `dprod-shapes:RejectRequestShape` | `odrl:Request` | DPROD contracts reject odrl:Request because Offer-Request-Agreement semantics are undefined; support is deferred. |
| `dprod-shapes:RejectObsoleteDprodPartOfShape` | `dprod:partOf` | Use `odrl:partOf` |
| `dprod-shapes:RejectObsoleteDprodMemberOfShape` | `dprod:memberOf` | Use `odrl:partOf` |
| `dprod-shapes:RejectInheritAllowedShape` | `odrl:inheritAllowed` | Not supported |
| `dprod-shapes:RejectInheritFromShape` | `odrl:inheritFrom` | Not supported |
| `dprod-shapes:RejectMixedLifecycleStatusOnDataOfferShape` | Non-offer lifecycle properties on `dprod:DataOffer` | Use `dprod:offerLifecycleStatus` |
| `dprod-shapes:RejectMixedLifecycleStatusOnDataContractShape` | Non-contract lifecycle properties on `dprod:DataContract` | Use `dprod:contractLifecycleStatus` |
| `dprod-shapes:RejectMixedLifecycleStatusOnDataProductShape` | Contract lifecycle properties on `dprod:DataProduct` | Use `dprod:dataProductLifecycleStatus` |
| `dprod-shapes:RejectObsoleteOfferLifecycleStatusSpellingShape` | Legacy mixed-capitalization offer status property | Use the canonical offer lifecycle property |
| `dprod-shapes:RejectObsoleteContractLifecycleStatusSpellingShape` | Legacy mixed-capitalization contract status property | Use the canonical contract lifecycle property |

---

## 6. Property Usage Matrix

Which concrete DPROD properties are valid on which classes (`dprod:lifecycleStatus` is an abstract super-property and is omitted):

| Property | Duty | DataProduct | DataOffer | DataContract | LeftOperand | LogicalConstraint | Asset | Party |
|----------|------|-------------|-----------|--------------|-------------|-------------------|-------|-------|
| `dprod:dutyState` | Yes | | | | | | | |
| `dprod:dataProductLifecycleStatus` | | Yes | | | | | | |
| `dprod:offerLifecycleStatus` | | | Yes | | | | | |
| `dprod:contractLifecycleStatus` | | | | Yes | | | | |
| `dprod:deadline` | Yes | | | | | | | |
| `dprod:recurrence` | Yes | | | | | | | |
| `dprod:subjectOfDuty` | Yes | | | | | | | |
| `dprod:objectOfDuty` | Yes | | | | | | | |
| `dprod:acceptsOffer` | | | | Yes | | | | |
| `dprod:effectiveDate` | | | Yes | Yes | | | | |
| `dprod:expirationDate` | | | Yes | Yes | | | | |
| `dprod:path` | | | | | Yes | | | |
| `dprod:not` | | | | | | Yes | | |

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
| `odrl:AssetCollection` | Supported with explicit membership | Assets and nested asset collections use `odrl:partOf`; `odrl:source` and collection refinement are rejected |
| `odrl:PartyCollection` | Supported with explicit membership | Parties and nested party collections use `odrl:partOf`; `odrl:source` and collection refinement are rejected |

DPROD contracts reject odrl:Request because Offer-Request-Agreement semantics are undefined; support is deferred. An `odrl:Request` MUST fail SHACL validation until the profile defines how it relates to `odrl:Offer` and `odrl:Agreement` and what evaluator behavior follows.

---

**Version**: 0.7 | **Date**: 2026-08-19
