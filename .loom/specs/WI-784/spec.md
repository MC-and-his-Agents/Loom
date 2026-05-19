# WI-784 Spec

## Goal

Protect `attach-only` adoption from creating a second Loom-authored truth chain in mature host-governed repositories.

## Acceptance Criteria

- `attach-only` scaffold profile declares `forbidden_authored_carriers`.
- Forbidden carriers include `.loom/work-items/**`, `.loom/progress/**`, `.loom/status/current.md`, `.loom/reviews/**`, and `.loom/specs/**`.
- `attach-only` dry-run lists required carriers and forbidden authored carriers.
- Generated `repo-interface.json` declares host truth locators for work item, project status, review, and closeout without copying host-owned results.
- `verify` fails closed if forbidden carriers exist on disk, appear in `init-result`, appear in `planned_writes`, appear in bootstrap manifest artifacts, or appear in write touched paths.
- Failure text requires migration to host truth locator, deletion of the competing carrier, or explicit upgrade to `execution-control`.
- `execution-control` still generates required Loom-owned work/progress/status/review/spec carriers.
- Generated skills surfaces and example bootstrap outputs are refreshed from source.

## Non-goals

- Do not remove placeholder release target truth; #780 owns that.
- Do not change blanket `.loom` gitignore behavior or stable Git visibility checks; #781 and #782 own those.
- Do not add pre-execution existing classification or decision prompts; #776 and #777 own those.
- Do not modify WebEnvoy or copy WebEnvoy-specific guardian/project rules into Loom core.
