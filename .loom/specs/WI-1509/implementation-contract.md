# WI-1509 Implementation Contract

## Change Class

- runtime
- contract
- test

## Ownership

The implementation owns only:

- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- `.loom/bin/loom_flow.py`
- `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `examples/new-project/.loom/bin/loom_flow.py`
- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1509.md`
- `.loom/progress/WI-1509.md`
- `.loom/specs/WI-1509/**`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/runtime/gate-freeze/**` only as ignored runtime output during local validation

## Required Boundaries

- Gate freeze must consume existing `pr metadata-preflight` body-file/readback evidence.
- Gate freeze must pin rendered/readback body hashes and machine metadata block hashes/fingerprints in the snapshot.
- Gate freeze must fail closed when rendered/readback PR body evidence mismatches.
- Gate freeze must fail closed when Work Item, branch, or head SHA carrier identity mismatches are reported by `pr metadata-preflight`.
- Next action for PR body drift must tell the operator to re-run `gh pr edit --body-file`, read back the PR body, and rerun freeze.
- Existing PR metadata, review, PR gate, controlled merge, release/no-release, and closeout semantics must not be weakened or replaced.

## Forbidden Changes

- No changes to `.github/workflows`.
- No PR template rewrite.
- No GitHub host writes from the freeze command.
- No hosted admission workflow implementation.
- No carrier/shadow freshness implementation.
- No review/head drift policy implementation.
- No release/tag/npm/GitHub Release changes.
