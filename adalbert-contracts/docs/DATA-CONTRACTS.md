# Adalbert Contracts Guide

A guide for data platform teams using Adalbert for data contracts and subscriptions.

---

## Overview

Adalbert models internal data sharing agreements as ODRL 2.2 policies. A **DataContract** is an offer from a data provider. A **Subscription** is an activated contract binding provider and consumer.

```
DataContract (Offer)          Subscription (Agreement)
┌──────────────────┐         ┌──────────────────────┐
│ Provider duties   │ accept  │ Provider duties       │
│ Consumer rights   │ ──────> │ Consumer rights       │
│ Prohibitions      │         │ Consumer duties       │
│ Recurrence rules  │         │ Prohibitions          │
└──────────────────┘         │ State tracking         │
                              └──────────────────────┘
```

---

## Key Concepts

### DataContract (Offer)

An `adalbert:DataContract` is a subclass of `odrl:Offer`. It specifies:

- **Provider** (`odrl:assigner`): the data team providing data
- **Target** (`odrl:target`): the data asset(s) covered — inherited by rules unless overridden
- **Provider duties** (`odrl:obligation` with `adalbert:subject` = provider): SLAs like delivery, notification, schema conformance
- **Consumer permissions** (`odrl:permission`): what consumers can do with the data
- **Consumer duties** (`odrl:obligation` without subject in Offer): obligations consumers accept upon subscribing
- **Prohibitions** (`odrl:prohibition`): what consumers cannot do

### Subscription (Agreement)

An `adalbert:Subscription` is a subclass of `odrl:Agreement`. It adds:

- **Consumer** (`odrl:assignee`): the subscribing team
- **Effective/expiration dates**: contract period
- **State tracking**: lifecycle state on duties and the subscription itself

### Provider Duties

Provider duties use DUE actions:

| Action | Description | Example |
|--------|-------------|---------|
| `adalbert-due:deliver` | Deliver data to consumers | Daily market data delivery |
| `adalbert-due:notify` | Send notifications | Schema change notification |
| `adalbert-due:conformTo` | Maintain conformance to a standard | Schema/quality SLA |

### Consumer Duties

| Action | Description | Example |
|--------|-------------|---------|
| `adalbert-due:report` | Submit usage reports | Monthly usage reporting |

### Permissions

Standard ODRL actions apply:

| Action | Description |
|--------|-------------|
| `odrl:display` | Display data |
| `adalbert-due:nonDisplay` | Non-display (algorithmic) use |
| `odrl:derive` | Create derived products |
| `odrl:read` | Read data |

---

## Step-by-Step Cookbook

Create your first DataContract in five steps.

### Step 1: Declare the Contract

Every contract starts with a type, profile declaration, and provider identity.

```turtle
@prefix odrl:         <http://www.w3.org/ns/odrl/2/> .
@prefix adalbert:     <https://vocabulary.bigbank/adalbert/> .
@prefix adalbert-due: <https://vocabulary.bigbank/adalbert/due/> .
@prefix xsd:          <http://www.w3.org/2001/XMLSchema#> .

ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    adalbert:state adalbert:Active .
```

### Step 2: Add Provider Duties (SLAs)

Provider duties declare what the data team commits to. The provider is identified by `adalbert:subject` on each duty. Use `adalbert:object` to identify who is affected (e.g., who receives notifications).

Rules inherit `odrl:target` from the policy unless they target a different asset.

```turtle
    # Daily delivery by 06:30 (target inherited from policy)
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:deliver ;
        adalbert:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
        adalbert:deadline "PT30M"^^xsd:duration
    ] ;

    # Schema conformance (different target — not inherited)
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:conformTo ;
        odrl:target ex:marketDataSchema
    ] ;
```

### Step 3: Add Consumer Permissions

Permissions define what subscribers can do. In an Offer, omit `odrl:assignee` — it is filled when the subscription is created. Target is inherited from the policy.

```turtle
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;

    odrl:permission [
        a odrl:Permission ;
        odrl:action adalbert-due:nonDisplay ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand adalbert-due:recipientType ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:internal
        ]
    ] ;
```

### Step 4: Add Consumer Duties and Prohibitions

Consumer duties activate upon subscription. Prohibitions apply to all subscribers.

```turtle
    # Consumer must report usage monthly (different target — not inherited)
    odrl:obligation [
        a odrl:Duty ;
        odrl:action adalbert-due:report ;
        odrl:target ex:usageStats ;
        adalbert:deadline "P30D"^^xsd:duration
    ] ;

    # No external redistribution (target inherited from policy)
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute
    ] .
```

### Step 5: Create a Subscription

When a consumer accepts the contract, create a Subscription (Agreement) referencing the contract:

```turtle
ex:subscription a adalbert:Subscription ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    adalbert:subscribesTo ex:contract ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:analyticsTeam ;
    adalbert:effectiveDate "2026-02-01T00:00:00Z"^^xsd:dateTime ;
    adalbert:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
```

The subscription materializes all duties from the contract with explicit `adalbert:subject` on each.

---

## Provider Duty Patterns

### Timeliness Pattern (Delivery SLA)

Scheduled data delivery with a fulfillment window. Target inherited from policy.

```turtle
odrl:obligation [
    a odrl:Duty ;
    adalbert:subject ex:dataTeam ;
    odrl:action adalbert-due:deliver ;
    adalbert:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
    adalbert:deadline "PT30M"^^xsd:duration
] .
```

**DCON equivalent**: `ProviderTimelinessPromise`

### Schema Pattern (Schema Conformance)

Provider guarantees data conforms to a published schema. Target differs from policy — specify explicitly.

```turtle
odrl:obligation [
    a odrl:Duty ;
    adalbert:subject ex:dataTeam ;
    odrl:action adalbert-due:conformTo ;
    odrl:target ex:marketDataSchema
] .
```

**DCON equivalent**: `ProviderSchemaPromise`

### Notification Pattern (Change Notification)

Provider must notify consumers before making changes, with a lead time expressed as a duration deadline. Use `adalbert:object` to identify who is notified.

```turtle
odrl:obligation [
    a odrl:Duty ;
    adalbert:subject ex:dataTeam ;
    adalbert:object ex:consumer ;
    odrl:action adalbert-due:notify ;
    odrl:target ex:schemaChanges ;
    adalbert:deadline "P14D"^^xsd:duration
] .
```

**DCON equivalent**: `ProviderChangeNotificationPromise`

### Quality SLA Pattern

Provider guarantees data quality via `conformTo` with a constraint. This replaces DCON's `ProviderQualityPromise`.

```turtle
odrl:obligation [
    a odrl:Duty ;
    adalbert:subject ex:dataTeam ;
    odrl:action adalbert-due:conformTo ;
    odrl:target ex:riskMetricsSchema ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand adalbert-due:timeliness ;
        odrl:operator odrl:eq ;
        odrl:rightOperand adalbert-due:realtime
    ]
] .
```

The constraint can check any DUE operand — timeliness, classification, environment, etc.

---

## Recurrence

Recurring duties use `adalbert:recurrence` — an RFC 5545 RRULE string. Combined with `adalbert:deadline`, this defines a schedule and fulfillment window.

```turtle
odrl:obligation [
    a odrl:Duty ;
    adalbert:subject ex:dataTeam ;
    odrl:action adalbert-due:deliver ;
    adalbert:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
    adalbert:deadline "PT30M"^^xsd:duration
] .
```

This means: deliver market prices daily at 06:00 (target inherited from policy), with a 30-minute window to fulfill.

### Common RRULE Patterns

| Pattern | RRULE |
|---------|-------|
| Daily at 06:00 | `FREQ=DAILY;BYHOUR=6;BYMINUTE=0` |
| Weekly on Monday | `FREQ=WEEKLY;BYDAY=MO` |
| Monthly on the 1st | `FREQ=MONTHLY;BYMONTHDAY=1` |
| Every 15 minutes | `FREQ=MINUTELY;INTERVAL=15` |
| Hourly | `FREQ=HOURLY` |

Each generated instance follows the standard duty lifecycle independently (Pending -> Active -> Fulfilled/Violated).

---

## Common Patterns Quick Reference

### Simple File Drop

Read-only access, no recurrence, no consumer duties. Target inherited from policy.

```turtle
ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ;
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
ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:customerData ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:deliver ;
        adalbert:recurrence "FREQ=DAILY;BYHOUR=7;BYMINUTE=0" ;
        adalbert:deadline "PT30M"^^xsd:duration
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:conformTo ;
        odrl:target ex:customerSchema
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action adalbert-due:nonDisplay
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        odrl:action adalbert-due:report ;
        odrl:target ex:usageStats ;
        adalbert:deadline "P30D"^^xsd:duration
    ] ;
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute
    ] .
```

### Mission-Critical Service

High-frequency delivery with quality SLA and change notification. Target inherited from policy unless overridden.

```turtle
ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:riskMetrics ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:deliver ;
        adalbert:recurrence "FREQ=MINUTELY;INTERVAL=1" ;
        adalbert:deadline "PT30S"^^xsd:duration
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:conformTo ;
        odrl:target ex:riskSchema ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand adalbert-due:timeliness ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:realtime
        ]
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:notify ;
        odrl:target ex:schemaChanges ;
        adalbert:deadline "P14D"^^xsd:duration
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action adalbert-due:nonDisplay
    ] .
```

### Multi-Dataset Contract

A single contract covering multiple targets. When a policy has multiple targets, rules must specify their target explicitly — inheritance is ambiguous.

```turtle
ex:contract a adalbert:DataContract ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ;
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
ex:contract a adalbert:DataContract ;
    odrl:target ex:marketPrices ;           # policy-level target
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read                # inherits ex:marketPrices
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:conformTo ;
        odrl:target ex:marketDataSchema      # different target — explicit
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

Use `adalbert:memberOf` to model team hierarchies. A permission granted to a team applies to its members via hierarchy subsumption during evaluation:

```turtle
ex:analyst a odrl:Party ;
    adalbert:memberOf ex:analyticsTeam .

ex:analyticsTeam a odrl:Party ;
    adalbert:memberOf ex:tradingDivision .
```

### Version Chains

Use `prov:wasRevisionOf` to link contract versions:

```turtle
ex:contract-v2 a adalbert:DataContract ;
    prov:wasRevisionOf ex:contract-v1 .

ex:contract-v3 a adalbert:DataContract ;
    prov:wasRevisionOf ex:contract-v2 .
```

Subscriptions reference the specific contract version they activate:

```turtle
ex:subscription adalbert:subscribesTo ex:contract-v2 .
```

### Expiration

Contracts and subscriptions can have explicit expiration dates:

```turtle
ex:subscription a adalbert:Subscription ;
    adalbert:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime ;
    adalbert:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime .
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
ex:contract-v2 a adalbert:DataContract ;
    prov:wasRevisionOf ex:contract-v1 .
```

Subscriptions reference the contract they activate via `adalbert:subscribesTo`:

```turtle
ex:subscription adalbert:subscribesTo ex:contract-v2 .
```

---

## Complete Example

See [examples/data-contract.ttl](../examples/data-contract.ttl) for a full working contract with bilateral duties, recurrence, schema conformance, and subscription.

For comprehensive test data covering all patterns, see [examples/baseline.ttl](../examples/baseline.ttl).

---

## DCON Migration

If migrating from DCON, see [adalbert-term-mapping.md](adalbert-term-mapping.md) for complete property equivalents and [comparisons/comparison-dcon.md](comparisons/comparison-dcon.md) for the supersession analysis.

---

## Validation Checklist

1. Every policy declares `odrl:profile <https://vocabulary.bigbank/adalbert/>` and `<https://vocabulary.bigbank/adalbert/due/>`
2. Conflict strategy (`odrl:conflict odrl:prohibit`) is inherited from the profile — do not repeat per-policy
3. DataContract has `odrl:assigner` (provider)
4. Subscription has both `odrl:assigner` and `odrl:assignee`
5. Subscription has `adalbert:subscribesTo` referencing a DataContract
6. Each duty has exactly one `odrl:action`
7. Each permission and prohibition has exactly one `odrl:action` and one `odrl:target`
8. Provider duties have `adalbert:subject` set to the provider
9. Deadlines use `xsd:dateTime` or `xsd:duration`
10. Recurrence uses a valid RFC 5545 RRULE starting with `FREQ=`
11. Constraints have `leftOperand`, `operator`, and `rightOperand`
12. LogicalConstraints use exactly one of `odrl:and`, `odrl:or`, or `adalbert:not`
13. Validate against SHACL shapes:

```bash
shacl validate --shapes ontology/adalbert-shacl.ttl --data my-contract.ttl
```
