DPROD keeps two questions apart. *Where is this offer or contract in its administrative life?* is answered by a person or a contract-management process and recorded with `dprod:offerLifecycleStatus` or `dprod:contractLifecycleStatus`. *Has this obligation been met?* is answered by an evaluator from observable facts and recorded with `dprod:dutyState`. Both take any `skos:Concept`; DPROD ships the optional scheme with `Pending`, `Active`, `Fulfilled` and `Violated`, and an enterprise may substitute its own.

The example shows lifecycle status and versioning, and where duty state belongs:

- **A version chain.** Customer API v2 supersedes v1 through `prov:wasRevisionOf`. The retired offer stays in the graph with its status set to `Fulfilled`, so contracts that accepted it remain interpretable.
- **A contract in force**, `Active`, with its effective and expiration dates. It restates the offer's daily delivery duty, since a contract binds only the rules it states.
- **Duty instances, which are not part of the contract.** When the daily delivery duty is evaluated, each occurrence that has come round is an instance with its own computed state. Evaluated on 5 February, the 4 February delivery may be `Fulfilled` and the 5 February one `Violated`, and there is no instance yet for 6 February, because an occurrence becomes an instance only at its scheduled time. That state records what happened, later and changing as time goes on, so it is kept outside the contract and supplied with each evaluation. The contract records only what the parties agreed.

Duty state is deliberately *not* a sub-property of `dprod:lifecycleStatus`: it is derived, and re-deriving it must never change an authored status.
