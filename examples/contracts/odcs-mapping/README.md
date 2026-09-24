The [Open Data Contract Standard (ODCS)](https://github.com/bitol-io/open-data-contract-standard) describes a data contract as a YAML document that bundles schema, quality rules, service levels, team and infrastructure. DPROD Contracts covers a narrower question, the rights and obligations, and leaves schema to DCAT and SHACL and infrastructure to deployment descriptors. The two are complementary. This example translates the policy parts of the ODCS reference document into a DPROD data offer; each rule's label names the ODCS field it came from.

| ODCS | DPROD |
|---|---|
| `kind: DataContract`, `status: active`, `version` | `dprod:DataOffer`, `dprod:offerLifecycleStatus`, `dct:hasVersion` |
| `team` owner | `odrl:assigner` |
| `slaProperties` `frequency` and `timeOfAvailability` | a delivery duty with `dprod:recurrence` and `dprod:deadline` |
| `slaProperties` `generalAvailability` and `endOfSupport` | `dprod:effectiveDate` and `dprod:expirationDate` |
| `quality` `nullValues mustBe 0`, scheduled nightly | a conformance duty constrained on completeness, with `dprod:recurrence` |
| `slaProperties` `retention` | a duty to `odrl:delete` beyond the retention period |
| `roles` with `access: read` | an `odrl:Permission` for the role's party |
| `description.limitations` | an `odrl:Prohibition` |

ODCS fields that are workflow or operations rather than policy, such as approver chains, severity and `servers`, have no counterpart and stay in ODCS.
