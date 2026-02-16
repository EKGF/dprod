# Adalbert Technical Specification

RDF/OWL vocabulary reference for the Adalbert ODRL 2.2 profile.

---

## 1. Introduction

This document is a vocabulary reference for implementers. It defines every class and property that Adalbert adds to ODRL 2.2, their types, domains, ranges, and cardinalities.

**Scope**: This document covers the RDF/OWL vocabulary. For formal evaluation semantics, see [Adalbert_Semantics.md](Adalbert_Semantics.md). For practical authoring guidance, see [contracts-guide.md](contracts-guide.md) and [policy-writers-guide.md](policy-writers-guide.md).

**Source files**:

| File | Contents |
|------|----------|
| `ontology/adalbert-core.ttl` | Core ontology (classes, properties) |
| `ontology/adalbert-shacl.ttl` | SHACL validation shapes |
| `profiles/adalbert-due.ttl` | DUE vocabulary (operands, actions, concept values) |
| `config/namespaces.ttl` | Authoritative namespace registry |

---

## 2. Namespace Declarations

```turtle
@prefix odrl:         <http://www.w3.org/ns/odrl/2/> .
@prefix adalbert:     <https://vocabulary.bigbank/adalbert/> .
@prefix adalbertsh:   <https://vocabulary.bigbank/adalbert/shapes/> .
@prefix adalbert-due: <https://vocabulary.bigbank/adalbert/due/> .
@prefix rdf:          <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:         <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:          <http://www.w3.org/2002/07/owl#> .
@prefix xsd:          <http://www.w3.org/2001/XMLSchema#> .
@prefix skos:         <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms:      <http://purl.org/dc/terms/> .
@prefix prov:         <http://www.w3.org/ns/prov#> .
@prefix sh:           <http://www.w3.org/ns/shacl#> .
```

---

## 3. Class Definitions

### 3.1 adalbert:State

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Label** | State |
| **Definition** | Unified lifecycle state for duties and contracts |
| **Enumeration** | `adalbert:Pending`, `adalbert:Active`, `adalbert:Fulfilled`, `adalbert:Violated` |

**Individuals**:

| Individual | Label | Definition |
|------------|-------|------------|
| `adalbert:Pending` | Pending | Condition not yet satisfied; not yet in force |
| `adalbert:Active` | Active | Condition satisfied, action required; in force |
| `adalbert:Fulfilled` | Fulfilled | Action performed; obligations complete |
| `adalbert:Violated` | Violated | Deadline passed without performance; breached |

**State transitions** (see [Adalbert_Semantics.md](Adalbert_Semantics.md) for formal definition):

```
Pending -> Active    (condition becomes true)
Active  -> Fulfilled (action performed)
Active  -> Violated  (deadline passed without performance)
```

### 3.2 adalbert:DataContract

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Superclass** | `odrl:Offer` |
| **Label** | Data Contract |
| **Definition** | Policy offer defining data access terms |

**Required properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:profile` | ODRL | 1..* (must include Adalbert profile URI) |
| `odrl:assigner` | ODRL | 1 |

**Recommended properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `odrl:target` | ODRL | 1..* |
| `adalbert:state` | Adalbert | 0..1 |
| `adalbert:effectiveDate` | Adalbert | 0..1 |
| `adalbert:expirationDate` | Adalbert | 0..1 |

**Rule properties** (from ODRL):

| Property | Contains |
|----------|----------|
| `odrl:obligation` | Provider duties (with `adalbert:subject`), consumer duties (without subject in Offer) |
| `odrl:permission` | Consumer permissions |
| `odrl:prohibition` | Restrictions |

**Example**:

```turtle
ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    adalbert:state adalbert:Active ;
    adalbert:effectiveDate "2026-01-01T00:00:00Z"^^xsd:dateTime .
```

### 3.3 adalbert:Subscription

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
| `adalbert:subscribesTo` | Adalbert | 1 |

**Recommended properties**:

| Property | Source | Cardinality |
|----------|--------|-------------|
| `adalbert:state` | Adalbert | 0..1 |
| `adalbert:effectiveDate` | Adalbert | 0..1 |
| `adalbert:expirationDate` | Adalbert | 0..1 |

**Example**:

```turtle
ex:subscription a adalbert:Subscription ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    adalbert:subscribesTo ex:contract ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:analyticsTeam ;
    adalbert:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime ;
    adalbert:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
```

### 3.4 adalbert:RuntimeReference

| Property | Value |
|----------|-------|
| **Type** | `owl:Class` |
| **Label** | Runtime Reference |
| **Definition** | Value resolved at evaluation time |

**Individuals**:

| Individual | Types | Definition |
|------------|-------|------------|
| `adalbert:currentAgent` | `adalbert:RuntimeReference`, `odrl:Party` | The requesting agent (resolved at evaluation time) |
| `adalbert:currentDateTime` | `odrl:LeftOperand`, `adalbert:RuntimeReference` | Evaluation timestamp (mapped to `odrl:dateTime`) |

---

## 4. Property Definitions

### 4.1 adalbert:state

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:Duty` | `adalbert:DataContract` | `adalbert:Subscription` |
| **Range** | `adalbert:State` |
| **Cardinality** | 0..1 |
| **Definition** | Current lifecycle state |

### 4.2 adalbert:deadline

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

### 4.3 adalbert:recurrence

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `odrl:Duty` |
| **Range** | `xsd:string` |
| **Cardinality** | 0..1 |
| **Pattern** | `^FREQ=(SECONDLY|MINUTELY|HOURLY|DAILY|WEEKLY|MONTHLY|YEARLY)` |
| **Definition** | RFC 5545 RRULE defining when duty instances are generated |

Each generated instance follows the standard duty lifecycle independently (Pending -> Active -> Fulfilled/Violated). The `deadline` property defines the per-instance fulfillment window. Any iCal-compliant library can parse the value.

### 4.4 adalbert:subscribesTo

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `adalbert:Subscription` |
| **Range** | `adalbert:DataContract` |
| **Cardinality** | 1 |
| **Definition** | The contract this subscription activates |

### 4.5 adalbert:effectiveDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `adalbert:DataContract` | `adalbert:Subscription` |
| **Range** | `xsd:dateTime` |
| **Cardinality** | 0..1 |
| **Definition** | When the contract/subscription becomes effective |

### 4.6 adalbert:expirationDate

| Property | Value |
|----------|-------|
| **Type** | `owl:DatatypeProperty` |
| **Domain** | `adalbert:DataContract` | `adalbert:Subscription` |
| **Range** | `xsd:dateTime` |
| **Cardinality** | 0..1 |
| **Definition** | When the contract/subscription expires |

### 4.7 adalbert:partOf

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty`, `owl:TransitiveProperty` |
| **SubPropertyOf** | `odrl:partOf` |
| **Domain** | `odrl:Asset` |
| **Range** | `odrl:Asset` |
| **Cardinality** | 0..* |
| **Definition** | Asset contained in a larger asset |

Transitive: if table `partOf` schema and schema `partOf` database, then table `partOf` database. Declared `rdfs:subPropertyOf odrl:partOf` so ODRL processors with RDFS reasoning can interpret Adalbert asset hierarchies.

### 4.8 adalbert:memberOf

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty`, `owl:TransitiveProperty` |
| **SubPropertyOf** | `odrl:partOf` |
| **Domain** | `odrl:Party` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..* |
| **Definition** | Party member of a group or organization |

Transitive: if person `memberOf` team and team `memberOf` division, then person `memberOf` division. Declared `rdfs:subPropertyOf odrl:partOf` so ODRL processors with RDFS reasoning can interpret Adalbert party hierarchies.

### 4.9 adalbert:resolutionPath

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

### 4.10 adalbert:not

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **Domain** | `odrl:LogicalConstraint` |
| **Range** | `odrl:Constraint` | `odrl:LogicalConstraint` |
| **Cardinality** | 0..1 (exactly one of `odrl:and`, `odrl:or`, `adalbert:not` per LogicalConstraint) |
| **Definition** | Logical negation on a constraint |

ODRL defines `odrl:and` and `odrl:or` but lacks negation. Adalbert adds `adalbert:not` following the same pattern.

### 4.11 adalbert:subject

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:assignee` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party bearing the duty (must perform the action) |

The duty bearer. Replaces `odrl:assignee` on duties to avoid role overloading — in a bilateral agreement, the data provider is `odrl:assigner` at the policy level but would also need to be `odrl:assignee` on their own delivery duty. `adalbert:subject` removes this confusion. Bridges to ODRL via `rdfs:subPropertyOf odrl:assignee` (itself a sub-property of `odrl:function`), so ODRL processors with RDFS reasoning can infer `odrl:assignee` from `adalbert:subject`. Aligns with `md:subject` (W3C Market Data) and `rl2:subject`.

### 4.12 adalbert:object

| Property | Value |
|----------|-------|
| **Type** | `owl:ObjectProperty` |
| **SubPropertyOf** | `odrl:function` |
| **Domain** | `odrl:Duty` |
| **Range** | `odrl:Party` |
| **Cardinality** | 0..1 |
| **Definition** | Party affected by the duty action |

The party affected by or receiving the result of the duty action (e.g., who is notified, who receives the report). Bridges to ODRL via `rdfs:subPropertyOf odrl:function`. Aligns with `md:object` (W3C Market Data) and `rl2:counterparty`.

**ODRL Common Vocabulary alternatives**: ODRL defines action-specific party functions that may be more semantically precise than `adalbert:object` in certain cases:

| ODRL Function | Use when... | Example |
|---|---|---|
| `odrl:informedParty` | The duty is to inform/notify a party | Schema change notification |
| `odrl:compensatedParty` | The duty involves compensation | License fee payment |
| `odrl:trackedParty` | The duty involves tracking/monitoring | Usage tracking |
| `odrl:consentingParty` | The duty requires obtaining consent | Data processing consent |

Use `adalbert:object` as the generic alternative when no specific ODRL function fits, or when you prefer consistency across duty types. All are sub-properties of `odrl:function`.

---

## 5. DUE Vocabulary Summary

The DUE profile (`profiles/adalbert-due.ttl`) provides the complete data governance vocabulary.

### 5.1 Operand Categories

| Category | Operands | Resolution Root |
|----------|----------|-----------------|
| **Purpose** | `odrl:purpose` | `context.purpose` |
| **Classification** | `adalbert-due:classification`, `adalbert-due:sensitivity` | `asset.*` |
| **Asset metadata** | `adalbert-due:assetClass`, `adalbert-due:market`, `adalbert-due:isBenchmark` | `asset.*` |
| **Jurisdiction** | `adalbert-due:jurisdiction`, `adalbert-due:residency` | `context.*`, `asset.*` |
| **Temporal** | `adalbert-due:retentionPeriod`, `adalbert-due:expiry` | `asset.*` |
| **Processing** | `adalbert-due:processingMode` | `context.processingMode` |
| **Audit** | `adalbert-due:auditRequired` | `asset.auditRequired` |
| **Identity** | `adalbert-due:role`, `adalbert-due:organization`, `adalbert-due:costCenter`, `adalbert-due:project`, `adalbert-due:recipientType` | `agent.*`, `context.*` |
| **Environment** | `adalbert-due:environment`, `adalbert-due:network` | `context.*` |
| **Timeliness** | `adalbert-due:timeliness`, `adalbert-due:delayMinutes` | `asset.*` |
| **Legal basis** | `adalbert-due:legalBasis`, `adalbert-due:consentId` | `context.*` |
| **Access pattern** | `adalbert-due:accessPattern`, `adalbert-due:volumeLimit`, `adalbert-due:rateLimit` | `context.*` |
| **Derivation** | `adalbert-due:derivationType` | `context.derivationType` |

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
| `adalbert-due:nonDisplay` | Automated/programmatic use | `includedIn odrl:use` |
| `adalbert-due:conformTo` | Conform to a schema or spec | No parent (duty-only governance action) |
| `adalbert-due:log` | Log access to the asset | `includedIn odrl:inform` |
| `adalbert-due:notify` | Notify relevant parties | `includedIn odrl:inform` |
| `adalbert-due:report` | Submit usage reports | `includedIn odrl:inform` |
| `adalbert-due:deliver` | Deliver data to consumer | `includedIn odrl:distribute` |
| `adalbert-due:calculateIndex` | Use for index calculation | `includedIn odrl:derive` |
| `adalbert-due:algorithmicTrading` | Use for automated trading | `includedIn adalbert-due:nonDisplay` |
| `adalbert-due:query` | Query/select data | `includedIn odrl:read` |
| `adalbert-due:export` | Export data outside system | `includedIn odrl:distribute` |
| `adalbert-due:copy` | Copy data to another location | `includedIn odrl:reproduce` |
| `adalbert-due:link` | Link/join with other datasets | `includedIn odrl:aggregate` |
| `adalbert-due:profile` | Create profiles from data | `includedIn odrl:derive` |

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
| Access pattern | `batch`, `streaming`, `interactive`, `api` |
| Derivation type | `commingled`, `nonSubstitutive`, `newProduct` |

---

## 6. SHACL Constraints Summary

Shapes are defined in `ontology/adalbert-shacl.ttl`. Key constraints:

### Policy-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `adalbertsh:PolicyShape` | `odrl:Policy` | Must declare `odrl:profile` (for engines with RDFS inference) |
| `adalbertsh:SetShape` | `odrl:Set` | Must declare `odrl:profile`; at least one `odrl:target`; at least one clause |
| `adalbertsh:OfferShape` | `odrl:Offer` | Must declare `odrl:profile`; exactly one `odrl:assigner`; at least one clause |
| `adalbertsh:AgreementShape` | `odrl:Agreement` | Must declare `odrl:profile`; exactly one `odrl:assigner` and one `odrl:assignee`; at least one clause |

### Rule-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `adalbertsh:PermissionShape` | `odrl:Permission` | Exactly one `odrl:action`; at most one `odrl:target` (inherited from policy if absent) |
| `adalbertsh:ProhibitionShape` | `odrl:Prohibition` | Exactly one `odrl:action`; at most one `odrl:target` (inherited from policy if absent) |
| `adalbertsh:DutyShape` | `odrl:Duty` | Exactly one `odrl:action`; `subject` 0..1; `object` 0..1; `deadline` 0..1 (dateTime/duration); `recurrence` 0..1 (RRULE pattern); `state` 0..1 |

### Constraint-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `adalbertsh:ConstraintShape` | `odrl:Constraint` | Exactly one `leftOperand`, `operator`, and at least one `rightOperand` |
| `adalbertsh:LogicalConstraintShape` | `odrl:LogicalConstraint` | Exactly one of: `odrl:and`, `odrl:or`, or `adalbert:not` |

### Contract-level shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `adalbertsh:DataContractShape` | `adalbert:DataContract` | Must declare `odrl:profile`; exactly one `odrl:assigner`; at least one clause; `state` 0..1; effective/expiration dates 0..1 |
| `adalbertsh:SubscriptionShape` | `adalbert:Subscription` | Must declare `odrl:profile`; exactly one `adalbert:subscribesTo` (must be `adalbert:DataContract`); at least one clause; `state` 0..1; effective/expiration dates 0..1 |

### Operand shapes

| Shape | Target | Key Constraints |
|-------|--------|-----------------|
| `adalbertsh:LeftOperandShape` | `odrl:LeftOperand` | `resolutionPath` 0..1; must start with `agent.`, `asset.`, or `context.` |
| `adalbertsh:DUEOperandShape` | All 26 DUE operands | Exactly one `resolutionPath` (pattern: `agent.\|asset.\|context.`) |

### Rejection shapes

| Shape | Rejects | Message |
|-------|---------|---------|
| `adalbertsh:RejectXoneShape` | `odrl:xone` | Not supported in Adalbert |
| `adalbertsh:RejectRemedyShape` | `odrl:remedy` | Deferred to RL2 |
| `adalbertsh:RejectConsequenceShape` | `odrl:consequence` | Deferred to RL2 |
| `adalbertsh:RejectTicketShape` | `odrl:Ticket` | Not supported |
| `adalbertsh:RejectRequestShape` | `odrl:Request` | Not supported |
| `adalbertsh:RejectAssetCollectionShape` | `odrl:AssetCollection` | Use `adalbert:partOf` instead |
| `adalbertsh:RejectPartyCollectionShape` | `odrl:PartyCollection` | Use `adalbert:memberOf` instead |
| `adalbertsh:RejectInheritAllowedShape` | `odrl:inheritAllowed` | Not supported |
| `adalbertsh:RejectInheritFromShape` | `odrl:inheritFrom` | Not supported |

---

## 7. Property Usage Matrix

Which Adalbert properties are valid on which classes:

| Property | Duty | DataContract | Subscription | LeftOperand | LogicalConstraint | Asset | Party |
|----------|------|-------------|-------------|-------------|-------------------|-------|-------|
| `adalbert:state` | Yes | Yes | Yes | | | | |
| `adalbert:deadline` | Yes | | | | | | |
| `adalbert:recurrence` | Yes | | | | | | |
| `adalbert:subject` | Yes | | | | | | |
| `adalbert:object` | Yes | | | | | | |
| `adalbert:subscribesTo` | | | Yes | | | | |
| `adalbert:effectiveDate` | | Yes | Yes | | | | |
| `adalbert:expirationDate` | | Yes | Yes | | | | |
| `adalbert:resolutionPath` | | | | Yes | | | |
| `adalbert:not` | | | | | Yes | | |
| `adalbert:partOf` | | | | | | Yes | |
| `adalbert:memberOf` | | | | | | | Yes |

---

## 8. Profile Constraints

Adalbert restricts certain ODRL features:

| Feature | Status | Reason |
|---------|--------|--------|
| `odrl:conflict` | Fixed to `odrl:prohibit` at profile level | Deterministic conflict resolution; declared once in `adalbert-prof.ttl` |
| `odrl:xone` | Rejected | Deferred to RL2 |
| `odrl:remedy` | Rejected | Deferred to RL2 |
| `odrl:consequence` | Rejected | Deferred to RL2 |
| `odrl:Ticket` | Not used | Not applicable to data governance |
| `odrl:Request` | Not used | Not applicable |
| `odrl:assignee` (on Duty) | Replaced by `adalbert:subject` | `adalbert:subject rdfs:subPropertyOf odrl:assignee` — avoids role overloading |
| `odrl:AssetCollection` | Not used | Use `adalbert:partOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |
| `odrl:PartyCollection` | Not used | Use `adalbert:memberOf` hierarchy instead (`rdfs:subPropertyOf odrl:partOf` bridges to ODRL) |

---

**Version**: 0.7 | **Date**: 2026-02-04
