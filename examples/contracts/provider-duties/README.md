Most of what a data contract promises is expressed as duties on the provider. DPROD needs no new rule type for this: each is an ordinary `odrl:Duty` in the offer's `odrl:obligation`, with `dprod:subjectOfDuty` naming the provider as the party that must act. Four patterns cover almost every service-level commitment:

- **Delivery.** `dprod:schedule` (an identified `dprod:Schedule`, here an RFC 5545 rule with its start time and timezone) says when each delivery is due and `dprod:deadline` how long after that the provider has to deliver.
- **Schema conformance.** The duty is about the schema, not the data, so it states its own `odrl:target` instead of inheriting the offer's.
- **Change notification.** The provider must notify consumers of schema changes, with 14 days' notice. The notice period is recorded with the example's own `ex:noticePeriod` as an agreed term.\*
- **Quality.** A conformance duty with an `odrl:constraint`. The constraint's left operand is declared where it is used: `dprod:operandSource` and `dprod:operandProperty` tell an evaluator to read `ex:timeliness` from the state snapshot, where the platform records how fresh the delivered data is.

Consumer duties use exactly the same construct, minus the subject.

\* DPROD does not yet evaluate a notice period. A `dprod:deadline` runs forward from when a duty becomes active, not back from a later action, so an evaluator cannot tell a timely notice from a late one. The term records what the parties agreed, and checking it is left to the change process.
