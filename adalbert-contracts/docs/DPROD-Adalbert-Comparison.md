# DPROD-Contracts vs Adalbert: Comparison Report

A comparison of the two ODRL-based data contract approaches contributed to EKGF/dprod.

---

## Overview

Both `dprod-contracts` and `adalbert-contracts` extend ODRL 2.2 for data governance. They share the same goal — formalizing bilateral data agreements between providers and consumers — but differ in scope, architecture, and formality.

| Dimension | dprod-contracts | adalbert-contracts |
|---|---|---|
| **Scope** | Data contracts only | Data contracts + data-use policies |
| **ODRL relationship** | Custom Rule subclass (Promise) | Proper ODRL 2.2 profile (Duty, Permission, Prohibition) |
| **Formal semantics** | No | Yes (normative, verification-ready) |
| **Lifecycle** | 4 statuses (Pending, Active, Expired, Cancelled) | 4 states (Pending, Active, Fulfilled, Violated) with formal transitions |
| **Bilateral duties** | Via ProviderPromise / ConsumerPromise | Via `adalbert:subject` / `adalbert:object` on standard `odrl:Duty` |
| **Recurrence** | `dprod:ICalSchedule` class + `dprod:icalRule` | `adalbert:recurrence` property (direct RRULE string on Duty) |
| **Validation** | SHACL shapes | SHACL shapes |
| **W3C Profile declaration** | ODRL Profile in ontology | Separate W3C DXPROF declaration |

---

## Architectural Differences

### 1. Promise vs Duty

**dprod-contracts** introduces `dprod:Promise` as a new `odrl:Rule` subclass, disjoint with `odrl:Duty`, `odrl:Permission`, and `odrl:Prohibition`. This creates a parallel class hierarchy:

```
odrl:Rule
├── odrl:Permission
├── odrl:Prohibition
├── odrl:Duty
└── dprod:Promise          ← new Rule type
    ├── dprod:ProviderPromise
    │   ├── dprod:ProviderTimelinessPromise
    │   ├── dprod:ProviderSchemaPromise
    │   ├── dprod:ProviderServiceLevelPromise
    │   └── ...
    └── dprod:ConsumerPromise
```

**Adalbert** uses standard `odrl:Duty` for all obligations, distinguishing provider from consumer duties via `adalbert:subject`:

```
odrl:Rule (unchanged)
├── odrl:Permission
├── odrl:Prohibition
└── odrl:Duty
    ├── with adalbert:subject = provider  → provider duty
    └── with adalbert:subject = consumer  → consumer duty
```

**Implication**: Adalbert policies are valid ODRL 2.2 — any ODRL processor can partially understand them. dprod-contracts requires Promise-aware processing.

### 2. Data-Use Policies

**dprod-contracts** focuses exclusively on bilateral contracts between named parties.

**Adalbert** also supports `odrl:Set` policies — organizational rules that apply to anyone matching constraints:

- Role-based access control
- Purpose restrictions
- Classification-based permissions
- Environment constraints
- Jurisdiction requirements
- Retention limits

This is a key differentiator. Real-world data governance requires both contracts (bilateral) and policies (organizational).

### 3. Formal Semantics

**dprod-contracts** defines classes and properties but not evaluation behavior.

**Adalbert** includes a normative formal semantics document defining:

- `Eval : Request × PolicySet × State → Decision × DutySet` (total function)
- Deterministic conflict resolution (Prohibition > Permission)
- Duty lifecycle state machine (Pending → Active → Fulfilled/Violated)
- Operand resolution from canonical roots (agent, asset, context)
- Recurrence expansion via RFC 5545 RRULE

This makes Adalbert amenable to formal verification (Dafny, Why3, Coq).

### 4. Recurrence

**dprod-contracts**:
```turtle
dprod:hasSchedule [
    a dprod:ICalSchedule ;
    dprod:icalRule "FREQ=DAILY;BYHOUR=6;BYMINUTE=0"
] .
```

**Adalbert**:
```turtle
adalbert:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
adalbert:deadline "PT30M"^^xsd:duration .
```

Adalbert is more concise (property on Duty vs. nested class) and adds `deadline` for the per-instance fulfillment window.

### 5. Operand Resolution

**dprod-contracts** does not define how constraint operands resolve.

**Adalbert** defines `adalbert:resolutionPath` — dot-separated paths from canonical roots:

```
agent.role, agent.organization, agent.costCenter
asset.classification, asset.market, asset.isBenchmark
context.purpose, context.environment, context.legalBasis
```

This enables deterministic constraint evaluation across implementations.

---

## Mapping Table

### Classes

| dprod-contracts | Adalbert | Notes |
|---|---|---|
| `dprod:DataContract` | `adalbert:DataContract` | Both subclass `odrl:Agreement` / `odrl:Offer` |
| `dprod:DataOffer` | `adalbert:DataContract` | Adalbert DataContract is an Offer; Subscription is the Agreement |
| `dprod:Promise` | `odrl:Duty` | Standard ODRL type |
| `dprod:ProviderPromise` | `odrl:Duty` + `adalbert:subject` | Subject identifies provider |
| `dprod:ConsumerPromise` | `odrl:Permission` / `odrl:Prohibition` / `odrl:Duty` | Split by semantics |
| `dprod:ProviderTimelinessPromise` | `odrl:Duty` + `adalbert-due:deliver` + `adalbert:recurrence` | |
| `dprod:ProviderSchemaPromise` | `odrl:Duty` + `adalbert-due:conformTo` | |
| `dprod:ProviderServiceLevelPromise` | `odrl:Duty` + `adalbert-due:conformTo` + constraints | |
| `dprod:ServiceLevelTarget` | `odrl:Constraint` | Expressed as constraint on duty |
| `dprod:ICalSchedule` | `adalbert:recurrence` (string property) | Simpler, same RRULE syntax |

### Properties

| dprod-contracts | Adalbert | Notes |
|---|---|---|
| `dprod:contractStatus` | `adalbert:state` | Similar lifecycle, different value names |
| `dprod:providerPromise` | `odrl:obligation` | Standard ODRL property |
| `dprod:consumerPromise` | `odrl:permission` / `odrl:obligation` / `odrl:prohibition` | Split by semantics |
| `dprod:hasSchedule` / `dprod:icalRule` | `adalbert:recurrence` | Direct RRULE on Duty |
| `dprod:hasEffectivePeriod` | `adalbert:effectiveDate` + `adalbert:expirationDate` | |
| `dprod:noticePeriod` | `adalbert:deadline` | Duration on notification duty |
| `dprod:supersedes` | `prov:wasRevisionOf` | Standard provenance |
| `dprod:hasServiceLevelTarget` | `odrl:constraint` on duty | |
| `dprod:hasPricing` | Not in scope | Adalbert focuses on rights, not pricing |

### Actions

| dprod-contracts | Adalbert | Notes |
|---|---|---|
| `dprod:deliverOnSchedule` | `adalbert-due:deliver` | `includedIn odrl:distribute` |
| `dprod:maintainSchema` | `adalbert-due:conformTo` | Duty-only action |
| `dprod:maintainQuality` | `adalbert-due:conformTo` + constraint | Quality as constrained conformance |
| `dprod:notifyChange` | `adalbert-due:notify` | `includedIn odrl:inform` |
| `dprod:notifyTermination` | `adalbert-due:notify` + `adalbert:deadline` | Deadline = notice period |
| `dprod:meetServiceLevel` | `adalbert-due:conformTo` + constraints | SLA as constrained conformance |
| `dprod:provideSupport` | `adalbert-due:notify` | Best fit |
| `dprod:reportUsage` | `adalbert-due:report` | `includedIn odrl:inform` |
| `dprod:query` | `adalbert-due:query` | `includedIn odrl:read` |
| `dprod:access` | `odrl:use` | Standard ODRL |
| `dprod:deriveInsights` | `odrl:derive` | Standard ODRL |
| `dprod:aggregate` | `odrl:aggregate` | Standard ODRL |
| `dprod:anonymize` | `odrl:anonymize` | Standard ODRL |
| `dprod:shareInternally` | `odrl:distribute` + constraint | Internal-only via constraint |
| `dprod:restrictPurpose` | `odrl:Prohibition` on `odrl:distribute` | Prohibition, not action |
| `dprod:deleteOnExpiry` | `odrl:Duty` with `odrl:delete` | Standard ODRL action |

### Status Values

| dprod-contracts | Adalbert | Notes |
|---|---|---|
| `dprod:ContractStatusPending` | `adalbert:Pending` | Same semantics |
| `dprod:ContractStatusActive` | `adalbert:Active` | Same semantics |
| `dprod:ContractStatusExpired` | `adalbert:Fulfilled` | Adalbert: natural completion = Fulfilled |
| `dprod:ContractStatusCancelled` | `adalbert:Violated` | Adalbert: early termination = Violated |

---

## What Adalbert Adds Beyond dprod-contracts

1. **Data-use policies** (`odrl:Set`) — organizational rules, access controls, not just bilateral contracts
2. **Formal semantics** — total evaluation function, deterministic conflict resolution, verifiable
3. **Duty lifecycle** — formal state machine with Pending → Active → Fulfilled/Violated transitions
4. **Structured operand resolution** — `resolutionPath` from canonical roots (agent, asset, context)
5. **Rich constraint vocabulary** — 33 operands across purpose, classification, jurisdiction, environment, timeliness, SLA metrics, data quality, channels, subscription tiers, legal basis, etc.
6. **Logical negation** — `adalbert:not` (ODRL lacks this)
7. **Target inheritance** — policy-level `odrl:target` inherited by rules
8. **Party hierarchies** — `adalbert:partOf` (assets) and `adalbert:memberOf` (parties) with transitivity

## What dprod-contracts Adds Beyond Adalbert

1. **Pricing** — `dprod:hasPricing` with `schema:PriceSpecification` (marketplace scenarios). Adalbert intentionally does not address pricing, focusing on rights and obligations.
2. **Promise class hierarchy** — richer typing for different commitment types (may aid discovery)

---

## Translated Examples

See `examples/dprod-translated.ttl` for all 8 dprod-contracts examples translated to Adalbert, demonstrating that Adalbert can express the same contracts while adding lifecycle tracking, deterministic evaluation, and structured constraints.

---

**Version**: 0.7 | **Date**: 2026-02-16
