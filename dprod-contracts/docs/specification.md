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
| `dprod-due.ttl` | DUE vocabulary (operands, actions, concept values) |

---

## 2. Namespace Declarations

```turtle
@prefix odrl:        <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:       <https://ekgf.github.io/dprod/contracts/> .
@prefix dprod-shapes: <https://ekgf.github.io/dprod/contracts/shapes/> .
@prefix dprod-due:   <https://ekgf.github.io/dprod/due/> .
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

### 3.1 dprod:State

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Label** | State |
| **Definition** | Unified lifecycle state for duties and contracts |
| **Enumeration** | `dprod:Pending`, `dprod:Active`, `dprod:Fulfilled`, `dprod:Violated` |

**Individuals**:

| Individual | Label | Definition |
|------------|-------|------------|
| `dprod:Pending` | Pending | Condition not yet satisfied; not yet in force |
| `dprod:Active` | Active | Condition satisfied, action required; in force |
| `dprod:Fulfilled` | Fulfilled | Action performed; obligations complete |
| `dprod:Violated` | Violated | Deadline passed without performance; breached |

**State transitions** (see [formal-semantics.md](formal-semantics.md) for formal definition):

```
Pending -> Active    (condition becomes true)
Active  -> Fulfilled (action performed)
Active  -> Violated  (deadline passed without performance)
```

### 3.2 dprod:DataContract

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Superclass** | `odrl:Offer` |
| **Label** | Data Contract |
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
| `dprod:state` | DPROD | 0..1 |
| `dprod:effectiveDate` | DPROD | 0..1 |
| `dprod:expirationDate` | DPROD | 0..1 |

**Rule properties** (from ODRL):

| Property | Contains |
|----------|----------|
| `odrl:obligation` | Provider duties (with `dprod:subject`), consumer duties (without subject in Offer) |
| `odrl:permission` | Consumer permissions |
| `odrl:prohibition` | Restrictions |

**Example**:

```turtle
ex:contract a dprod:DataContract ;
    odrl:profile <https://ekgf.github.io/dprod/contracts/> ,
                 <https://ekgf.github.io/dprod/due/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    dprod:state dprod:Active ;
    dprod:effectiveDate "2026-01-01T00:00:00Z"^^xsd:dateTime .
```

### 3.3 dprod:Subscription

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Superclass** | `odrl:Agreement` |
| **Label** | Subscription |
| **Definition** | Activated data contract binding provider and consumer |

**Required properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:profile` | ODRL | 1..* |
| `odrl:assigner` | ODRL | 1 |
| `odrl:assignee` | ODRL | 1 |
| `dprod:subscribesTo` | DPROD | 1 |

**Recommended properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `dprod:state` | DPROD | 0..1 |
| `dprod:effectiveDate` | DPROD | 0..1 |
| `dprod:expirationDate` | DPROD | 0..1 |

**Example**:

```turtle
ex:subscription a dprod:Subscription ;
    odrl:profile <https://ekgf.github.io/dprod/contracts/> ,
                 <https://ekgf.github.io/dprod/due/> ;
    dprod:subscribesTo ex:contract ;
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
| `dprod:currentDateTime` | `odrl:LeftOperand`, `dprod:RuntimeReference` | Evaluation timestamp (mapped to `odrl:dateTime`) |

---

## 4. Property Definitions

### 4.1 dprod:state

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:Duty` | `dprod:DataContract` | `dprod:Subscription` |
| **Range** | `dprod:State` |
| **Cardinality** | 0..1 |
| **Definition** | Current lifecycle state |

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

### 4.4 dprod:subscribesTo

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `dprod:Subscription` |
| **Range** | `dprod:DataContract` |
| **Cardinality** | 1 |
| **Definition** | The contract this subscription activates |

### 4.5 dprod:effectiveDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `dprod:DataContract` | `dprod:Subscription` |
| **Range** | `xsd:dateTime` |
| **Cardinality** | 0..1 |
| **Definition** | When the contract/subscription becomes effective |

### 4.6 dprod:expirationDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `dprod:DataContract` | `dprod:Subscription` |
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

### 4.9 dprod:resolutionPath

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `odrl:LeftOperand` |
| **Range** | `xsd:string` |
| **Cardinality** | 0..1 |
| **Pattern** | `^(agent|asset|context)\.` |
| **Definition** | Dot-separated path from canonical root to value |

Canonical roots:

| Root | Meaning | Examples |
|------|---------|----------|
| `agent` | Requesting agent | `agent.role`, `agent.organization`, `agent.costCenter` |
| `asset` | Target asset | `asset.classification`, `asset.market`, `asset.residency` |
| `context` | Request context | `context.purpose`, `context.environment`, `context.legalBasis` |

### 4.10 dprod:not

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:LogicalConstraint` |
| **Range** | `odrl:Constraint` | `odrl:LogicalConstraint` |
| **Cardinality** | 0..1 (exactly one of `odrl:and`, `odrl:or`, `dprod:not` per LogicalConstraint) |
| **Definition** | Logical negation on a constraint |

ODRL defines `odrl:and` and `odrl:or` but lacks negation. DPROD Contracts adds `dprod:not` following the same pattern.

### 4.11 dprod:subject

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:assignee` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party bearing the duty (must perform the action) |

The duty bearer. Replaces `odrl:assignee` on duties to avoid role overloading -- in a bilateral agreement, the data provider is `odrl:assigner` at the policy level but would also need to be `odrl:assignee` on their own delivery duty. `dprod:subject` removes this confusion. Bridges to ODRL via `rdfs:subPropertyOf odrl:assignee` (itself a sub-property of `odrl:function`), so ODRL processors with RDFS reasoning can infer `odrl:assignee` from `dprod:subject`. Aligns with `md:subject` (W3C Market Data).

### 4.12 dprod:object

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:function` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party affected by the duty action |

The party affected by or receiving the result of the duty action (e.g., who is notified, who receives the report). Bridges to ODRL via `rdfs:subPropertyOf odrl:function`. Aligns with `md:object` (W3C Market Data).

**ODRL Common Vocabulary alternatives**: ODRL defines action-specific party functions that may be more semantically precise than `dprod:object` in certain cases:

| ODRL Function | Use when... | Example |
|---|---|---|
| `odrl:informedParty` | The duty is to inform/notify a party | Schema change notification |
| `odrl:compensatedParty` | The duty involves compensation | License fee payment |
| `odrl:trackedParty` | The duty involves tracking/monitoring | Usage tracking |
| `odrl:consentingParty` | The duty requires obtaining consent | Data processing consent |

Use `dprod:object` as the generic alternative when no specific ODRL function fits, or when you prefer consistency across duty types. All are sub-properties of `odrl:function`.

---

## 5. DUE Vocabulary Summary

The DUE profile (`dprod-due.ttl`) provides the complete data governance vocabulary.

### 5.1 Operand Categories

| Category | Operands | Resolution Root |
|----------|----------|-----------------|
| **Purpose** | `odrl:purpose` | `context.purpose` |
| **Classification** | `dprod-due:classification`, `dprod-due:sensitivity` | `asset.*` |
| **Asset metadata** | `dprod-due:assetClass`, `dprod-due:market`, `dprod-due:isBenchmark` | `asset.*` |
| **Jurisdiction** | `dprod-due:jurisdiction`, `dprod-due:residency` | `context.*`, `asset.*` |
| **Temporal** | `dprod-due:retentionPeriod`, `dprod-due:expiry` | `asset.*` |
| **Processing** | `dprod-due:processingMode` | `context.processingMode` |
| **Audit** | `dprod-due:auditRequired` | `asset.auditRequired` |
| **Identity** | `dprod-due:role`, `dprod-due:organization`, `dprod-due:costCenter`, `dprod-due:project`, `dprod-due:recipientType` | `agent.*`, `context.*` |
| **Environment** | `dprod-due:environment`, `dprod-due:network` | `context.*` |
| **Service level** | `dprod-due:availability`, `dprod-due:latency`, `dprod-due:throughput` | `context.*` |
| **Data quality** | `dprod-due:completeness`, `dprod-due:accuracy` | `asset.*` |
| **Timeliness** | `dprod-due:timeliness`, `dprod-due:delayMinutes` | `asset.*` |
| **Legal basis** | `dprod-due:legalBasis`, `dprod-due:consentId` | `context.*` |
| **Access pattern** | `dprod-due:accessPattern`, `dprod-due:volumeLimit`, `dprod-due:rateLimit` | `context.*` |
| **Channel** | `dprod-due:channel`, `dprod-due:serviceWindow` | `context.*` |
| **Subscription** | `dprod-due:subscriptionTier` | `context.subscriptionTier` |
| **Derivation** | `dprod-due:derivationType` | `context.derivationType` |

### 5.2 Actions

**ODRL Common Vocabulary** (used directly):

| Action | Definition | Hierarchy |
|--------|------------|-----------|
| `odrl:use` | General use | Top of hierarchy |
| `odrl:read` | Read/view | `includedIn odrl:use` |
| `odrl:display` | Display to users | `includedIn odrl:use` |
| `odrl:distribute` | Distribute to third parties | `includedIn odrl:use` |
| `odrl:delete` | Delete the asset | `includedIn odrl:use` |
| `odrl:modify` | Modify the asset | `includedIn odrl:use` |
| `odrl:aggregate` | Aggregate with other data | `includedIn odrl:use` |
| `odrl:anonymize` | Remove identifying info | `includedIn odrl:use` |
| `odrl:derive` | Create derived data | `includedIn odrl:use` |

**DUE-specific actions**:

| Action | Definition | Hierarchy |
|--------|------------|-----------|
| `dprod-due:nonDisplay` | Automated/programmatic use | `includedIn odrl:use` |
| `dprod-due:conformTo` | Conform to a schema or spec | No parent (duty-only governance action) |
| `dprod-due:log` | Log access to the asset | `includedIn odrl:inform` |
| `dprod-due:notify` | Notify relevant parties | `includedIn odrl:inform` |
| `dprod-due:report` | Submit usage reports | `includedIn odrl:inform` |
| `dprod-due:deliver` | Deliver data to consumer | `includedIn odrl:distribute` |
| `dprod-due:calculateIndex` | Use for index calculation | `includedIn odrl:derive` |
| `dprod-due:algorithmicTrading` | Use for automated trading | `includedIn dprod-due:nonDisplay` |
| `dprod-due:query` | Query/select data | `includedIn odrl:read` |
| `dprod-due:export` | Export data outside system | `includedIn odrl:distribute` |
| `dprod-due:copy` | Copy data to another location | `includedIn odrl:reproduce` |
| `dprod-due:link` | Link/join with other datasets | `includedIn odrl:aggregate` |
| `dprod-due:profile` | Create profiles from data | `includedIn odrl:derive` |

### 5.3 Concept Values

Key SKOS concept values defined by DUE:

| Category | Values |
|----------|--------|
| Purpose | `analytics`, `research`, `compliance`, `operations` |
| Classification | `public`, `internal`, `confidential`, `restricted` |
| Sensitivity | `pii` (PII), `mnpi` (MNPI), `phi` (PHI) |
| Processing mode | `human`, `automated`, `modelTraining`, `inference` |
| Environment | `production`, `staging`, `development`, `sandbox` |
| Network | `internalNetwork`, `externalNetwork`, `cloudNetwork` |
| Timeliness | `realtime`, `nearRealtime`, `delayed`, `endOfDay`, `historical` |
| Legal basis | `consent`, `contract`, `legalObligation`, `vitalInterest`, `publicTask`, `legitimateInterest` |
| Recipient type | `internalRecipient`, `externalRecipient`, `professional`, `retail` |
| Access pattern | `batch`, `streaming`, `interactive`, `api` |
| Derivation type | `commingled`, `nonSubstitutive`, `newProduct` |

---

## 6. SHACL Constraints Summary

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
| `dprod-shapes:DutyShape` | `odrl:Duty` | Exactly one `odrl:action`; `subject` 0..1; `object` 0..1; `deadline` 0..1 (dateTime/duration); `recurrence` 0..1 (RRULE pattern); `state` 0..1 |

### Constraint-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:ConstraintShape` | `odrl:Constraint` | Exactly one `leftOperand`, `operator`, and at least one `rightOperand` |
| `dprod-shapes:LogicalConstraintShape` | `odrl:LogicalConstraint` | Exactly one of: `odrl:and`, `odrl:or`, or `dprod:not` |

### Contract-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:DataContractShape` | `dprod:DataContract` | Must declare `odrl:profile`; exactly one `odrl:assigner`; at least one clause; `state` 0..1; effective/expiration dates 0..1 |
| `dprod-shapes:SubscriptionShape` | `dprod:Subscription` | Must declare `odrl:profile`; exactly one `dprod:subscribesTo` (must be `dprod:DataContract`); at least one clause; `state` 0..1; effective/expiration dates 0..1 |

### Operand shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `dprod-shapes:LeftOperandShape` | `odrl:LeftOperand` | `resolutionPath` 0..1; must start with `agent.`, `asset.`, or `context.` |
| `dprod-shapes:DUEOperandShape` | All 26 DUE operands | Exactly one `resolutionPath` (pattern: `agent.\|asset.\|context.`) |

### Rejection shapes

| Shape | Rejects | Message |
|-------|---------|---------|
| `dprod-shapes:RejectXoneShape` | `odrl:xone` | Not supported in DPROD Contracts |
| `dprod-shapes:RejectRemedyShape` | `odrl:remedy` | Noted as future extension |
| `dprod-shapes:RejectConsequenceShape` | `odrl:consequence` | Noted as future extension |
| `dprod-shapes:RejectTicketShape` | `odrl:Ticket` | Not supported |
| `dprod-shapes:RejectRequestShape` | `odrl:Request` | Not supported |
| `dprod-shapes:RejectAssetCollectionShape` | `odrl:AssetCollection` | Use `dprod:partOf` instead |
| `dprod-shapes:RejectPartyCollectionShape` | `odrl:PartyCollection` | Use `dprod:memberOf` instead |
| `dprod-shapes:RejectInheritAllowedShape` | `odrl:inheritAllowed` | Not supported |
| `dprod-shapes:RejectInheritFromShape` | `odrl:inheritFrom` | Not supported |

---

## 7. Property Usage Matrix

Which DPROD properties are valid on which classes:

| Property | Duty | DataContract | Subscription | LeftOperand | LogicalConstraint | Asset | Party |
|----------|------|-------------|-------------|-------------|-------------------|-------|-------|
| `dprod:state` | Yes | Yes | Yes | | | | |
| `dprod:deadline` | Yes | | | | | | |
| `dprod:recurrence` | Yes | | | | | | |
| `dprod:subject` | Yes | | | | | | |
| `dprod:object` | Yes | | | | | | |
| `dprod:subscribesTo` | | | Yes | | | | |
| `dprod:effectiveDate` | | Yes | Yes | | | | |
| `dprod:expirationDate` | | Yes | Yes | | | | |
| `dprod:resolutionPath` | | | | Yes | | | |
| `dprod:not` | | | | | Yes | | |
| `dprod:partOf` | | | | | | Yes | |
| `dprod:memberOf` | | | | | | | Yes |

---

## 8. Profile Constraints

DPROD Contracts restricts certain ODRL features:

| Feature | Status | Reason |
|---------|--------|--------|
| `odrl:conflict` | Fixed to `odrl:prohibit` at profile level | Deterministic conflict resolution; declared once in `dprod-contracts-prof.ttl` |
| `odrl:xone` | Rejected | Noted as future extension |
| `odrl:remedy` | Rejected | Noted as future extension |
| `odrl:consequence` | Rejected | Noted as future extension |
| `odrl:Ticket` | Not used | Not applicable to data governance |
| `odrl:Request` | Not used | Not applicable |
| `odrl:assignee` (on Duty) | Replaced by `dprod:subject` | `dprod:subject rdfs:subPropertyOf odrl:assignee` -- avoids role overloading |
| `odrl:AssetCollection` | Not used | Use `dprod:partOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |
| `odrl:PartyCollection` | Not used | Use `dprod:memberOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |

---

**Version**: 0.7 | **Date**: 2026-02-04
