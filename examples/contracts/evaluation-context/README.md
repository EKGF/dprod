A DPROD evaluator answers one question: may this agent perform this action on this asset, now, under these policies? To make the answer reproducible, it never consults a live graph. The caller hands it one immutable `dprod:EvaluationContext` with four parts: the normalised authorisation **request**, an immutable **state**-of-the-world snapshot (a `prov:Entity`, so its provenance can be kept), the requesting **agent**, and the **clock**.

Each `odrl:LeftOperand` a policy uses declares where its value comes from with `dprod:operandSource` (the request, the state snapshot or the context itself) and which single property to read with `dprod:operandProperty`. Resolution is one lookup; there is no path traversal. A missing, multiple or wrongly typed value is an evaluation error, never a quietly false constraint.

This policy permits internal recipients to use market prices while the market is open. `ex:recipientType` is read from the request and `ex:marketOpen` from the state snapshot:

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-context.jsonld",
    { "ex": "https://example.org/" }
  ],
  "@id": "ex:marketHoursPolicy",
  "@type": "odrl:Set",
  "odrl:profile": "https://ekgf.org/dprod/spec/develop/",
  "odrl:target": "ex:marketPrices",
  "odrl:permission": {
    "@type": "odrl:Permission",
    "odrl:action": "odrl:use",
    "odrl:constraint": {
      "@type": "odrl:LogicalConstraint",
      "odrl:and": { "@list": [
        {
          "@type": "odrl:Constraint",
          "odrl:leftOperand": {
            "@id": "ex:recipientType",
            "dprod:operandSource": "dprod:requestSource",
            "dprod:operandProperty": "ex:recipientType"
          },
          "odrl:operator": "odrl:eq",
          "odrl:rightOperand": { "@id": "ex:internal" }
        },
        {
          "@type": "odrl:Constraint",
          "odrl:leftOperand": {
            "@id": "ex:marketOpen",
            "dprod:operandSource": "dprod:stateSource",
            "dprod:operandProperty": "ex:marketOpen"
          },
          "odrl:operator": "odrl:eq",
          "odrl:rightOperand": true
        }
      ] }
    }
  }
}
```

The document below is the evaluation context an evaluator would be given for Alice's request at 09:15 on 2 March. Against the policy above it yields a permit. DPROD's `dprod:currentAgent` and ODRL's standard `odrl:dateTime` are built-in operands bound to the context's agent and clock, and need no declaration.
