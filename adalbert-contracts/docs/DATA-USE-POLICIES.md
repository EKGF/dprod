# Adalbert Policy Writers Guide

A guide for data stewards writing data use policies with Adalbert.

---

## 1. When to Use Policies vs Contracts

Adalbert supports two document types for different purposes:

| Type | ODRL Base | Use Case | Parties |
|------|-----------|----------|---------|
| **Policy** (`odrl:Set`) | Set | Organizational rules, access controls | None (applies to anyone matching constraints) |
| **Offer / Contract** (`adalbert:DataContract`) | Offer | Bilateral agreements between teams | Provider (assigner) required |
| **Subscription** (`adalbert:Subscription`) | Agreement | Activated contract | Both parties required |

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
@prefix odrl:         <http://www.w3.org/ns/odrl/2/> .
@prefix adalbert:     <https://vocabulary.bigbank/adalbert/> .
@prefix adalbert-due: <https://vocabulary.bigbank/adalbert/due/> .
@prefix xsd:          <http://www.w3.org/2001/XMLSchema#> .

ex:policy a odrl:Set ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
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
            odrl:rightOperand adalbert-due:analytics
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
        odrl:rightOperand adalbert-due:compliance
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
        odrl:leftOperand adalbert-due:classification ;
        odrl:operator odrl:isAnyOf ;
        odrl:rightOperand (adalbert-due:public adalbert-due:internal)
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
        odrl:leftOperand adalbert-due:role ;
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
        odrl:leftOperand adalbert:currentDateTime ;
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
                odrl:leftOperand adalbert-due:sensitivity ;
                odrl:operator odrl:eq ;
                odrl:rightOperand adalbert-due:pii
            ]
            [
                a odrl:Constraint ;
                odrl:leftOperand adalbert-due:processingMode ;
                odrl:operator odrl:eq ;
                odrl:rightOperand adalbert-due:modelTraining
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
        odrl:leftOperand adalbert-due:derivationType ;
        odrl:operator odrl:eq ;
        odrl:rightOperand adalbert-due:commingled
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
    odrl:rightOperand adalbert-due:analytics
] .
```

### Classification Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand adalbert-due:classification ;
    odrl:operator odrl:eq ;
    odrl:rightOperand adalbert-due:confidential
] .
```

### Jurisdiction Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand adalbert-due:jurisdiction ;
    odrl:operator odrl:isAnyOf ;
    odrl:rightOperand ("US" "UK" "EU")
] .
```

### Retention Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand adalbert-due:retentionPeriod ;
    odrl:operator odrl:lteq ;
    odrl:rightOperand "P7Y"^^xsd:duration
] .
```

### Environment Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand adalbert-due:environment ;
    odrl:operator odrl:eq ;
    odrl:rightOperand adalbert-due:production
] .
```

---

## 6. DUE Operands Quick Reference

All operands are `odrl:LeftOperand` with `adalbert:resolutionPath`.

### Agent Operands (resolved from requesting agent)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `adalbert-due:role` | `agent.role` | String |
| `adalbert-due:organization` | `agent.organization` | IRI |
| `adalbert-due:costCenter` | `agent.costCenter` | String |
| `adalbert-due:recipientType` | `agent.recipientType` | `internal`, etc. |

### Asset Operands (resolved from target asset)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `adalbert-due:classification` | `asset.classification` | `public`, `internal`, `confidential`, `restricted` |
| `adalbert-due:sensitivity` | `asset.sensitivity` | `pii`, `mnpi`, `phi` |
| `adalbert-due:assetClass` | `asset.class` | String (equity, fx, etc.) |
| `adalbert-due:market` | `asset.market` | String (NYSE, LSE, etc.) |
| `adalbert-due:isBenchmark` | `asset.isBenchmark` | Boolean |
| `adalbert-due:residency` | `asset.residency` | String (country) |
| `adalbert-due:retentionPeriod` | `asset.retentionPeriod` | `xsd:duration` |
| `adalbert-due:expiry` | `asset.expiry` | `xsd:dateTime` |
| `adalbert-due:timeliness` | `asset.timeliness` | `realtime`, `nearRealtime`, `delayed`, `endOfDay`, `historical` |
| `adalbert-due:delayMinutes` | `asset.delayMinutes` | Integer |
| `adalbert-due:auditRequired` | `asset.auditRequired` | Boolean |

### Context Operands (resolved from request context)

| Operand | Resolution Path | Values / Type |
|---------|----------------|---------------|
| `odrl:purpose` | `context.purpose` | `analytics`, `research`, `compliance`, `operations` |
| `adalbert-due:jurisdiction` | `context.jurisdiction` | String (country) |
| `adalbert-due:environment` | `context.environment` | `production`, `staging`, `development`, `sandbox` |
| `adalbert-due:network` | `context.network` | `internalNetwork`, `externalNetwork`, `cloudNetwork` |
| `adalbert-due:processingMode` | `context.processingMode` | `human`, `automated`, `modelTraining`, `inference` |
| `adalbert-due:legalBasis` | `context.legalBasis` | `consent`, `contract`, `legalObligation`, `vitalInterest`, `publicTask`, `legitimateInterest` |
| `adalbert-due:consentId` | `context.consentId` | String |
| `adalbert-due:accessPattern` | `context.accessPattern` | `batch`, `streaming`, `interactive`, `api` |
| `adalbert-due:volumeLimit` | `context.volumeLimit` | Integer |
| `adalbert-due:rateLimit` | `context.rateLimit` | Integer |
| `adalbert-due:derivationType` | `context.derivationType` | `commingled`, `nonSubstitutive`, `newProduct` |
| `adalbert-due:project` | `context.project` | String |

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
| `adalbert-due:nonDisplay` | Automated/programmatic use | `use` |
| `adalbert-due:conformTo` | Conform to schema/spec | None |
| `adalbert-due:log` | Log access | `inform` |
| `adalbert-due:notify` | Notify parties | `inform` |
| `adalbert-due:report` | Submit reports | `inform` |
| `adalbert-due:deliver` | Deliver data | `distribute` |
| `adalbert-due:query` | Query/select | `read` |
| `adalbert-due:export` | Export outside system | `distribute` |
| `adalbert-due:copy` | Copy to another location | `reproduce` |
| `adalbert-due:link` | Link/join datasets | `aggregate` |
| `adalbert-due:profile` | Create profiles | `derive` |
| `adalbert-due:calculateIndex` | Index calculation | `derive` |
| `adalbert-due:algorithmicTrading` | Automated trading | `nonDisplay` |

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
            odrl:rightOperand adalbert-due:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand adalbert-due:legalBasis ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:legitimateInterest
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
            odrl:rightOperand adalbert-due:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand adalbert-due:operations
        ]
    )
] .
```

### Logical NOT

Negate a constraint. Use `adalbert:not`:

```turtle
odrl:constraint [
    a odrl:LogicalConstraint ;
    adalbert:not [
        a odrl:Constraint ;
        odrl:leftOperand adalbert-due:environment ;
        odrl:operator odrl:eq ;
        odrl:rightOperand adalbert-due:production
    ]
] .
```

This means: the constraint is satisfied when the environment is **not** production.

A `LogicalConstraint` must have exactly one of `odrl:and`, `odrl:or`, or `adalbert:not`.

---

## 9. Common Policy Patterns

### Internal Analytics Only

```turtle
ex:policy a odrl:Set ;
    odrl:profile <https://vocabulary.bigbank/adalbert/> ,
                 <https://vocabulary.bigbank/adalbert/due/> ;
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
                    odrl:rightOperand adalbert-due:analytics
                ]
                [
                    a odrl:Constraint ;
                    odrl:leftOperand adalbert-due:recipientType ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand adalbert-due:internal
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
        odrl:leftOperand adalbert-due:jurisdiction ;
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
        odrl:leftOperand adalbert-due:retentionPeriod ;
        odrl:operator odrl:gt ;
        odrl:rightOperand "P5Y"^^xsd:duration
    ]
] .
```

### Audit-Required

```turtle
odrl:obligation [
    a odrl:Duty ;
    odrl:action adalbert-due:log ;
    odrl:target ex:accessLog ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand adalbert-due:classification ;
        odrl:operator odrl:eq ;
        odrl:rightOperand adalbert-due:confidential
    ] ;
    adalbert:deadline "PT1H"^^xsd:duration
] .
```

---

## 10. Policy Review Checklist

1. Every policy declares `odrl:profile <https://vocabulary.bigbank/adalbert/>` and `<https://vocabulary.bigbank/adalbert/due/>`
2. Conflict strategy (`odrl:conflict odrl:prohibit`) is inherited from the profile — do not repeat per-policy
3. Policy has at least one `odrl:target`
4. Each permission and prohibition has exactly one `odrl:action` and one effective `odrl:target` — either declared on the rule or inherited from the policy-level target (rule-level `odrl:target` may be omitted when a policy-level target exists)
5. Each duty has exactly one `odrl:action`
6. Each constraint has `leftOperand`, `operator`, and `rightOperand`
7. LogicalConstraints use exactly one of `odrl:and`, `odrl:or`, or `adalbert:not`
8. Resolution paths match canonical roots (`agent.`, `asset.`, `context.`)
9. Prohibitions cover the intended restrictions (prohibition overrides permission)
10. Duties have appropriate deadlines where time-sensitive
11. Classification and sensitivity values match the DUE vocabulary
12. Validate against SHACL shapes:

```bash
shacl validate --shapes ontology/adalbert-shacl.ttl --data my-policy.ttl
```

---

## Further Reading

- [adalbert-overview.md](adalbert-overview.md) — What is Adalbert?
- [adalbert-specification.md](adalbert-specification.md) — Technical vocabulary reference
- [adalbert-term-mapping.md](adalbert-term-mapping.md) — Business term -> property mapping
- [examples/data-use-policy.ttl](../examples/data-use-policy.ttl) — Complete working policy example
- [examples/baseline.ttl](../examples/baseline.ttl) — Comprehensive test data

---

**Version**: 0.7 | **Date**: 2026-02-04
