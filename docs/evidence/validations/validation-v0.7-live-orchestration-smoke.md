# v0.7.0 Live Orchestration Smoke

本记录归档 v0.7.0 的最小 adopted repo live smoke evidence。

它是 `orchestration-live` release confidence 输入，不是普通 PR 的默认 blocking gate。

## 1. Target

- Adopted repo family: Syvert-style strong governance adopted repo
- Prior smoke evidence: [validation-syvert-reverse-consumption-smoke.md](./validation-syvert-reverse-consumption-smoke.md)
- Smoke branch recorded there: `chore/loom-phase-d-smoke-companion`
- Smoke commit recorded there: `9a7b2923b6ab39631d8a3eafc1be8e5090709b9d`
- Smoke worktree recorded there: `/Users/mc/dev/syvert-loom-phase-d-smoke`

This v0.7.0 evidence consumes that existing adopted repo smoke path as real feedback for release readiness. It does not require the Syvert smoke branch to be merged into Syvert `main`.

## 2. Commands

The live smoke path is considered available when the adopted repo worktree exists locally:

```bash
test -d /Users/mc/dev/syvert-loom-phase-d-smoke
python3 <loom_repo_root>/tools/loom_flow.py governance-profile status --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 <loom_repo_root>/tools/loom_flow.py governance-profile upgrade-plan --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 <loom_repo_root>/tools/loom_flow.py runtime-parity validate --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 <loom_repo_root>/tools/loom_flow.py shadow-parity --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 <loom_repo_root>/tools/loom_flow.py shadow-parity --target /Users/mc/dev/syvert-loom-phase-d-smoke --blocking
python3 <loom_repo_root>/tools/loom_flow.py flow resume --target /Users/mc/dev/syvert-loom-phase-d-smoke --item INIT-0001
```

If the adopted repo worktree, host credentials, or branch is unavailable, the smoke must emit explicit `skip` / `unavailable` evidence with the missing path or host precondition. It must not silently pass.

## 3. Evidence Status

Current release evidence status: `versioned-prior-pass`.

Basis:

- The Syvert reverse-consumption smoke is versioned in this repository.
- It records target, smoke branch, smoke commit, worktree and command set.
- It demonstrates Loom can consume an adopted repo strong-governance surface without copying that repo's guardian or release-specific rules into Loom core.

Current environment fallback:

- If `/Users/mc/dev/syvert-loom-phase-d-smoke` is unavailable during a normal PR, `orchestration-live` reports `unavailable` and remains non-blocking for the ordinary PR.
- Release closeout may choose to rerun the live smoke or consume this versioned prior-pass evidence as confidence input.

## 4. Current PR Availability Evidence

- Date: 2026-05-08
- Loom checkout: `/Users/mc/dev/Loom-worktrees/work-556-conformance-live-readiness`
- Adopted repo target: `/Users/mc/dev/syvert-loom-phase-d-smoke`
- Result: `unavailable`
- Missing precondition: adopted repo worktree is not present at `/Users/mc/dev/syvert-loom-phase-d-smoke`
- Commands run: `test -d /Users/mc/dev/syvert-loom-phase-d-smoke`
- Commands not run: governance-profile status, governance-profile upgrade-plan, runtime-parity validate, shadow-parity, blocking shadow-parity, flow resume
- Release interpretation: explicit unavailable evidence is a non-blocking confidence input for the ordinary PR; it does not silently pass and does not replace the versioned prior-pass basis.

## 5. Release Boundary

This smoke raises release confidence for v0.7.0 because it exercises a real adopted repo path.

It does not:

- replace `orchestration-core`
- become a default PR blocking gate
- require Syvert `main` migration
- promote Syvert repo-native guardian, sprint, release or integration-contract semantics into Loom core
