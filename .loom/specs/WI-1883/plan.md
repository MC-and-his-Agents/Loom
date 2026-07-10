# WI-1883 Plan

- Suite path decision consumed from `.loom/specs/WI-1883/spec.md`.

## Implementation Steps

1. Replace generated host `AGENTS.md` managed-block content with concise Loom execution guidance focused on route/resume, Work Item to PR binding, formal spec path freshness, review/gate freshness, validation evidence, and closeout.
2. Remove bootstrap/install runbook details from generated host `AGENTS.md`, including global install and host plugin registration commands.
3. Keep root-entry generator, shared skill runtime copies, source runtime copy, plugin payload copy, and example new-project fixture aligned.
4. Update contract checks to assert the new execution guidance and absence of obsolete install/register guidance.
5. Refresh plugin payload metadata and validate skills, fixture drift/generation, CLI contract surfaces, package/release surfaces, and full Loom source checks.
6. Complete PR #1885 review/gate and merge, then hand off to #1884 for publishing the updated plugin/runtime payload.

## Ownership Constraints

- WI-1883 owns generated host AGENTS guidance, root-entry generator parity, fixture/test updates, plugin payload metadata, PR #1885 metadata, and Loom carrier evidence for this implementation PR.
- WI-1883 does not own unrelated release mechanics, downstream repository-specific policy, security/permission behavior, data behavior, or reopening WI-1876/v0.26.2 closeout.
- Release ownership after merge belongs to #1884.

## Validation

- `git diff --check`
- `python3 tools/skills_surface.py check`
- `python3 tools/skills_surface.py check --surface cache-artifacts`
- `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `python3 tools/check_cli_contract.py --surface aggregate`
- `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`
- `python3 tools/check_demo_bootstrap_fixture.py --surface generation`
- `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization`
- `make loom-demo-new-project-check`
- `make release-surface-doc-contract-check`
- `make skills-check`
- `make py-compile`
- `make version-surface-check`
- `make release-surface-check`
- `make npm-package-check`
- `make loom-check`
- PR metadata render/readback and hosted PR gate before merge.
