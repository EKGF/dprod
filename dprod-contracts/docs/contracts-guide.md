# DPROD Contracts Guide

A guide for data platform teams using DPROD for data contracts and subscriptions.

---

## Overview

DPROD models internal data sharing agreements as ODRL 2.2 policies. A **DataOffer** is an offer from a data provider. A **DataContract** is an activated offer binding provider and consumer.

```
DataOffer (Offer)          DataContract (Agreement)
+--------------------------+  +--------------------------+
| Provider duties          |  | Provider duties          |
| Consumer rights          |  | Consumer rights          |
| Prohibitions             |  | Consumer duties          |
| Schedule rules           |  | Prohibitions             |
+--------------------------+  | Status + duty state      |
              accept          +--------------------------+
            -------->
```

---

## Key Concepts

### DataOffer (Offer)

A `dprod:DataOffer` is a subclass of `odrl:Offer`. It specifies:

- **Provider** (`odrl:assigner`): the data team providing data
- **Target** (`odrl:target`): the data asset(s) covered -- inherited by rules unless overridden
- **Provider duties** (`odrl:obligation` with `dprod:subjectOfDuty` = provider): SLAs like delivery, notification, schema conformance
- **Consumer permissions** (`odrl:permission`): what consumers can do with the data
- **Consumer duties** (`odrl:obligation` without subject in Offer): obligations consumers accept upon subscribing
- **Prohibitions** (`odrl:prohibition`): what consumers cannot do

### DataContract (Agreement)

A `dprod:DataContract` is a subclass of `odrl:Agreement`. It adds:

- **Consumer** (`odrl:assignee`): the subscribing team
- **Effective/expiration dates**: contract period
- **Lifecycle status**: authored administrative status of the contract
- **Duty state**: evaluator-computed state of each obligation

### Provider Duties

Provider duties use DPROD actions:

| Action | Description | Example |
|--------|-------------|---------|
| `ex:deliver` | Deliver data to consumers | Daily market data delivery |
| `ex:notify` | Send notifications | Schema change notification |
| `ex:conformTo` | Maintain conformance to a standard | Schema/quality SLA |

### Consumer Duties

| Action | Description | Example |
|--------|-------------|---------|
| `ex:report` | Submit usage reports | Monthly usage reporting |

### Permissions

Standard ODRL actions apply:

| Action | Description |
|--------|-------------|
| `odrl:display` | Display data |
| `ex:nonDisplay` | Non-display (algorithmic) use |
| `odrl:derive` | Create derived products |
| `odrl:read` | Read data |

---

## Step-by-Step Cookbook

Create your first DataOffer in five steps.

### Step 1: Declare the Contract

Every contract starts with a type, profile declaration, and provider identity.

```turtle
@prefix odrl:     <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://www.omg.org/spec/DPROD/dprod/> .
@prefix dct:      <http://purl.org/dc/terms/> .
@prefix ex:       <https://example.org/> .
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

ex:daily-0600-london a dprod:Schedule ;
    rdfs:label "Daily at 06:00 Europe/London" ;
    dct:conformsTo dprod:Rfc5545ScheduleFormat ;
    dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260101T060000\nRRULE:FREQ=DAILY" .

ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    dprod:offerLifecycleStatus dprod:Active .
```

### Step 2: Add Provider Duties (SLAs)

Provider duties declare what the data team commits to. The provider is identified by `dprod:subjectOfDuty` on each duty. Use `dprod:objectOfDuty` to identify who is affected (e.g., who receives notifications).

Rules inherit `odrl:target` from the policy unless they target a different asset.

```turtle
    # Daily delivery by 06:30 (target inherited from policy)
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:deliver ;
        dprod:schedule ex:daily-0600-london ;
        dprod:deadline "PT30M"^^xsd:duration
    ] ;

    # Schema conformance (different target -- not inherited)
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:conformTo ;
        odrl:target ex:marketDataSchema
    ] ;
```

### Step 3: Add Consumer Permissions

Permissions define what subscribers can do. In an Offer, omit `odrl:assignee` -- it is filled when the subscription is created. Target is inherited from the policy.

```turtle
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;

    odrl:permission [
        a odrl:Permission ;
        odrl:action ex:nonDisplay ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand ex:recipientType ;
            odrl:operator odrl:eq ;
            odrl:rightOperand ex:internal
        ]
    ] ;
```

### Step 4: Add Consumer Duties and Prohibitions

Consumer duties activate upon subscription. Prohibitions apply to all subscribers.

```turtle
    # Consumer must report usage monthly (different target -- not inherited)
    odrl:obligation [
        a odrl:Duty ;
        odrl:action ex:report ;
        odrl:target ex:usageStats ;
        dprod:deadline "P30D"^^xsd:duration
    ] ;

    # No external redistribution (target inherited from policy)
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute
    ] .
```

### Step 5: Create a DataContract

When a consumer accepts the offer, create a DataContract (Agreement) referencing the offer:

```turtle
ex:subscription a dprod:DataContract ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    dprod:acceptsOffer ex:contract ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:analyticsTeam ;
    dprod:effectiveDate "2026-02-01T00:00:00Z"^^xsd:dateTime ;
    dprod:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
```

The contract materializes all duties from the offer with explicit `dprod:subjectOfDuty` on each.

---

## Provider Duty Patterns

### Timeliness Pattern (Delivery SLA)

Scheduled data delivery with a fulfillment window. Target inherited from policy.

```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:deliver ;
    dprod:schedule ex:daily-0600-london ;
    dprod:deadline "PT30M"^^xsd:duration
] .
```


### Schema Pattern (Schema Conformance)

Provider guarantees data conforms to a published schema. Target differs from policy -- specify explicitly.

```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:conformTo ;
    odrl:target ex:marketDataSchema
] .
```

### Notification Pattern (Change Notification)

Provider must notify consumers before making changes, with a lead time expressed as a duration deadline. Use `dprod:objectOfDuty` to identify who is notified.

```turtle
odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    dprod:objectOfDuty ex:consumer ;
    odrl:action ex:notify ;
    odrl:target ex:schemaChanges ;
    dprod:deadline "P14D"^^xsd:duration
] .
```

### Quality SLA Pattern

Provider guarantees data quality via `conformTo` with a constraint.

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

The constraint can check any DPROD operand -- timeliness, classification, environment, etc.

---

## Schedule

`dprod:schedule` links a duty or another DPROD resource to an identified,
reusable `dprod:Schedule`. The Schedule declares exactly one representation
through `dct:conformsTo` and exactly one `dprod:scheduleExpression`. The
referring resource defines what the occurrences mean. On a duty, the Schedule
and `dprod:deadline` define instance generation and the fulfillment window.

```turtle
ex:daily-0600-london a dprod:Schedule ;
    rdfs:label "Daily at 06:00 Europe/London" ;
    dct:conformsTo dprod:Rfc5545ScheduleFormat ;
    dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260101T060000\nRRULE:FREQ=DAILY" .

odrl:obligation [
    a odrl:Duty ;
    dprod:subjectOfDuty ex:dataTeam ;
    odrl:action ex:deliver ;
    dprod:schedule ex:daily-0600-london ;
    dprod:deadline "PT30M"^^xsd:duration
] .
```

This means: deliver market prices daily at 06:00 (target inherited from policy), with a 30-minute window to fulfill.

The built-in formats are `dprod:Rfc5545ScheduleFormat` and
`dprod:PosixCrontabScheduleFormat`. POSIX crontab schedules also declare
`dprod:scheduleTimeZone`, because the five-field expression does not carry a
timezone. RFC 5545 expressions carry their timezone in `TZID`;
`dprod:scheduleTimeZone` is then redundant and, if present, must match the
embedded `TZID`. Extension formats must identify an exact dialect, declare
`dprod:carriesTimeZone` so validators know whether `dprod:scheduleTimeZone`
is required, and provide their own SHACL and processor profile. Unknown or
malformed formats fail validation or processing; they never silently produce
an empty schedule.

### Common RFC 5545 Schedule Expressions

An RFC 5545 `dprod:scheduleExpression` is iCalendar content: a `DTSTART` line
that anchors the first occurrence, the time of day, and the timezone (`TZID`),
followed by an `RRULE` line that defines the recurrence. Optional `EXDATE` /
`RDATE` lines remove or add specific occurrences. Time of day comes from
`DTSTART`, not from `BYHOUR`/`BYMINUTE` rule parts. The `\n` below is the
Turtle escape for the newline separating the lines, as in the example above.

| Pattern | `dprod:scheduleExpression` |
|---------|----------------------------|
| Daily at 06:00 | `DTSTART;TZID=Europe/London:20260101T060000\nRRULE:FREQ=DAILY` |
| Weekly on Monday at 09:00 | `DTSTART;TZID=Europe/London:20260105T090000\nRRULE:FREQ=WEEKLY;BYDAY=MO` |
| Monthly on the 1st | `DTSTART;TZID=Europe/London:20260101T000000\nRRULE:FREQ=MONTHLY;BYMONTHDAY=1` |
| Every 15 minutes | `DTSTART;TZID=Europe/London:20260101T000000\nRRULE:FREQ=MINUTELY;INTERVAL=15` |
| Hourly | `DTSTART;TZID=Europe/London:20260101T000000\nRRULE:FREQ=HOURLY` |
| Daily at 06:00, skipping Christmas Day | `DTSTART;TZID=Europe/London:20260101T060000\nRRULE:FREQ=DAILY\nEXDATE;TZID=Europe/London:20261225T060000` |

Each generated instance follows the standard duty lifecycle independently (Pending -> Active -> Fulfilled/Violated).

---

## Common Patterns Quick Reference

### Simple File Drop

Read-only access, no schedule, no consumer duties. Target inherited from policy.

```turtle
ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:referenceData ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read
    ] ;
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:modify
    ] .
```

### API with SLA

Daily delivery, schema conformance, display + non-display, monthly reporting. Target inherited from policy unless overridden.

```turtle
ex:daily-0700-london a dprod:Schedule ;
    rdfs:label "Daily at 07:00 Europe/London" ;
    dct:conformsTo dprod:Rfc5545ScheduleFormat ;
    dprod:scheduleExpression "DTSTART;TZID=Europe/London:20260101T070000\nRRULE:FREQ=DAILY" .

ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:customerData ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:deliver ;
        dprod:schedule ex:daily-0700-london ;
        dprod:deadline "PT30M"^^xsd:duration
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:conformTo ;
        odrl:target ex:customerSchema
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action ex:nonDisplay
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        odrl:action ex:report ;
        odrl:target ex:usageStats ;
        dprod:deadline "P30D"^^xsd:duration
    ] ;
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute
    ] .
```

### Mission-Critical Service

High-frequency delivery with quality SLA and change notification. Target inherited from policy unless overridden.

```turtle
ex:every-minute-london a dprod:Schedule ;
    rdfs:label "Every minute Europe/London" ;
    dct:conformsTo dprod:PosixCrontabScheduleFormat ;
    dprod:scheduleTimeZone "Europe/London" ;
    dprod:scheduleExpression "* * * * *" .

ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:riskMetrics ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:deliver ;
        dprod:schedule ex:every-minute-london ;
        dprod:deadline "PT30S"^^xsd:duration
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:conformTo ;
        odrl:target ex:riskSchema ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand ex:timeliness ;
            odrl:operator odrl:eq ;
            odrl:rightOperand ex:realtime
        ]
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:notify ;
        odrl:target ex:schemaChanges ;
        dprod:deadline "P14D"^^xsd:duration
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action ex:nonDisplay
    ] .
```

### Multi-Dataset Contract

A single contract covering multiple targets. When a policy has multiple targets, rules must specify their target explicitly -- inheritance is ambiguous.

```turtle
ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices , ex:referenceData , ex:riskMetrics ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read ;
        odrl:target ex:marketPrices
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read ;
        odrl:target ex:referenceData
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read ;
        odrl:target ex:riskMetrics
    ] .
```

---

## Advanced Topics

### Target Inheritance

`odrl:target` at the policy level is inherited by rules that don't declare their own target. This reduces redundancy:

```turtle
ex:contract a dprod:DataOffer ;
    odrl:target ex:marketPrices ;           # policy-level target
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read                # inherits ex:marketPrices
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:conformTo ;
        odrl:target ex:marketDataSchema      # different target -- explicit
    ] .
```

**Rules**:
- Single-target policy: rules inherit the target unless they specify a different one
- Multi-target policy: rules must specify their target (inheritance is ambiguous)
- Named duty instances (standalone): always specify their target

### Multi-Asset Contracts

A contract can cover multiple targets. When multiple targets exist, each rule must specify its own target (inheritance is ambiguous):

```turtle
ex:contract odrl:target ex:asset1 , ex:asset2 ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read ;
        odrl:target ex:asset1
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display ;
        odrl:target ex:asset2
    ] .
```

### Team Delegation

Use `dprod:memberOf` to model team hierarchies. A permission granted to a team applies to its members via hierarchy subsumption during evaluation:

```turtle
ex:analyst a odrl:Party ;
    dprod:memberOf ex:analyticsTeam .

ex:analyticsTeam a odrl:Party ;
    dprod:memberOf ex:tradingDivision .
```

### Version Chains

Use `prov:wasRevisionOf` to link contract versions:

```turtle
ex:contract-v2 a dprod:DataOffer ;
    prov:wasRevisionOf ex:contract-v1 .

ex:contract-v3 a dprod:DataOffer ;
    prov:wasRevisionOf ex:contract-v2 .
```

DataContracts reference the specific offer version they activate:

```turtle
ex:subscription dprod:acceptsOffer ex:contract-v2 .
```

### Expiration

Contracts and subscriptions can have explicit expiration dates:

```turtle
ex:subscription a dprod:DataContract ;
    dprod:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime ;
    dprod:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
```

---

## Lifecycle

Duties and contracts share four states:

```
         condition true
Pending ──────────────> Active
                         |  |
          action done    |  |  deadline passed
                         v  v
                   Fulfilled  Violated
```

- **Pending**: condition not yet met / not yet in force
- **Active**: condition met, action required / in force
- **Fulfilled**: action performed / obligations complete
- **Violated**: deadline passed / breached

---

## Versioning

Contracts can be versioned using `prov:wasRevisionOf`:

```turtle
ex:contract-v2 a dprod:DataOffer ;
    prov:wasRevisionOf ex:contract-v1 .
```

DataContracts reference the offer they activate via `dprod:acceptsOffer`:

```turtle
ex:subscription dprod:acceptsOffer ex:contract-v2 .
```

---

## Complete Example

See [examples/data-contract.ttl](../examples/data-contract.ttl) for a full working contract with bilateral duties, schedule, schema conformance, and subscription.

For comprehensive test data covering all patterns, see [examples/baseline.ttl](../examples/baseline.ttl).

---

## Validation Checklist

1. Every policy declares `odrl:profile <https://www.omg.org/spec/DPROD/>`
2. Conflict strategy (`odrl:conflict odrl:prohibit`) is inherited from the profile -- do not repeat per-policy
3. DataOffer has `odrl:assigner` (provider)
4. DataContract has both `odrl:assigner` and `odrl:assignee`
5. DataContract has `dprod:acceptsOffer` referencing a DataOffer
6. Each duty has exactly one `odrl:action`
7. Each permission and prohibition has exactly one `odrl:action` and one `odrl:target`
8. Provider duties have `dprod:subjectOfDuty` set to the provider
9. Deadlines use `xsd:dateTime` or `xsd:duration`
10. Schedule references use IRIs; each Schedule has one exact format and one expression
11. RFC 5545 schedules include `DTSTART` with `TZID`; schedules whose format carries no timezone (such as POSIX crontab) declare an IANA timezone; extension formats declare `dprod:carriesTimeZone`
12. Constraints have `leftOperand`, `operator`, and `rightOperand`
13. LogicalConstraints use exactly one of `odrl:and`, `odrl:or`, or `dprod:not`
14. Validate against SHACL shapes:

```bash
shacl validate --shapes dprod-contracts-shapes.ttl --data my-contract.ttl
```
