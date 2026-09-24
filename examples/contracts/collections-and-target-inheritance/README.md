Two ODRL mechanisms keep large contracts short, and DPROD gives both a precise meaning.

**Target inheritance.** A rule with no `odrl:target` of its own inherits every target of its policy. The bundle offer names three products at policy level. Its blanket rules, read permitted and redistribution prohibited, say nothing about targets and so apply to all three. The aggregation permission is about the bundle as a whole, so it names that asset explicitly.

**Collections.** Assets and parties are grouped with `odrl:partOf` into an `odrl:AssetCollection` or `odrl:PartyCollection`, and a rule addressed to a collection applies to every member. DPROD evaluates membership over the transitive closure of `odrl:partOf`. So the contract's assignee is the whole Trading Division and both of its teams are covered, and a rule on the reference data collection covers the country-codes table inside it. Only explicit membership is supported; ODRL's derived collections (`odrl:source` with `odrl:refinement`) are rejected by the profile.

Membership is stated on the member, pointing up at its collection, so the members cannot be nested inside the contract. This is the one example that needs a `@graph`: the contract first, then the collection memberships.

A contract accepts exactly one offer. If a consumer wants a subset of what a provider publishes, the provider publishes an offer for that subset, or a multi-target offer such as this one.
