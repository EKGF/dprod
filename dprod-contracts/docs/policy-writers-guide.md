# DPROD Policy Writers Guide

A guide for data stewards writing data use policies with DPROD Contracts.

---

## 1. When to Use Policies vs Contracts

DPROD supports two document types for different purposes:

| Type | ODRL Base | Use Case | Parties |
|------|-----------|----------|---------|
| **Policy** (`odrl:Set`) | Set | Organizational rules, access controls | None (applies to anyone matching constraints) |
| **Offer / Contract** (`dprod:DataContract`) | Offer | Bilateral agreements between teams | Provider (assigner) required |
| **Subscription** (`dprod:Subscription`) | Agreement | Activated contract | Both parties required |

Use **policies** (`odrl:Set`) when:
- Writing organizational data governance rules
- Defining access controls by role, purpose, or classification
- Setting restrictions that apply universally (no specific consumer)
- Encoding regulatory requirements (GDPR, data residency)

Use **contracts** when two specific teams need a bilateral agreement with SLAs. See [contracts-guide.md](contracts-guide.md) for contract authoring.

---

## 2. Quick Start

A minimal data use policy:

```turtle
@prefix odrl:     <http://www.w3.org/ns/odrl/2/> .
@prefix dprod:    <https://ekgf.github.io/dprod/contracts/> .
@prefix dprod-due: <https://ekgf.github.io/dprod/due/> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

ex:policy a odrl:Set ;
    odrl:profile <https://ekgf.github.io/dprod/contracts/> ,
                 <https://ekgf.github.io/dprod/due/> ;
    odrl:target ex:customerData ;

    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:analyticsTeam ;
        odrl:action odrl:read ;
        odrl:target ex:customerData ;
        odrl:constraint [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod-due:analytics
        ]
    ] ;

    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute ;
        odrl:target ex:customerData
    ] .
```

This policy says: the analytics team may read customer data for analytics purposes, and no one may distribute it.

---

## 3. Permission Patterns

### Purpose-Restricted Permission

Grant access only for a specific purpose.

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:assignee ex:complianceTeam ;
    odrl:action odrl:read ;
    odrl:target ex:transactionData ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand odrl:purpose ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod-due:compliance
    ]
] .
```

### Classification-Based Permission

Grant access based on the data's classification level.

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:action odrl:read ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:classification ;
        odrl:operator odrl:isAnyOf ;
        odrl:rightOperand (dprod-due:public dprod-due:internal)
    ]
] .
```

### Role-Based Permission

Grant access based on the requesting agent's role.

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:action odrl:read ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:role ;
        odrl:operator odrl:eq ;
        odrl:rightOperand "data-analyst"
    ]
] .
```

### Time-Limited Permission

Grant access only before a certain date.

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:action odrl:read ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod:currentDateTime ;
        odrl:operator odrl:lt ;
        odrl:rightOperand "2026-12-31T23:59:59Z"^^xsd:dateTime
    ]
] .
```

---

## 4. Prohibition Patterns

### No External Distribution

```turtle
odrl:prohibition [
    a odrl:Prohibition ;
    odrl:action odrl:distribute ;
    odrl:target ex:data
] .
```

### No PII Processing

Prohibit use of data classified as PII for certain processing modes.

```turtle
odrl:prohibition [
    a odrl:Prohibition ;
    odrl:action odrl:use ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:LogicalConstraint ;
        odrl:and (
            [
                a odrl:Constraint ;
                odrl:leftOperand dprod-due:sensitivity ;
                odrl:operator odrl:eq ;
                odrl:rightOperand dprod-due:pii
            ]
            [
                a odrl:Constraint ;
                odrl:leftOperand dprod-due:processingMode ;
                odrl:operator odrl:eq ;
                odrl:rightOperand dprod-due:modelTraining
            ]
        )
    ]
] .
```

### No Commingling

Prohibit mixing data with other sources.

```turtle
odrl:prohibition [
    a odrl:Prohibition ;
    odrl:action odrl:derive ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:derivationType ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod-due:commingled
    ]
] .
```

---

## 5. Constraint Patterns

Constraints restrict when rules apply. An `odrl:Constraint` has three parts:

| Part | Property | Description |
|------|----------|-------------|
| Left operand | `odrl:leftOperand` | What to check (from DUE vocabulary) |
| Operator | `odrl:operator` | How to compare (`eq`, `neq`, `lt`, `gt`, `lteq`, `gteq`, `isAnyOf`, `isNoneOf`, `isAllOf`) |
| Right operand | `odrl:rightOperand` | Expected value(s) |

### Purpose Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand odrl:purpose ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod-due:analytics
] .
```

### Classification Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod-due:classification ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod-due:confidential
] .
```

### Jurisdiction Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod-due:jurisdiction ;
    odrl:operator odrl:isAnyOf ;
    odrl:rightOperand ("US" "UK" "EU")
] .
```

### Retention Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod-due:retentionPeriod ;
    odrl:operator odrl:lteq ;
    odrl:rightOperand "P7Y"^^xsd:duration
] .
```

### Environment Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod-due:environment ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod-due:production
] .
```

---

## 6. DUE Operands Quick Reference

All operands are `odrl:LeftOperand` with `dprod:resolutionPath`.

### Agent Operands (resolved from requesting agent)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `dprod-due:role` | `agent.role` | String |
| `dprod-due:organization` | `agent.organization` | IRI |
| `dprod-due:costCenter` | `agent.costCenter` | String |
| `dprod-due:recipientType` | `agent.recipientType` | `internal`, etc. |

### Asset Operands (resolved from target asset)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `dprod-due:classification` | `asset.classification` | `public`, `internal`, `confidential`, `restricted` |
| `dprod-due:sensitivity` | `asset.sensitivity` | `pii`, `mnpi`, `phi` |
| `dprod-due:assetClass` | `asset.class` | String (equity, fx, etc.) |
| `dprod-due:market` | `asset.market` | String (NYSE, LSE, etc.) |
| `dprod-due:isBenchmark` | `asset.isBenchmark` | Boolean |
| `dprod-due:residency` | `asset.residency` | String (country) |
| `dprod-due:retentionPeriod` | `asset.retentionPeriod` | `xsd:duration` |
| `dprod-due:expiry` | `asset.expiry` | `xsd:dateTime` |
| `dprod-due:timeliness` | `asset.timeliness` | `realtime`, `nearRealtime`, `delayed`, `endOfDay`, `historical` |
| `dprod-due:delayMinutes` | `asset.delayMinutes` | Integer |
| `dprod-due:auditRequired` | `asset.auditRequired` | Boolean |

### Context Operands (resolved from request context)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `odrl:purpose` | `context.purpose` | `analytics`, `research`, `compliance`, `operations` |
| `dprod-due:jurisdiction` | `context.jurisdiction` | String (country) |
| `dprod-due:environment` | `context.environment` | `production`, `staging`, `development`, `sandbox` |
| `dprod-due:network` | `context.network` | `internalNetwork`, `externalNetwork`, `cloudNetwork` |
| `dprod-due:processingMode` | `context.processingMode` | `human`, `automated`, `modelTraining`, `inference` |
| `dprod-due:legalBasis` | `context.legalBasis` | `consent`, `contract`, `legalObligation`, `vitalInterest`, `publicTask`, `legitimateInterest` |
| `dprod-due:consentId` | `context.consentId` | String |
| `dprod-due:accessPattern` | `context.accessPattern` | `batch`, `streaming`, `interactive`, `api` |
| `dprod-due:volumeLimit` | `context.volumeLimit` | Integer |
| `dprod-due:rateLimit` | `context.rateLimit` | Integer |
| `dprod-due:derivationType` | `context.derivationType` | `commingled`, `nonSubstitutive`, `newProduct` |
| `dprod-due:project` | `context.project` | String |

---

## 7. DUE Actions Quick Reference

### ODRL Common Vocabulary (used directly)

| Action | Definition | Hierarchy |
|--------|------------|-----------|
| `odrl:use` | General use | Top |
| `odrl:read` | Read/view | `includedIn use` |
| `odrl:display` | Display to users | `includedIn use` |
| `odrl:distribute` | Distribute to third parties | `includedIn use` |
| `odrl:delete` | Delete the asset | `includedIn use` |
| `odrl:modify` | Modify the asset | `includedIn use` |
| `odrl:aggregate` | Aggregate with other data | `includedIn use` |
| `odrl:anonymize` | Remove identifying info | `includedIn use` |
| `odrl:derive` | Create derived data | `includedIn use` |

### DUE-Specific Actions

| Action | Definition | Parent |
|--------|------------|--------|
| `dprod-due:nonDisplay` | Automated/programmatic use | `use` |
| `dprod-due:conformTo` | Conform to schema/spec | None |
| `dprod-due:log` | Log access | `inform` |
| `dprod-due:notify` | Notify parties | `inform` |
| `dprod-due:report` | Submit reports | `inform` |
| `dprod-due:deliver` | Deliver data | `distribute` |
| `dprod-due:query` | Query/select | `read` |
| `dprod-due:export` | Export outside system | `distribute` |
| `dprod-due:copy` | Copy to another location | `reproduce` |
| `dprod-due:link` | Link/join datasets | `aggregate` |
| `dprod-due:profile` | Create profiles | `derive` |
| `dprod-due:calculateIndex` | Index calculation | `derive` |
| `dprod-due:algorithmicTrading` | Automated trading | `nonDisplay` |

Action hierarchy uses `odrl:includedIn`. A permission on `odrl:use` implicitly permits all actions below it.

---

## 8. Combining Constraints

### Logical AND

All conditions must be true. Use `odrl:LogicalConstraint` with `odrl:and`:

```turtle
odrl:constraint [
    a odrl:LogicalConstraint ;
    odrl:and (
        [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod-due:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand dprod-due:legalBasis ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod-due:legitimateInterest
        ]
    )
] .
```

### Logical OR

At least one condition must be true. Use `odrl:or`:

```turtle
odrl:constraint [
    a odrl:LogicalConstraint ;
    odrl:or (
        [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod-due:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod-due:operations
        ]
    )
] .
```

### Logical NOT

Negate a constraint. Use `dprod:not`:

```turtle
odrl:constraint [
    a odrl:LogicalConstraint ;
    dprod:not [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:environment ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod-due:production
    ]
] .
```

This means: the constraint is satisfied when the environment is **not** production.

A `LogicalConstraint` must have exactly one of `odrl:and`, `odrl:or`, or `dprod:not`.

---

## 9. Common Policy Patterns

### Internal Analytics Only

```turtle
ex:policy a odrl:Set ;
    odrl:profile <https://ekgf.github.io/dprod/contracts/> ,
                 <https://ekgf.github.io/dprod/due/> ;
    odrl:target ex:data ;

    odrl:permission [
        a odrl:Permission ;
        odrl:action odrl:read ;
        odrl:target ex:data ;
        odrl:constraint [
            a odrl:LogicalConstraint ;
            odrl:and (
                [
                    a odrl:Constraint ;
                    odrl:leftOperand odrl:purpose ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand dprod-due:analytics
                ]
                [
                    a odrl:Constraint ;
                    odrl:leftOperand dprod-due:recipientType ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand dprod-due:internal
                ]
            )
        ]
    ] ;

    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:action odrl:distribute ;
        odrl:target ex:data
    ] .
```

### Jurisdiction-Restricted

```turtle
odrl:permission [
    a odrl:Permission ;
    odrl:action odrl:read ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:jurisdiction ;
        odrl:operator odrl:isAnyOf ;
        odrl:rightOperand ("US" "UK")
    ]
] .
```

### Retention-Limited

```turtle
odrl:obligation [
    a odrl:Duty ;
    odrl:action odrl:delete ;
    odrl:target ex:data ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:retentionPeriod ;
        odrl:operator odrl:gt ;
        odrl:rightOperand "P5Y"^^xsd:duration
    ]
] .
```

### Audit-Required

```turtle
odrl:obligation [
    a odrl:Duty ;
    odrl:action dprod-due:log ;
    odrl:target ex:accessLog ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod-due:classification ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod-due:confidential
    ] ;
    dprod:deadline "PT1H"^^xsd:duration
] .
```

---

## 10. Policy Review Checklist

1. Every policy declares `odrl:profile <https://ekgf.github.io/dprod/contracts/>` and `<https://ekgf.github.io/dprod/due/>`
2. Conflict strategy (`odrl:conflict odrl:prohibit`) is inherited from the profile -- do not repeat per-policy
3. Policy has at least one `odrl:target`
4. Each permission and prohibition has exactly one `odrl:action` and one effective `odrl:target` -- either declared on the rule or inherited from the policy-level target (rule-level `odrl:target` may be omitted when a policy-level target exists)
5. Each duty has exactly one `odrl:action`
6. Each constraint has `leftOperand`, `operator`, and `rightOperand`
7. LogicalConstraints use exactly one of `odrl:and`, `odrl:or`, or `dprod:not`
8. Resolution paths match canonical roots (`agent.`, `asset.`, `context.`)
9. Prohibitions cover the intended restrictions (prohibition overrides permission)
10. Duties have appropriate deadlines where time-sensitive
11. Classification and sensitivity values match the DUE vocabulary
12. Validate against SHACL shapes:

```bash
shacl validate --shapes dprod-contracts-shapes.ttl --data my-policy.ttl
```

---

## Further Reading

- [overview.md](overview.md) -- What is DPROD Contracts?
- [specification.md](specification.md) -- Technical vocabulary reference
- [term-mapping.md](term-mapping.md) -- Business term -> property mapping
- [examples/data-use-policy.ttl](../examples/data-use-policy.ttl) -- Complete working policy example
- [examples/baseline.ttl](../examples/baseline.ttl) -- Comprehensive test data

---

**Version**: 0.7 | **Date**: 2026-02-04
