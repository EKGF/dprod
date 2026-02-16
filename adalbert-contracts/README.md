# Adalbert: Data Contracts and Data-Use Policies

**An ODRL 2.2 profile with deterministic evaluation semantics for data governance.**

Adalbert provides a formal, standards-based approach to data contracts and data-use policies. It uses ODRL 2.2 terms for all standard constructs and adds only genuinely new extensions for lifecycle management, bilateral duties, recurrence, and structured operand resolution.

---

## What This Is

This folder contains the Adalbert data governance framework as a contribution to EKGF/dprod, complementing the `dprod-contracts` approach with:

1. **Data contracts** — bilateral agreements between data providers and consumers (like dprod-contracts)
2. **Data-use policies** — organizational access controls, purpose restrictions, classification rules (unique to Adalbert)
3. **Formal semantics** — normative evaluation specification amenable to formal verification
4. **ODRL 2.2 compliance** — every Adalbert policy is a valid ODRL 2.2 policy

## Key Differentiators

| Capability | dprod-contracts | Adalbert |
|---|---|---|
| Data contracts | Yes | Yes |
| Data-use policies | No | **Yes** |
| Formal semantics | No | **Yes** (normative, verification-ready) |
| Bilateral duties | Via Promise subclass | **Via standard odrl:Duty** |
| Lifecycle states | Status enum | **Formal state machine** (Pending → Active → Fulfilled/Violated) |
| Recurrence | ICalSchedule class | **RRULE property** + deadline window |
| Operand resolution | Unspecified | **Structured paths** (agent.role, asset.classification, context.purpose) |
| Constraint vocabulary | Minimal | **33 operands** across 15 categories |
| ODRL compatibility | Custom Rule subclass | **Standard Rule types** (Permission, Duty, Prohibition) |

---

## Folder Contents

```
adalbert-contracts/
├── README.md                          # This file
├── adalbert-core.ttl                  # OWL ontology (ODRL profile extension)
├── adalbert-shacl.ttl                 # SHACL validation shapes
├── adalbert-prof.ttl                  # W3C DXPROF profile metadata
├── adalbert-due.ttl                   # Data use vocabulary (operands, actions, values)
├── examples/
│   ├── data-contract.ttl              # Bilateral contract with provider SLA + consumer duties
│   ├── data-use-policy.ttl            # Role-based access control with purpose constraints
│   ├── dprod-translated.ttl           # dprod-contracts examples translated to Adalbert
│   └── baseline.ttl                   # Comprehensive test suite (8 contracts, 2 subscriptions)
└── docs/
    ├── DATA-CONTRACTS.md              # Data contract authoring guide
    ├── DATA-USE-POLICIES.md           # Data-use policy authoring guide
    ├── SPECIFICATION.md               # Technical vocabulary reference
    ├── SEMANTICS.md                   # Formal evaluation semantics (normative)
    └── DPROD-Adalbert-Comparison.md   # Comparison with dprod-contracts
```

---

## Quick Start

### Data Contract (bilateral agreement)

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
    adalbert:state adalbert:Active ;

    # Provider SLA: daily delivery with 30-min window
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        odrl:action adalbert-due:deliver ;
        adalbert:recurrence "FREQ=DAILY;BYHOUR=6;BYMINUTE=0" ;
        adalbert:deadline "PT30M"^^xsd:duration
    ] ;

    # Consumer: may read
    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read
    ] ;

    # Consumer: must report monthly
    odrl:obligation [
        a odrl:Duty ;
        odrl:action adalbert-due:report ;
        adalbert:deadline "P30D"^^xsd:duration
    ] ;

    # No redistribution
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute
    ] .
```

### Data-Use Policy (organizational access control)

```turtle
ex:policy a odrl:Set ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
    odrl:target ex:employeeData ;

    # HR Analytics: read for analytics purpose only
    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:hrAnalytics ;
        odrl:action odrl:read ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:analytics
        ]
    ] ;

    # No ML training on employee data
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:use ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand adalbert-due:processingMode ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:modelTraining
        ]
    ] .
```

---

## Relationship to dprod-contracts

Adalbert and dprod-contracts are complementary approaches to the same problem space. See `docs/DPROD-Adalbert-Comparison.md` for a detailed comparison and `examples/dprod-translated.ttl` for all 8 dprod-contracts examples expressed in Adalbert.

Key architectural difference: dprod-contracts introduces `dprod:Promise` as a new `odrl:Rule` subclass. Adalbert uses standard `odrl:Duty`, `odrl:Permission`, and `odrl:Prohibition`, making every Adalbert policy a valid ODRL 2.2 policy that any ODRL processor can partially understand.

---

## SHACL Validation

Validate any Adalbert policy against the SHACL shapes:

```bash
shacl validate --shapes adalbert-shacl.ttl --data examples/data-contract.ttl
```

---

## Namespaces

| Prefix | Namespace | Role |
|--------|-----------|------|
| `odrl:` | `http://www.w3.org/ns/odrl/2/` | Primary — all standard ODRL constructs |
| `adalbert:` | `https://vocabulary.bigbank/adalbert/` | Extensions only (State, deadline, recurrence, DataContract, Subscription) |
| `adalbert-due:` | `https://vocabulary.bigbank/adalbert/due/` | Data use vocabulary (operands, actions, concept values) |

---

## References

- [ODRL 2.2 Information Model](https://www.w3.org/TR/odrl-model/)
- [W3C ODRL Profile Best Practices](https://www.w3.org/community/reports/odrl/CG-FINAL-profile-bp-20240808.html)
- [W3C Market Data Profile](https://www.w3.org/2021/md-odrl-profile/v1/)
- [EKGF DPROD](https://ekgf.github.io/dprod/)

---

**Version**: 0.7 | **Date**: 2026-02-16
