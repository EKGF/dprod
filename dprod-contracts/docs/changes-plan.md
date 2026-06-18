# Plan: Apply outstanding suggestions from Matthias

Working plan for the DPROD-contracts review items not yet applied on `add-dprod-contracts`.
Source emails (oldest -> newest): `19d08a1d` 2026-03-19, `19d92a2a` 2026-04-15, `19da58f8` 2026-04-19, `19db5fe8` 2026-04-22, Stephen 2026-05-14 (DataDuty consistency / DataOffer target / acceptsOffer basket model).

Buckets, in suggested execution order:
1. Quick textual fixes (low risk, no semantics)
2. SHACL shape improvements (mechanical)
3. DCON remnant cleanup (documentation)
4. Recurrence redesign (one large change; spec already drafted in `recurrence-redesign.md`)
5. Ontology design decisions
6. Deferred / needs more info

A "verify" step is included for each item so the work can be checked without re-reading the email.

---

## Triage notes (2026-05-10)

Cross-cutting status pass over all items in this plan. Verified line numbers and existence of each cited file/string before classifying. Where the original plan had an incorrect premise or imprecise line number, that is flagged here and corrected in-line under the item.

### Done already
- **1.1** — marked PASS in-line.
- **1.4** — marked Done in-line.
- **3.3** — done 2026-05-10; "+ DCON migration" trimmed from `dprod-contracts/README.md:120`; `rg` for DCON across both READMEs returns nothing.
- **3.1** — done 2026-05-10; DCON Migration section + redundant `---` removed from `overview.md`, table row + inventory cell trimmed; `rg` for DCON in overview.md returns nothing.
- **3.2** — done 2026-05-10; both `**DCON equivalent**` lines removed, the "replaces DCON's ProviderQualityPromise" sentence trimmed, and the `## DCON Migration` section + redundant `---` removed from `contracts-guide.md`; `rg` confirms zero hits.
- **2.1** — done 2026-05-10; `sh:message "…must be a single xsd:dateTime value."` added to all four date property shapes (DataOffer + DataContract × effectiveDate + expirationDate). Wording covers both `sh:maxCount` and `sh:datatype` violations.
- **2.2** — done 2026-05-10; all five Reject* shapes (`Xone`, `Remedy`, `Consequence`, `InheritAllowed`, `InheritFrom`) swapped from `sh:SPARQLTarget` SPARQL queries to declarative `sh:targetSubjectOf`. SHACL-Core only, no SHACL-SPARQL dependency. Validation outcomes unchanged.
- **1.5** — done 2026-05-10; Option A executed across three files. `rdfs:comment` rewritten on `dprod:currentDateTime`; `formal-semantics.md` §6.2 gets a Normalisation paragraph + `let ref' = …` line in `resolveRuntime`; `specification.md:163` parenthetical updated. Optional info-shape step skipped.
- **5.3** — done 2026-05-10; Option A (keep `subPropertyOf` + document deliberate domain narrowing). Both `dprod:partOf` and `dprod:memberOf` `rdfs:comment` blocks extended.
- **5.2** — done 2026-05-14; hybrid of option (a). Renamed `dprod:subject` → `dprod:subjectOfDuty` and `dprod:object` → `dprod:objectOfDuty`; both now `rdfs:subPropertyOf odrl:function` (symmetric, mirrors the W3C Market Data ODRL Profile's duty-scoped `md:subject`/`md:object`). Propagated across `dprod-contracts.ttl`, `dprod-contracts-shapes.ttl`, all three example TTLs, and all docs (spec, guides, formal-semantics, term-mapping, og.md). All TTL files re-parsed cleanly with rdflib.
- **3.4** — done 2026-05-14; no action. The plan's premise conflated two distinct things: `dct:conformsTo` is the *predicate* ("the data conforms to schema X" — a static fact, already in core DPROD) and `ex:conformTo` is the *ODRL action* in the concept scheme used inside Duty patterns ("the provider must conform to X by date Y" — a deontic obligation). They are not redundant ways of saying the same thing; they encode different commitments. Current usage is correct as-is — nothing to rewrite.
- **5.1** — done 2026-05-14. Confirmed all contracts terms are minted under the core `dprod:` namespace (they always were — the prefix was already `dprod:`). Cleaned up the confusing `@base <…/contracts/>` directive in `dprod-contracts.ttl` (no relative IRIs depended on it) and re-pointed every `rdfs:isDefinedBy` from `<…/contracts/>` to `dprod:` so the terms self-declare as part of core DPROD. The artifact-level `owl:Ontology` IRI at `<…/contracts/>` is kept because `dprod-contracts-prof.ttl` and `dprod-contracts-shapes.ttl` reference it as a `prof:hasArtifact` / `owl:imports` target. All three TTL files re-parse cleanly with rdflib.
- **5.6** — done 2026-05-10; Option D (do nothing). Plan's premise was wrong: nothing in DPROD-contracts is typed `dct:Standard` (that label sits correctly on `odrl:core`). Current `prof:Profile` + `owl:Ontology` typing kept; `voaf:Vocabulary` not added.

### Superseded by group decision (no longer a quick textual fix)
- ~~**1.3** — group agreed to remove `owl:oneOf` and split `dprod:State` into Contract-state and Duty-state subclasses.~~ Resolved 2026-06-04 — went further: removed `dprod:State` entirely; added three domain-specific properties (`dprod:offerLifeCycleStatus`, `dprod:contractLifeCycleStatus`, `dprod:dutyState`) with `skos:Concept` range. See §1.3.
- Rename to life cycle state so a :dutyLifeCycleState and a :dataContractLifeCycleState. 
### Quick wins — low risk, no decision needed (verified)


### Needs decision
- **5.4** — `dprod:path` OWL typing. Affects 2.3 and Bucket 6.2.
- ~~**5.5** — `dprod:select`: implement, mark non-normative, or delete.~~ Resolved 2026-06-04 — deleted (option c). See §5.5.
- **1.3 follow-on** — naming and algorithm-branching for the Contract-state / Duty-state split.
- **5.7** — consistency: introduce `dprod:DataDuty` subtype of `odrl:Duty`? (Stephen, 2026-05-14)
- **5.8** — `odrl:target` on DataOffer: drop to exactly 1? (Stephen, 2026-05-14; couples with 5.9)
- **5.9** — `dprod:acceptsOffer` on DataContract: allow 1..* (basket model)? (Stephen, 2026-05-14; couples with 5.8)

### Could decide unilaterally if you want to dispatch
- **2.3** — SHACL shape for `dprod:path` value structure: mechanical if you keep it SHACL-Core. Soft-blocks on 5.4 only if 5.4 changes how `dprod:path` is OWL-typed.

### Large but spec'd — schedule, do not re-decide
- **Bucket 4 (recurrence redesign)** — `recurrence-redesign.md` exists (213 lines) and contains the design. Execute as one PR. The former item 1.2 (line-34 header rewording) is now item 4.6 and travels with this PR.

### Deferred — needs external input
- **6.1** — fetch `fixme.md` Gmail attachment for message `19d7952e` before triaging.
- **6.2** — downstream of decision 5.4.

### Suggested execution order (refines the existing one at the bottom)
1. **Now (independent commits, all verified):** 1.5 (apply the three Option-A edits), 2.1, 2.2, 2.4, 3.1, 3.2, 3.3. (Item 1.2 is no longer standalone — folded into Bucket 4 as item 4.6.)
2. **Then:** 2.3 if you want to dispatch it unilaterally.
3. **Surface to group in one message:** 5.4, 5.5, 5.7, 5.8+5.9 (treat as one bundle — they are tightly coupled), plus the 1.3 follow-on.
4. **Fetch attachment** for 6.1.
5. **Bucket 4** as a dedicated PR.
6. **Bucket 5 → Bucket 6.2** after decisions land.

---

## Bucket 1 — Quick textual fixes

### 1.1 README: "SHACL-style" -> "SPARQL-style" property paths
- Source: 19db5fe8 item A
- Why: README claims SHACL-style paths, but the operand resolution path grammar in `dprod:path` is SPARQL property-path syntax.
- Where: `README.md` (root) — Matthias cited lines 15 and 91, but root README is short and does not contain those strings; the actual occurrence is `dprod-contracts/dprod-contracts.ttl:38` and likely in one of the contracts docs. Search-and-replace across `dprod-contracts/`.
- Steps:
  1. `rg -n "SHACL-style" dprod-contracts/` to locate every occurrence.
  2. Replace "SHACL-style property paths" -> "SPARQL-style property paths" wherever it describes `dprod:path`.
  3. Update `dprod-contracts.ttl:38` (header description bullet) and any docs hits.
- Verify: `rg -n "SHACL-style" dprod-contracts/` returns nothing.
- PASS (re-swept 2026-05-28: six remaining occurrences across `dprod-contracts.ttl`, `README.md`, `docs/specification.md`, `docs/formal-semantics.md` replaced; only `changes-plan.md` itself still mentions the historical phrase to describe this task).

### 1.2 Ontology header: recurrence description (line 34)
- MOVED (2026-05-10) to item 4.6 in Bucket 4. The rewording only makes sense once the property definition at `dprod-contracts.ttl:175-188` has been updated, so it travels with the recurrence redesign rather than as a standalone textual fix.

### 1.3 Closed-world note on `dprod:State owl:oneOf`
- Source: 19d08a1d item #6
- Why: `owl:oneOf` is a closed-world enumeration — extenders cannot add new states. Matthias asked us to acknowledge that this is deliberate so reviewers do not treat it as a bug.
- Where: `dprod-contracts/dprod-contracts.ttl:64-85`.
- Steps:
  1. Append a paragraph to the existing `rdfs:comment` on `dprod:State`: "These four states are intentionally closed (`owl:oneOf`); profiles MUST NOT introduce new states because evaluation algorithms branch on them."
- Verify: text appears in `:State` comment; ontology still parses.
- NOTE: ignore:  removed owl:oneOf - Group agreed that this should be open. Follow on action:  The group has decided that we will split the two-state into two separate properties: (Contract state and Duty state
They should subclass from the DPROD enumeration)
- DONE (2026-06-04): went further than the original split. (a) Deleted `dprod:State` (the class) entirely — no replacement class. (b) Deleted `dprod:state` (the union-domain property). (c) Added three domain-specific replacement properties: `dprod:offerLifeCycleStatus` (domain `dprod:DataOffer`, range `skos:Concept`), `dprod:contractLifeCycleStatus` (domain `dprod:DataContract`, range `skos:Concept`), `dprod:dutyState` (domain `odrl:Duty`, range `skos:Concept`). (d) Retyped the four canonical state instances (`dprod:Pending`, `dprod:Active`, `dprod:Fulfilled`, `dprod:Violated`) from `dprod:State` to `skos:Concept`; they remain the canonical vocabulary but are no longer instances of a closed class. (e) Why this design rather than the "subclass from a DPROD enumeration" the group originally discussed: making the range `skos:Concept` (an open class) keeps the group's open-world intent intact; subclassing from a DPROD enumeration would re-introduce closed-world semantics under a different name. SKOS is the standard W3C vocabulary for open concept enumerations and integrates naturally with the way DPROD already uses `skos:Concept` for operands, actions, and other values (see `examples/baseline.ttl` lines 30–195). (f) Profiles MAY introduce additional `skos:Concept` values, but the standard DPROD evaluation algorithm (formal-semantics §5) still only transitions between the four canonical concepts; this is now documented prose rather than an OWL constraint. (g) Reshape side-effects: `dprod-shapes:StatePropertyGroup` (with closed `sh:in` over the four states) was split into `dprod-shapes:OfferLifeCycleStatusPropertyGroup`, `dprod-shapes:ContractLifeCycleStatusPropertyGroup`, and `dprod-shapes:DutyStatePropertyGroup` — each constraining `sh:maxCount 1` and `sh:class skos:Concept` (no enumeration, open vocabulary). (h) All examples rewritten by enclosing-entity type: 9 `dprod:state` lines in `examples/baseline.ttl` became `dprod:offerLifeCycleStatus`, 6 became `dprod:dutyState`; in `examples/data-contract.ttl` 1 became `dprod:offerLifeCycleStatus` and 3 became `dprod:dutyState`; `examples/odcs.ttl` and `docs/contracts-guide.md` had a single offer-status each. (i) Doc updates: `README.md`, `docs/specification.md` (§3.1, §3.2 Recommended properties, §3.3 Recommended properties, §4.1, property-incidence table), `docs/overview.md` (still mentions the four states unchanged), `docs/term-mapping.md` (Contract Status section and Quick Reference table), `docs/policy-writers-guide.md` (no remaining references), `docs/formal-semantics.md` §11.1 (still describes the abstract formal model using the metalanguage `State` type and `state` function — these are not RDF terms and are left as-is; only RDF references were changed), `examples/odcs.md` (status row).

### 1.4 `examples/odcs.md` reference to non-existent `odcs-translated.ttl`
- Source: 19d08a1d item #17
- Why: Doc points readers at a file that doesn't exist; the actual example is `odcs.ttl`.
- Where: `dprod-contracts/examples/odcs.md:243`.
- Steps:
  1. Change `odcs-translated.ttl` -> `odcs.ttl` in that line and any other occurrences.
- Verify: `rg -n "odcs-translated" dprod-contracts/` returns nothing; the cited file exists.
- NOTE: Done

### 1.5 Clarify `dprod:currentDateTime` vs `odrl:dateTime`
- Source: 19d08a1d item #15
- Why: Today the comment only says "Equivalent to odrl:dateTime" + `rdfs:seeAlso odrl:dateTime`. ODRL implementers will not know which to use, or whether they alias.
- Where: `dprod-contracts/dprod-contracts.ttl:322-330`.
- Steps:
  1. Extend `rdfs:comment` to specify: ODRL evaluators use `odrl:dateTime`; DPROD evaluators MUST treat `dprod:currentDateTime` as the canonical operand and resolve `odrl:dateTime` to the same value at evaluation time.
  2. Add `owl:sameAs odrl:dateTime` only if you actually want OWL inference; otherwise keep `rdfs:seeAlso` and document the equivalence in the formal semantics.
- Verify: `formal-semantics.md` mentions both names and states which is canonical; ontology still parses.
- DECISION (2026-05-10): **Option A** — `dprod:currentDateTime` is canonical; document the rule, no OWL `sameAs`. Concrete edits:
  1. `dprod-contracts.ttl:321-329` — rewrite `rdfs:comment` to: "Canonical DPROD operand for the evaluation timestamp. Dual-typed as `dprod:RuntimeReference` so `resolveRuntime` binds it to the evaluator's clock. ODRL's `odrl:dateTime` is the upstream equivalent; DPROD evaluators MUST canonicalise `odrl:dateTime` to `dprod:currentDateTime` before resolution. Keep `rdfs:seeAlso`; do NOT assert `owl:sameAs` (DPROD evaluation does not require an OWL reasoner)."
  2. `formal-semantics.md` §6.2 (around line 614/622) — add a one-line normalization step before the `resolveRuntime` switch: "if `op = odrl:dateTime` then `op ← currentDateTime`". Cross-reference the ontology comment.
  3. `specification.md:163` — change parenthetical from "(mapped to `odrl:dateTime`)" to "(canonical form; `odrl:dateTime` normalises to this)".
  4. (Optional, deferred) SHACL `sh:Info`-severity shape on `odrl:Constraint` flagging `odrl:leftOperand odrl:dateTime` with message "use `dprod:currentDateTime` for DPROD contracts". Skip for now to keep the change small.
- Reasoning: formal-semantics already canonicalises on `currentDateTime` (line 622: `currentDateTime → Env.Σ.clock`); examples already use it; option B (`owl:sameAs`) would unilaterally extend the ODRL namespace and bind DPROD evaluation to an OWL reasoner that implementers don't otherwise need; option C (drop `currentDateTime`) loses the dual-typing trick that triggers `resolveRuntime`.
- DONE (2026-05-10): three edits applied. (1) Rewrote `rdfs:comment` on `dprod:currentDateTime` at `dprod-contracts.ttl:325` as a triple-quoted multi-line literal that names the operand as canonical, spells out the evaluator canonicalisation rule, and explains why equivalence sits on `rdfs:seeAlso` instead of `owl:sameAs`. (2) Added a "Normalisation" paragraph plus a `let ref' = if ref = odrl:dateTime then currentDateTime else ref` line to `resolveRuntime` in `formal-semantics.md` §6.2. (3) Updated `specification.md:163` parenthetical to "(canonical form; `odrl:dateTime` normalises to this)". Optional step 4 (SHACL info-shape) intentionally skipped.
---

## Bucket 2 — SHACL shape improvements

### 2.1 Add `sh:message` to date shapes
- Source: 19db5fe8 item C
- Why: Validators that report violations on missing/wrong `effectiveDate`/`expirationDate` will surface `sh:datatype` errors with no human message — bad UX.
- Where: `dprod-contracts/dprod-contracts-shapes.ttl` — `effectiveDate` shapes at lines 291 (DataOffer) and 331 (DataContract); `expirationDate` shapes at lines 296 (DataOffer) and 336 (DataContract).
- Steps:
  1. Add `sh:message "effectiveDate, if present, must be xsd:dateTime."` to each `effectiveDate` property shape.
  2. Add `sh:message "expirationDate, if present, must be xsd:dateTime."` to each `expirationDate` property shape.
- Verify: `rg -n "effectiveDate|expirationDate" dprod-contracts/dprod-contracts-shapes.ttl -A 4` shows `sh:message` under each occurrence.
- DONE (2026-05-10): added `sh:message` to all four shapes (DataOffer + DataContract × effectiveDate + expirationDate) at lines 294, 300, 336, 342. Used unified wording "effectiveDate/expirationDate, if present, must be a single xsd:dateTime value." so the message is correct for both `sh:datatype` and `sh:maxCount` violations (the property shape's single message applies to both constraints). Note: line numbers shifted by 3 vs the pre-edit range (291/296/331/336 → 291/297/333/339 for the `sh:path` lines).

### 2.2 Replace `sh:SPARQLTarget` with `sh:targetSubjectOf` in Reject* shapes
- Source: 19db5fe8 item D
- Why: Five Reject* shapes use `sh:SPARQLTarget` to find the subjects of `odrl:xone`/`odrl:remedy`/`odrl:consequence`/`odrl:inheritAllowed`/`odrl:inheritFrom`. `sh:targetSubjectOf` does exactly this declaratively, without SHACL-SPARQL extension.
- Where: `dprod-contracts/dprod-contracts-shapes.ttl:373, 390, 407, 472, 489`.
- Steps:
  1. For each shape (`RejectXoneShape`, `RejectRemedyShape`, `RejectConsequenceShape`, `RejectInheritAllowedShape`, `RejectInheritFromShape`) replace the `sh:target [ a sh:SPARQLTarget ; sh:select "..." ]` block with `sh:targetSubjectOf <predicate>`.
  2. Drop the `sh:property [ sh:path <predicate> ; sh:maxCount 0 ; ... ]` block in favour of the existing `sh:message`/`sh:severity`. With `sh:targetSubjectOf` the violation message can sit on the NodeShape directly OR be moved to a `sh:property` with `sh:path <predicate>; sh:maxCount 0` — keep whichever style matches the Ticket/Request shapes for consistency.
  3. Confirm Ticket/Request/AssetCollection/PartyCollection shapes (which use `sh:targetClass` + `sh:sparql`) stay as-is — they are class-targeted, not predicate-targeted.
- Verify: `rg -n "sh:SPARQLTarget" dprod-contracts/` returns no hits; SHACL validation suite (if any) still passes; conformance examples flag the same violations as before.
- DONE (2026-05-10): all five Reject* shapes refactored. The 7-line `sh:target [ a sh:SPARQLTarget; sh:select ... ]` block in each was replaced with a single `sh:targetSubjectOf <predicate>` line; the existing `sh:property [ sh:path <pred>; sh:maxCount 0; sh:severity; sh:message ]` block was left untouched. Verified: `sh:SPARQLTarget` no longer appears in any source file (only in this plan's descriptive text); five new `sh:targetSubjectOf` lines at 376, 387, 398, 457, 468. Ignored the plan's "match Ticket/Request style" hint per triage — those shapes solve a different problem (rejecting class membership via `sh:sparql` constraint, not predicate presence).

### 2.3 SHACL shape validating `dprod:path` value structure
- Source: 19d08a1d item #10
- Why: `dprod:path` is "either a single property IRI or an RDF list of property IRIs". Today only cardinality is enforced (`LeftOperandShape` at `:346-356`). A malformed value (e.g. a literal) silently breaks evaluation.
- Where: `dprod-contracts/dprod-contracts-shapes.ttl:346-363`.
- Steps:
  1. Inside `LeftOperandShape`, extend the `sh:path dprod:path` property shape with `sh:or ( [ sh:nodeKind sh:IRI ] [ sh:node dprod-shapes:RdfListOfIris ] )`.
  2. Add a new shape `dprod-shapes:RdfListOfIris` that walks `rdf:rest*/rdf:first` and asserts each element is `sh:nodeKind sh:IRI`. (SHACL-Core idiom: `sh:property [ sh:path ( [ sh:zeroOrMorePath rdf:rest ] rdf:first ) ; sh:nodeKind sh:IRI ] .`)
- Verify: a `LeftOperand` whose `dprod:path` is a literal triggers a violation; existing examples in `dprod-contracts/examples/` still validate.
- DONE (2026-06-04): implemented exactly as the plan's SHACL-Core idiom. Added `dprod-shapes:RdfListOfIris` with a single `sh:property` walking `( [ sh:zeroOrMorePath rdf:rest ] rdf:first )` and asserting `sh:nodeKind sh:IRI` + `sh:minCount 1` (the minCount rejects literals and `rdf:nil` that otherwise yield empty member sets). Extended the existing `sh:path dprod:path` block in `LeftOperandShape` with `sh:or ( [ sh:nodeKind sh:IRI ] [ sh:node dprod-shapes:RdfListOfIris ] )` alongside the original `sh:maxCount 1`. Also expanded the `rdfs:comment` on `dprod:path` in `dprod-contracts.ttl` to document the SHACL Core subset (predicate + sequence only; no inverse/alternative/cardinality forms), to reference SHACL §2.3, and to explain why no `rdfs:range` is declared (the permitted value set IRI ∪ rdf:List of IRIs is not expressible as a single RDFS class — mirroring SHACL's own choice for `sh:path`). Considered the recursive helper variant (`sh:property [ sh:path rdf:first ; sh:nodeKind sh:IRI ] ; sh:property [ sh:path rdf:rest ; sh:or ( [ sh:hasValue rdf:nil ] [ sh:node dprod-shapes:RdfListOfIris ] ) ]`) but rejected it because pyshacl emits a `ShapeRecursionWarning` and bails at depth 14; the property-path version walks the list in one shape evaluation. Verified with pyshacl: `baseline.ttl`, `data-contract.ttl`, `data-use-policy.ttl` all conform with zero recursion warnings; negative tests confirm literal-as-path and list-containing-a-literal both produce violations; positive tests confirm bare IRI and rdf:List of IRIs both pass.

### 2.4 Reject-shape for per-policy `odrl:conflict odrl:prohibit` override
- Source: 19d08a1d item #13
- Why: DPROD spec fixes the conflict policy to "Prohibition > Permission". Per-policy `odrl:conflict` would silently change semantics. Should be rejected by SHACL.
- Where: `dprod-contracts/dprod-contracts-shapes.ttl` (new shape, after the existing Reject* block).
- Steps:
  1. Add `dprod-shapes:RejectPolicyConflictShape` with `sh:targetSubjectOf odrl:conflict` and a `sh:property [ sh:path odrl:conflict ; sh:maxCount 0 ; sh:severity sh:Violation ; sh:message "DPROD contracts fix conflict resolution to Prohibition > Permission; per-policy odrl:conflict is not allowed." ]`.
- Verify: A test policy with `odrl:conflict odrl:prohibit` triggers a violation; existing examples without it still pass.

---

## Bucket 3 — DCON remnant cleanup

`term-mapping.md` already had its DCON content removed (commit f51b0b3). The remaining files still reference DCON or link to the now-empty section in term-mapping.

### 3.1 Remove "DCON Migration" section from `overview.md`
- Source: 19d92a2a, 19db5fe8 items G/I
- Where: `dprod-contracts/docs/overview.md:211-220`.
- Steps:
  1. Delete the "## DCON Migration" heading (line 211) and its bullet list (through line 220).
  2. Delete the "Migrating from DCON" row in the role table at `:233`.
  3. Update the inventory at `:242` ("Business term -> property mapping + DCON migration") to drop the trailing "+ DCON migration".
- Verify: `rg -n "DCON" dprod-contracts/docs/overview.md` returns nothing.
- DONE (2026-05-10): deleted the section + the trailing `---` to avoid two adjacent separators; removed the table row; trimmed the inventory cell. `rg` confirms zero DCON hits in overview.md.

### 3.2 Drop DCON references from `contracts-guide.md`
- Source: 19db5fe8 item I (agent cited lines 211, 228, 232, 550-552).
- Where: `dprod-contracts/docs/contracts-guide.md`.
- Steps:
  1. `rg -n "DCON|dcon:" dprod-contracts/docs/contracts-guide.md` to enumerate.
  2. For each hit, decide: (a) delete the DCON-specific paragraph, or (b) rewrite without DCON. Most are likely "if migrating from DCON, ..." asides — delete.
  3. If a "Further reading" link points to `term-mapping.md#dcon-migration`, drop the anchor or remove the link.
- Verify: `rg -n "DCON|dcon:" dprod-contracts/docs/contracts-guide.md` returns nothing.
- DONE (2026-05-10): removed both `**DCON equivalent**` lines (after Schema and Notification patterns); trimmed the "This replaces DCON's `ProviderQualityPromise`." sentence from the Quality SLA paragraph; removed the `## DCON Migration` section + redundant `---` near the end. `rg` confirms zero hits.

### 3.3 Drop DCON entry from root README ToC
- Source: 19db5fe8 item I (agent cited `README.md:120`).
- Where: `README.md`. (Note: the root README we read is only 21 lines. The line-120 reference was likely in `dprod-contracts/README.md` — re-check there.)
- Steps:
  1. `rg -n "DCON|dcon:" README.md dprod-contracts/README.md`.
  2. Remove ToC entries / cross-references to the deleted DCON Migration section.
- Verify: `rg -n "DCON|dcon:" README.md dprod-contracts/README.md` returns nothing.
- DONE (2026-05-10): trimmed "+ DCON migration" from `dprod-contracts/README.md:120`. Root `README.md` had no DCON refs. Verify `rg` returns no hits — confirmed.

### 3.4 Standardize on `dprod:conformsTo`, drop `ex:conformTo` action pattern
- Source: 19db5fe8 item H
- Why: Two ways to express the same thing — `dprod:conformsTo` (a property) vs an `odrl:action ex:conformTo` duty pattern. Keep one.
- Where: `dprod-contracts/docs/contracts-guide.md:54, 116, 206, 232, 238, 323, 365, 435` (and any examples).
- Steps:
  1. Confirm `dprod:conformsTo` is defined in `dprod-contracts.ttl` with appropriate domain/range; if not, define it as the canonical form.
  2. Walk each cited line; for each "duty with `odrl:action ex:conformTo`" idiom, rewrite to use `dprod:conformsTo` directly on the asset/contract. If the duty wraps additional metadata (deadline, recurrence) keep the duty but switch its action — discuss with author before mass-rewrite.
  3. Update `examples/` files that demonstrate the action pattern.
- Verify: `rg -n "ex:conformTo|conformTo" dprod-contracts/` shows only `dprod:conformsTo` occurrences (or none) in normative docs/examples.
- Risk: this changes example semantics — pause after step 1 and confirm the direction with group before doing the bulk rewrite.
- CORRECTION (2026-05-10): The plan's premise is wrong. `dprod:conformsTo` does **not** exist anywhere. What actually exists:
  - `dct:conformsTo` — used by core DPROD (`ontology/dprod/dprod-shapes.ttl:97,112,293` define `Distribution-conformsTo`/`Dataset-conformsTo` with `sh:path dct:conformsTo`); also in `dprod-contracts-prof.ttl:39,45` and the recurrence-spec design.
  - `ex:conformTo` — example-namespace `odrl:Action`, used in Duty patterns in `examples/baseline.ttl`, `examples/odcs.ttl`, `contracts-guide.md`, `term-mapping.md`, `policy-writers-guide.md`.
- Reframed decision space (needs group):
  - **(a) Replace `ex:conformTo` Duty pattern with direct `dct:conformsTo` triples on the asset.** Loses the deontic framing — "the data conforms to X" becomes a static fact, not an enforceable obligation. Probably wrong for SLA/quality use where deadlines/constraints attach to the duty.
  - **(b) Promote `ex:conformTo` to a real DPROD action `dprod:conformTo`** (typed as `odrl:Action`). Same Duty pattern, stable IRI, out of the example namespace. Minimal semantic change.
  - **(c) Hybrid (recommended starting point):** keep `dct:conformsTo` for static "this is the schema we conform to" facts (already in core DPROD), AND mint `dprod:conformTo` as an `odrl:Action` for the Duty pattern. They coexist because they mean different things — fact vs obligation.
- Until decision is made, **do not** bulk-rewrite. The current `ex:conformTo` usages are functionally fine but live in the example namespace.

---

## Bucket 4 — Recurrence redesign (large)

The spec is already drafted in `dprod-contracts/docs/recurrence-redesign.md`. This section operationalises that spec.

Source: 19da58f8 (full proposal in recurrence-redesign.md).

### 4.1 Add `dprod:RecurrenceSpec` class
- Where: `dprod-contracts.ttl`, after `dprod:RuntimeReference` block.
- Steps:
  1. Copy the class definition from `recurrence-redesign.md` lines 9-51 into the ontology.
  2. Add `prov:Plan` superclass if you want recurrence specs to participate in PROV (open question — see 5.x).
- Verify: ontology parses; `RecurrenceSpec` resolves under `https://www.omg.org/spec/DPROD/`.

### 4.2 Add `dprod:RRuleScheme` and `dprod:CrontabScheme` named individuals
- Where: same file, after the new class.
- Steps:
  1. Copy individual definitions from `recurrence-redesign.md` lines 61-89.
  2. Sanity-check the `rdfs:seeAlso` URLs still resolve (RFC 5545 §3.3.10, opengroup crontab spec).
- Verify: each is `a dprod:RecurrenceSpec` and has `rdfs:seeAlso`.

### 4.3 Replace `dprod:recurrence` definition
- Where: `dprod-contracts.ttl:176-189` (current `owl:DatatypeProperty` form).
- Steps:
  1. Delete the current `dprod:recurrence` block.
  2. Insert the replacement block from `recurrence-redesign.md:133-193` (`owl:ObjectProperty` with `rdfs:range dprod:RecurrenceSpec`).
- Verify: ontology parses; range is `dprod:RecurrenceSpec`.

### 4.4 Update SHACL shapes for recurrence
- Where: `dprod-contracts-shapes.ttl` (whichever shape currently constrains `dprod:recurrence`; if none, add one).
- Steps:
  1. Replace any `sh:datatype xsd:string` constraint with `sh:or ( [ sh:nodeKind sh:IRI ] [ sh:node dprod-shapes:RecurrenceSpecShape ] )`.
  2. Define `RecurrenceSpecShape`: requires exactly one `dct:conformsTo` (range `dprod:RecurrenceSpec`), exactly one `rdf:value` (xsd:string), nothing else.
- Verify: examples with both styles validate; a string literal directly under `dprod:recurrence` fails.

### 4.5 Update examples
- Where: `dprod-contracts/examples/*.ttl` and `dprod-contracts/examples/odcs.ttl` in particular (uncommitted exploratory edits already there — see `git status`).
- Steps:
  1. Reconcile the uncommitted `odcs.ttl` edits with the canonical pattern from `recurrence-redesign.md`. The existing edits use names like `dprod:IcalRecurrence` / `dprod:CronRecurrence` and `dc:conformsTo` — these need to become `dprod:RRuleScheme` / `dprod:CrontabScheme` and `dct:conformsTo`.
  2. Add at least one expression-based and one vocabulary-based recurrence example.
- Verify: examples parse; SHACL validation passes; the chosen names match the ontology.

### 4.6 Update header bullet at `dprod-contracts.ttl:34`
- Source: 19da58f8 (also referenced in `recurrence-redesign.md` section "Also update the ontology header description (line 34)").
- Why: Header still says "RFC 5545 RRULE" but the redesign permits crontab and frequency URIs too. Apply this last in the Bucket-4 PR so the description matches the property definition that 4.3 introduces.
- Where: `dprod-contracts/dprod-contracts.ttl:34`.
- Steps:
  1. Replace `- Recurrence property on odrl:Duty (RFC 5545 RRULE)` with `- Recurrence property on odrl:Duty (iCal RRULE, crontab, or frequency URI)`.
- Verify: line 34 reads the new wording; ontology still parses (`riot --validate dprod-contracts/dprod-contracts.ttl`).
- (Originally tracked as item 1.2 under Bucket 1; folded in here on 2026-05-10 because it only makes sense once the property definition has changed.)

### 4.7 Update prose docs
- Where: `dprod-contracts/docs/overview.md`, `contracts-guide.md`, `formal-semantics.md`, `specification.md`.
- Steps:
  1. Find existing recurrence prose: `rg -n "recurrence|RRULE|RFC 5545" dprod-contracts/docs/`.
  2. Reframe as "either a structured `RecurrenceSpec` (RRULE/crontab/...) or a frequency URI".
- Verify: docs no longer claim "must be an RRULE string".

### 4.8 Delete `dprod-contracts/docs/recurrence-redesign.md` once 4.1-4.7 are merged.
- Verify: `git status` clean.

---

## Bucket 5 — Ontology design decisions

### 5.2 `dprod:subject subPropertyOf odrl:assignee` — wrong inference?
- Source: 19d08a1d items #2/#3, 19db5fe8 item B
- Where: `dprod-contracts.ttl:241-263`.
- Issue: Today `dprod:subject` -> `odrl:assignee` and `dprod:object` -> `odrl:function`. Matthias argues `odrl:assignee` is the wrong super-property — the duty bearer in ODRL is the *assignee* of an action, but DPROD's `subject` is "the party who must perform" which fits `odrl:function`'s "party affected" semantics inversely. Matthias also flags that the rename to clearer names (`bearerParty`/`affectedParty` or `assignerParty`/`assigneeParty`) would resolve the confusion entirely.
- Decision: **(a)** Rename `subject`/`object` to descriptive names AND fix the super-property choice, or **(b)** Keep names, just swap super-properties, or **(c)** Leave alone and document the intentional choice.
- If (a): coordinated rename across ontology + shapes + docs + examples — non-trivial.
- DONE (2026-05-14): Hybrid of option (a). Renamed `dprod:subject` → `dprod:subjectOfDuty` and `dprod:object` → `dprod:objectOfDuty` (the `OfDuty` suffix makes the duty-only scope explicit and matches the SHACL domain). Super-property changed: both are now `rdfs:subPropertyOf odrl:function` (symmetric; the previously-asserted `odrl:assignee` parent on `subject` produced the inference Matthias flagged). The W3C Market Data ODRL Profile sets the precedent — `md:subject`/`md:object` are stand-alone duty-scoped properties with no `subPropertyOf` to `odrl:assignee`; we keep a single bridge to the abstract `odrl:function` umbrella so ODRL processors still see *some* role link. Propagated across shapes, all three example TTLs, and all docs (spec, guides, formal-semantics, term-mapping, og.md). `rdfs:label` left as "subject"/"object" for human-readable display.

### 5.3 `dprod:memberOf subPropertyOf odrl:partOf`
- Source: 19d08a1d item #4
- Where: `dprod-contracts.ttl:230-240`.
- Issue: ODRL's `partOf` is generic (party or asset). Sub-classing for parties only is fine if the domain restriction is enforced, which it is (`rdfs:domain odrl:Party`). Matthias flagged this as "debatable" — the inference is correct, just narrow. Probably keep.
- Decision: keep, drop, or replace with `skos:broader` style? Default: keep + add an `rdfs:comment` explaining the deliberate domain restriction.
- DONE (2026-05-10): Option A executed. Kept both `subPropertyOf odrl:partOf` axioms; extended `rdfs:comment` on both `dprod:partOf` and `dprod:memberOf` to explain that domain/range are deliberately narrowed (Asset/Asset and Party/Party respectively) and that DPROD does not produce mixed party-and-asset hierarchies. Door left open: revisit Option B (drop the subPropertyOf) is cheap if future feedback shows inferred `odrl:partOf` triples cause trouble in real deployments.

### 5.4 `dprod:path` lacks OWL type and `rdfs:range`
- Source: 19d08a1d item #5
- Where: `dprod-contracts.ttl:266-277`.
- Issue: declared `a rdf:Property` (not `owl:ObjectProperty` or `owl:DatatypeProperty`) and no `rdfs:range`. Tooling that loads the ontology as OWL DL will treat it as untyped. Range is technically `rdfs:Resource | rdf:List` — awkward for OWL DL.
- Decision: **(a)** Type as `owl:ObjectProperty` with `rdfs:range [ owl:unionOf ( rdfs:Resource rdf:List ) ]` (works in OWL Full), **(b)** Leave as `rdf:Property` and document why, or **(c)** Split into two properties (`dprod:pathSimple` -> IRI, `dprod:pathSequence` -> rdf:List). Most ontologies in the wild pick (b) and add a SHACL shape (covered in 2.3).

### 5.5 `dprod:select` — wire in or remove
- Source: 19d08a1d item #12
- Where: `dprod-contracts.ttl:279-290`; check `formal-semantics.md` for usage.
- Issue: Defined but the resolve algorithm ignores it. Either dead code or unfinished feature.
- Decision: **(a)** Implement in formal semantics (a SPARQL evaluation step that runs when `dprod:select` is present), or **(b)** Mark as non-normative ("for future use"), or **(c)** Delete entirely.
- DONE (2026-06-04): chose **(c) delete entirely**. Reasoning: (1) Every documented example of `dprod:select` was a verbatim restatement of an existing `dprod:path` sequence — the worked example in spec §4.9b declared `dprod:path (odrl:target ex:timeliness)` and `dprod:select "SELECT ?v WHERE { $request odrl:target/ex:timeliness ?v }"` side-by-side, contributing nothing new. (2) The few capabilities that SPARQL genuinely adds over the SHACL-Core predicate+sequence subset already chosen for `dprod:path` (§2.3) — namely filters, joins, aggregates, inverse and alternative paths — are not exercised by any policy in `dprod-contracts/examples/`. (3) The existing specification was underdefined when measured against SHACL's own SPARQL machinery (`sh:SPARQLConstraint`, §5.2 of the SHACL spec): variable name disagreed across documents (`?v` vs `?value`), no prefix-resolution mechanism, contradictory composition with `dprod:path` (spec said "alongside", formal semantics said "path takes precedence"), multi-row behaviour hand-waved as "first row" without an `ORDER BY`, graph context undefined, error semantics undefined. (4) Option (b) "mark as non-normative" was rejected — a non-normative feature that the formal-semantics `resolve` algorithm references is worse than either fully-defined or deleted; it is an active hazard. Implementation: removed the `dprod:select` declaration from `dprod-contracts.ttl`; removed the `sh:property [ sh:path dprod:select ... ]` block from `LeftOperandShape` in `dprod-contracts-shapes.ttl`; removed the `op.select`/`sparqlEval` case from the `resolve` function in `formal-semantics.md` §6.2 and the matching variable definitions; removed §4.9b (`dprod:select`) from `specification.md` and the row from the property-incidence table; removed the property from the SHACL shape table; deleted the `dprod:select` literal from `examples/baseline.ttl` (the `dprod:path (odrl:target ex:retentionPeriod)` it sat next to already resolves the operand); updated mentions in `README.md`, `overview.md`, `policy-writers-guide.md`, and `formal-semantics.md` §11.1 to describe `dprod:path` as the sole operand-resolution mechanism. Future-revisit trigger: a real policy example needs filters, joins, aggregates, inverse traversal, or alternatives — at that point reinstate either (i) a properly-specified `dprod:select` modelled on `sh:SPARQLConstraint` (pre-bound variable set, `sh:prefixes`-style prefix mechanism, single result variable, at-most-one row constraint, defined graph context, defined error semantics, mutual exclusion with `dprod:path` via `sh:xone`), or (ii) extend `dprod:path` to additional SHACL-Core path forms (`sh:inversePath`, `sh:alternativePath`) before falling back to SPARQL.

### 5.6 Profile decl: `dct:Standard` vs `voaf:Vocabulary`
- Source: 19d08a1d item #16
- Where: `dprod-contracts/dprod-contracts-prof.ttl:16`.
- Issue: Upstream ODRL profile typings often use `voaf:Vocabulary`; DPROD-contracts uses `dct:Standard`. Mostly cosmetic; affects how vocabulary catalogs (LOV, etc.) display the profile.
- Decision: keep `dct:Standard`, add `voaf:Vocabulary`, or replace.
- CORRECTION (2026-05-10): the plan's premise is partly wrong. Nothing in DPROD-contracts is typed `dct:Standard`. The `dct:Standard` at `dprod-contracts-prof.ttl:16` is on `odrl:core` (the upstream ODRL spec), which is the correct primitive for "this is the reference specification we extend". The three actual root resources are:
  - `odrl:core` → `dct:Standard` (correct as-is; the upstream spec)
  - `<https://www.omg.org/spec/DPROD/>` (DPROD profile) → `prof:Profile` in `dprod-contracts-prof.ttl:24-25`
  - `<https://www.omg.org/spec/DPROD/contracts/>` (contracts ontology) → `owl:Ontology` in `dprod-contracts.ttl:23-24`
  Reframed, the real question is whether to *add* `voaf:Vocabulary` (for LOV discoverability) to the contracts ontology root, the profile node, or neither.
- DONE (2026-05-10): **Option D — do nothing.** Current `prof:Profile` + `owl:Ontology` typing is correct and DXPROF-compliant. `voaf:Vocabulary` would only matter for LOV-style auto-discovery, which isn't a priority. Revisit cheap if LOV indexing becomes a goal.

### 5.7 Consistency: introduce `dprod:DataDuty` as a subtype of `odrl:Duty`?
- Source: Stephen (email, 2026-05-14) — comment #1.
- Where: `dprod-contracts.ttl` — `dprod:DataOffer` (`rdfs:subClassOf odrl:Offer`) and `dprod:DataContract` (`rdfs:subClassOf odrl:Agreement`) are confirmed subclasses, but no `dprod:DataDuty` exists; the duty-specific properties (`dprod:subjectOfDuty`, `dprod:objectOfDuty`, `dprod:deadline`, `dprod:recurrence`, `dprod:state`) hang directly off `odrl:Duty`.
- Issue: Inconsistent. The Offer/Agreement extensions are scoped to a DPROD subclass; the Duty extension is *not*, so it widens the meaning of any `odrl:Duty` that happens to share a graph with DPROD. Stephen argues a `dprod:DataDuty` subclass would mirror the Offer/Contract pattern and contain the lifecycle/deadline/recurrence semantics inside DPROD-land.
- Decision: **(a)** Mint `dprod:DataDuty rdfs:subClassOf odrl:Duty` and re-domain the duty-only properties (`subjectOfDuty`, `objectOfDuty`, `deadline`, `recurrence`, `state` restricted to duty case) to `dprod:DataDuty`; update SHACL `DutyShape` to target `dprod:DataDuty` rather than `odrl:Duty`. Coordinated change across ontology + shapes + examples + docs. Or **(b)** Document the asymmetry as deliberate (duty extensions are *cross-cutting* and apply to any ODRL duty in a DPROD-profile graph, by design). Or **(c)** Run both: add `dprod:DataDuty` as an annotation-only subclass with no shape change.
- Risk: Option (a) is non-trivial because `dprod:state` has a union domain `(odrl:Duty | dprod:DataOffer | dprod:DataContract)` — re-domaining the duty branch means split state semantics or leave the union as-is.

### 5.8 `odrl:target` cardinality on `dprod:DataOffer` — drop from 1..* to 1?
- Source: Stephen (email, 2026-05-14) — comment #2.
- Where: `dprod-contracts-shapes.ttl` — `dprod-shapes:SetShape:99-102` allows unbounded `odrl:target` at the policy level (inherited by `OfferShape` and `DataOfferShape`); `dprod-shapes:DataOfferShape:275-302` adds no further `odrl:target` constraint.
- Issue: Current shape permits multiple targets per `dprod:DataOffer`. This forces inline duties to re-declare `odrl:target` to disambiguate which dataset each obligation refers to. Stephen argues for a tighter model: exactly one `odrl:target` per offer, and bundle multiple offers into a contract instead (see 5.9). Outcome: simpler offers, cleaner duty scoping, easier reuse.
- Decision: **(a)** Constrain `dprod-shapes:DataOfferShape` to `sh:minCount 1; sh:maxCount 1` on `odrl:target` and remove the per-duty `odrl:target` workaround in examples. Or **(b)** Keep 1..* and document when authors should split into multiple offers. Or **(c)** Leave as 0..* (matches ODRL Set inheritance) and treat single-target as a convention.
- Coupling: tightly linked to 5.9 — if 5.9 lets a contract accept multiple offers, 5.8 (single target per offer) becomes the natural composition unit.

### 5.9 `dprod:acceptsOffer` cardinality on `dprod:DataContract` — 1 vs 1..*?
- Source: Stephen (email, 2026-05-14) — comment #3 ("shopping basket" model).
- Where: `dprod-contracts.ttl:192-198` (`dprod:acceptsOffer` property) and `dprod-contracts-shapes.ttl:324-330` (`sh:minCount 1; sh:maxCount 1; sh:class dprod:DataOffer`).
- Issue: Today a `dprod:DataContract` references exactly one `dprod:DataOffer`. Stephen's reference-data use case has 100s of distributions from one provider, of which any subscriber takes a different subset — so the 1:1 model either forces 80 near-duplicate contracts, or one contract referencing a 100-distribution offer with extra metadata about which 80 obligations apply. Stephen proposes: pair (5.8) "single-target offer" with (5.9) `dprod:acceptsOffer` cardinality `1..*` so a contract is a *basket* of accepted offers. Bonus: lets provider-duties and consumer-duties be authored as separate offers and composed in the contract, instead of stuffed into one generic provider offer.
- Decision: **(a)** Change `dprod-shapes:DataContractShape` `dprod:acceptsOffer` to `sh:minCount 1` only (drop `sh:maxCount`), accepting the basket model. Or **(b)** Keep `1`, document the workaround (one mega-offer + selective obligation refs). Or **(c)** Add a sibling property `dprod:acceptsOffers` (plural, basket) and keep `acceptsOffer` as the single-offer shorthand.
- Coupling: depends on 5.8. Whatever is decided here, the formal-semantics resolve algorithm (norm matching across the contract's offers) needs an explicit rule.

## TSNOTE:  for now we're rejecting 5.8 and 5.9 as it seems to increase complexity rather than reduce it. Interest here from Stephen on the justifications. 
---

## Bucket 6 — Deferred / needs more info

### 6.1 `fixme.md` attachment from email 19d7952e (2026-04-10)
- Email body says only "Maybe useful?" — actual feedback in attached `fixme.md`. We have not retrieved the attachment.
- Action: download the attachment via `mcp__google_workspace__get_gmail_attachment_content` for message `19d7952e55251e29` and re-evaluate.

### 6.2 Path-traversal sandboxing/grammar (Adalbert's `deref`)
- Source: 19d08a1d "hardening" note.
- Issue: An earlier prototype by Adalbert constrained `dprod:path` with a formal grammar that excluded back-references and circular paths. The current ontology dropped it. Whether to restore is partly a security question (untrusted policy authors) and partly a complexity question.
- Action: revisit after Bucket 5 decisions are made; this is downstream of 5.4.
# TS NOTE: we are rejecting this one. It seems like probably quite a minor issue, and restricting it here doesn't seem necessary at this stage. We could always introduce something later on down the road once we know more about how the usage goes. 
---

## Suggested execution order

1. Bucket 1 items 1.1, 1.3, 1.4, 1.5 — small, independent commits. (1.2 moved to 4.6.)
2. Bucket 2 items 2.1, 2.2 — independent commits.
3. Bucket 3 — one commit per file (overview, contracts-guide, README), then 3.4 separately because it's larger.
4. Bucket 5 design decisions — surface as discussion points (Slack / call). Block Bucket 4 only if 5.4 changes how `dprod:path` is typed (it doesn't really; orthogonal).
5. Bucket 4 — single feature branch / PR; large diff, easy to review as one unit.
6. Bucket 5 changes after decisions are taken.
7. Bucket 6 once attachments are read.

After each bucket: `riot --validate` on every `.ttl`, run any SHACL conformance suite under `dprod-contracts/examples/`.

---

## Appendix A — §5.8 / §5.9 modelling comparison (for the 2026-06-18 meeting)

Scenario used in every example below: one provider (`ex:dataPlatform`) wants to give one consumer (`ex:analytics`) access to **three datasets** — `ex:marketPrices`, `ex:referenceData`, `ex:riskMetrics` — with the following rules:

- `read` permission on each dataset
- `distribute` prohibition on each dataset
- one cross-cutting permission: `aggregate` on the bundle, restricted to `environment = production`

Prefixes elided for brevity (`@prefix ex:`, `odrl:`, `dprod:`, `xsd:`).

### Option A — Status quo: multi-target offer (current shape allows this)

ODRL 2.2 §2.4 lets a child rule omit `odrl:target` and inherit every target declared at the policy level. DPROD's `dprod-shapes:PermissionShape` and `ProhibitionShape` already encode this (`sh:maxCount 1` on `odrl:target`, no `minCount`, message: *"inherits from policy if absent"*). So a rule that should apply to *all* the policy's targets simply omits its target; a rule that should apply to a different asset declares its own. The example below uses that — the three blanket rules ("read", "distribute" prohibition) inherit; only the cross-cutting `aggregate` rule names `ex:multiAssetBundle` explicitly because that asset isn't at the policy level.

```turtle
ex:multiAssetOffer a dprod:DataOffer ;
    odrl:profile dprod: ;
    odrl:assigner ex:dataPlatform ;
    odrl:target ex:marketPrices , ex:referenceData , ex:riskMetrics ;
    odrl:permission   [ a odrl:Permission   ; odrl:action odrl:read ] ;         # inherits all 3 targets
    odrl:prohibition  [ a odrl:Prohibition  ; odrl:action odrl:distribute ] ;   # inherits all 3 targets
    odrl:permission   [ a odrl:Permission   ; odrl:action odrl:aggregate ;
                        odrl:target ex:multiAssetBundle ;
                        odrl:constraint [ odrl:leftOperand ex:environment ;
                                          odrl:operator odrl:eq ;
                                          odrl:rightOperand ex:production ] ] .

ex:contract a dprod:DataContract ;
    odrl:profile dprod: ;
    dprod:acceptsOffer ex:multiAssetOffer ;
    odrl:assigner ex:dataPlatform ;
    odrl:assignee ex:analytics .
```

**Subject IRI count**: 2 (offer + contract). **Blank-node rules on the offer**: 3. **Lines**: ~10 substantive.

**Pros**:
- Genuinely compact thanks to target inheritance — one rule covers all targets it semantically applies to.
- ODRL-native: this is exactly what the upstream `odrl:Set` / `odrl:Offer` shape was designed to express.
- One place to read the whole "what data is offered, what can/can't be done".
- Cross-cutting rules are still expressible by declaring an explicit `odrl:target` on the rule (as the `aggregate` example shows).

**Cons**:
- Reuse is poor: if a second consumer wants only `ex:marketPrices`, the provider either accepts that this consumer gets the whole bundle (wrong rules apply) or authors a second offer that duplicates the marketPrices rules.
- "Which rules apply to which dataset" requires evaluating inheritance — a tool computing "rules for `ex:marketPrices`" walks both rule-level and policy-level targets.
- When the policy has many targets and rules should apply to *different subsets* of them (not "all" or "one different asset"), inheritance can't help — you have to enumerate. The example here is the kindest case; a busy real-world catalogue may not be.
- Cross-cutting rules (aggregate on `ex:multiAssetBundle`) sit alongside per-target-set rules with no structural distinction.

### Option B — §5.8 alone: single-target offers, but `dprod:acceptsOffer` still 1:1

This is dysfunctional but illustrative. To cover three datasets you need **three separate contracts**, because `dprod:acceptsOffer` is capped at 1.

```turtle
ex:marketPricesOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:marketPrices ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:referenceDataOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:referenceData ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:riskMetricsOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:riskMetrics ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:bundleOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:multiAssetBundle ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:aggregate ;
        odrl:constraint [ odrl:leftOperand ex:environment ; odrl:operator odrl:eq ; odrl:rightOperand ex:production ] ] .

# Four separate contracts, one per accepted offer:
ex:contract-marketPrices a dprod:DataContract ;
    dprod:acceptsOffer ex:marketPricesOffer ; odrl:assigner ex:dataPlatform ; odrl:assignee ex:analytics .

ex:contract-referenceData a dprod:DataContract ;
    dprod:acceptsOffer ex:referenceDataOffer ; odrl:assigner ex:dataPlatform ; odrl:assignee ex:analytics .

ex:contract-riskMetrics a dprod:DataContract ;
    dprod:acceptsOffer ex:riskMetricsOffer ; odrl:assigner ex:dataPlatform ; odrl:assignee ex:analytics .

ex:contract-bundle a dprod:DataContract ;
    dprod:acceptsOffer ex:bundleOffer ; odrl:assigner ex:dataPlatform ; odrl:assignee ex:analytics .
```

**Subject IRI count**: 8 (4 offers + 4 contracts). **Blank-node rules**: 7 (one per ODRL rule, same as Option A). **Lines**: ~25 substantive.

**Pros**:
- Offers are reusable: another consumer who only wants `ex:marketPrices` accepts that one offer.
- Rule semantics are unambiguous: each rule inherits the offer's single `odrl:target`.

**Cons**:
- **Contract explosion**: one "subscription relationship" becomes four contracts. Renewal, billing, audit and lifecycle tracking all multiply by 4.
- This is the worst of both worlds and we should **not** ship it. It only exists here to illustrate why §5.8 has to land with §5.9 or not at all.

### Option C — §5.8 + §5.9 together: single-target offers, basket contract

```turtle
ex:marketPricesOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:marketPrices ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:referenceDataOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:referenceData ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:riskMetricsOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:riskMetrics ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:bundleOffer a dprod:DataOffer ;
    odrl:assigner ex:dataPlatform ; odrl:target ex:multiAssetBundle ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:aggregate ;
        odrl:constraint [ odrl:leftOperand ex:environment ; odrl:operator odrl:eq ; odrl:rightOperand ex:production ] ] .

ex:contract a dprod:DataContract ;
    odrl:profile dprod: ;
    dprod:acceptsOffer ex:marketPricesOffer , ex:referenceDataOffer , ex:riskMetricsOffer , ex:bundleOffer ;
    odrl:assigner ex:dataPlatform ;
    odrl:assignee ex:analytics .
```

**Subject IRI count**: 5 (4 offers + 1 contract). **Blank-node rules**: 7. **Lines**: ~18 substantive.

**Pros**:
- Offers are reusable across consumers; contracts are mix-and-match baskets.
- Each rule's target is implicit from its offer — no per-rule `odrl:target` boilerplate.
- "Which rules apply to `ex:marketPrices`" is a graph query: `?contract dprod:acceptsOffer ?o . ?o odrl:target ex:marketPrices . ?o (odrl:permission|odrl:prohibition|odrl:obligation) ?rule`.
- Cross-cutting rules sit in their own offer (`ex:bundleOffer`), structurally separated from per-dataset rules.

**Cons**:
- **Indirection cost**: to understand "what does this contract grant?" a reader/tool must follow `dprod:acceptsOffer` to four other subjects. Compare Option A where it's all in one place.
- Requires the basket-union rule in formal-semantics (rule-set = union of offers' rules). New machinery; new edge cases (e.g. cross-offer conflict between a permission in offer X and a prohibition in offer Y over the same `(action, target)`).
- 4 IRIs to mint and govern per "subscription relationship" instead of 1. Naming and lifecycle of bundleOffer specifically is awkward — it isn't really an offer in the everyday sense, it's a holder for cross-cutting rules.
- ODRL processors that don't know DPROD will see "an Agreement that accepts an Offer" 4 times — the basket semantics is DPROD-specific, not ODRL-native.

### Option D — Asymmetric: keep multi-target offers but allow 1..* on `dprod:acceptsOffer`

Don't tighten §5.8 (offers can still be multi-target), but do open §5.9 (contracts can accept multiple offers). This gives provider authors the choice: ship one mega-offer (Option A style), ship lots of small offers and let consumers basket (Option C style), or mix.

```turtle
# Multi-target offer (as Option A) OR
# Several single-target offers (as Option C) — either is valid.
# The contract can accept one offer or many.
ex:contract a dprod:DataContract ;
    dprod:acceptsOffer ex:multiAssetOffer .                 # picks the big one
# or
ex:contract a dprod:DataContract ;
    dprod:acceptsOffer ex:marketPricesOffer , ex:bundleOffer .  # picks two small ones
```

**Pros**:
- Doesn't force a refactor for existing multi-target offers.
- Provider chooses granularity per use case (broad-spectrum offer vs catalogue of small offers).
- The basket-union rule still buys composition for consumers who want it.

**Cons**:
- Two competing patterns coexist in the spec. Reviewers have to learn both. Tools that compute "all rules applicable to consumer X" need both code paths.
- Conflict resolution gets more complex: cross-offer conflicts AND multi-target-within-offer conflicts (which currently have unambiguous semantics) both need rules.
- Doesn't solve Stephen's original motivation (catalogue reuse) any better than Option C — and arguably worse, because providers can shortcut to a multi-target mega-offer and skip the reuse benefits.

### Discussion seed

The pivot question for the meeting is **what does a "DataOffer" represent**:

- If a DataOffer is a **product** (Stephen's lean) — one offer per dataset, basket contracts for shopping-cart subscriptions, catalogue-style reuse. Pushes us to Option C.
- If a DataOffer is a **deal** (current shape's lean) — one offer per provider/consumer relationship, multi-target if the deal covers many things, no basket. Stays at Option A.

DPROD's data-product framing favours the first reading; ODRL's `Offer` term favours the second. The basket-union rule is the bridge between "DataOffer = product" and "DataContract = subscription". Whether we want to build that bridge — and pay the indirection cost — is the call.

**Secondary points for the meeting:**

1. Is `ex:bundleOffer` (the holder for cross-cutting rules) a legitimate use of `DataOffer`, or is it a smell that suggests we need a separate construct for cross-cutting rules?
2. If §5.9 lands, do we require all accepted offers to share `odrl:assigner` (so the contract's provider is well-defined), or do we permit multi-provider baskets (which raise their own bilateral-duty questions)?
3. Migration: does §5.8 break existing DPROD adopters with multi-target offers? If so, ship a v2 schema with the constraint and keep v1 multi-target-tolerant?

---

### Catalogue / shopping-basket scenario

The single-customer scenario above made Option A look very compact. The picture changes for **catalogue-style** providers — Stephen's original motivating use case. A provider has, say, 100 distributions; different consumers subscribe to different subsets.

In what follows: the provider `ex:dataPlatform` publishes 5 distributions (`ex:marketPrices`, `ex:referenceData`, `ex:riskMetrics`, `ex:customerData`, `ex:transactionFiles`) with the same "read permitted, distribute prohibited" rule on each. Consumer **A** wants `{marketPrices, customerData}`. Consumer **B** wants `{referenceData, riskMetrics, transactionFiles}`. Consumer **C** wants `{marketPrices, riskMetrics}` — a third subset, overlapping both.

**Option A (status quo) — provider-authored, consumer-specific offers**

To express "consumer A gets these 2; consumer B gets those 3; consumer C gets that overlapping pair", the provider has to mint a fresh offer for each subscription, because ODRL has no native way for a single contract to accept a strict subset of a multi-target offer's targets:

```turtle
ex:offerA a dprod:DataOffer ; odrl:assigner ex:dataPlatform ;
    odrl:target ex:marketPrices , ex:customerData ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:offerB a dprod:DataOffer ; odrl:assigner ex:dataPlatform ;
    odrl:target ex:referenceData , ex:riskMetrics , ex:transactionFiles ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:offerC a dprod:DataOffer ; odrl:assigner ex:dataPlatform ;
    odrl:target ex:marketPrices , ex:riskMetrics ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:contractA dprod:acceptsOffer ex:offerA ; odrl:assignee ex:consumerA .
ex:contractB dprod:acceptsOffer ex:offerB ; odrl:assignee ex:consumerB .
ex:contractC dprod:acceptsOffer ex:offerC ; odrl:assignee ex:consumerC .
```

Three offers — one per subscription. Add a fourth consumer `D` with a different subset and you mint `ex:offerD`. The same "read permitted / distribute prohibited" rule pair is **duplicated three times** (it would be five, six, ten as more subscribers arrive). The marketing-friendly notion of a *catalogue* (5 distributions to choose from) is not present in the data — there's no IRI for "the marketPrices distribution as an offer the provider makes". When the provider updates the read/distribute rule (e.g., adds a new prohibition), every customer-specific offer has to be re-authored.

**Option C (basket) — one catalogue, many baskets**

The provider mints one offer per distribution (the catalogue). Each consumer's contract is a basket that picks the subset they want:

```turtle
ex:marketPricesOffer    a dprod:DataOffer ; odrl:assigner ex:dataPlatform ; odrl:target ex:marketPrices ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:referenceDataOffer   a dprod:DataOffer ; odrl:assigner ex:dataPlatform ; odrl:target ex:referenceData ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:riskMetricsOffer     a dprod:DataOffer ; odrl:assigner ex:dataPlatform ; odrl:target ex:riskMetrics ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:customerDataOffer    a dprod:DataOffer ; odrl:assigner ex:dataPlatform ; odrl:target ex:customerData ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:transactionFilesOffer a dprod:DataOffer ; odrl:assigner ex:dataPlatform ; odrl:target ex:transactionFiles ;
    odrl:permission [ a odrl:Permission ; odrl:action odrl:read ] ;
    odrl:prohibition [ a odrl:Prohibition ; odrl:action odrl:distribute ] .

ex:contractA dprod:acceptsOffer ex:marketPricesOffer , ex:customerDataOffer ;             odrl:assignee ex:consumerA .
ex:contractB dprod:acceptsOffer ex:referenceDataOffer , ex:riskMetricsOffer ,
                                  ex:transactionFilesOffer ;                              odrl:assignee ex:consumerB .
ex:contractC dprod:acceptsOffer ex:marketPricesOffer , ex:riskMetricsOffer ;              odrl:assignee ex:consumerC .
```

**Sub-counts** for this scenario (provider with 5 distributions, 3 consumers):

| Cost dimension | Option A | Option C |
|---|---|---|
| DataOffer IRIs | 1 per subscription = **3** (grows linearly with consumers) | 1 per distribution = **5** (grows with catalogue, fixed wrt consumers) |
| Rule blank-nodes | 2 rules × 3 offers = **6** | 2 rules × 5 offers = **10** |
| Rule duplication | "read"/"distribute" duplicated per offer | "read"/"distribute" duplicated per offer |
| Add a 4th consumer with a new subset | **new offer required** | new contract only |
| Update the "no distribute" rule | edit **3 offers** | edit **5 offers** |

Rule duplication is similar in both, because the rule live on the offers in both cases. The decisive difference is the **left column under "Add a 4th consumer"**: under Option A, every new subscription is a new authored asset; under Option C, the catalogue is fixed and consumers compose. For a 100-distribution catalogue with 200 consumers, Option A approaches 200 customer-specific offers; Option C stays at 100 offers + 200 contracts.

(Note: rule duplication across offers in Option C is a real cost; both columns inherit it. The cleaner solution would be a fourth modelling option where the "read permitted, distribute prohibited" rule pair is itself a reusable resource that each offer references — but ODRL doesn't have first-class shared-rule semantics, and that proposal is outside §5.8/§5.9 scope.)

---

### Query complexity comparison

Same scenario as above. SPARQL queries against each model. Prefixes elided.

#### Q1 — "What assets does contract `C` cover?"

Both models, identical structure:

```sparql
SELECT ?asset WHERE {
  :C dprod:acceptsOffer ?offer .
  ?offer odrl:target ?asset .
}
```

Option A returns the assets directly off the (one) accepted offer's multi-valued `odrl:target`. Option C returns the assets, one each, off the (several) accepted offers. **Query complexity: identical.** Result-set semantics: identical.

#### Q2 — "Can consumer `Z` read asset `T` under contract `C`?"

**Option A** — must compute effective rule target by ODRL inheritance (rule-level target if present, else policy-level target):

```sparql
ASK {
  :C dprod:acceptsOffer ?offer ;
     odrl:assignee :Z .
  ?offer odrl:permission ?p .
  ?p odrl:action odrl:read .

  # Effective target of the rule = rule's own target if present, else inherited from the offer.
  {
    ?p odrl:target :T .
  } UNION {
    FILTER NOT EXISTS { ?p odrl:target ?anyT }
    ?offer odrl:target :T .
  }
}
```

The `UNION` + `FILTER NOT EXISTS` is the inheritance computation. Either the rule has the explicit target, or the rule has *no* target and the offer carries it. Conceptually two cases joined; in practice three triple patterns plus a negation.

**Option C** — target is always at the offer level (single-target offer), so there's no inheritance:

```sparql
ASK {
  :C dprod:acceptsOffer ?offer ;
     odrl:assignee :Z .
  ?offer odrl:target :T ;
         odrl:permission ?p .
  ?p odrl:action odrl:read .
}
```

Four triple patterns. **No `UNION`, no `FILTER NOT EXISTS`.** This is the query complexity argument for §5.8 — single-target offers eliminate the inheritance branch.

#### Q3 — "Which contracts grant any consumer access to asset `T`?"

**Option A**:

```sparql
SELECT DISTINCT ?contract WHERE {
  ?contract dprod:acceptsOffer ?offer ;
            odrl:assignee ?consumer .
  ?offer odrl:permission ?p .
  ?p odrl:action odrl:read .
  {
    ?p odrl:target :T .
  } UNION {
    FILTER NOT EXISTS { ?p odrl:target ?anyT }
    ?offer odrl:target :T .
  }
}
```

**Option C**:

```sparql
SELECT DISTINCT ?contract WHERE {
  ?contract dprod:acceptsOffer ?offer .
  ?offer odrl:target :T ;
         odrl:permission ?p .
  ?p odrl:action odrl:read .
}
```

Same inheritance asymmetry. Same shape difference.

#### Q4 — "Reuse audit: how many contracts include `:marketPricesOffer`?"

**Option C** — trivial, expresses the catalogue-reuse intent directly:

```sparql
SELECT (COUNT(DISTINCT ?contract) AS ?reuses) WHERE {
  ?contract dprod:acceptsOffer :marketPricesOffer .
}
```

**Option A** — **cannot be expressed**. There is no shared `:marketPricesOffer` IRI to count against; each consumer-specific offer is its own subject. The closest approximation is "count contracts whose accepted offer's target set contains `:marketPrices`":

```sparql
SELECT (COUNT(DISTINCT ?contract) AS ?contractsCovering) WHERE {
  ?contract dprod:acceptsOffer ?offer .
  ?offer odrl:target :marketPrices .
}
```

But that's a different question: it counts subscriptions that *happen to include* marketPrices, not reuses of a single canonical offer — because in Option A there is no canonical offer. This is the structural query that Option A cannot express, and it's exactly the analysis Stephen wants for catalogue management ("how many of my customers take this distribution?").

#### Summary

| Query | Option A | Option C |
|---|---|---|
| Q1 — assets in a contract | 2 triple patterns | 2 triple patterns |
| Q2 — does consumer have read on asset? | 4 patterns + `UNION` + `FILTER NOT EXISTS` | 4 patterns |
| Q3 — which contracts grant asset access? | same as Q2 + `DISTINCT` | 4 patterns + `DISTINCT` |
| Q4 — offer reuse count | **not expressible**; only "contracts covering an asset" | 1 pattern + `COUNT` |

So §5.8 buys query simplicity for Q2/Q3 (eliminates the inheritance branch), and §5.9 buys a new query (Q4) that cannot be asked of Option A at all.

