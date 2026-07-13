# Loom Scenario Route Matrix

Scenario skills choose one of the 30 public CLI commands. Skill names are agent
interaction entrypoints; they do not expand the CLI surface.

| User intent | Scenario skill | Public CLI path |
| --- | --- | --- |
| Start or diagnose Loom | `loom-init` | `loom detect`, `loom doctor`, `loom installed-state validate` |
| Adopt a repository | `loom-adopt` | `loom install --apply`, then `loom verify` |
| Resume bounded work | `loom-resume` | `loom status`, `loom workspace check`, optionally `loom route` |
| Shape a product story | `loom-story` | `loom story`, then `loom route` |
| Start implementation | `loom-build` | `loom build --issue <WI> --branch <branch>` |
| Pre-review binding check | `loom-pre-review` | `loom pre-review --issue <WI> --pr <PR> --branch <branch>` |
| Semantic or spec review | `loom-review` / `loom-spec-review` | `loom review` plus `loom attestation readback` |
| Merge readiness | `loom-merge-ready` | `loom merge-ready` or `loom merge check` |
| Deliver a PR | root route | `loom ship` or `loom merge run --apply` |
| Handoff | `loom-handoff` | `loom status` plus `loom workspace check`; session summary only |
| Retire a worksite | `loom-retire` | `loom workspace retire` |
| Verify a release | root route | `loom release readback` |

`loom-story` produces a User Story, story readiness, and story business confirmation
before a Work Item enters delivery.

## Routing invariants

- Planning FRs may have zero Work Items. Build admission requires an explicit
  typed Work Item and issue-scoped branch, but no PR.
- PR-dependent stages read the real GitHub PR, current head, reviews, checks,
  mergeability, and host attestation only after those facts exist.
- No scenario reads or writes repo current, progress, review, shadow, or
  closeout carriers.
- Reinforced governance increases host review and validation strength; it does
  not re-enable removed commands or carriers.
- Each failure exposes one primary cause and one remediation. A removed command
  always redirects to `loom help --json`, never to a compatibility path.
- Product acceptance remains independent from delivery. Loom may resolve an
  authenticated acceptance locator but cannot infer product completion from a
  green gate or merged PR.

## Evidence boundary

Skills summarize public command output and artifact locators. They do not
create a second state machine, copy GitHub-owned head/check/merge fields, or
persist session state in the repository. Handoff is a conversation artifact;
closeout and release are authenticated host readbacks.
