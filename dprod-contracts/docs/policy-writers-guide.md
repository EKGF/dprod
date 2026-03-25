# DPROD Policy Writers Guide

A guide for data stewards writing data use policies with DPROD Contracts.

---

## 1. When to Use Policies vs Contracts

DPROD supports two document types for different purposes:

| Type | ODRL Base | Use Case | Parties |
|------|-----------|----------|---------|
| **Policy** (`odrl:Set`) | Set | Organizational rules, access controls | None (applies to anyone matching constraints) |
| **Offer / Contract** (`dprod:DataOffer`) | Offer | Bilateral agreements between teams | Provider (assigner) required |
| **DataContract** (`dprod:DataContract`) | Agreement | Activated offer | Both parties required |

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
@prefix dprod:    <https://ekgf.github.io/dprod/> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .

ex:policy a odrl:Set ;
    odrl:profile <https://ekgf.github.io/dprod/> ;
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
            odrl:rightOperand dprod:analytics
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
        odrl:rightOperand dprod:compliance
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
        odrl:leftOperand dprod:classification ;
        odrl:operator odrl:isAnyOf ;
        odrl:rightOperand (dprod:public dprod:internal)
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
        odrl:leftOperand dprod:role ;
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
                odrl:leftOperand dprod:sensitivity ;
                odrl:operator odrl:eq ;
                odrl:rightOperand dprod:pii
            ]
            [
                a odrl:Constraint ;
                odrl:leftOperand dprod:processingMode ;
                odrl:operator odrl:eq ;
                odrl:rightOperand dprod:modelTraining
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
        odrl:leftOperand dprod:derivationType ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod:commingled
    ]
] .
```

---

## 5. Constraint Patterns

Constraints restrict when rules apply. An `odrl:Constraint` has three parts:

| Part | Property | Description |
|------|----------|-------------|
| Left operand | `odrl:leftOperand` | What to check |
| Operator | `odrl:operator` | How to compare (`eq`, `neq`, `lt`, `gt`, `lteq`, `gteq`, `isAnyOf`, `isNoneOf`, `isAllOf`) |
| Right operand | `odrl:rightOperand` | Expected value(s) |

### Purpose Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand odrl:purpose ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod:analytics
] .
```

### Classification Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod:classification ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod:confidential
] .
```

### Jurisdiction Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod:jurisdiction ;
    odrl:operator odrl:isAnyOf ;
    odrl:rightOperand ("US" "UK" "EU")
] .
```

### Retention Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod:retentionPeriod ;
    odrl:operator odrl:lteq ;
    odrl:rightOperand "P7Y"^^xsd:duration
] .
```

### Environment Constraint

```turtle
odrl:constraint [
    a odrl:Constraint ;
    odrl:leftOperand dprod:environment ;
    odrl:operator odrl:eq ;
    odrl:rightOperand dprod:production
] .
```

---

## 6. Operands Quick Reference

All operands are `odrl:LeftOperand` with `dprod:path` (and optionally `dprod:select` for multi-step paths).

### Context Operands (single-step — direct property on request)

| Operand | `dprod:path` | Values / Type |
|---------|-------------|---------------|
| `odrl:purpose` | `odrl:purpose` | `analytics`, `research`, `compliance`, `operations` |
| `dprod:environment` | `dprod:environment` | `production`, `staging`, `development`, `sandbox` |
| `dprod:processingMode` | `dprod:processingMode` | `human`, `automated`, `modelTraining`, `inference` |
| `dprod:legalBasis` | `dprod:legalBasis` | `consent`, `contract`, `legalObligation`, `vitalInterest`, `publicTask`, `legitimateInterest` |
| `dprod:derivationType` | `dprod:derivationType` | `commingled`, `nonSubstitutive`, `newProduct` |
| `dprod:channel` | `dprod:channel` | String |
| `dprod:serviceWindow` | `dprod:serviceWindow` | String |
| `dprod:jurisdiction` | `dprod:jurisdiction` | String (country) |
| `dprod:network` | `dprod:network` | `internalNetwork`, `externalNetwork`, `cloudNetwork` |
| `dprod:consentId` | `dprod:consentId` | String |
| `dprod:accessPattern` | `dprod:accessPattern` | `batch`, `streaming`, `interactive`, `api` |
| `dprod:volumeLimit` | `dprod:volumeLimit` | Integer |
| `dprod:rateLimit` | `dprod:rateLimit` | Integer |
| `dprod:project` | `dprod:project` | String |

### Asset Operands (two-step — via `odrl:target`)

| Operand | `dprod:path` | Values / Type |
|---------|-------------|---------------|
| `dprod:classification` | `(odrl:target dprod:classification)` | `public`, `internal`, `confidential`, `restricted` |
| `dprod:sensitivity` | `(odrl:target dprod:sensitivity)` | `pii`, `mnpi`, `phi` |
| `dprod:assetClass` | `(odrl:target dprod:assetClass)` | String (equity, fx, etc.) |
| `dprod:market` | `(odrl:target dprod:market)` | String (NYSE, LSE, etc.) |
| `dprod:isBenchmark` | `(odrl:target dprod:isBenchmark)` | Boolean |
| `dprod:residency` | `(odrl:target dprod:residency)` | String (country) |
| `dprod:retentionPeriod` | `(odrl:target dprod:retentionPeriod)` | `xsd:duration` |
| `dprod:expiry` | `(odrl:target dprod:expiry)` | `xsd:dateTime` |
| `dprod:timeliness` | `(odrl:target dprod:timeliness)` | `realtime`, `nearRealtime`, `delayed`, `endOfDay`, `historical` |
| `dprod:delayMinutes` | `(odrl:target dprod:delayMinutes)` | Integer |
| `dprod:auditRequired` | `(odrl:target dprod:auditRequired)` | Boolean |
| `dprod:completeness` | `(odrl:target dprod:completeness)` | Decimal |
| `dprod:volumeCount` | `(odrl:target dprod:volumeCount)` | Integer |

### Agent Operands (two-step — via `odrl:assignee`)

| Operand | `dprod:path` | Values / Type |
|---------|-------------|---------------|
| `dprod:role` | `(odrl:assignee dprod:role)` | String |
| `dprod:organization` | `(odrl:assignee dprod:organization)` | IRI |
| `dprod:costCenter` | `(odrl:assignee dprod:costCenter)` | String |
| `dprod:recipientType` | `(odrl:assignee dprod:recipientType)` | `internal`, etc. |

---

## 7. Actions Quick Reference

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

### DPROD-Specific Actions

| Action | Definition | Parent |
|--------|------------|--------|
| `dprod:nonDisplay` | Automated/programmatic use | `use` |
| `dprod:conformTo` | Conform to schema/spec | None |
| `dprod:log` | Log access | `inform` |
| `dprod:notify` | Notify parties | `inform` |
| `dprod:report` | Submit reports | `inform` |
| `dprod:deliver` | Deliver data | `distribute` |
| `dprod:query` | Query/select | `read` |
| `dprod:export` | Export outside system | `distribute` |
| `dprod:copy` | Copy to another location | `reproduce` |
| `dprod:link` | Link/join datasets | `aggregate` |
| `dprod:profile` | Create profiles | `derive` |
| `dprod:calculateIndex` | Index calculation | `derive` |
| `dprod:algorithmicTrading` | Automated trading | `nonDisplay` |

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
            odrl:rightOperand dprod:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand dprod:legalBasis ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod:legitimateInterest
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
            odrl:rightOperand dprod:compliance
        ]
        [
            a odrl:Constraint ;
            odrl:leftOperand odrl:purpose ;
            odrl:operator odrl:eq ;
            odrl:rightOperand dprod:operations
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
        odrl:leftOperand dprod:environment ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod:production
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
    odrl:profile <https://ekgf.github.io/dprod/> ;
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
                    odrl:rightOperand dprod:analytics
                ]
                [
                    a odrl:Constraint ;
                    odrl:leftOperand dprod:recipientType ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand dprod:internal
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
        odrl:leftOperand dprod:jurisdiction ;
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
        odrl:leftOperand dprod:retentionPeriod ;
        odrl:operator odrl:gt ;
        odrl:rightOperand "P5Y"^^xsd:duration
    ]
] .
```

### Audit-Required

```turtle
odrl:obligation [
    a odrl:Duty ;
    odrl:action dprod:log ;
    odrl:target ex:accessLog ;
    odrl:constraint [
        a odrl:Constraint ;
        odrl:leftOperand dprod:classification ;
        odrl:operator odrl:eq ;
        odrl:rightOperand dprod:confidential
    ] ;
    dprod:deadline "PT1H"^^xsd:duration
] .
```

---

## 10. Policy Review Checklist

1. Every policy declares `odrl:profile <https://ekgf.github.io/dprod/>`
2. Conflict strategy (`odrl:conflict odrl:prohibit`) is inherited from the profile -- do not repeat per-policy
3. Policy has at least one `odrl:target`
4. Each permission and prohibition has exactly one `odrl:action` and one effective `odrl:target` -- either declared on the rule or inherited from the policy-level target (rule-level `odrl:target` may be omitted when a policy-level target exists)
5. Each duty has exactly one `odrl:action`
6. Each constraint has `leftOperand`, `operator`, and `rightOperand`
7. LogicalConstraints use exactly one of `odrl:and`, `odrl:or`, or `dprod:not`
8. Operand `dprod:path` values are valid property paths (single IRIs or RDF lists)
9. Prohibitions cover the intended restrictions (prohibition overrides permission)
10. Duties have appropriate deadlines where time-sensitive
11. Classification and sensitivity values match the DPROD vocabulary
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
