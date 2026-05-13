# Hook Locator Contract

This file defines Loom's lifecycle hook locator contract. It freezes declaration
and adapter semantics only; it does not introduce hook execution.

## Goal

Loom hooks let a repository declare where lifecycle hook guidance or scripts live
without copying host-native hook files into Loom core.

The stable lifecycle names are:

- `before-run`
- `after-run`
- `cleanup`

These names are Loom lifecycle semantics, not host event names.

## Locator Rules

Each hook locator must be a repository-relative path.

Invalid locators fail closed for every requirement level:

- absolute paths
- paths containing `..`
- paths that resolve outside the repository root
- non-string or empty locators when the hook is `required`

Missing optional or advisory locators are reported as optional gaps. They must
not pollute core `missing_inputs`.

Hook locators are evaluated by the optional `orchestration-extension/hooks`
profile when a repository declares `hook_locators`. Repositories with no
`hook_locators` stay `not_applicable`.

## Repo Companion Declaration

Adopted repositories declare hook locators through the repo companion
`hook_locators` section.

Each entry uses:

- `id`
- `summary`
- `lifecycle`
- `locator`
- `owner`
- `requirement`
- `fallback_to`
- `safety`

Allowed `lifecycle` values are `before-run`, `after-run`, and `cleanup`.
Allowed `requirement` values are `required`, `optional`, and `advisory`.

`fallback_to` must point to a Loom surface or manual repair path. It must not
point to a host-private action such as a Codex or Claude Code native hook event.

`hook_locators` are declaration-time locators. They must not carry runtime
state, execution result, authored progress, review verdict, validation status,
host action result, or closeout basis.

## Safety Invariants

Each enabled or required hook declaration must include a `safety` object. Missing
safety on an optional or advisory hook remains profile-local advisory evidence;
missing safety on a required hook fails closed.

The stable safety fields are:

- `path_containment`: must be `repo_relative`
- `truth_boundary`: `runtime_evidence_only`, `context_only`, or `blocking_decision_only`
- `cleanup_scope`: `not_applicable` or `loom_owned_only`
- `host_trust`: `trusted`, `requires_review`, or `untrusted`
- `permission_risk`: `none`, `approval_required`, `sandbox_required`, or `unknown`

Safety evaluation is declaration-time only. It does not execute hooks, inspect
host-private hook files, or write status/recovery truth.

Missing or incomplete optional/advisory safety remains profile-local advisory
evidence. It can produce a hooks extension warning, but it must not become an
`orchestration-core` missing input.

Stable fail-closed conditions:

- locator is absolute, contains `..`, or resolves outside the repository root
- a required hook locator is missing or unreadable
- a required hook lacks a safety declaration
- the declaration carries authored progress, recovery/status truth, validation,
  review, host action, or closeout fields
- `host_trust` is `untrusted`
- `permission_risk` is `unknown`
- `cleanup` does not declare `cleanup_scope: loom_owned_only`
- non-cleanup lifecycle declares cleanup deletion scope

Cleanup safety is constrained to explicit Loom-owned residue. Cleanup hooks must
not delete the workspace root, host git worktree state, repo-owned artifacts, or
unmarked files. Unsafe cleanup declarations fail closed before any host-native
hook mapping can be consumed.

## Host Adapter Mapping

Host adapters may install or generate host-native hook config from Loom
locators, but generated config remains downstream of Loom's locator contract.
It does not become Loom-authored truth.

Codex mapping:

- `before-run`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`
- `after-run`: `PostToolUse`, `Stop`, `PostCompact`
- `cleanup`: `not_applicable` or Loom explicit `workspace cleanup|retire` extension

Codex cleanup must never be required as a native host hook.

Claude Code mapping:

- `before-run`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`
- `after-run`: `PostToolUse`, `Stop`, `SubagentStop`, `PostCompact`
- `cleanup`: optional `SessionEnd`, constrained by Loom cleanup safety

The adapter result vocabulary is:

- `supported`
- `not_applicable`
- `advisory`
- `unsafe`

`unsafe` adapter results fail closed when the hook path is required. Advisory or
not-applicable mappings remain profile-local evidence unless an adopted
repository explicitly opts into a stronger extension gate.

## Evidence Boundary

Host-native hook output can only become Loom runtime evidence after adapter
mapping.

Hook output must not write:

- authored progress
- recovery or status truth
- review verdict
- validation summary
- host action result
- closeout basis

Cleanup hooks are always constrained by [workspace-lifecycle.md](./workspace-lifecycle.md):
only Loom-owned residue may be removed, and unmarked content must be preserved.

## Non-goals

- executing hooks
- generating host-native hook files
- copying Codex or Claude Code hook file shapes into Loom core
- replacing `workspace cleanup|retire`
