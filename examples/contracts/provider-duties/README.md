Most of what a data contract promises is expressed as duties on the provider. DPROD needs no new rule type for this: each is an ordinary `odrl:Duty` in the offer's `odrl:obligation`, with `dprod:subjectOfDuty` naming the provider as the party that must act. Four patterns cover almost every service-level commitment:

- **Delivery.** `dprod:recurrence` (an RFC 5545 recurrence rule) says when each delivery is due and `dprod:deadline` how long after that the provider has to deliver.
- **Schema conformance.** The duty is about the schema, not the data, so it states its own `odrl:target` instead of inheriting the offer's.
- **Change notification.** A deadline with no recurrence is a lead time.
- **Quality.** A conformance duty with an `odrl:constraint`. The constraint's left operand is declared where it is used: `dprod:operandSource` and `dprod:operandProperty` tell an evaluator to read `ex:timeliness` from the authorisation request.

Consumer duties use exactly the same construct, minus the subject.
