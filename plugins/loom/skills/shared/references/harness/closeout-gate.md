# Closeout Gate

Ordinary closeout is host-derived. It consumes the merged PR, merge commit,
target branch containment, required checks, issue state, and current-head host
attestation. It does not create a closeout/current-retire PR or write terminal
repository carriers.

## Required order

1. read the typed Work Item and PR binding;
2. verify current head attestation and required delivery checks;
3. verify merge and target-branch containment;
4. read back issue/project state;
5. retire the explicit local worktree when it is clean and owned;
6. report delivery closeout separately from product acceptance.

`delivery_closed_out` never implies `product_acceptance.passed`. A release may
write version/package source in its release PR, but post-merge facts remain on
GitHub and the registry.

Any removed carrier closeout command fails closed with
`unsupported_command_surface` and must not access or mutate the target.
