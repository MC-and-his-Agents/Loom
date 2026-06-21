# Milestone 11 Final Closeout Evidence

## Scope

- Work Item: `WI-1489`
- Issue: `#1489`
- Parent FR: `#1480`
- Phase: `#1476`
- Release consumed: `v0.17.1`
- Branch: `work/1489-final-regression-closeout`

This evidence closes the milestone/11 context-safe runtime line. It consumes the already implemented runtime output envelope, configurable budget, artifact locator, full-output mode, global CLI default, Codex user-level plugin payload, docs/help migration boundary, closeout resolver hardening, and v0.17.1 release readback.

## Support Boundary Consumed

- Supported runtime surface after v0.17.0: global `loom` CLI plus Codex user-level plugin.
- Host repositories remain metadata-only adoption/work fact carriers.
- Repo-local plugin/runtime/skills installs, single-skill package distribution, and old installer compatibility paths are not supported completion paths.

## Regression Matrix

| Area | Evidence | Status |
| --- | --- | --- |
| Output envelope, budget, artifact locator, explicit full output | `python3 test/output_envelope_test.py` at 2026-06-21T04:32Z | pass |
| CLI help and command matrix | `python3 tools/loom.py help --json` at 2026-06-21T04:32Z | pass |
| Codex user-level plugin payload | `python3 tools/skills_surface.py check` at 2026-06-21T04:32Z | pass |
| Release/package surface | `python3 tools/check_release_surface.py` at 2026-06-21T04:32Z; `python3 tools/check_npm_package.py` at 2026-06-21T04:44Z after removing validation-generated `tools/__pycache__` | pass |
| Published release readback | `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 3e17dd73fb4ccb260ede68e5518b83aa904fb682 --release-judgment release_required --json` at 2026-06-21T04:32Z | pass |
| WI-1658 release closeout | `docs/evidence/v0.17.1-release-readiness.md`; `.loom/progress/WI-1658-goal-completion.json`; PR #1672 | present |
| Closeout identity binding | #1493 closed and consumed as closeout resolver hardening, not as the context-budget runtime fix | present |
| Final suite and fact chain | WI-1489 suite validate and carrier validate passed at 2026-06-21T04:32Z; suite evidence validate passed at 2026-06-21T04:33Z; fact-chain passed after status surface refresh; shadow parity passed | pass |
| Aggregate CLI contract | `python3 tools/check_cli_contract.py` at 2026-06-21T04:35Z-04:44Z | pass |

## Dependency Consumption

- #1482: budget protection and regression fixtures are closed and consumed by output envelope tests.
- #1483/#1484/#1485: high-noise command output, flow/gate summaries, and global CLI defaults are closed and consumed by CLI help/output checks.
- #1486: Codex user-level plugin payload is closed and consumed by skill surface validation.
- #1487: thread handoff/rotation guidance is closed and consumed as documentation/process evidence.
- #1488: docs/help/migration wording is closed and consumed by release readiness and final closeout evidence.
- #1493: closeout retained Work Item parsing is closed and consumed as identity-binding hardening.
- #1658: v0.17.1 release and carrier sync are closed and consumed as release evidence.

## Release Evidence Consumed

- Release PR #1671 merged at `2026-06-21T03:38:23Z`.
- Release merge commit: `3e17dd73fb4ccb260ede68e5518b83aa904fb682`.
- Carrier sync PR #1672 merged at `2026-06-21T04:17:35Z`.
- Carrier sync merge commit: `2445ebe89f844566ff0637ca654c4ace5f20d140`.
- Release workflow run: `27892441113`, success.
- GitHub Release: `https://github.com/MC-and-his-Agents/Loom/releases/tag/v0.17.1`.
- npm package: `@mc-and-his-agents/loom@0.17.1`, `latest=0.17.1`.
- Installed CLI smoke: temporary npm global prefix installed the package and `loom help --json` returned a valid `pass` payload.

## Final Closeout Readiness

Current branch local validation has passed the targeted matrix and aggregate CLI contract suite. PR metadata, hosted checks, current-head review record consumption, and PR gate remain before merge. After this evidence is merged, close #1489 first. Then close #1480 and #1476 only after readback confirms #1489 is closed and no milestone/11 issues remain open.
