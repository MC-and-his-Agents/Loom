# Validation: Global CLI Runtime Regression Fixtures

## Scope

This record covers #1244 synthetic regression fixtures for the global CLI
runtime migration follow-up under #1238.

The fixtures intentionally model repository shapes rather than copying HotCP
history:

- `hotcp-style-global-cli-no-loom-bin`: installed-state metadata plus
  fact-chain/status carriers, with no `.loom/bin` payload.
- `repo-local-wrapper-compatibility`: existing-style installed-state that still
  owns `.loom/bin` as a CLI-managed repo-local runtime wrapper.
- `global-cli-retained-loom-bin-residue`: global CLI installed-state with
  retained `.loom/bin` compatibility residue.
- `global-cli-retained-loom-bin-carrier-blocker`: retained `.loom/bin` where
  repo-local gate carriers still point at `python3 .loom/bin`.
- `global-cli-provider-command-mismatch`: global CLI provider command support
  drift with stable provider diagnostics.

The catalog lives in
[`legacy-migration-validation-fixtures.json`](../fixtures/legacy-migration-validation-fixtures.json).

## Command Evidence

Targeted validation:

```bash
python3 tools/check_cli_contract.py --surface aggregate
```

The aggregate check asserts:

- `loom installed-state validate`, `loom detect`, `loom doctor`, and
  `loom verify` pass for no-`.loom/bin` global CLI repositories.
- `loom fact-chain`, `loom status`, and `loom story` report global `loom ...`
  entrypoints rather than `python3 .loom/bin/...` entrypoints.
- CLI-managed repo-local `.loom/bin` remains classified as current
  `repo-local-wrapper` compatibility, not legacy repair debt.
- Retained `.loom/bin` under `global-cli` remains repairable residue and can
  only be deleted through proposal-only repair/upgrade planning.
- Retained `.loom/bin` deletion is blocked while gate carriers still reference
  repo-local runtime wrappers.
- Provider command mismatch fails closed at `global-cli-runtime-provider` with
  stable `missing_commands` diagnostics.

## Release Judgment For #1244

#1244 is a regression fixture and validation batch with a `no_release`
readiness judgment. It does not change the npm package payload, version
authority, GitHub release surface, or publish decision by itself.

Parent #1238 closeout or a later release carrier may consume these fixtures as
supporting evidence, but this PR does not publish, tag, or modify VERSION.
