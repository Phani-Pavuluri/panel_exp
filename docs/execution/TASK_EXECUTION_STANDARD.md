# Branch-bound execution

Resolve task identity and feature branch only from synchronized `main`, switch
explicitly to that branch, and run the standard-library binding verifier in
`preflight`, `prepush`, and `postpush` phases. Any nonzero result is fail-closed.
