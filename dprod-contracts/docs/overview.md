# DPROD Contracts Overview

What DPROD Contracts is, who it is for, and how to get started.

---

## Quick Start

DPROD Contracts is a **deterministic ODRL 2.2 profile** for data governance. It fixes ODRL's ambiguities -- undefined duty lifecycle, unilateral-only agreements, implicit evaluation order -- while remaining a proper profile: every DPROD policy is a valid ODRL 2.2 policy.

DPROD Contracts is designed for organizations that need:

- **Data contracts** between providers and consumers (SLAs, delivery schedules, usage restrictions)
- **Data use policies** governing access by purpose, role, jurisdiction, and classification
- **Deterministic evaluation** where the same request always produces the same decision
- **Formal verification** of policy correctness (amenable to Dafny, Why3, Coq)

### Minimal Data Offer

```turtle
@prefix odrl:     <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://www.omg.org/spec/DPROD/dprod/> .
@prefix ex:       <https://example.org/> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

ex:contract a dprod:DataOffer ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:assigner ex:dataTeam ;
    odrl:target ex:marketPrices ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:deliver ;
        dprod:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
        dprod:deadline "PT30M"^^xsd:duration
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:display
    ] .
```

### Minimal Data Contract

A `dprod:DataContract` activates an offer, binding both parties:

```turtle
@prefix odrl:     <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://www.omg.org/spec/DPROD/dprod/> .
@prefix ex:       <https://example.org/> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

ex:agreement a dprod:DataContract ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    dprod:acceptsOffer ex:contract ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:quantResearch ;
    odrl:target ex:marketPrices ;
    dprod:effectiveDate "2026-01-15T00:00:00Z"^^xsd:dateTime ;
    dprod:expirationDate "2026-12-31T23:59:59Z"^^xsd:dateTime ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        odrl:action ex:deliver ;
        dprod:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
        dprod:deadline "PT30M"^^xsd:duration
    ] ;
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:quantResearch ;
        odrl:action ex:report ;
        odrl:target ex:usageStats ;
        dprod:deadline "P30D"^^xsd:duration
    ] ;
    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:quantResearch ;
        odrl:action odrl:display
    ] ;
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:assignee ex:quantResearch ;
        odrl:action odrl:distribute
    ] .
```

### Minimal Data Use Policy

```turtle
ex:policy a odrl:Set ;
    odrl:profile <https://www.omg.org/spec/DPROD/> ;
    odrl:target ex:employeeData ;
    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:hrTeam ;
        odrl:action odrl:read ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand ex:analytics
        ]
    ] .
```

---

## Key Concepts

### Permission, Duty, Prohibition

DPROD Contracts uses ODRL's three rule types directly:

| Rule Type | Meaning | Example |
|-----------|---------|---------|
| `odrl:Permission` | Grants access under conditions | "Analytics team may read for analytics purpose" |
| `odrl:Duty` | Requires an action | "Provider must deliver data daily by 06:30" |
| `odrl:Prohibition` | Denies access | "No external distribution" |

Prohibitions always override permissions (fixed conflict resolution: `odrl:prohibit`).

### Constraint

Conditions on rules. An `odrl:Constraint` compares a left operand to a right operand via an operator:

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand odrl:purpose ;
    odrl:operator odrl:eq ;
    odrl:rightOperand ex:analytics
] .
```

Constraints can be combined with `odrl:and`, `odrl:or`, or negated with `dprod:not` via `odrl:LogicalConstraint`.

### State

Duties and contracts share a four-state lifecycle:

```
         condition true
Pending ──────────────> Active
                         |  |
          action done    |  |  deadline passed
                         v  v
                   Fulfilled  Violated
```

### DataOffer and DataContract

A `dprod:DataOffer` (subclass of `odrl:Offer`) is a provider's offer specifying SLAs, permissions, and restrictions. A `dprod:DataContract` (subclass of `odrl:Agreement`) is an activated offer binding both parties.

### Recurrence

Recurring duties use `dprod:recurrence` -- an RFC 5545 RRULE string. Combined with `dprod:deadline`, this defines a schedule and per-instance fulfillment window. Each generated instance follows the lifecycle independently.

---

## Architecture

DPROD Contracts has a layered architecture:

```
ODRL 2.2 Core (W3C Standard)
  Permission, Duty, Prohibition, Set, Offer, Agreement,
  Constraint, Action, Asset, Party, LeftOperand, operators
         |
         | proper profile (thin extension)
         v
DPROD Core (dprod:)
  State, deadline, recurrence, DataOffer, DataContract,
  path, RuntimeReference, not
         |
         | domain profiles define (ex:)
         v
Domain Vocabulary
  actions, operands, and SKOS concept values
  (deliver, notify, conformTo, nonDisplay, classification, ...)
```

### Namespaces

| Prefix | Namespace | Role |
|--------|-----------|------|
| `odrl:` | `http://www.w3.org/ns/odrl/2/` | Primary -- all standard constructs |
| `dprod:` | `https://www.omg.org/spec/DPROD/dprod/` | Core extensions (lifecycle, operand resolution, contract types) |
| `ex:` | (domain-specific) | Domain actions, operands, and concept values |

---

## How It Differs from ODRL 2.2

ODRL 2.2 is a flexible framework. DPROD Contracts makes it deterministic and governance-ready:

| Aspect | ODRL 2.2 | DPROD Contracts |
|--------|----------|-----------------|
| Duty lifecycle | Undefined | Pending -> Active -> Fulfilled/Violated |
| Agreement evaluation | Assignee duties only | Both assigner and assignee duties (bilateral) |
| Conflict resolution | Configurable | Fixed: Prohibition > Permission |
| Evaluation order | Undefined | Deterministic left-to-right |
| Operand resolution | Implicit | Explicit `dprod:path` property paths (SHACL-Core predicate + sequence subset) |
| Recurring duties | Not supported | `recurrence` (RFC 5545 RRULE) + `deadline` |
| Contract types | Generic Offer/Agreement | `DataOffer` (Offer) / `DataContract` (Agreement) |
| Logical negation | Not supported | `dprod:not` on LogicalConstraint |

Every DPROD policy remains a valid ODRL 2.2 policy. Standard ODRL processors can parse them; DPROD-aware processors additionally enforce lifecycle, bilateral duties, and deterministic evaluation.

---

## Document Map

Which document to read next depends on your role:

| Role | Start Here | Then Read |
|------|-----------|-----------|
| **Contract writer** (data platform team) | [contracts-guide.md](contracts-guide.md) | [examples/data-contract.ttl](../examples/data-contract.ttl) |
| **Policy writer** (data steward) | [policy-writers-guide.md](policy-writers-guide.md) | [examples/data-use-policy.ttl](../examples/data-use-policy.ttl) |
| **Implementer** (runtime developer) | [formal-semantics.md](formal-semantics.md) | [specification.md](specification.md) |
| **Evaluating DPROD** | This document | -- |

### Full Document Inventory

| Document | Description |
|----------|-------------|
| [overview.md](overview.md) | What is DPROD Contracts? (this document) |
| [specification.md](specification.md) | Technical vocabulary reference |
| [term-mapping.md](term-mapping.md) | Business term -> property mapping |
| [contracts-guide.md](contracts-guide.md) | Data contract authoring guide |
| [policy-writers-guide.md](policy-writers-guide.md) | Data use policy authoring guide |
| [formal-semantics.md](formal-semantics.md) | Formal operational semantics (normative) |

---

**Version**: 0.7 | **Date**: 2026-08-19
