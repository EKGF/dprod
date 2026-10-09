---
title: "DPROD Contracts Formal Semantics"
subtitle: "Deterministic Policy Evaluation for Data Governance"
version: "0.7"
status: "Draft"
date: 2026-08-20
abstract: |
  DPROD Contracts is a proper ODRL 2.2 profile with deterministic, total evaluation
  semantics and bilateral agreement support. This document specifies the formal
  semantics in a style amenable to mechanization in Dafny, Why3, or similar
  verification frameworks.
---

## 1. Introduction

DPROD Contracts addresses semantic gaps in ODRL 2.2:

1. **Duty Ambiguity**: ODRL conflates pre-conditions with post-obligations
2. **Unilateral Agreements**: ODRL evaluates only from assignee perspective
3. **Undefined States**: ODRL permits evaluation to be "undefined"

DPROD Contracts provides:

- Explicit duty lifecycle with state machine semantics
- Bilateral agreement evaluation (grantor and grantee duties)
- Total evaluation functions (always terminate with defined result)
- Clear separation of Condition (pre-requisite) from Duty (obligation)
- One-hop operand resolution over normalized request, state, and context graphs

### 1.1 Scope and Runtime Boundary

This specification defines **evaluation semantics** — the contract a conformant engine
must satisfy. The duty `State` and immutable `WorldSnapshot` parameters in `Eval`
are opaque inputs provided by the runtime environment. DPROD Contracts specifies
what outcome and state transitions *should* result from evaluation, but does not define:

- How `State` is persisted or managed between evaluations
- How the runtime obtains facts before freezing them into `WorldSnapshot`
- Event-driven triggers for duty activation or deadline enforcement
- Protocols for requirement fulfillment claims or re-evaluation

These operational concerns are out of scope for a declarative policy profile.
Implementations requiring runtime state management, event processing, and enforcement
protocols should consult RL2, which extends DPROD Contracts's evaluation semantics with a
complete operational protocol layer.

### 1.2 Notation

- `×` for Cartesian product
- `→` for function types
- `∪` for union
- `∈` for set membership
- `⊥` for undefined/bottom value
- `⟦e⟧` for denotation of expression `e`
- `Γ ⊢ e : τ` for typing judgement ("in context Γ, expression e has type τ")

### 1.3 Document Status

This document is **normative** for DPROD Contracts implementations.

---

## 2. Type System

The type system ensures well-formed policies.

### 2.1 Typing Judgements

We use:

```
Γ ⊢ e : τ
```

Where Γ is a typing context mapping identifiers to types.

### 2.2 Types

```
τ ::= Agent | Action | Asset | Condition | Time | Duration | Boolean | Value | Norm | State | Policy
```

### 2.3 Key Typing Rules

Permission:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset     Γ ⊢ c : Condition
---------------------------------------------------------------------------
       Γ ⊢ Permission(a, x, s, c) : Norm
```

Duty:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition     Γ ⊢ dl : Deadline     Γ ⊢ r : Recurrence
--------------------------------------------------------------------------
        Γ ⊢ Duty(a, x, s, c, dl, r) : Norm
```

Prohibition:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset     Γ ⊢ c : Condition
---------------------------------------------------------------------------
   Γ ⊢ Prohibition(a, x, s, c) : Norm
```

AtomicConstraint:

```
Γ ⊢ left : LeftOperand     Γ ⊢ op : ComparisonOperator     Γ ⊢ right : Value
-------------------------------------------------------------------------------
        Γ ⊢ AtomicConstraint(left, op, right) : Condition
```

Logical connectives follow standard typing rules for Boolean-valued expressions.

---

## 3. Abstract Syntax

We define DPROD Contracts's abstract syntax using a typed algebraic grammar.

### 3.1 Syntactic Domains

| Domain | Symbol | Description |
|--------|--------|-------------|
| Agents | **A** | Set of agent identifiers |
| Actions | **X** | Set of action identifiers |
| Assets | **S** | Set of asset identifiers |
| Values | **V** | Set of atomic values (strings, numbers, URIs) |
| Time | **T** | Time domain (ISO 8601 instants) |
| Duration | **D** | Duration domain (ISO 8601 durations) |

### 3.2 Norms

```
Norm ::= Permission(subject: Agent, action: Action, asset: Asset, condition: Condition?)
       | Duty(subject: Agent, action: Action, asset: Asset,
              object: Agent?, condition: Condition?, deadline: Deadline?, recurrence: Recurrence?)
       | Prohibition(subject: Agent, action: Action, asset: Asset, condition: Condition?)

Deadline ::= AbsoluteDeadline(time: Time)
           | RelativeDeadline(duration: Duration)

Recurrence ::= RRule(rule: String)
```

**Notes**:

- `Permission` corresponds to `odrl:Permission`; `Prohibition` to `odrl:Prohibition`; `Duty` to `odrl:Duty`.
- The formal `subject` parameter maps to `dprod:subjectOfDuty` on duties (rdfs:subPropertyOf `odrl:function`) and to `odrl:assignee` on permissions/prohibitions.
- The formal `object` parameter (duties only) maps to `dprod:objectOfDuty` — the party affected by the duty action (e.g., who is notified). Not used in norm matching.
- `AbsoluteDeadline`: Fixed point in time (e.g., 2026-12-31T23:59:59Z)
- `RelativeDeadline`: Duration from activation (e.g., P30D, PT24H)

**Abstract-to-RDF Name Mapping**:

| Abstract Syntax | RDF Encoding | Notes |
|---|---|---|
| `Permission` | `odrl:Permission` | |
| `Duty` | `odrl:Duty` | |
| `Prohibition` | `odrl:Prohibition` | |
| `subject` (Permission/Prohibition) | `odrl:assignee` | Party to whom the norm applies |
| `subject` (Duty) | `dprod:subjectOfDuty` | Party bearing the duty (rdfs:subPropertyOf odrl:function) |
| `object` (Duty) | `dprod:objectOfDuty` | Party affected by the duty action (metadata, not used in matching) |
| `grantor` | `odrl:assigner` | Party granting rights |
| `grantee` | `odrl:assignee` | Party receiving rights (policy-level) |
| `condition` | `odrl:constraint` | |
| `Set` | `odrl:Set` | |
| `Offer` | `odrl:Offer` | `DataOffer` is a subtype |
| `Agreement` | `odrl:Agreement` | `DataContract` is a subtype |
| `lte` | `odrl:lteq` | |
| `gte` | `odrl:gteq` | |
| `recurrence` | `dprod:recurrence` | RFC 5545 RRULE string |

### 3.3 Conditions

```
Condition ::= AtomicConstraint(leftOperand: LeftOperand,
                               operator: ComparisonOperator,
                               rightOperand: Value)
            | And(operands: Condition+)
            | Or(operands: Condition+)
            | Not(operand: Condition)

ComparisonOperator ::= eq | neq | lt | lte | gt | gte | isAnyOf | isNoneOf
```

**Notes**:

- Every `leftOperand` declares exactly one `dprod:operandSource` and one IRI-valued `dprod:operandProperty`.
- The source is one of `dprod:requestSource`, `dprod:stateSource`, or `dprod:contextSource`; extension sources are not permitted.
- The evaluator performs exactly one property lookup on the selected normalized source node. RDF-list paths and multi-step traversal are not part of the grammar.
- `dprod:currentAgent` binds `contextSource` to `dprod:agent`. Standard ODRL `odrl:dateTime` binds `contextSource` to `dprod:clock`; DPROD does not define a duplicate clock operand.
- Right operands are literal values. ODRL `odrl:rightOperandReference` identifies an externally dereferenced right operand; DPROD source/property bindings are left-operand metadata and are not permitted in right-operand position.

### 3.4 Policies

```
Policy ::= Set(target: Asset?, clauses: Norm+, condition: Condition?)
         | Offer(grantor: Agent, grantee: Agent?, target: Asset?, clauses: Norm+, condition: Condition?)
         | Agreement(grantor: Agent, grantee: Agent, target: Asset?, clauses: Norm+, condition: Condition?)
```

**Notes**:

- `Set`: Unilateral declaration, no parties. Maps to `odrl:Set` in the RDF encoding.
- `Offer`: Proposal from grantor, grantee optional (open offer). Maps to `odrl:Offer`. `DataOffer` is a subtype of `Offer`.
- `Agreement`: Bilateral binding, both parties identified. Maps to `odrl:Agreement`. `DataContract` is a subtype of `Agreement`.
- The formal `grantor` parameter maps to `odrl:assigner` (the party granting rights) in the RDF encoding.
- The formal `grantee` parameter maps to `odrl:assignee` (the party receiving rights) in the RDF encoding.

### 3.5 Requests

```
Request = {
    node    : Node,
    graph   : FiniteGraph,
    agent   : Agent,
    action  : Action,
    asset   : Asset,
    context : Context
}

Context ::= Map<String, Value>
```

The formal `Request` evaluation input is not an RDF `odrl:Request` policy. It is an abstract runtime authorization query evaluated against supported policy types. Until DPROD defines a transition model connecting `odrl:Offer`, `odrl:Request`, and `odrl:Agreement`, an RDF `odrl:Request` is outside the supported policy grammar and MUST be rejected by SHACL validation.

**Normalization requirement**: `Request.graph` MUST materialize every
policy-relevant request fact directly on `Request.node`. For example, the
requested asset's timeliness is copied to `(Request.node, ex:timeliness, value)`
before evaluation. Policies do not traverse through `odrl:target` or party nodes.

---

## 4. Semantic Domains

### 4.1 Duty State

```
Σ = {
    clock       : Time,
    state       : Duty → State,
    activatedAt : Duty → Time?,           // When duty became Active
    performed   : Set<(Agent, Action, Asset, Time)>
}

State ::= Pending | Active | Fulfilled | Violated
```

**Notes**:

- The formal `State` domain contains evaluator-computed duty states only. It does not model authored data-product, offer, or contract lifecycle statuses; those are open SKOS concepts asserted through domain-specific subproperties of `dprod:lifecycleStatus` and remain outside evaluation state Σ.
- Terminal states (`Fulfilled`, `Violated`) are permanent — see §9.4.

**Initial state** Σ₀:

```
Σ₀ = {
    clock       = currentSystemTime,
    state       = λd. Pending,
    activatedAt = λd. ⊥,
    performed   = ∅
}
```

**State Update Notation**: We use `Σ[f ↦ v]` to denote state update:

```
Σ[state(d) ↦ Active] =
    (Σ.clock, Σ.state[d ↦ Active], Σ.activatedAt, Σ.performed)

Σ[state(d) ↦ Active, activatedAt(d) ↦ t] =
    (Σ.clock, Σ.state[d ↦ Active], Σ.activatedAt[d ↦ t], Σ.performed)
```

### 4.2 Evaluation Environment

```
WorldSnapshot = {
    node       : Node,
    graph      : FiniteGraph,
    provenance : Provenance
}

Env = {
    node     : EvaluationContext,
    graph    : FiniteGraph,
    request  : Request,
    world    : WorldSnapshot,
    Σ        : Σ
}
```

`Env.node`, `Env.request.node`, and `Env.world.node` are the three closed operand
sources. `Env.graph` is the union of their finite graphs and these context bindings:
`Env.request.graph`, and `Env.world.graph`:

```
(Env.node, dprod:request, Env.request.node)
(Env.node, dprod:state,   Env.world.node)
(Env.node, dprod:agent,   Env.request.agent)
(Env.node, dprod:clock,   Env.Σ.clock)
```

`WorldSnapshot` is immutable for the duration of evaluation. Its provenance and
the provenance of `Env.node` MUST be retained with the result so the input can be
reconstructed for audit. Operand resolution MUST NOT read a live global graph,
perform a network request, or switch snapshots during evaluation.

Like the request, the world snapshot is normalized: every state fact exposed by
a supported operand is a direct `(WorldSnapshot.node, property, value)` triple.
Normalization is part of environment construction and fails before policy
evaluation if a required source fact cannot be produced unambiguously.

**Environment Construction**: Given a Request `R = (a, x, s, ctx)`, duty state Σ,
and world snapshot W:

```
buildEnv(R, Σ, W) = {
    let E = freshNode()
    node    = E,
    graph   = R.graph ∪ W.graph ∪ {
                  (E, dprod:request, R.node),
                  (E, dprod:state, W.node),
                  (E, dprod:agent, R.agent),
                  (E, dprod:clock, Σ.clock)
              },
    request = R,
    world   = W,
    Σ       = Σ
}
```

For policy matching notation below, `Env.agent`, `Env.action`, and `Env.asset`
are projections of `Env.request`; they are not additional operand-resolution
roots.

### 4.3 Decision

```
Decision ::= Permit | Deny | NotApplicable
```

### 4.4 Evaluation Result

```
Result = {
    decision      : Decision,
    grantorDuties : Set<Duty>,    // Duties on the grantor (data provider)
    granteeDuties : Set<Duty>,    // Duties on the grantee (data consumer)
    violations    : Set<Duty>,
    inputProvenance : Provenance, // EvaluationContext and WorldSnapshot provenance
    explanation   : Explanation
}
```

---

## 5. Duty Lifecycle

### 5.1 State Diagram

```
                    condition becomes true
         ┌─────────────────────────────────────┐
         │                                     ▼
     ┌───────┐                            ┌────────┐
     │Pending│                            │ Active │
     └───────┘                            └────────┘
                                           │     │
                         action performed  │     │  deadline exceeded
                                           ▼     ▼
                                    ┌──────────┐ ┌─────────┐
                                    │Fulfilled │ │Violated │
                                    └──────────┘ └─────────┘
```

### 5.2 Transition Rules

**Rule D-ACTIVATE** (Pending → Active):

```
Σ.state(duty) = Pending
duty.condition = ⊥ ∨ ⟦duty.condition⟧(Env) = true
─────────────────────────────────────────────────
Σ' = Σ[state(duty) ↦ Active, activatedAt(duty) ↦ Σ.clock]
```

Activation is **condition-driven**: when the duty's condition first evaluates to true (or the duty has no condition), the duty becomes active.

**Rule D-FULFILL** (Active → Fulfilled):

```
Σ.state(duty) = Active
performed(duty.subject, duty.action, duty.asset, Σ) = true
effectiveDeadline(duty, Σ) ≥ Σ.clock  ∨  effectiveDeadline(duty, Σ) = ∞
────────────────────────────────────────────────────────────────────────
Σ' = Σ[state(duty) ↦ Fulfilled]
```

Fulfillment is **event-driven**: when a performed action matches the duty's required action (including narrower actions via `includedIn` subsumption), the duty is fulfilled.

**Rule D-VIOLATE** (Active → Violated):

```
Σ.state(duty) = Active
Σ.clock > effectiveDeadline(duty, Σ)
performed(duty.subject, duty.action, duty.asset, Σ) = false
────────────────────────────────────────────────────────────
Σ' = Σ[state(duty) ↦ Violated]
```

Violation is **time-driven**: when the deadline passes without fulfillment, the duty is violated.

**Algorithmic form** (for implementation):

```
updateDutyStates(duties, Env, Σ) =
    foldl(updateOneDuty(Env), Σ, duties)

updateOneDuty(Env)(Σ, d) =
    case Σ.state(d) of
        Pending → if (d.condition = ⊥ ∨ ⟦d.condition⟧(Env)) = true
                  then Σ[state(d) ↦ Active, activatedAt(d) ↦ Σ.clock]
                  else Σ
        Active  → if performed(d.subject, d.action, d.asset, Σ)
                  then Σ[state(d) ↦ Fulfilled]
                  else if Σ.clock > effectiveDeadline(d, Σ)
                  then Σ[state(d) ↦ Violated]
                  else Σ
        _       → Σ  -- Fulfilled/Violated are terminal
```

### 5.3 Effective Deadline

```
effectiveDeadline(duty, Σ) =
    case duty.deadline of
        ⊥                        → ∞
        AbsoluteDeadline(t)      → t
        RelativeDeadline(d)      → Σ.activatedAt(duty) + d
```

### 5.4 Match Semantics

Action, asset, and party matching support hierarchy subsumption:

```
x₁ matches x₂ ⟺ x₁ = x₂ ∨ x₁ includedIn⁺ x₂
s₁ matches s₂ ⟺ s₁ = s₂ ∨ s₁ partOf⁺ s₂
a₁ matches a₂ ⟺ a₁ = a₂ ∨ a₁ partOf⁺ a₂
```

Where `includedIn⁺` is the transitive closure of `odrl:includedIn` and `partOf⁺` is the typed transitive closure of `odrl:partOf`. Asset paths may traverse only `odrl:Asset` to `odrl:AssetCollection` and `odrl:AssetCollection` to `odrl:AssetCollection` edges. Party paths may traverse only `odrl:Party` to `odrl:PartyCollection` and `odrl:PartyCollection` to `odrl:PartyCollection` edges. Cross-kind paths are invalid.

The subsumption-aware performed check is:

```
performed(a, x, s, Σ) :=
    ∃(a', x', s', t) ∈ Σ.performed :
        a' = a ∧ (x' = x ∨ x' includedIn⁺ x) ∧ s' matches s
```

`Σ.performed` records exact actions as they occur. `performed()` is the query-time subsumption check used in all fulfillment and violation rules. This is a bounded graph traversal over the `odrl:includedIn` hierarchy.

### 5.5 Recurrence Semantics

A duty with a `recurrence` field defines a recurring obligation. The recurrence value is an RFC 5545 RRULE string (e.g., `FREQ=DAILY;BYHOUR=6;BYMINUTE=0`).

**Instance Generation**:

```
expand : Recurrence × Time → Set<Time>

expand(RRule(rule), clock) =
    The set of occurrence times generated by parsing rule as an
    RFC 5545 RRULE, evaluated relative to clock.
```

`expand` is a **pure function**: given the same `RRule` value and clock value, it always produces the same set of occurrence times. It is total (an invalid RRULE yields ∅) and deterministic.

**Condition Guard**: If the duty template has a condition, instances are only generated for occurrence times where the condition holds:

```
occurrences(duty, Σ) =
    let times = expand(duty.recurrence, Σ.clock)
    in  { t ∈ times | duty.condition = ⊥ ∨ ⟦duty.condition⟧(Σ.env) }
```

**Per-Instance Lifecycle**:

Each occurrence time `t` from `occurrences(duty, Σ)` produces an independent duty instance:

```
instantiate(duty, t) =
    Duty(subject    = duty.subject,
         action     = duty.action,
         asset      = duty.asset,
         object     = duty.object,
         condition  = ⊥,
         deadline   = duty.deadline,
         recurrence = ⊥)
    with activationTime = t
```

Fields carried from the template: `subject`, `action`, `asset`, `object`, `deadline`. Fields dropped: `condition` (the template condition gates instance generation, not individual instances) and `recurrence` (instances are not themselves recurring).

Each instance follows the standard lifecycle (§5.1–§5.2) independently:
- Activation occurs at the occurrence time `t`
- The `deadline` defines the per-instance fulfillment window from `t`
- Fulfillment and violation are tracked per instance

**Interaction with other fields**:

- `recurrence` defines **when** duty instances are generated (scheduling)
- `deadline` defines **how long** each instance has to be fulfilled (window)
- Permissions and prohibitions are unaffected by recurrence (recurrence applies only to duties)

---

## 6. Condition Evaluation

### 6.1 Denotational Semantics

```
Truth ::= true | false | Err(E)        -- E : non-empty Set<ResolutionError>

⟦_⟧ : Condition × Env → Truth
```

**Atomic constraints**:

```
⟦AtomicConstraint(left, op, right)⟧(Env) =
    let leftVal = resolve(left, Env)
    in case leftVal of
         ResolutionError(e) → Err({e})
         Value(v)           → case apply(op, v, right) of
                                 ResolutionError(e) → Err({e})
                                 b                  → b
```

Missing or invalid runtime data must not be converted to `false`, because that
would confuse an evaluator-capability failure with an unsatisfied business
condition. An error is an unknown truth value: it propagates through the
connectives, and `Eval` returns `Failure` unless the outcome is decided without
it (§7.2).

**Logical connectives** (strong Kleene logic, order-independent):

```
⟦And(c₁, ..., cₙ)⟧(Env) =
    false             if ∃i. ⟦cᵢ⟧(Env) = false
    Err(⋃ errors)     else if ∃i. ⟦cᵢ⟧(Env) = Err(_)
    true              otherwise

⟦Or(c₁, ..., cₙ)⟧(Env) =
    true              if ∃i. ⟦cᵢ⟧(Env) = true
    Err(⋃ errors)     else if ∃i. ⟦cᵢ⟧(Env) = Err(_)
    false             otherwise

⟦Not(c)⟧(Env) =
    case ⟦c⟧(Env) of true → false | false → true | Err(E) → Err(E)
```

where `⋃ errors` is the union of the error sets of the operands that evaluate to `Err`.

**Evaluation Order**: The value of a connective depends only on the set of its operand values, never on their order. `And` is `false` if any operand is `false`, whatever the others are, errors included; `Or` is `true` if any operand is `true`. An implementation may evaluate operands in any order and stop early on a deciding `false` (for `And`) or `true` (for `Or`), but not on an error, since a later operand may still decide the value. Replacing an error by either Boolean never changes a `true` or `false` result.

### 6.2 Helper Function Specifications

The condition semantics rely on several helper functions. For a verified kernel, these must be precisely specified.

#### resolve : LeftOperand × Env → Value ∪ {ResolutionError}

The function `resolve(leftOperand, Env)` selects one normalized source node and
reads one property from it. There is no traversal language, second resolver, or
fallback branch.

```
resolve : LeftOperand × Env → Value ∪ {ResolutionError}

resolve(op, Env) =
    if op.operandSource = ⊥ then
        ResolutionError(MissingSource, op)
    else if op.operandProperty = ⊥ then
        ResolutionError(MissingProperty, op)
    else
        let node = sourceNode(op.operandSource, Env)
        in case node of
             ResolutionError(e) → ResolutionError(e, op)
             Node(n)            → lookupOne(op.operandProperty, n, Env.graph, op.range)
```

**Architectural Principle**: All contextual data access MUST go through declared
`odrl:LeftOperand` instances with exactly one source/property binding. This ensures:
- Type safety (operands can declare expected ranges via `rdfs:range`)
- Validation (SHACL can verify operand usage at authoring time)
- Mechanization (clear mapping to formal verification targets)
- Auditability (all data access points and snapshots are declared and retained)
- Bounded evaluation (one indexed graph lookup per operand)

Profiles define domain-specific bindings:
* `purpose` → `(requestSource, odrl:purpose)`
* `classification` → `(requestSource, ex:classification)`
* `recipientType` → `(requestSource, ex:recipientType)`
* `marketOpen` → `(stateSource, ex:marketOpen)`
* `currentAgent` → `(contextSource, dprod:agent)`
* `odrl:dateTime` → `(contextSource, dprod:clock)`

#### sourceNode : OperandSource × Env → Node ∪ {ResolutionError}

```
sourceNode(source, Env) =
    case source of
        requestSource → Env.request.node
        stateSource   → Env.world.node
        contextSource → Env.node
        _             → ResolutionError(UnknownSource, source)
```

The source enumeration is closed. Merely typing another resource as
`dprod:OperandSource` does not make it valid.

#### lookupOne : IRI × Node × FiniteGraph × Type? → Value ∪ {ResolutionError}

```
lookupOne(property, node, graph, expectedType) =
    if property is not an IRI then
        ResolutionError(InvalidProperty, property)
    else
        let values = { v | (node, property, v) ∈ graph }
        in case values of
             ∅   → ResolutionError(MissingValue, node, property)
             {v} → if expectedType ≠ ⊥ ∧ ¬conforms(v, expectedType)
                   then ResolutionError(TypeMismatch, property, v)
                   else v
             _   → ResolutionError(MultipleValues, node, property)
```

**Safety Properties** (normative):

1. **Closed sources**: Only request, state, and context sources are valid.
2. **IRI-only property**: `operandProperty` MUST be one IRI, never an RDF list.
3. **One hop**: Resolution performs one direct triple lookup and no traversal.
4. **Normalized inputs**: Nested request or state structure is flattened before evaluation.
5. **No external reads**: Lookup is confined to the immutable evaluation graph.
6. **Fail fast**: Missing, multiple, ill-typed, or otherwise unresolvable values are `ResolutionError` values; they never become `false`.
7. **Deterministic**: The same normalized graph and binding produce the same value or the same error.

#### apply : ComparisonOperator × Value × Value → Boolean ∪ {ResolutionError}

The function `apply(op, left, right)` applies a comparison operator:

```
apply : ComparisonOperator × Value × Value → Boolean ∪ {ResolutionError}

apply(op, left, right) =
    case op of
        eq       → left = right
        neq      → left ≠ right
        lt       → left < right
        lte      → left ≤ right
        gt       → left > right
        gte      → left ≥ right
        isAnyOf  → left ∈ right
        isNoneOf → left ∉ right
```

**Type requirements**: Every operator requires operands of the same type: both numbers, both date-times, both durations, both IRIs, or both literals of one datatype. For `isAnyOf` and `isNoneOf`, each member of the right operand must have the left operand's type. `lt`, `lte`, `gt`, and `gte` further require the two values to be ordered: a date-time without a timezone and one with a timezone less than 14 hours apart are not ordered (XML Schema §3.3.7.3), and neither are `P1M` and `P30D`. Otherwise `apply` returns `ResolutionError(Incomparable, op, left, right)`. Returning `false` instead would let `neq`, `isNoneOf`, or `Not` turn a type error into `true`, and would make a prohibition guarded by an ill-typed comparison fail open.

---

## 7. Policy Evaluation

### 7.1 Evaluation Function Signature

```
EvaluationOutcome ::= Success(Result) | Failure(EvaluationError)

EvaluationError = Set<ResolutionError>      -- non-empty

Eval : Request × Set<Policy> × Σ × WorldSnapshot → EvaluationOutcome
```

`Failure(E)` reports every error in `E`, not the first one found, so the outcome does not depend on evaluation order.

### 7.2 Evaluation Algorithm

In the algorithm, returning a `Result` r means `Success(r)`, and `errors(V) = ⋃ { E | Err(E) ∈ V }` collects the errors in a set of truth values. Every step quantifies over sets, and `updateDutyStates` updates each duty independently of the others, so the outcome does not depend on the order of policies, rules, or operands (§9.6). A `Success` decision does not depend on any error; `Failure` may be returned where every way of resolving the errors would give the same decision (§9.7).

```
Eval(request, policies, Σ, world) =
    let Env = buildEnv(request, Σ, world)

    // Conditions are three-valued (§6.1); ∧ and ∨ over truth values are
    // the strong Kleene connectives.

    // Step 0: Find applicable policies; E₀ holds errors in applicability
    let applicable = { p ∈ policies | PolicyApplicable(p, Env) = true }
    let E₀ = errors({ PolicyApplicable(p, Env) | p ∈ policies })

    // Step 1: Collect matching norms within applicable policies
    let prohibitions = { n ∈ p.clauses | p ∈ applicable, n : Prohibition, matches(n, request) }
    let permissions  = { n ∈ p.clauses | p ∈ applicable, n : Permission, matches(n, request) }
    let allDuties    = { n ∈ p.clauses | p ∈ applicable, n : Duty, matches(n, request) }

    // Step 2: Partition duties by bearer (bilateral)
    let grantorDuties = { d ∈ allDuties | d.subject = policy(d).grantor }
    let granteeDuties = { d ∈ allDuties | d.subject = policy(d).grantee }

    // Step 3: Prohibition overrides. An active prohibition denies, even if
    // other rules or policies are in error. If none is active, an error in a
    // prohibition or in a policy's applicability gives Failure, since
    // resolving it could give Deny.
    if ∃p ∈ prohibitions. NormActive(p, Env) = true then
        return {decision: Deny, ...}
    let E₁ = E₀ ∪ errors({ NormActive(p, Env) | p ∈ prohibitions })
    if E₁ ≠ ∅ then
        return Failure(E₁)

    // Step 4: Check for granting privilege. An error in a permission
    // matters only if no permission is active.
    if ∄p ∈ permissions. NormActive(p, Env) = true then
        let E₂ = errors({ NormActive(p, Env) | p ∈ permissions })
        if E₂ ≠ ∅ then
            return Failure(E₂)
        return {decision: NotApplicable, ...}

    // Step 5: Update duty states. A pending duty whose activation condition
    // is in error has an unknown state (E₃) and stays Pending in Σ'.
    let E₃ = errors({ ⟦d.condition⟧(Env) | d ∈ allDuties, Σ.state(d) = Pending, d.condition ≠ ⊥ })
    let Σ' = updateDutyStates(allDuties, Env, Σ)

    // Step 6: Check for violations
    let violated = { d ∈ allDuties | Σ'.state(d) = Violated }
    if violated ≠ ∅ then
        return {decision: Deny, violations: violated, ...}

    // Step 7: A duty in an unknown state could be active
    if E₃ ≠ ∅ then
        return Failure(E₃)

    // Step 8: Collect active duties for both parties
    let activeGrantor = { d ∈ grantorDuties | Σ'.state(d) = Active }
    let activeGrantee = { d ∈ granteeDuties | Σ'.state(d) = Active }

    return {
        decision: Permit,
        grantorDuties: activeGrantor,
        granteeDuties: activeGrantee,
        violations: ∅
    }
```

Duty states advance only when evaluation reaches Step 5, that is, when some permission is active and no prohibition is.

### 7.3 Policy Applicability

```
PolicyApplicable(p, Env) =
    // Target matches (if specified)
    (p.target = ⊥ ∨ Env.asset matches p.target) ∧
    // Policy condition satisfied
    (p.condition = ⊥ ∨ ⟦p.condition⟧(Env))
```

For Agreements (including DataContracts), the agent must be a party:

```
PolicyApplicable(Agreement(grantor, grantee, ...), Env) =
    ... ∧ (Env.agent matches grantee ∨ Env.agent matches grantor)
```

### 7.4 Norm Activation

A norm within a policy is active when both the policy is applicable and the norm's own conditions hold:

```
NormActive(norm, Env) =
    (norm.subject = ⊥ ∨ norm.subject = Env.agent ∨ norm.subject = *
     ∨ Env.agent partOf⁺ norm.subject) ∧
    norm.action matches Env.action ∧
    (norm.asset = ⊥ ∨ norm.asset matches Env.asset) ∧
    (norm.condition = ⊥ ∨ ⟦norm.condition⟧(Env))
```

Where `⊥` indicates no assignee specified (rule applies to any requesting agent), `*` is the wildcard agent, and `partOf⁺` is typed transitive ODRL collection membership. In standard ODRL usage, Set and Offer policies omit `odrl:assignee` on rules that apply to any requesting agent; `dprod:currentAgent` is reserved for constraint comparisons (identity binding), not for assignee position.

---

## 8. Conflict Resolution

### 8.1 Strategy: Prohibition Overrides by Default

DPROD Contracts uses the following conflict resolution strategy by default:

```
Prohibition > Permission
```

If both a prohibition and permission match, the prohibition wins. This default is declared once on the DPROD profile as `odrl:conflict odrl:prohibit`. A policy may override it by declaring its own `odrl:conflict` (for example `odrl:perm`), in which case that policy's strategy applies to its rules instead.

### 8.2 Algorithm

```
resolveDecision(prohibitions, permissions) =
    if ∃p ∈ prohibitions. active(p) = true then
        Deny
    else if ∃p ∈ prohibitions. active(p) = Err(_) then
        Failure
    else if ∃p ∈ permissions. active(p) = true then
        Permit
    else if ∃p ∈ permissions. active(p) = Err(_) then
        Failure
    else
        NotApplicable
```

No specificity ordering within norm types. All matching norms contribute. An active prohibition decides `Deny` even if other rules are in error, and an active permission decides past a permission in error.

**Note**: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

---

## 9. Correctness Properties

**Note on recurrence**: All four theorems below hold in the presence of `recurrence`. The `expand` function is total and deterministic (§5.5), each generated instance follows the standard lifecycle independently, and recurrence applies only to duties — permissions and prohibitions are unaffected.

### 9.1 Totality

**Theorem**: For all well-formed inputs, `Eval` terminates with a defined result.

```
∀ request, policies, Σ, world.
    WellFormed(request) ∧ WellFormed(policies) ∧ WellFormed(Σ) ∧ WellFormed(world)
    ⟹ ∃ outcome. Eval(request, policies, Σ, world) = outcome ∧ outcome ≠ ⊥
```

### 9.2 Determinism

**Theorem**: Evaluation is deterministic.

```
∀ request, policies, Σ, world.
    Eval(request, policies, Σ, world) = o₁ ∧
    Eval(request, policies, Σ, world) = o₂
    ⟹ o₁ = o₂
```

### 9.3 Prohibition Monotonicity

**Theorem**: Adding policies cannot remove prohibitions.

```
∀ request, P, P', Σ, world, r, r'.
    P ⊆ P' ∧
    Eval(request, P, Σ, world) = Success(r) ∧ r.decision = Deny ∧
    Eval(request, P', Σ, world) = Success(r')
    ⟹ r'.decision = Deny
```

### 9.4 Duty Lifecycle Invariants

**Theorem**: Terminal states are permanent.

```
∀ d, Σ, Σ'.
    Σ → Σ' ∧ Σ.state(d) ∈ {Fulfilled, Violated}
    ⟹ Σ'.state(d) = Σ.state(d)
```

**Theorem**: Duty-state consistency (no duty is in two states simultaneously).

```
∀ d, Σ.
    WellFormed(Σ) ⟹ |{ s | Σ.state(d) = s }| = 1
```

### 9.5 Operand Lookup Safety

**Theorem**: Operand resolution performs exactly one graph lookup.

```
∀ op, Env.
    WellFormed(op) ⟹ graphLookupCount(resolve(op, Env)) = 1
```

**Theorem**: Operand properties are IRIs.

```
∀ op.
    WellFormed(op) ⟹ op.operandProperty ∈ IRI
```

**Theorem**: Lookup is total and fail-fast.

```
∀ op, Env.
    resolve(op, Env) ∈ Value ∪ {ResolutionError}
```

### 9.6 Order Independence

**Theorem**: The outcome depends on policies, rules, and constraint operands as sets, not on their order.

```
∀ request, policies, Σ, world, π.
    π a permutation of the policies, of the rules within a policy,
      or of the operands of a logical constraint
    ⟹ Eval(request, π(policies), Σ, world) = Eval(request, policies, Σ, world)
```

It follows from §6.1 (each connective is a function of the set of its operand values), §7.2 (each step quantifies over sets, and `updateDutyStates` changes each duty's state from that duty's own state), and `Failure` carrying the set of errors rather than the first.

### 9.7 Error Soundness

**Theorem**: A successful decision never depends on an error. A *completion* replaces every `Err` produced by an atomic constraint with `true` or `false`.

```
∀ request, policies, Σ, world, r.
    Eval(request, policies, Σ, world) = Success(r)
    ⟹ every completion yields Success(r') with r'.decision = r.decision,
       and if r.decision = Permit then
       r'.grantorDuties = r.grantorDuties ∧ r'.granteeDuties = r.granteeDuties
```

In particular, a type or data error in a prohibition never yields `Permit`. For `Deny` on violations, `r.violations` lists the violations found without resolving any error; a completion may find more. The converse does not hold: `Failure` is returned whenever an error is consulted, which may include cases where every completion agrees.

---

## 10. Complexity and Constraints

*This section is non-normative.*

DPROD Contracts evaluation is designed to be **polynomial-time** and **total** under the following constraints.

### 10.1 Structural Constraints

1. **Finite policy universe**: The set of policies is finite
2. **Bounded condition nesting**: Conditions have bounded depth (recommended ≤ 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite Σ**: State contains finite sets (performed actions, duty states)
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### 10.2 Operand Resolution Constraints

6. **Closed source set**: Request, state, or context only
7. **One property IRI**: RDF lists and traversal expressions are rejected
8. **One lookup**: Resolution returns exactly one value or an explicit `ResolutionError`

### 10.3 Complexity Analysis

Given these constraints:

| Operation | Complexity |
|-----------|------------|
| Operand lookup | O(1) with a predicate index |
| Condition evaluation | O(n) where n = condition tree size |
| Norm matching | O(\|P\| × m) where m = max clauses per policy |
| Hierarchy traversal (`matches`) | O(h) where h = hierarchy depth |
| Conflict resolution | O(k) where k = matched norms |
| **Total `Eval`** | **O(\|P\| × m × n × h)** — polynomial |

### 10.4 Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (resolution is confined to the supplied finite graph)
- Diverges due to condition structure (bounded, acyclic)

---

## 11. Profile Extension Points

### 11.1 Left Operands

Profiles bind operands to one direct property on one normalized source. Standard
ODRL operands can be extended in place; domain-specific operands are declared as
new `odrl:LeftOperand` instances:

```turtle
# Built-in context values
dprod:currentAgent
    dprod:operandSource dprod:contextSource ;
    dprod:operandProperty dprod:agent .

odrl:dateTime
    dprod:operandSource dprod:contextSource ;
    dprod:operandProperty dprod:clock .

# Direct property on the normalized request
ex:timeliness a odrl:LeftOperand ;
    dprod:operandSource dprod:requestSource ;
    dprod:operandProperty ex:timeliness .

# Direct property on the normalized world snapshot
ex:marketOpen a odrl:LeftOperand ;
    dprod:operandSource dprod:stateSource ;
    dprod:operandProperty ex:marketOpen .
```

SHACL validation enforces the closed source set and single-property cardinality:

```turtle
dprod-shapes:LeftOperandShape a sh:NodeShape ;
    sh:targetClass odrl:LeftOperand ;
    sh:targetObjectsOf odrl:leftOperand ;
    sh:property [
        sh:path dprod:operandSource ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:in (dprod:requestSource dprod:stateSource dprod:contextSource)
    ] ;
    sh:property [
        sh:path dprod:operandProperty ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:nodeKind sh:IRI
    ] .
```

### 11.2 Action Hierarchies

```turtle
odrl:display a odrl:Action ;
    odrl:includedIn odrl:use .
```

Action subsumption is defined by the transitive closure of `odrl:includedIn`:

```
x' ⊑ x  :=  reachable(x', odrl:includedIn, x)
```

Evaluators MUST support transitive traversal of `odrl:includedIn`.

### 11.3 Asset Hierarchies

```turtle
ex:customerTable a odrl:Asset ;
    odrl:partOf ex:customerSchema .

ex:customerSchema a odrl:AssetCollection ;
    odrl:partOf ex:customerData .

ex:customerData a odrl:AssetCollection .
```

Asset subsumption is defined by the typed transitive closure of `odrl:partOf`:

```
s' ⊑ s  :=  reachableAsset(s', odrl:partOf, s)
```

Every object in the path MUST be an `odrl:AssetCollection`. Collection membership is explicit: `odrl:source` and collection `odrl:refinement` are outside this profile and fail validation.

### 11.4 Agent Hierarchies

```turtle
ex:analyst a odrl:Party ;
    odrl:partOf ex:analyticsTeam .

ex:analyticsTeam a odrl:PartyCollection ;
    odrl:partOf ex:dataDivision .

ex:dataDivision a odrl:PartyCollection .
```

Agent subsumption is defined by the typed transitive closure of `odrl:partOf`:

```
a' ⊑ a  :=  reachableParty(a', odrl:partOf, a)
```

Policy on `ex:dataDivision` applies to `ex:analyst` via transitivity.

ODRL does not declare `odrl:partOf` transitive. Transitive closure is a mandatory DPROD evaluation rule for valid, typed collection paths; DPROD does not alter the ODRL vocabulary by redeclaring the property.

---

## 12. Bilateral Agreement Semantics

### 12.1 Motivation

ODRL 2.2 evaluates agreements from the assignee's perspective only. This prevents modeling provider obligations (SLAs, data quality commitments).

DPROD Contracts fixes this: evaluation returns duties for **both** parties.

### 12.2 Formal Definition

For an Agreement (or DataContract), duties are partitioned by bearer:

```
grantorDuties(agreement) = { d ∈ agreement.clauses | d : Duty ∧ d.subject = agreement.grantor }
granteeDuties(agreement) = { d ∈ agreement.clauses | d : Duty ∧ d.subject = agreement.grantee }
```

Both sets are included in the evaluation result, with independent lifecycle tracking.

### 12.3 Example

```turtle
@prefix ex:   <http://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://ekgf.org/dprod/spec/develop/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ex:agreement a odrl:Agreement ;
    odrl:assigner ex:dataTeam ;
    odrl:assignee ex:analyticsTeam ;
    odrl:target ex:marketData ;

    # Assignee permission (target inherited from policy)
    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:analyticsTeam ;
        odrl:action odrl:display
    ] ;

    # Assignee duty (consumer reports to provider)
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:analyticsTeam ;
        dprod:objectOfDuty ex:dataTeam ;
        odrl:action ex:report ;
        odrl:target ex:usageStats ;
        dprod:deadline "P30D"^^xsd:duration
    ] ;

    # Assigner duty (provider notifies consumer)
    odrl:obligation [
        a odrl:Duty ;
        dprod:subjectOfDuty ex:dataTeam ;
        dprod:objectOfDuty ex:analyticsTeam ;
        odrl:action ex:notify ;
        odrl:target ex:schemaChanges ;
        dprod:deadline "P7D"^^xsd:duration
    ] .
```

Evaluation returns:
- `granteeDuties`: report usage within 30 days
- `grantorDuties`: notify of schema changes within 7 days

---

## 13. Mechanization

*This section is non-normative.*

DPROD Contracts's semantics are explicitly designed for mechanization. The abstract syntax maps to algebraic datatypes, and the operational rules are syntax-directed.

### 13.1 Target Platforms

| Platform | Strengths | Status |
|----------|-----------|--------|
| **Dafny** | Algebraic types, Z3 backend, compiles to Go/Java/C# | Primary target |
| **Why3** | Multi-prover backend, mature specification language | Alternative |

### 13.2 Dafny Sketch

```dafny
datatype State = Pending | Active | Fulfilled | Violated

datatype Condition =
  | AtomicConstraint(op: LeftOperand, cmp: Operator, val: Value)
  | And(left: Condition, right: Condition)
  | Or(left: Condition, right: Condition)
  | Not(inner: Condition)

datatype ResolutionResult = Resolved(value: Value) | ResolutionFailure(error: ResolutionError)

function SourceNode(source: OperandSource, env: Env): ResolutionResult<Node>
{
  match source
    case RequestSource => Resolved(env.request.node)
    case StateSource => Resolved(env.world.node)
    case ContextSource => Resolved(env.node)
    case _ => ResolutionFailure(UnknownSource(source))
}

function LookupOne(property: IRI, node: Node, graph: FiniteGraph): ResolutionResult
{
  var values := LookupAll(graph, node, property);
  if |values| == 0 then ResolutionFailure(MissingValue(node, property))
  else if |values| > 1 then ResolutionFailure(MultipleValues(node, property))
  else Resolved(Choose(values))
}

function Resolve(op: LeftOperand, env: Env): ResolutionResult
  requires ValidEnv(env)
{
  if !op.operandSource.Some? then ResolutionFailure(MissingSource(op))
  else if !op.operandProperty.Some? then ResolutionFailure(MissingProperty(op))
  else
    match SourceNode(op.operandSource.value, env)
      case ResolutionFailure(error) => ResolutionFailure(error)
      case Resolved(node) =>
        match LookupOne(op.operandProperty.value, node, env.graph)
          case ResolutionFailure(error) => ResolutionFailure(error)
          case Resolved(value) =>
            if op.range.Some? && !Conforms(value, op.range.value)
              then ResolutionFailure(TypeMismatch(op))
            else Resolved(value)
}

datatype Truth = T | F | Err(errors: set<ResolutionError>)

function KAnd(a: Truth, b: Truth): Truth
{
  if a == F || b == F then F
  else if a.Err? && b.Err? then Err(a.errors + b.errors)
  else if a.Err? then a
  else if b.Err? then b
  else T
}

function KNot(a: Truth): Truth
{
  match a
    case T => F
    case F => T
    case Err(e) => Err(e)
}

function KOr(a: Truth, b: Truth): Truth
{
  KNot(KAnd(KNot(a), KNot(b)))
}

// Commutativity and associativity make an n-ary And (§3.3), folded from
// binary KAnd, independent of operand order.
lemma KAndCommutes(a: Truth, b: Truth)
  ensures KAnd(a, b) == KAnd(b, a)
{}

lemma KAndAssociates(a: Truth, b: Truth, c: Truth)
  ensures KAnd(KAnd(a, b), c) == KAnd(a, KAnd(b, c))
{}

function EvalCondition(c: Condition, env: Env): Truth
  requires ValidEnv(env)
{
  match c
    case AtomicConstraint(op, cmp, val) =>
      match Resolve(op, env)
        case ResolutionFailure(error) => Err({error})
        case Resolved(value) =>
          match Apply(cmp, value, val)   // ResolutionFailure if incomparable
            case ResolutionFailure(error) => Err({error})
            case Resolved(b) => if b then T else F
    case And(l, r) => KAnd(EvalCondition(l, env), EvalCondition(r, env))
    case Or(l, r) => KOr(EvalCondition(l, env), EvalCondition(r, env))
    case Not(inner) => KNot(EvalCondition(inner, env))
}
```

Transition rules are expressed as Dafny lemmas with pre/post-conditions verified by Z3.

### 13.3 Proof Obligations

The following properties should be proved for a verified implementation:

1. **(S1) Determinism**: Given Σ, request, policies, evaluation produces a unique result, independent of the order of policies, rules, and operands
2. **(S2) Totality**: `Eval` terminates for all well-formed inputs
3. **(S3) Duty-state consistency**: No duty can be simultaneously in two states
4. **(S4) Terminal permanence**: Fulfilled/Violated states never revert
5. **(S5) Lookup safety**: an unresolvable operand or incomparable comparison produces an explicit `ResolutionError`, never a Boolean result
6. **(S6) Prohibition monotonicity**: Adding policies cannot remove prohibitions
7. **(S7) Error soundness**: A `Success` decision is the same under every completion of its errors, and so are the duties reported with a `Permit`

---

## 14. References

- [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/)
- [ODRL Vocabulary 2.2](https://www.w3.org/TR/odrl-vocab/)
- [RL2 Formal Semantics](../../RL2/RL2_Semantics.md)
- DPROD Contracts Core Ontology — `ontology/dprod-contracts.ttl`
- DPROD Contracts SHACL Shapes — `ontology/dprod-contracts-shapes.ttl`
