DPROD keeps two questions apart. *Where is this offer or contract in its administrative life?* is answered by a person or a contract-management process and recorded with `dprod:offerLifecycleStatus` or `dprod:contractLifecycleStatus`. *Has this obligation been met?* is answered by an evaluator from observable facts and recorded with `dprod:dutyState`. Both take any `skos:Concept`; DPROD ships the optional scheme with `Pending`, `Active`, `Fulfilled` and `Violated`, and an enterprise may substitute its own.

The example shows both, plus versioning:

- **A version chain.** Customer API v2 supersedes v1 through `prov:wasRevisionOf`. The retired offer stays in the graph with its status set to `Fulfilled`, so contracts that accepted it remain interpretable.
- **A contract in force**, `Active`, with its effective and expiration dates.
- **Duty instances.** When the daily delivery duty is evaluated, each occurrence becomes its own `odrl:Duty` with a computed state: the 4 February delivery was made on time, the 5 February one missed its 30-minute window, and the 6 February one is not yet due.

Duty state is deliberately *not* a sub-property of `dprod:lifecycleStatus`: it is derived, and re-deriving it must never change an authored status.
