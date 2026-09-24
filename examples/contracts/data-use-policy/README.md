Not every rule about data is a contract between two parties. An organisation also has standing rules: who may read employee data and for what purpose, what must be logged, what may never be done. These are expressed as an `odrl:Set`, an ODRL policy with no assigner or assignee, and evaluated by the same DPROD evaluator as a contract. The profile's fixed conflict rule applies: a prohibition always wins over a permission.

The HR data access policy shows the constraint patterns a policy writer typically needs:

- **Purpose**, using ODRL's own `odrl:purpose` operand.
- **Role**, through the permission's `odrl:assignee`.
- **Classification**, so the audit-logging duty applies only to confidential data. Its target is the access log, not the employee data, so it is stated explicitly.
- **Set membership**, with `odrl:isNoneOf` and a list of values.
- **Logical combination.** An `odrl:LogicalConstraint` with `odrl:and`, and DPROD's `dprod:not` for negation: model training is forbidden unless the environment is the isolated one.
- **Retention**, as a duty to delete once the retention period is exceeded.

Every operand a policy reads must say where its value comes from. Each is declared the first time it is used, with one `dprod:operandSource` and one `dprod:operandProperty`; later uses just name it.
