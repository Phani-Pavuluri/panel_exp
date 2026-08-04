# Branch-bound execution

Synchronize and verify `main`, read its task identity, switch to its declared
feature branch, run binding `preflight`, execute validation, run `prepush`, push
only the declared branch, fetch it, run `postpush`, and prove exact equality.
Any nonzero verifier result is fail-closed.
