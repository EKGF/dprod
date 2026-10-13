DPROD is a specification, not a program. It defines what a policy means and what a conformant evaluator must do with it, but nothing in DPROD receives a request or returns a decision. An **evaluator** is an external program, written or chosen by an implementer, that follows this specification to answer one question: may this agent perform this action on this asset, now, under these policies?

A decision is made in three steps:

1. **The calling system** (for example an application, an API gateway or a data platform) needs a decision. It gathers every fact the policies need and builds one immutable `dprod:EvaluationContext` with four parts: the **request**, a **state**-of-the-world snapshot, the requesting **agent** and the **clock**.
2. **The evaluator** receives the policies and that context. It reads nothing else: no live graph, no database and no network.
3. It resolves each operand with a single lookup, applies the policies and returns a decision. A missing, multiple or wrongly typed value is an evaluation error, never a quietly false constraint.

Each `odrl:LeftOperand` a policy uses says where in the context its value comes from with `dprod:operandSource`, and which single property to read there with `dprod:operandProperty`:

- `requestSource` reads from the **request**: a node built by the calling system to describe what is being asked for (who, which action, which asset) together with any facts about the request that policies need. It is plain RDF, not an `odrl:Request`.
- `stateSource` reads from the **state** snapshot: facts about the world at the time of the request, such as whether the market is open, frozen by the calling system as a `prov:Entity` so their provenance can be kept.
- `contextSource` reads from the context itself, which is how the built-in agent and clock operands work.

This policy permits internal recipients to use market prices while the market is open. `ex:recipientType` is read from the request and `ex:marketOpen` from the state snapshot:

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
    { "ex": "https://example.org/" }
  ],
  "id": "ex:marketHoursPolicy",
  "type": "Set",
  "profile": "https://ekgf.org/dprod/spec/develop/",
  "target": "ex:marketPrices",
  "permission": {
    "type": "Permission",
    "action": "use",
    "constraint": {
      "type": "LogicalConstraint",
      "and": {
        "@list": [
          {
            "type": "Constraint",
            "leftOperand": {
              "id": "ex:recipientType",
              "operandSource": "requestSource",
              "operandProperty": "ex:recipientType"
            },
            "operator": "eq",
            "rightOperand": { "id": "ex:internal" }
          },
          {
            "type": "Constraint",
            "leftOperand": {
              "id": "ex:marketOpen",
              "operandSource": "stateSource",
              "operandProperty": "ex:marketOpen"
            },
            "operator": "eq",
            "rightOperand": true
          }
        ]
      }
    }
  }
}
```

**Facts more than one hop away.** Policies often depend on a fact that is not stored directly on the request. Suppose use of market prices is permitted only to recipients whose organisation is regulated in the EU. In the source data that fact is two hops from the agent:

```turtle
@prefix ex: <https://example.org/> .

ex:alice ex:memberOf ex:acmeBank .
ex:acmeBank ex:regulatedIn ex:EU .
```

An operand cannot follow `ex:memberOf` and then `ex:regulatedIn`; earlier drafts allowed that with `dprod:path`, which has been removed. Instead the calling system, which already knows who Alice is and can query that data, resolves the join while building the request and writes the answer onto the request as a single property. The policy then reads it in one lookup:

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
    { "ex": "https://example.org/" }
  ],
  "id": "ex:euRecipientPolicy",
  "type": "Set",
  "profile": "https://ekgf.org/dprod/spec/develop/",
  "target": "ex:marketPrices",
  "permission": {
    "type": "Permission",
    "action": "use",
    "constraint": {
      "type": "Constraint",
      "leftOperand": {
        "id": "ex:recipientRegulator",
        "operandSource": "requestSource",
        "operandProperty": "ex:recipientRegulatedIn"
      },
      "operator": "eq",
      "rightOperand": { "id": "ex:EU" }
    }
  }
}
```

The normalised request carries the resolved value:

```json
{
  "@context": [
    "https://ekgf.org/dprod/spec/develop/dprod-simple.jsonld",
    { "ex": "https://example.org/" }
  ],
  "id": "ex:request-2026-03-02-0915",
  "assignee": "ex:alice",
  "action": "use",
  "target": "ex:marketPrices",
  "ex:recipientRegulatedIn": { "id": "ex:EU" }
}
```

This keeps the evaluator a pure, one-lookup function of its input. The join happens in the calling system, where the data lives, and its result becomes part of the immutable context, so a later audit sees exactly the value the decision was based on. A fact that describes the world rather than the request, such as whether the market is open, is flattened onto the state snapshot in the same way and read with `stateSource`.

The document below is the evaluation context an evaluator would be given for Alice's request at 09:15 on 2 March. Against the market-hours policy at the top of this example it yields a permit. DPROD's `dprod:currentAgent` and ODRL's standard `odrl:dateTime` are built-in operands bound to the context's agent and clock, and need no declaration.
