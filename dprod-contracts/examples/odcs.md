# ODCS vs DPROD Contracts: Comparison Report

A comparison of the Open Data Contract Standard (ODCS v3.1.0) and DPROD Contracts (ODRL 2.2 Profile).

---

## Overview

ODCS and DPROD Contracts solve the same problem — formalizing data agreements — but take fundamentally different approaches. ODCS is a YAML schema for describing data contracts as configuration files. DPROD Contracts is an RDF-based ODRL 2.2 profile that expresses contracts as linked data policies with formal semantics.

| Dimension | ODCS v3.1.0 | DPROD Contracts |
|---|---|---|
| **Format** | YAML (JSON Schema validated) | RDF/Turtle (ODRL 2.2 + SHACL validated) |
| **Foundation** | Custom schema | W3C ODRL 2.2 standard |
| **Scope** | Bilateral contracts only | Bilateral contracts + organizational data-use policies |
| **Schema definition** | Inline (tables, columns, types) | External (DCAT, SHACL — separation of concerns) |
| **Quality rules** | Inline metrics with operators | `odrl:Duty` + `dprod:conformTo` + `odrl:Constraint` |
| **SLAs** | `slaProperties` key-value list | `odrl:Duty` with measurable constraints |
| **Access control** | `roles` with approval chains | `odrl:Permission` / `odrl:Prohibition` with constraints |
| **Pricing** | `price` section | Out of scope (rights and obligations only) |
| **Formal semantics** | No | Yes (deterministic evaluation, conflict resolution) |
| **Lifecycle** | `status` field | 4-state machine (Pending, Active, Fulfilled, Violated) |
| **Interoperability** | YAML tooling | SPARQL, linked data, ODRL processors |
| **Infrastructure** | `servers` section | Out of scope (not policy) |

---

## Architectural Differences

### 1. Contract as Configuration vs Contract as Policy

**ODCS** treats a data contract as a configuration document — a flat YAML file that bundles schema, quality rules, SLAs, team info, pricing, and infrastructure into one artifact. This is convenient for CI/CD pipelines and data platform tooling.

**DPROD Contracts** treats a data contract as a *policy* — a formal rights expression that can be evaluated deterministically. Schema lives in DCAT/SHACL, infrastructure in deployment descriptors. The contract focuses on: what actions are permitted, prohibited, or obligated, and under what constraints.

### 2. Quality and SLAs

**ODCS** has purpose-built sections for quality (`schema[].quality`) and SLAs (`slaProperties`) with domain-specific operators (`mustBe`, `mustBeGreaterThan`, etc.) and dimensions (`accuracy`, `completeness`, etc.).

**DPROD Contracts** unifies quality and SLAs as duties with constraints:

```turtle
# ODCS quality rule: nullValues mustBe 0
odrl:obligation [
    a odrl:Duty ;
    dprod:subject ex:data-team ;
    odrl:action dprod:conformTo ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod:completeness ;
        odrl:operator odrl:eq ;
        odrl:rightOperand "100"^^xsd:decimal
    ]
] .
```

The advantage: a single constraint model covers quality, SLAs, access rules, and purpose restrictions. The trade-off: less domain-specific syntax.

### 3. Access Control

**ODCS** has a `roles` section with approval chains:

```yaml
roles:
  - role: microstrategy_user_opr
    access: read
    firstLevelApprovers: Reporting Manager
    secondLevelApprovers: mandolorian
```

**DPROD Contracts** uses ODRL Permission/Prohibition with constraints:

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:assignee ex:reporting-users ;
    odrl:action odrl:read ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod:recipientType ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod:internal
    ]
] .
```

DPROD Contracts adds prohibition rules and purpose constraints that ODCS cannot express.

### 4. Data-Use Policies

**ODCS** supports only bilateral contracts between a producer and consumers.

**DPROD Contracts** also supports `odrl:Set` policies — organizational rules without named parties:

- Classification-based access (confidential, restricted, public)
- Purpose restrictions (analytics only, no ML training)
- Jurisdiction requirements (EU data stays in EU)
- Environment constraints (production only)
- Retention obligations

This is critical for enterprise data governance beyond bilateral agreements.

### 5. Lifecycle and State

**ODCS** has a `status` field with no formal transition rules.

**DPROD Contracts** has a formal 4-state machine:

```
Pending → Active → Fulfilled
                  → Violated
```

Each duty instance tracks its own state, enabling fine-grained compliance monitoring.

---

## Mapping Table

### Top-Level Sections

| ODCS Section | DPROD Contracts | Notes |
|---|---|---|
| `kind: DataContract` | `a dprod:DataContract` | Subclass of `odrl:Offer` |
| `status` | `dprod:state` | 4-state lifecycle (Pending, Active, Fulfilled, Violated) |
| `version` | `dct:hasVersion` | Standard Dublin Core |
| `domain` / `dataProduct` | Core DPROD `dprod:DataProduct` | Linked via `odrl:hasPolicy` |
| `description.purpose` | `odrl:purpose` constraint | On permission or duty |
| `description.limitations` | `odrl:Prohibition` + constraints | Express as restrictions |
| `apiVersion` | `odrl:profile` | Profile URI identifies version |
| `tenant` | Organization context on `odrl:Party` | Via `dprod:memberOf` |
| `id` | Resource URI | Inherent in RDF |
| `contractCreatedTs` | `dct:created` | Standard Dublin Core |

### Schema

| ODCS | DPROD Contracts | Notes |
|---|---|---|
| `schema` (tables/columns) | External: DCAT + SHACL | Separation of concerns — schema is not policy |
| `schema[].classification` | `dprod:classification` constraint | On permission/prohibition |
| `schema[].tags` | External: DCAT keywords | Not policy metadata |
| `schema[].quality` | `odrl:Duty` + `dprod:conformTo` | Quality as obligation |
| `schema[].relationships` | External: SHACL / OWL | Not policy metadata |

### Data Quality

| ODCS Quality | DPROD Contracts | Notes |
|---|---|---|
| `metric: nullValues` | Constraint: `dprod:completeness` | Quality dimension operand |
| `metric: rowCount` | Constraint: `dprod:volumeCount` | Custom constraint |
| `mustBe` / `mustBeGreaterThan` | `odrl:operator` (`odrl:eq`, `odrl:gt`, `odrl:gteq`) | Standard ODRL operators |
| `dimension: accuracy` | `dprod:accuracy` | DPROD operand |
| `dimension: completeness` | `dprod:completeness` | DPROD operand |
| `dimension: timeliness` | `dprod:timeliness` | DPROD operand |
| `dimension: uniqueness` | Constraint on `dprod:conformTo` | Custom quality constraint |
| `severity` | Not directly modeled | Operational metadata |
| `businessImpact` | Not directly modeled | Operational metadata |
| `schedule` / `scheduler` | `dprod:recurrence` on duty | RFC 5545 RRULE |

### SLA Properties

| ODCS SLA | DPROD Contracts | Notes |
|---|---|---|
| `latency` | `dprod:latency` + constraint | On conformance duty |
| `availability` | `dprod:availability` + constraint | On conformance duty |
| `throughput` | `dprod:throughput` + constraint | On conformance duty |
| `frequency` | `dprod:recurrence` on delivery duty | RFC 5545 RRULE string |
| `timeOfAvailability` | `dprod:deadline` on delivery duty | XSD duration |
| `retention` | `odrl:Duty` + `odrl:delete` + `dprod:retentionPeriod` | Retention as obligation |
| `generalAvailability` | `dprod:effectiveDate` | Contract start date |
| `endOfSupport` / `endOfLife` | `dprod:expirationDate` | Contract end date |
| `timeToRepair` | `dprod:deadline` on repair duty | Per-incident SLA |
| `timeToNotify` | `dprod:deadline` on notify duty | Notification SLA |
| `driver` | `odrl:purpose` constraint | Regulatory, analytics, operational |

### Team and Roles

| ODCS | DPROD Contracts | Notes |
|---|---|---|
| `team.members` | `odrl:Party` instances | With `dprod:memberOf` hierarchy |
| `team.members[].role: Owner` | `odrl:assigner` | Data provider |
| `roles[].role` | `odrl:assignee` on Permission | Role-based access |
| `roles[].access: read` | `odrl:action odrl:read` | Standard ODRL action |
| `roles[].access: write` | `odrl:action odrl:modify` | Standard ODRL action |
| `roles[].firstLevelApprovers` | Not modeled | Workflow, not policy |
| `roles[].secondLevelApprovers` | Not modeled | Workflow, not policy |

### Support

| ODCS | DPROD Contracts | Notes |
|---|---|---|
| `support[].channel` | `odrl:Duty` + `dprod:notify` | With channel constraint |
| `support[].tool` | `dprod:channel` constraint value | Slack, email, teams |
| Response time | `dprod:deadline` on notify duty | SLA as duration |

### Pricing and Infrastructure

| ODCS | DPROD Contracts | Notes |
|---|---|---|
| `price` | Not in scope | DPROD Contracts focuses on rights and obligations |
| `servers` | Not in scope | Infrastructure, not policy |
| `customProperties` | Not in scope | Use RDF extension mechanism |

---

## What DPROD Contracts Adds Beyond ODCS

1. **Data-use policies** — organizational rules, role-based access, purpose restrictions (not just bilateral contracts)
2. **Formal semantics** — deterministic evaluation function, conflict resolution, verifiable
3. **Prohibitions** — explicit "you must NOT" rules (ODCS has no prohibition concept)
4. **Duty lifecycle** — 4-state machine tracking fulfillment per obligation instance
5. **Constraint composition** — `odrl:and` / `odrl:or` / `dprod:not` for complex rules
6. **Target inheritance** — policy-level target inherited by rules
7. **Party hierarchies** — `dprod:memberOf` for organizational structures with transitivity
8. **Asset hierarchies** — `dprod:partOf` for dataset containment with transitivity
9. **Linked data** — SPARQL-queryable, federable across organizations
10. **Subscriptions** — formal bilateral agreements (`dprod:Subscription` as `odrl:Agreement`)

## What ODCS Adds Beyond DPROD Contracts

1. **Inline schema** — table/column definitions with types, partitions, relationships
2. **Pricing** — `price` section with amount, currency, unit
3. **Infrastructure** — `servers` section with connection details
4. **Approval workflows** — multi-level approver chains on roles
5. **Custom quality engines** — integration with Soda, Great Expectations, dbt, Montecarlo
6. **Lower barrier to entry** — YAML is more accessible than RDF/ODRL for data engineers

---

## Complementary Use

ODCS and DPROD Contracts are not mutually exclusive. An organization could:

- Use **ODCS** for schema documentation, data quality CI/CD, and platform configuration
- Use **DPROD Contracts** for formal rights management, access policy evaluation, and compliance

The bridge between them is the core DPROD ontology: a `dprod:DataProduct` links to both its DCAT distribution metadata (which could be generated from ODCS schema) and its `odrl:hasPolicy` (the DPROD Contract).

---

## Translated Examples

See `examples/odcs-translated.ttl` for the ODCS full example translated to DPROD Contracts, demonstrating how each ODCS section maps to ODRL constructs.

---

**Version**: 0.7 | **Date**: 2026-02-26
