# DPROD Data Contracts: Deterministic Policy Language for Data Governance

**An ODRL 2.2 profile with deterministic evaluation semantics for data governance.**

---

## What This Is

DPROD Contracts is an ODRL 2.2 profile. It uses ODRL terms for all standard constructs (Permission, Duty, Prohibition, Agreement, etc.) and only adds extensions where ODRL 2.2 leaves behavior undefined:

1. **Explicit lifecycle**: Pending -> Active -> Fulfilled/Violated (unified for duties and contracts)
2. **Bilateral agreements**: Both assigner and assignee may have duties
3. **Deterministic evaluation**: Total functions, no undefined states
4. **Formal verification target**: Amenable to Dafny, Why3, Coq
5. **Structured operand resolution**: SPARQL-style `dprod:path` property paths
6. **Recurring duties**: `recurrence` via RFC 5545 RRULE for scheduled obligations

DPROD Contracts is **specification-first**. The semantics document defines what any conformant implementation must do. Every DPROD policy is a valid ODRL 2.2 policy.

---

## Quick Start

See [examples/](examples/) for complete working policies:

- [data-contract.ttl](examples/data-contract.ttl) -- DataOffer, DataContract, bilateral duties
- [data-use-policy.ttl](examples/data-use-policy.ttl) -- Role-based access, purpose constraints

---

## What DPROD Contracts Adds to ODRL 2.2

| Extension | ODRL 2.2 | What DPROD Adds |
|-----------|----------|-----------------|
| Duty lifecycle | Undefined | Pending -> Active -> Fulfilled/Violated |
| Bilateral duties | Unilateral (assignee only) | Assigner duties + assignee duties |
| Conflict resolution | Configurable | Fixed: Prohibition > Permission |
| Evaluation order | Undefined | Deterministic left-to-right |
| Operand resolution | Implicit | Explicit `dprod:path` property paths (+ `dprod:select` for complex resolution) |
| Recurring duties | -- | `recurrence` via RFC 5545 RRULE with per-instance `deadline` |
| Contract types | -- | `DataOffer` (subclass of Offer), `DataContract` (subclass of Agreement) |

**Note**: DPROD Contracts is an ODRL profile, not a parallel vocabulary. Standard ODRL processors can parse DPROD policies; DPROD-aware processors additionally enforce lifecycle, bilateral duties, and deterministic evaluation.

---

## Design Principles

### 1. Specification Precedes Implementation

The [formal semantics](docs/formal-semantics.md) is the normative reference.

### 2. Total Functions

Every evaluation terminates with a defined result:

```
Eval : Request x PolicySet x State -> Decision x DutySet
```

### 3. Bilateral Agreements

Agreements return duties for **both** parties:

```
Result = {
    decision: Permit | Deny | NotApplicable,
    assignerDuties: Set<Duty>,   // Provider obligations (SLAs)
    assigneeDuties: Set<Duty>,   // Consumer obligations
    violations: Set<Duty>
}
```

### 4. Unified Lifecycle State

Duties and contracts share four states:

```
         condition true
Pending ──────────────> Active
                         │  │
          action done    │  │  deadline passed
                         ▼  ▼
                   Fulfilled  Violated
```

An `odrl:Duty` progresses through `dprod:State` values. A `dprod:DataOffer` shares the same state machine.

### 5. Structured Operand Resolution

Operands resolve via `dprod:path` -- SPARQL-style property paths from the evaluation context:

```turtle
# Context-rooted (single-step): direct property on request
ex:environment  dprod:path ex:environment .

# Asset-rooted (two-step): via odrl:target
ex:timeliness   dprod:path (odrl:target ex:timeliness) .

# Agent-rooted (two-step): via odrl:assignee
ex:recipientType dprod:select "SELECT ?v WHERE { $request odrl:assignee/ex:recipientType ?v }" .
```

---

## Repository Structure

```
dprod-contracts/
├── dprod-contracts.ttl              # Core ontology (ODRL profile extension)
├── dprod-contracts-shapes.ttl       # SHACL validation shapes
├── dprod-contracts-prof.ttl         # DXPROF profile declaration
├── examples/
│   ├── data-contract.ttl            # Complete contract example (with recurrence)
│   ├── data-use-policy.ttl          # Access control example
│   └── baseline.ttl                 # Comprehensive test data (8 offers, 2 contracts)
└── docs/
    ├── overview.md                  # What is DPROD Contracts? (start here)
    ├── specification.md             # Technical vocabulary reference
    ├── term-mapping.md              # Business term -> property mapping
    ├── formal-semantics.md          # Formal semantics (normative)
    ├── contracts-guide.md           # Data contract authoring guide
    └── policy-writers-guide.md      # Data use policy authoring guide
```


---

## Namespaces

| Prefix | Namespace | Role |
|--------|-----------|------|
| `odrl:` | `http://www.w3.org/ns/odrl/2/` | Primary -- all standard constructs |
| `dprod:` | `https://ekgf.github.io/dprod/` | Extensions (State, deadline, recurrence, DataOffer, DataContract, path, select, hierarchy) + domain-specific actions, operands, and concept values |

---

## Conformance

An implementation conforms to DPROD Contracts if:

1. It accepts policies that validate against `dprod-contracts-shapes.ttl`
2. It uses `odrl:Permission`, `odrl:Duty`, `odrl:Prohibition`, `odrl:Agreement` for standard constructs
3. Its evaluation function produces identical results for identical inputs
4. All functions are total (no undefined behavior)
5. State transitions match the operational semantics
6. Agreement evaluation returns duties for both assigner and assignee

---

## References

- [ODRL 2.2 Information Model](https://www.w3.org/TR/odrl-model/)
- [W3C Market Data Profile](https://www.w3.org/2021/md-odrl-profile/v1/)
- [W3C ODRL Profile Best Practices](https://www.w3.org/community/reports/odrl/CG-FINAL-profile-bp-20240808.html)

---

**Version**: 0.7 | **Date**: 2026-02-04
