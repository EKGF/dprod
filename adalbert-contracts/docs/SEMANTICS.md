---
title: "Adalbert Formal Semantics"
subtitle: "Deterministic Policy Evaluation for Data Governance"
version: "0.7"
status: "Draft"
date: 2026-02-03
abstract: |
  Adalbert is a proper ODRL 2.2 profile with deterministic, total evaluation
  semantics and bilateral agreement support. This document specifies the formal
  semantics in a style amenable to mechanization in Dafny, Why3, or similar
  verification frameworks.
---

## 1. Introduction

Adalbert addresses semantic gaps in ODRL 2.2:

1. **Duty Ambiguity**: ODRL conflates pre-conditions with post-obligations
2. **Unilateral Agreements**: ODRL evaluates only from assignee perspective
3. **Undefined States**: ODRL permits evaluation to be "undefined"

Adalbert provides:

- Explicit duty lifecycle with state machine semantics
- Bilateral agreement evaluation (grantor and grantee duties)
- Total evaluation functions (always terminate with defined result)
- Clear separation of Condition (pre-requisite) from Duty (obligation)
- Path-based operand resolution with formal grammar and security constraints

### 1.1 Scope and Runtime Boundary

This specification defines **evaluation semantics** — the contract a conformant engine
must satisfy. The `State` parameter in `Eval` is an opaque input provided by the
runtime environment. Adalbert specifies what decision and state transitions *should*
result from evaluation, but does not define:

- How `State` is persisted or managed between evaluations
- Event-driven triggers for duty activation or deadline enforcement
- Protocols for requirement fulfillment claims or re-evaluation

These operational concerns are out of scope for a declarative policy profile.
Implementations requiring runtime state management, event processing, and enforcement
protocols should consult RL2, which extends Adalbert's evaluation semantics with a
complete operational protocol layer.

### 1.2 Notation

- `×` for Cartesian product
- `→` for function types
- `∪` for union
- `∈` for set membership
- `⊥` for undefined/bottom value
- `⟦e⟧` for denotation of expression `e`
- `Γ ⊢ e : τ` for typing judgement ("in context Γ, expression e has type τ")

### 1.2 Document Status

This document is **normative** for Adalbert implementations.

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

We define Adalbert's abstract syntax using a typed algebraic grammar.

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
- The formal `subject` parameter maps to `adalbert:subject` on duties (rdfs:subPropertyOf `odrl:assignee`) and to `odrl:assignee` on permissions/prohibitions.
- The formal `object` parameter (duties only) maps to `adalbert:object` — the party affected by the duty action (e.g., who is notified). Not used in norm matching.
- `AbsoluteDeadline`: Fixed point in time (e.g., 2026-12-31T23:59:59Z)
- `RelativeDeadline`: Duration from activation (e.g., P30D, PT24H)

**Abstract-to-RDF Name Mapping**:

| Abstract Syntax | RDF Encoding | Notes |
|---|---|---|
| `Permission` | `odrl:Permission` | |
| `Duty` | `odrl:Duty` | |
| `Prohibition` | `odrl:Prohibition` | |
| `subject` (Permission/Prohibition) | `odrl:assignee` | Party to whom the norm applies |
| `subject` (Duty) | `adalbert:subject` | Party bearing the duty (rdfs:subPropertyOf odrl:assignee) |
| `object` (Duty) | `adalbert:object` | Party affected by the duty action (metadata, not used in matching) |
| `grantor` | `odrl:assigner` | Party granting rights |
| `grantee` | `odrl:assignee` | Party receiving rights (policy-level) |
| `condition` | `odrl:constraint` | |
| `Set` | `odrl:Set` | |
| `Offer` | `odrl:Offer` | `DataContract` is a subtype |
| `Agreement` | `odrl:Agreement` | `Subscription` is a subtype |
| `lte` | `odrl:lteq` | |
| `gte` | `odrl:gteq` | |
| `recurrence` | `adalbert:recurrence` | RFC 5545 RRULE string |

### 3.3 Conditions

```
Condition ::= AtomicConstraint(leftOperand: LeftOperand,
                               operator: ComparisonOperator,
                               rightOperand: Value)
            | And(operands: Condition+)
            | Or(operands: Condition+)
            | Not(operand: Condition)

ComparisonOperator ::= eq | neq | lt | lte | gt | gte | isAnyOf | isNoneOf

RuntimeRef ::= currentAgent | currentDateTime
```

**Notes**:

- `leftOperand` is drawn from profile-defined operands with `resolutionPath`, or dual-typed `RuntimeReference` operands (e.g., `currentDateTime`)
- Dynamic value resolution on the left side uses `LeftOperand` with `adalbert:resolutionPath` or dual-typed `RuntimeReference` operands resolved via `resolveRuntime`
- Right operands are literal values. Identity binding via runtime references in right-operand position is deferred to RL2 (`rl2:rightOperandRef`)

### 3.4 Policies

```
Policy ::= Set(target: Asset?, clauses: Norm+, condition: Condition?)
         | Offer(grantor: Agent, grantee: Agent?, target: Asset?, clauses: Norm+, condition: Condition?)
         | Agreement(grantor: Agent, grantee: Agent, target: Asset?, clauses: Norm+, condition: Condition?)
```

**Notes**:

- `Set`: Unilateral declaration, no parties. Maps to `odrl:Set` in the RDF encoding.
- `Offer`: Proposal from grantor, grantee optional (open offer). Maps to `odrl:Offer`. `DataContract` is a subtype of `Offer`.
- `Agreement`: Bilateral binding, both parties identified. Maps to `odrl:Agreement`. `Subscription` is a subtype of `Agreement`.
- The formal `grantor` parameter maps to `odrl:assigner` (the party granting rights) in the RDF encoding.
- The formal `grantee` parameter maps to `odrl:assignee` (the party receiving rights) in the RDF encoding.

### 3.5 Requests

```
Request ::= Request(agent: Agent, action: Action, asset: Asset, context: Context)

Context ::= Map<String, Value>
```

**Note**: Context keys correspond to the second segment of resolution paths (e.g., the path `context.purpose` resolves by looking up `"purpose"` in `Context`).

---

## 4. Semantic Domains

### 4.1 State

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

- `State` is a unified lifecycle enum shared by duties, contracts, and subscriptions. The formal semantics tracks duty state during evaluation; contract and subscription state is administrative (not evaluated at request time).
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

### 4.2 Environment

```
Env = {
    agent   : Agent,          // Canonical root: agent
    action  : Action,
    asset   : Asset,          // Canonical root: asset
    context : Context,        // Canonical root: context
    Σ       : Σ
}
```

The three canonical roots (`agent`, `asset`, `context`) are the entry points for `deref` path resolution (see §6.3).

**Environment Construction**: Given a Request `R = (a, x, s, ctx)` and state Σ:

```
buildEnv(R, Σ) = {
    agent   = R.agent,
    action  = R.action,
    asset   = R.asset,
    context = R.context,
    Σ       = Σ
}
```

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
        Pending → if d.condition = ⊥ ∨ ⟦d.condition⟧(Env)
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

Action and asset matching support hierarchy subsumption:

```
x₁ matches x₂ ⟺ x₁ = x₂ ∨ x₁ includedIn⁺ x₂
s₁ matches s₂ ⟺ s₁ = s₂ ∨ s₁ partOf⁺ s₂
```

Where `includedIn⁺` and `partOf⁺` are the transitive closures of `odrl:includedIn` and `adalbert:partOf` respectively.

Agent matching supports hierarchy subsumption:

```
a₁ matches a₂ ⟺ a₁ = a₂ ∨ a₁ memberOf⁺ a₂
```

Where `memberOf⁺` is the transitive closure of `adalbert:memberOf`.

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
⟦_⟧ : Condition × Env → Boolean
```

**Atomic constraints**:

```
⟦AtomicConstraint(left, op, right)⟧(Env) =
    let leftVal = resolve(left, Env)
    in if leftVal = ⊥ then false
       else apply(op, leftVal, right)
```

**Logical connectives** (short-circuit evaluation, left-to-right):

```
⟦And(c₁, ..., cₙ)⟧(Env) = ⟦c₁⟧(Env) ∧ ... ∧ ⟦cₙ⟧(Env)
⟦Or(c₁, ..., cₙ)⟧(Env)  = ⟦c₁⟧(Env) ∨ ... ∨ ⟦cₙ⟧(Env)
⟦Not(c)⟧(Env)           = ¬⟦c⟧(Env)
```

**Evaluation Order**: `And` evaluates left-to-right, short-circuiting on `false`. `Or` evaluates left-to-right, short-circuiting on `true`. This ensures deterministic evaluation and enables optimizations.

### 6.2 Helper Function Specifications

The condition semantics rely on several helper functions. For a verified kernel, these must be precisely specified.

#### resolve : LeftOperand × Env → Value

The function `resolve(leftOperand, Env)` maps a left operand to a value.

**Resolution Precedence**: Operands are resolved in the following order:

1. **Path-based resolution** — if `op.resolutionPath` is defined, use `deref()`
2. **Fallback** — return `⊥`

```
resolve : LeftOperand × Env → Value ∪ {⊥}

resolve(op, Env) =
    case op of
        -- Profile-declared operands with resolution path
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, Env)

        -- Dual-typed operands (LeftOperand ∩ RuntimeReference)
        _ | op ∈ RuntimeRef →
            resolveRuntime(op, Env)

        -- No resolution path and not a runtime reference
        _ → ⊥
```

Where:
* `op.resolutionPath` — path expression declared on the operand via `adalbert:resolutionPath`
* `op ∈ RuntimeRef` — the operand is also typed as `adalbert:RuntimeReference` (e.g., `currentDateTime`); resolution delegates to `resolveRuntime` (§6.2). Path-based resolution takes precedence.
* `⊥` indicates undefined (condition evaluates to `false` when encountered — see §6.1)

**Architectural Principle**: All contextual data access MUST go through declared `odrl:LeftOperand` instances with explicit `adalbert:resolutionPath`, or through dual-typed `RuntimeReference` operands resolved via `resolveRuntime`. This ensures:
- Type safety (operands can declare expected ranges via `rdfs:range`)
- Validation (SHACL can verify operand usage at authoring time)
- Mechanization (clear mapping to formal verification targets)
- Auditability (all data access points are declared in the profile)

Profiles define domain-specific left operands with resolution paths:
* `purpose` → `adalbert:resolutionPath "context.purpose"`
* `classification` → `adalbert:resolutionPath "asset.classification"`
* `role` → `adalbert:resolutionPath "agent.role"`
* `environment` → `adalbert:resolutionPath "context.environment"`
* `timeliness` → `adalbert:resolutionPath "asset.timeliness"`
* `organization` → `adalbert:resolutionPath "agent.organization"`

#### deref : Path × Env → Value

The function `deref(path, Env)` traverses a path expression to retrieve a value. This is the **primary mechanism for resolving profile-declared operands** via `adalbert:resolutionPath`.

**Path Grammar** (normative):

All path expressions MUST conform to the following grammar:

```
Path       ::= Root '.' Segment ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context'
Segment    ::= Identifier
Identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
```

Constraints:
- Paths MUST begin with a valid Root
- Identifiers MUST NOT contain `.`, `/`, `..`, or URL-encoded characters
- Minimum path depth: 2 segments (root + at least one identifier)
- Maximum path depth: 10 segments (implementation MAY enforce)

Paths not conforming to this grammar MUST be rejected at parse time, not at evaluation time. This ensures that malformed paths cannot be used to probe for valid segments.

**Canonical Path Roots** (normatively defined):

| Root | Meaning | Example Paths |
|------|---------|---------------|
| `agent` | Env.agent (requesting agent) | `agent.role`, `agent.organization`, `agent.costCenter` |
| `asset` | Env.asset (requested asset) | `asset.classification`, `asset.sensitivity`, `asset.timeliness` |
| `context` | External request context | `context.purpose`, `context.environment`, `context.jurisdiction` |

```
deref : Path × Env → Value ∪ {⊥}

deref(path, Env) =
    let segments = split(path, '.')
    let root = case head(segments) of
        "agent"   → Env.agent
        "asset"   → Env.asset
        "context" → Env.context
        _         → ⊥
    in foldl(navigate, root, tail(segments))

navigate(obj, segment) =
    case obj of
        ⊥       → ⊥
        Record  → obj.segment if segment ∈ fields(obj) else ⊥
        Map     → obj[segment] if segment ∈ keys(obj) else ⊥
        _       → ⊥
```

**Security Requirement: Path Sandboxing** (normative)

Implementations MUST enforce a strict sandbox for `deref` operations. The evaluator MUST reject any path that:

1. Contains directory traversal sequences (e.g., `..`, `/`, `\`)
2. References roots other than the canonical set (`agent`, `asset`, `context`)
3. Contains URL-encoded characters or escape sequences
4. Attempts to access host system variables or environment settings not explicitly mapped to the `Env` object

Rationale: Without these constraints, a malicious path like `context.../../private/key` could escape the policy evaluation sandbox and access host system resources. Path validation MUST occur at parse time to prevent timing-based probing attacks.

**Security Requirements Summary** (normative):

1. **Root validation**: Reject paths not starting with a canonical root (`agent`, `asset`, `context`)
2. **Grammar validation**: Reject paths containing `..`, `/`, `%`, or other traversal/encoding patterns
3. **Depth limiting**: MAY reject paths exceeding implementation-defined maximum depth
4. **Fail-closed**: Return `⊥` (not an error message) for invalid paths to prevent information leakage

These constraints prevent path traversal attacks and unauthorized data access via malformed resolution paths.

#### resolveRuntime : RuntimeRef × Env → Value

Runtime references resolve to values at evaluation time. These are used by `resolve()` for dual-typed left operands (§6.2) — operands typed as both `odrl:LeftOperand` and `adalbert:RuntimeReference` (e.g., `currentDateTime`).

```
resolveRuntime : RuntimeRef × Env → Value ∪ {⊥}

resolveRuntime(ref, Env) =
    case ref of
        currentAgent    → Env.agent
        currentDateTime → Env.Σ.clock
        _               → ⊥  -- Unknown runtime reference
```

#### apply : ComparisonOperator × Value × Value → Boolean

The function `apply(op, left, right)` applies a comparison operator:

```
apply : ComparisonOperator × Value × Value → Boolean

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

**Type requirements**: Comparison operators `lt`, `lte`, `gt`, `gte` require that both operands are of a comparable type (numbers, dates, durations). If operands are not comparable, the operator returns `false`.

---

## 7. Policy Evaluation

### 7.1 Evaluation Function Signature

```
Eval : Request × Set<Policy> × Σ → Result
```

### 7.2 Evaluation Algorithm

```
Eval(request, policies, Σ) =
    let Env = buildEnv(request, Σ)

    // Step 0: Find applicable policies
    let applicable = { p ∈ policies | PolicyApplicable(p, Env) }

    // Step 1: Collect matching norms within applicable policies
    let prohibitions = { n ∈ p.clauses | p ∈ applicable, n : Prohibition, matches(n, request) }
    let permissions  = { n ∈ p.clauses | p ∈ applicable, n : Permission, matches(n, request) }
    let allDuties    = { n ∈ p.clauses | p ∈ applicable, n : Duty, matches(n, request) }

    // Step 2: Partition duties by bearer (bilateral)
    let grantorDuties = { d ∈ allDuties | d.subject = policy(d).grantor }
    let granteeDuties = { d ∈ allDuties | d.subject = policy(d).grantee }

    // Step 3: Update duty states
    let Σ' = updateDutyStates(allDuties, Env, Σ)

    // Step 4: Check for active prohibitions (prohibition overrides)
    if ∃p ∈ prohibitions. NormActive(p, Env) then
        return {decision: Deny, ...}

    // Step 5: Check for granting privilege
    if ∄p ∈ permissions. NormActive(p, Env) then
        return {decision: NotApplicable, ...}

    // Step 6: Check for violations
    let violated = { d ∈ allDuties | Σ'.state(d) = Violated }
    if violated ≠ ∅ then
        return {decision: Deny, violations: violated, ...}

    // Step 7: Collect active duties for both parties
    let activeGrantor = { d ∈ grantorDuties | Σ'.state(d) = Active }
    let activeGrantee = { d ∈ granteeDuties | Σ'.state(d) = Active }

    return {
        decision: Permit,
        grantorDuties: activeGrantor,
        granteeDuties: activeGrantee,
        violations: ∅
    }
```

### 7.3 Policy Applicability

```
PolicyApplicable(p, Env) =
    // Target matches (if specified)
    (p.target = ⊥ ∨ Env.asset matches p.target) ∧
    // Policy condition satisfied
    (p.condition = ⊥ ∨ ⟦p.condition⟧(Env))
```

For Agreements (including Subscriptions), the agent must be a party:

```
PolicyApplicable(Agreement(grantor, grantee, ...), Env) =
    ... ∧ (Env.agent matches grantee ∨ Env.agent matches grantor)
```

### 7.4 Norm Activation

A norm within a policy is active when both the policy is applicable and the norm's own conditions hold:

```
NormActive(norm, Env) =
    (norm.subject = ⊥ ∨ norm.subject = Env.agent ∨ norm.subject = *
     ∨ Env.agent memberOf⁺ norm.subject) ∧
    norm.action matches Env.action ∧
    (norm.asset = ⊥ ∨ norm.asset matches Env.asset) ∧
    (norm.condition = ⊥ ∨ ⟦norm.condition⟧(Env))
```

Where `⊥` indicates no assignee specified (rule applies to any requesting agent), `*` is the wildcard agent, and `memberOf⁺` is transitive party membership. In standard ODRL usage, Set and Offer policies omit `odrl:assignee` on rules that apply to any requesting agent; `adalbert:currentAgent` is reserved for constraint comparisons (identity binding), not for assignee position.

---

## 8. Conflict Resolution

### 8.1 Strategy: Prohibition Overrides

Adalbert uses a fixed conflict resolution strategy:

```
Prohibition > Permission
```

If both a prohibition and permission match, the prohibition wins. This strategy is not configurable in Adalbert (RL2 offers configurable strategies).

### 8.2 Algorithm

```
resolveDecision(prohibitions, permissions) =
    if ∃p ∈ prohibitions. active(p) then
        Deny
    else if ∃p ∈ permissions. active(p) then
        Permit
    else
        NotApplicable
```

No specificity ordering within norm types. All matching norms contribute.

**Note**: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

---

## 9. Correctness Properties

**Note on recurrence**: All four theorems below hold in the presence of `recurrence`. The `expand` function is total and deterministic (§5.5), each generated instance follows the standard lifecycle independently, and recurrence applies only to duties — permissions and prohibitions are unaffected.

### 9.1 Totality

**Theorem**: For all well-formed inputs, `Eval` terminates with a defined result.

```
∀ request, policies, Σ.
    WellFormed(request) ∧ WellFormed(policies) ∧ WellFormed(Σ)
    ⟹ ∃ result. Eval(request, policies, Σ) = result ∧ result ≠ ⊥
```

### 9.2 Determinism

**Theorem**: Evaluation is deterministic.

```
∀ request, policies, Σ.
    Eval(request, policies, Σ) = r₁ ∧ Eval(request, policies, Σ) = r₂
    ⟹ r₁ = r₂
```

### 9.3 Prohibition Monotonicity

**Theorem**: Adding policies cannot remove prohibitions.

```
∀ request, P, P', Σ.
    P ⊆ P' ∧ Eval(request, P, Σ).decision = Deny
    ⟹ Eval(request, P', Σ).decision = Deny
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

### 9.5 Path Resolution Safety

**Theorem**: Path resolution is sandboxed.

```
∀ path, Env.
    ¬conformsToGrammar(path) ⟹ deref(path, Env) = ⊥
```

**Theorem**: Path resolution cannot escape canonical roots.

```
∀ path, Env.
    deref(path, Env) ≠ ⊥ ⟹ head(split(path, '.')) ∈ {"agent", "asset", "context"}
```

**Theorem**: Path resolution is total and fail-closed.

```
∀ path, Env.
    conformsToGrammar(path) ⟹ deref(path, Env) ∈ Value ∪ {⊥}
```

---

## 10. Complexity and Constraints

*This section is non-normative.*

Adalbert evaluation is designed to be **polynomial-time** and **total** under the following constraints.

### 10.1 Structural Constraints

1. **Finite policy universe**: The set of policies is finite
2. **Bounded condition nesting**: Conditions have bounded depth (recommended ≤ 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite Σ**: State contains finite sets (performed actions, duty states)
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### 10.2 Path Resolution Constraints

6. **Bounded path depth**: Maximum 10 segments (enforced by grammar)
7. **No joins**: Path resolution is single-threaded navigation, not graph pattern matching
8. **Deterministic navigation**: Each segment resolves to exactly one value or `⊥`

### 10.3 Complexity Analysis

Given these constraints:

| Operation | Complexity |
|-----------|------------|
| Path resolution (`deref`) | O(d) where d = path depth |
| Condition evaluation | O(n × d) where n = condition tree size |
| Norm matching | O(\|P\| × m) where m = max clauses per policy |
| Hierarchy traversal (`matches`) | O(h) where h = hierarchy depth |
| Conflict resolution | O(k) where k = matched norms |
| **Total `Eval`** | **O(\|P\| × m × n × d × h)** — polynomial |

### 10.4 Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (resolution is synchronous or fails to `⊥`)
- Diverges due to condition structure (bounded, acyclic)

---

## 11. Profile Extension Points

### 11.1 Left Operands

Profiles attach Adalbert resolution paths to operands. Standard ODRL operands (like `odrl:purpose`) are extended in-place; domain-specific operands are declared as new `odrl:LeftOperand` instances:

```turtle
# Extend an existing ODRL operand with a resolution path
odrl:purpose adalbert:resolutionPath "context.purpose" .

# Declare a new domain-specific operand
adalbert-due:timeliness a odrl:LeftOperand ;
    adalbert:resolutionPath "asset.timeliness" .
```

The `resolutionPath` value must conform to the path grammar defined in §6.2 (`deref`). SHACL validation enforces that all resolution paths start with a canonical root:

```turtle
adalbertsh:LeftOperandShape a sh:NodeShape ;
    sh:targetClass odrl:LeftOperand ;
    sh:property [
        sh:path adalbert:resolutionPath ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^(agent|asset|context)\\." ;
        sh:message "resolutionPath must start with agent., asset., or context."
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
    adalbert:partOf ex:customerSchema .
```

Asset subsumption is defined by the transitive closure of `adalbert:partOf`:

```
s' ⊑ s  :=  reachable(s', adalbert:partOf, s)
```

### 11.4 Agent Hierarchies

```turtle
ex:analyst adalbert:memberOf ex:analyticsTeam .
ex:analyticsTeam adalbert:memberOf ex:dataDivision .
```

Agent subsumption is defined by the transitive closure of `adalbert:memberOf`:

```
a' ⊑ a  :=  reachable(a', adalbert:memberOf, a)
```

Policy on `ex:dataDivision` applies to `ex:analyst` via transitivity.

---

## 12. Bilateral Agreement Semantics

### 12.1 Motivation

ODRL 2.2 evaluates agreements from the assignee's perspective only. This prevents modeling provider obligations (SLAs, data quality commitments).

Adalbert fixes this: evaluation returns duties for **both** parties.

### 12.2 Formal Definition

For an Agreement (or Subscription), duties are partitioned by bearer:

```
grantorDuties(agreement) = { d ∈ agreement.clauses | d : Duty ∧ d.subject = agreement.grantor }
granteeDuties(agreement) = { d ∈ agreement.clauses | d : Duty ∧ d.subject = agreement.grantee }
```

Both sets are included in the evaluation result, with independent lifecycle tracking.

### 12.3 Example

```turtle
@prefix ex:   <http://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix adalbert:     <https://vocabulary.bigbank/adalbert/> .
@prefix adalbert-due: <https://vocabulary.bigbank/adalbert/due/> .
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
        adalbert:subject ex:analyticsTeam ;
        adalbert:object ex:dataTeam ;
        odrl:action adalbert-due:report ;
        odrl:target ex:usageStats ;
        adalbert:deadline "P30D"^^xsd:duration
    ] ;

    # Assigner duty (provider notifies consumer)
    odrl:obligation [
        a odrl:Duty ;
        adalbert:subject ex:dataTeam ;
        adalbert:object ex:analyticsTeam ;
        odrl:action adalbert-due:notify ;
        odrl:target ex:schemaChanges ;
        adalbert:deadline "P7D"^^xsd:duration
    ] .
```

Evaluation returns:
- `granteeDuties`: report usage within 30 days
- `grantorDuties`: notify of schema changes within 7 days

---

## 13. Mechanization

*This section is non-normative.*

Adalbert's semantics are explicitly designed for mechanization. The abstract syntax maps to algebraic datatypes, and the operational rules are syntax-directed.

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

function Deref(path: string, env: Env): Option<Value>
  requires ValidPath(path)
  ensures Deref(path, env).None? ==> !PathResolvable(path, env)
{
  var segments := Split(path, '.');
  var root := match segments[0]
    case "agent" => Some(env.agent)
    case "asset" => Some(env.asset)
    case "context" => Some(env.context)
    case _ => None;
  FoldNavigate(root, segments[1..])
}

function Resolve(op: LeftOperand, env: Env): Option<Value>
  requires ValidEnv(env)
{
  if op.resolutionPath.Some? then Deref(op.resolutionPath.value, env)
  else None
}

function EvalCondition(c: Condition, env: Env): bool
  requires ValidEnv(env)
  ensures EvalCondition(c, env) ==> ConditionSatisfied(c, env)
{
  match c
    case AtomicConstraint(op, cmp, val) =>
      var leftVal := Resolve(op, env);
      if leftVal.None? then false
      else Apply(cmp, leftVal.value, val)
    case And(l, r) => EvalCondition(l, env) && EvalCondition(r, env)
    case Or(l, r) => EvalCondition(l, env) || EvalCondition(r, env)
    case Not(inner) => !EvalCondition(inner, env)
}
```

Transition rules are expressed as Dafny lemmas with pre/post-conditions verified by Z3.

### 13.3 Proof Obligations

The following properties should be proved for a verified implementation:

1. **(S1) Determinism**: Given Σ, request, policies, evaluation produces a unique result
2. **(S2) Totality**: `Eval` terminates for all well-formed inputs
3. **(S3) Duty-state consistency**: No duty can be simultaneously in two states
4. **(S4) Terminal permanence**: Fulfilled/Violated states never revert
5. **(S5) Path safety**: `deref` returns `⊥` for any non-conforming path
6. **(S6) Prohibition monotonicity**: Adding policies cannot remove prohibitions

---

## 14. References

- [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/)
- [ODRL Vocabulary 2.2](https://www.w3.org/TR/odrl-vocab/)
- [RL2 Formal Semantics](../../RL2/RL2_Semantics.md)
- Adalbert Core Ontology — `ontology/adalbert-core.ttl`
- Adalbert SHACL Shapes — `ontology/adalbert-shacl.ttl`
- Adalbert DUE Profile — `profiles/adalbert-due.ttl`
