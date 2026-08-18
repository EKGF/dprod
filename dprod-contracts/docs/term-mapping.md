# DPROD Contracts Term Mapping

Maps business language to DPROD/ODRL vocabulary.

---

## 1. How to Use This Document

This document bridges the gap between business terminology and the technical ODRL/DPROD vocabulary. Each section covers a category of terms. For each term you will find:

- **Business term**: what people say in conversation
- **DPROD property**: the RDF property or class to use
- **Used on**: which policy elements this applies to
- **Cardinality**: how many values are allowed
- **Source**: whether the term comes from ODRL or DPROD

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

### Lifecycle Status and Duty State

**Business term:** `status`, `lifecycle status`
**DPROD status properties:**
- `dprod:dataProductLifecycleStatus` on `dprod:DataProduct` (authored)
- `dprod:offerLifecycleStatus` on `dprod:DataOffer` (administrative)
- `dprod:contractLifecycleStatus` on `dprod:DataContract` (administrative)
**Cardinality:** 0..1 each
**Super-property:** `dprod:lifecycleStatus`
**Range:** `skos:Concept`. DPROD schemes are optional; enterprises MAY supply their own SKOS taxonomies.

**Business term:** `duty state`
**DPROD state property:** `dprod:dutyState` on `odrl:Duty` (evaluator-computed at runtime)
**Cardinality:** 0..1
**Range:** `skos:Concept`. The standard evaluation algorithm transitions between `dprod:Pending`, `dprod:Active`, `dprod:Fulfilled`, and `dprod:Violated`.

`dprod:dutyState` is not a sub-property of `dprod:lifecycleStatus`: state is computed, while lifecycle status is authored.
**Source:** DPROD
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

### Expiration Date

**Business term:** `end date`, `expiry`, `contract end`
**DPROD property:** `dprod:expirationDate`
**Used on:** `dprod:DataOffer`, `dprod:DataContract`
**Cardinality:** 0..1
**Datatype:** `xsd:dateTime`
**Source:** DPROD

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

### Schedule

**Business term:** `schedule`, `frequency`, `how often`
**DPROD property:** `dprod:schedule`
**Used on:** Any resource whose meaning includes scheduled occurrences; duties use 0..1
**Value:** IRI of a `dprod:Schedule`
**Source:** DPROD
**Example:**
```turtle
ex:daily-0600-london a dprod:Schedule ;
    dct:conformsTo dprod:Rfc5545ScheduleFormat ;
    dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260101T060000\nRRULE:FREQ=DAILY" .

ex:deliveryDuty dprod:schedule ex:daily-0600-london .
```

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

### Duty Holder

**Business term:** `responsible party`, `obligee`, `who must do it`
**DPROD property:** `dprod:subjectOfDuty` (on `odrl:Duty`)
**Used on:** `odrl:Duty`
**Cardinality:** 0..1
**Source:** DPROD (`rdfs:subPropertyOf odrl:function`)
**Note:** In a DataOffer (Offer), provider duties have `dprod:subjectOfDuty` set to the provider. Consumer duties omit `dprod:subjectOfDuty` -- it is filled in when the DataContract is created.
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
**DPROD pattern:** `odrl:Duty` with `ex:deliver` + `dprod:schedule` + `dprod:deadline`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:deliver ;
    odrl:target ex:marketPrices ;
    dprod:schedule ex:daily-0600-london ;
    dprod:deadline "PT30M"^^xsd:duration
] .
```

### Schema Conformance

**Business term:** `schema guarantee`, `data quality SLA`, `format compliance`
**DPROD pattern:** `odrl:Duty` with `ex:conformTo`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:conformTo ;
    odrl:target ex:marketDataSchema
] .
```

### Quality SLA

**Business term:** `quality guarantee`, `accuracy SLA`, `data quality commitment`
**DPROD pattern:** `odrl:Duty` with `ex:conformTo` + `odrl:constraint`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
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

### Change Notification

**Business term:** `notification`, `advance notice`, `change alert`
**DPROD pattern:** `odrl:Duty` with `ex:notify` + `dprod:deadline`
**Example:**
```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:notify ;
    odrl:target ex:schemaChanges ;
    dprod:deadline "P14D"^^xsd:duration
] .
```

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

---

## 7. Rights and Restrictions

### Display Permission

**Business term:** `can view`, `display rights`, `screen display`
**DPROD property:** `odrl:display` (action on `odrl:Permission`)

### Non-Display Permission

**Business term:** `algorithmic use`, `automated use`, `programmatic access`
**DPROD property:** `ex:nonDisplay` (action on `odrl:Permission`)
**Note:** Distinct from `odrl:display`. Covers models, automation, calculations.

### Derivation Permission

**Business term:** `can create derived data`, `derivation rights`
**DPROD property:** `odrl:derive` (action on `odrl:Permission`)

### Distribution Prohibition

**Business term:** `no redistribution`, `no sharing outside`
**DPROD property:** `odrl:distribute` (action on `odrl:Prohibition`)

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
| Status (data product) | `dprod:dataProductLifecycleStatus` (`skos:Concept`) | DPROD |
| Status (offer) | `dprod:offerLifecycleStatus` (`skos:Concept`) | DPROD |
| Status (contract) | `dprod:contractLifecycleStatus` (`skos:Concept`) | DPROD |
| State (duty) | `dprod:dutyState` (`skos:Concept`) | DPROD |
| Delivery SLA | Duty + `deliver` + `schedule` + `deadline` | DPROD |
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
| Schedule | `dprod:schedule` → identified `dprod:Schedule` | DPROD |
| Deadline | `dprod:deadline` | DPROD |
| Contract link | `dprod:acceptsOffer` | DPROD |

---

**Version**: 0.7 | **Date**: 2026-08-12
