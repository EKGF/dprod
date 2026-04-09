# DPROD Contracts Term Mapping

Maps business language to DPROD/ODRL vocabulary. Includes complete DCON -> DPROD migration mapping.

---

## 1. How to Use This Document

This document bridges the gap between business terminology and the technical ODRL/DPROD vocabulary. Each section covers a category of terms. For each term you will find:

- **Business term**: what people say in conversation
- **DPROD property**: the RDF property or class to use
- **Used on**: which policy elements this applies to
- **Cardinality**: how many values are allowed
- **Source**: whether the term comes from ODRL or DPROD
- **DCON equivalent**: for migration reference

For the formal vocabulary reference, see [specification.md](specification.md). For authoring guidance, see [contracts-guide.md](contracts-guide.md) or [policy-writers-guide.md](policy-writers-guide.md).

---

## 2. Contract Metadata

### Contract Title

**Business term:** `title`, `contract name`, `policy name`
**DPROD property:** `rdfs:label`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`, `odrl:Set`
**Cardinality:** 0..1
**Source:** RDFS
**Example:**
```turtle
ex:contract a dprod:DataOffer ;
    rdfs:label "Market Price Data Contract v2" .
```
**DCON equivalent:** `rdfs:label` (same)

### Contract Description

**Business term:** `description`, `summary`
**DPROD property:** `dct:description`
**Used on:** Any policy
**Cardinality:** 0..1
**Source:** Dublin Core

### Contract Version

**Business term:** `version`, `revision`
**DPROD property:** `prov:wasRevisionOf`
**Used on:** `dprod:DataOffer`
**Cardinality:** 0..1
**Source:** W3C PROV
**Example:**
```turtle
ex:contract-v2 a dprod:DataOffer ;
    prov:wasRevisionOf ex:contract-v1 .
```
**DCON equivalent:** `prov:wasRevisionOf` (same)

### Contract Status

**Business term:** `status`, `state`, `lifecycle state`
**DPROD property:** `dprod:state`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`, `odrl:Duty`
**Cardinality:** 0..1
**Values:** `dprod:Pending`, `dprod:Active`, `dprod:Fulfilled`, `dprod:Violated`
**Source:** DPROD
**DCON equivalent:** `dcon:contractState` (partial; DCON also had Draft/Published which are not modeled)

---

## 3. Temporal Properties

### Effective Date

**Business term:** `start date`, `effective date`, `goes live`
**DPROD property:** `dprod:effectiveDate`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`
**Cardinality:** 0..1
**Datatype:** `xsd:dateTime`
**Source:** DPROD
**Example:**
```turtle
ex:subscription dprod:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime .
```
**DCON equivalent:** `dcon:effectiveDate`

### Expiration Date

**Business term:** `end date`, `expiry`, `contract end`
**DPROD property:** `dprod:expirationDate`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`
**Cardinality:** 0..1
**Datatype:** `xsd:dateTime`
**Source:** DPROD
**DCON equivalent:** `dcon:expirationDate`

### Deadline

**Business term:** `due date`, `SLA window`, `fulfillment deadline`
**DPROD property:** `dprod:deadline`
**Used on:** `odrl:Duty`
**Cardinality:** 0..1
**Datatype:** `xsd:dateTime` | `xsd:duration`
**Source:** DPROD
**Example:**
```turtle
# Absolute deadline
dprod:deadline "2026-12-31T23:59:59Z"^^xsd:dateTime .

# Relative deadline (30 days from activation)
dprod:deadline "P30D"^^xsd:duration .
```
**DCON equivalent:** `dcon:hasTerminationClause` (partial)

### Recurrence Schedule

**Business term:** `schedule`, `frequency`, `how often`
**DPROD property:** `dprod:recurrence`
**Used on:** `odrl:Duty`
**Cardinality:** 0..1
**Datatype:** `xsd:string` (RFC 5545 RRULE)
**Source:** DPROD
**Example:**
```turtle
dprod:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" .
```
**DCON equivalent:** `dcon:hasSchedule` + `dcon:icalRule` (two properties collapsed into one)

---

## 4. Parties and Responsibility

### Contract Provider

**Business term:** `provider`, `data provider`, `data owner`, `publisher`
**DPROD property:** `odrl:assigner`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`
**Cardinality:** 1 (required)
**Source:** ODRL
**Example:**
```turtle
ex:contract a dprod:DataOffer ;
    odrl:assigner ex:dataTeam .
```
**DCON equivalent:** `odrl:assigner` (same)

### Contract Consumer

**Business term:** `consumer`, `subscriber`, `data consumer`, `client`
**DPROD property:** `odrl:assignee`
**Used on:** `dprod:DataContract` (required), `odrl:Permission`/`odrl:Duty` (optional)
**Cardinality:** 1 on DataContract; 0..1 on rules
**Source:** ODRL
**Example:**
```turtle
ex:subscription a dprod:DataContract ;
    odrl:assignee ex:analyticsTeam .
```
**DCON equivalent:** `dcon:subscriber` -> `odrl:assignee`

### Duty Holder

**Business term:** `responsible party`, `obligee`, `who must do it`
**DPROD property:** `dprod:subject` (on `odrl:Duty`)
**Used on:** `odrl:Duty`
**Cardinality:** 0..1
**Source:** DPROD (`rdfs:subPropertyOf odrl:assignee`)
**Note:** In a DataOffer (Offer), provider duties have `dprod:subject` set to the provider. Consumer duties omit `dprod:subject` -- it is filled in when the DataContract is created.
**DCON equivalent:** `dcon:promisor`

### Party Hierarchy

**Business term:** `team membership`, `department`, `division`
**DPROD property:** `dprod:memberOf`
**Used on:** `odrl:Party`
**Cardinality:** 0..*
**Source:** DPROD
**Example:**
```turtle
ex:analyst a odrl:Party ;
    dprod:memberOf ex:analyticsTeam .
ex:analyticsTeam a odrl:Party ;
    dprod:memberOf ex:tradingDivision .
```

---

## 5. Assets

### Target Asset

**Business term:** `data`, `dataset`, `covered data`, `target`
**DPROD property:** `odrl:target`
**Used on:** Policies, `odrl:Permission`, `odrl:Duty`, `odrl:Prohibition`
**Cardinality:** 1..* on policies; 1 on rules
**Source:** ODRL
**Example:**
```turtle
ex:contract odrl:target ex:marketPrices .
```
**DCON equivalent:** `odrl:target` (same)

### Asset Hierarchy

**Business term:** `part of`, `contained in`, `sub-asset`
**DPROD property:** `dprod:partOf`
**Used on:** `odrl:Asset`
**Cardinality:** 0..*
**Source:** DPROD
**Example:**
```turtle
ex:priceTable a odrl:Asset ;
    dprod:partOf ex:marketDataSchema .
ex:marketDataSchema a odrl:Asset ;
    dprod:partOf ex:marketDataLake .
```

---

## 6. Obligations

### Delivery SLA

**Business term:** `data delivery`, `SLA`, `timeliness guarantee`
**DPROD pattern:** `odrl:Duty` with `ex:deliver` + `dprod:recurrence` + `dprod:deadline`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subject ex:dataTeam ;
    odrl:action ex:deliver ;
    odrl:target ex:marketPrices ;
    dprod:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
    dprod:deadline "PT30M"^^xsd:duration
] .
```
**DCON equivalent:** `dcon:ProviderTimelinessPromise`

### Schema Conformance

**Business term:** `schema guarantee`, `data quality SLA`, `format compliance`
**DPROD pattern:** `odrl:Duty` with `ex:conformTo`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subject ex:dataTeam ;
    odrl:action ex:conformTo ;
    odrl:target ex:marketDataSchema
] .
```
**DCON equivalent:** `dcon:ProviderSchemaPromise`

### Quality SLA

**Business term:** `quality guarantee`, `accuracy SLA`, `data quality commitment`
**DPROD pattern:** `odrl:Duty` with `ex:conformTo` + `odrl:constraint`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subject ex:dataTeam ;
    odrl:action ex:conformTo ;
    odrl:target ex:riskMetricsSchema ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand ex:timeliness ;
        odrl:operator odrl:eq ;
        odrl:rightOperand ex:realtime
    ]
] .
```
**DCON equivalent:** `dcon:ProviderQualityPromise`

### Change Notification

**Business term:** `notification`, `advance notice`, `change alert`
**DPROD pattern:** `odrl:Duty` with `ex:notify` + `dprod:deadline`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subject ex:dataTeam ;
    odrl:action ex:notify ;
    odrl:target ex:schemaChanges ;
    dprod:deadline "P14D"^^xsd:duration
] .
```
**DCON equivalent:** `dcon:ProviderChangeNotificationPromise`

### Usage Reporting

**Business term:** `usage report`, `consumption report`
**DPROD pattern:** `odrl:Duty` with `ex:report` + `dprod:deadline`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    odrl:action ex:report ;
    odrl:target ex:usageStats ;
    dprod:deadline "P30D"^^xsd:duration
] .
```
**DCON equivalent:** `dcon:ConsumerUsageReportingPromise` (implied)

---

## 7. Rights and Restrictions

### Display Permission

**Business term:** `can view`, `display rights`, `screen display`
**DPROD property:** `odrl:display` (action on `odrl:Permission`)
**DCON equivalent:** `odrl:display` (same)

### Non-Display Permission

**Business term:** `algorithmic use`, `automated use`, `programmatic access`
**DPROD property:** `ex:nonDisplay` (action on `odrl:Permission`)
**Note:** Distinct from `odrl:display`. Covers models, automation, calculations.

### Derivation Permission

**Business term:** `can create derived data`, `derivation rights`
**DPROD property:** `odrl:derive` (action on `odrl:Permission`)
**DCON equivalent:** `odrl:derive` (same)

### Distribution Prohibition

**Business term:** `no redistribution`, `no sharing outside`
**DPROD property:** `odrl:distribute` (action on `odrl:Prohibition`)
**DCON equivalent:** Prohibition with `odrl:distribute`

### Constrained Permission

**Business term:** `can do X if Y`, `conditional access`
**DPROD pattern:** Permission with `odrl:constraint`
**Example:**
```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:action odrl:read ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand odrl:purpose ;
        odrl:operator odrl:eq ;
        odrl:rightOperand ex:analytics
    ]
] .
```

---

## 8. State and Lifecycle

### Duty States

| State | Business meaning | DPROD value |
|-------|-----------------|-------------|
| Not started | Condition not yet met | `dprod:Pending` |
| In progress | Action required, deadline ticking | `dprod:Active` |
| Done | Successfully completed | `dprod:Fulfilled` |
| Breached | Deadline passed without completion | `dprod:Violated` |

### Contract States

| State | Business meaning | DPROD value |
|-------|-----------------|-------------|
| Not yet active | Effective date not reached | `dprod:Pending` |
| Live | In force, duties being tracked | `dprod:Active` |
| Complete | All obligations met | `dprod:Fulfilled` |
| Breached | Material obligation violated | `dprod:Violated` |

**Note:** DCON's `Draft` and `Published` are pre-normative workflow metadata. DPROD does not model them -- they belong to the authoring system, not policy evaluation.

---

## 9. Quick Reference Table

| Business Term | DPROD Property / Pattern | Source |
|--------------|--------------------------|--------|
| Contract title | `rdfs:label` | RDFS |
| Provider | `odrl:assigner` | ODRL |
| Consumer | `odrl:assignee` | ODRL |
| Covered data | `odrl:target` | ODRL |
| Start date | `dprod:effectiveDate` | DPROD |
| End date | `dprod:expirationDate` | DPROD |
| Status | `dprod:state` | DPROD |
| Delivery SLA | Duty + `deliver` + `recurrence` + `deadline` | DPROD |
| Schema guarantee | Duty + `conformTo` | DPROD |
| Quality SLA | Duty + `conformTo` + constraint | DPROD |
| Change notice | Duty + `notify` + `deadline` | DPROD |
| Usage report | Duty + `report` + `deadline` | DPROD |
| View rights | Permission + `display` | ODRL |
| Algo use | Permission + `nonDisplay` | DPROD |
| Derivation | Permission + `derive` | ODRL |
| No sharing | Prohibition + `distribute` | ODRL |
| Team membership | `dprod:memberOf` | DPROD |
| Data hierarchy | `dprod:partOf` | DPROD |
| Version chain | `prov:wasRevisionOf` | W3C PROV |
| Schedule | `dprod:recurrence` (RRULE) | DPROD |
| Deadline | `dprod:deadline` | DPROD |
| Contract link | `dprod:acceptsOffer` | DPROD |

---

## 10. DCON -> DPROD Migration

Complete mapping of every DCON term to its DPROD equivalent.

### 10.1 Classes

| DCON Class | DPROD Equivalent | Status | Notes |
|------------|------------------|--------|-------|
| `dcon:DataContract` | `dprod:DataOffer` | Direct | Subclass of `odrl:Offer` |
| `dcon:DataContractSubscription` | `dprod:DataContract` | Direct | Subclass of `odrl:Agreement` |
| `dcon:Promise` | `odrl:Duty` | Dissolved | All obligations are duties |
| `dcon:ProviderPromise` | `odrl:Duty` + DPROD action | Dissolved | Action differentiates duty type |
| `dcon:ProviderTimelinessPromise` | Duty + `deliver` + `recurrence` + `deadline` | Pattern | Schedule + window replaces delivery time |
| `dcon:ProviderSchemaPromise` | Duty + `conformTo` | Pattern | Schema conformance duty |
| `dcon:ProviderChangeNotificationPromise` | Duty + `notify` + `deadline` | Pattern | Deadline as duration for lead time |
| `dcon:ProviderQualityPromise` | Duty + `conformTo` + constraint | Pattern | Quality constraints on conformance duty |
| `dcon:ConsumerPromise` | `odrl:Duty` (assignee duty) | Dissolved | Standard ODRL duty |
| `dcon:Schedule` | `dprod:recurrence` value | Simplified | Single RRULE string, not a class |
| `dcon:ICalSchedule` | `dprod:recurrence` value | Absorbed | RRULE is the iCal format |
| `dcon:PromiseState` | `dprod:State` | Extended | 4 states (adds Pending) vs DCON's 3 |
| `dcon:Condition` | `odrl:Constraint` | Standard | Use ODRL directly |
| `dcon:ContractStatus` (Draft/Active/Retired/Cancelled) | -- | Not modeled | Pre-normative workflow metadata |

### 10.2 Properties

| DCON Property | DPROD Equivalent | Status | Notes |
|---------------|------------------|--------|-------|
| `dcon:provider` | `odrl:assigner` | Standard | ODRL term |
| `dcon:subscriber` | `odrl:assignee` | Standard | ODRL term |
| `dcon:contractState` | `dprod:state` | Direct | Unified 4-state lifecycle |
| `dcon:effectiveDate` | `dprod:effectiveDate` | Direct | Same semantics |
| `dcon:expirationDate` | `dprod:expirationDate` | Direct | Same semantics |
| `dcon:subscribesTo` | `dprod:acceptsOffer` | Direct | Same semantics |
| `dcon:promisedDeliveryTime` | `dprod:recurrence` + `dprod:deadline` | Simplified | Schedule + window |
| `dcon:notificationLeadTime` | `dprod:deadline` (as `xsd:duration`) | Simplified | Duration value |
| `dcon:promisor` | `dprod:subject` (on Duty) | DPROD | `rdfs:subPropertyOf odrl:assignee` |
| `dcon:promisee` | Implicit (other party) | Not needed | Bilateral agreement handles this |
| `dcon:promiseContent` | `odrl:action` (on Duty) | Standard | ODRL term |
| `dcon:promiseState` | `dprod:state` | Direct | Unified lifecycle |
| `dcon:fulfillsPromise` | `prov:wasDerivedFrom` (on DataContract) | Standard | W3C PROV |
| `dcon:hasPromise` | `odrl:obligation` | Standard | ODRL term |
| `dcon:hasContract` | `dcat:hasPolicy` (external systems) | External | Not policy semantics |
| `dcon:hasEffectivePeriod` | `dprod:effectiveDate` + `dprod:expirationDate` | Simplified | Two dates instead of period object |
| `dcon:hasTerminationClause` | `dprod:deadline` (as duration) | Simplified | Duration on duty |
| `dcon:hasSchedule` | `dprod:recurrence` | Simplified | Single property |
| `dcon:icalRule` | `dprod:recurrence` value | Absorbed | RRULE string is the value |

### 10.3 Actions

| DCON Action | DPROD Equivalent | Status |
|-------------|------------------|--------|
| `dcon:deliver` | `ex:deliver` | Direct |
| `dcon:maintain` (schema) | `ex:conformTo` | Renamed |
| `dcon:notify` | `ex:notify` | Direct |
| `dcon:report` (implied) | `ex:report` | Direct |

### 10.4 Not Modeled (by design)

These DCON concepts are intentionally not modeled in DPROD Contracts, with rationale:

| DCON Concept | Reason Not Modeled |
|--------------|--------------------|
| `dcon:Draft` / `dcon:Retired` / `dcon:Cancelled` | Pre-normative workflow metadata, not policy semantics. Belongs to authoring system. |
| `dcon:promiseContent` (as class) | Dissolved into `odrl:action` on duties. Actions provide the semantic differentiation. |
| `dcon:fulfillsPromise` (as property) | Replaced by `prov:wasDerivedFrom` on DataContract. Standard W3C provenance. |
| `dcon:hasContract` | External relationship. Systems use `dcat:hasPolicy` to link datasets to policies. |
| `dcon:Condition` (as class) | Use `odrl:Constraint` directly. Standard ODRL. |
| `schema:Schedule` format | DPROD uses RRULE string only. Single property instead of class hierarchy. |
| Promise/ProviderPromise hierarchy | Dissolved into `odrl:Duty` patterns. DPROD actions differentiate duty types. |
| Promise Theory semantics (ought-to-be) | Duties suffice for DPROD's scope. Future extensions may add full Promise support for voluntary cooperation. |
| `dcat:Distribution` integration | Use DCAT directly outside policies. Not policy semantics. |
| Contract billing | Operational concern, out of scope for policy evaluation. |

### 10.5 Migration Checklist

When migrating a DCON contract to DPROD Contracts:

1. Change `dcon:DataContract` -> `dprod:DataOffer`
2. Change `dcon:DataContractSubscription` -> `dprod:DataContract`
3. Add `odrl:profile <https://ekgf.github.io/dprod/>` declaration
4. Replace promise subclasses with `odrl:Duty` + DPROD action (see table above)
5. Replace `dcon:promisor` with `dprod:subject` on duties
6. Replace `dcon:hasSchedule`/`dcon:icalRule` with `dprod:recurrence`
7. Map `dcon:contractState` to `dprod:state`
8. Validate against SHACL shapes: `shacl validate --shapes dprod-contracts-shapes.ttl --data migrated.ttl`

---

**Version**: 0.7 | **Date**: 2026-02-04
