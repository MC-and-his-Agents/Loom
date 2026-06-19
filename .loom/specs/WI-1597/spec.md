# WI-1597 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1597 is a focused host API authentication and failure-classification hardening slice with deterministic host adapter checks, CLI contract coverage, generated runtime parity, and demo fixture validation; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1598 convergence, and milestone closeout may consume this minimal suite only for host API auth/readback behavior; recheck condition: require broader suite artifacts if scope expands into PR metadata update semantics, closeout PR role roles, release resume/publishing, issue dependency parsing, controlled merge behavior, permissions beyond host API classification, or external-visible host mutations.

## Objective

Make host API reads use local `gh` authentication safely and classify unreadable, rate-limit, and permission failures consistently.

## Acceptance Scenarios

### S1: Host reads prefer authenticated `gh` calls

Given a local `gh` keyring is available, host REST readback uses that authenticated path before considering public anonymous fallbacks.

### S2: Failures produce actionable classifiers

Given host REST is unreadable, rate-limited, or permission-denied, Loom reports `host_api_unreadable` or `permission` with a stable next action instead of conflating the failures.

## Acceptance Criteria

- A1: host REST helpers prefer `gh api` and avoid anonymous fallback when local auth exists but the process lacks `GH_TOKEN`.
- A2: anonymous public REST rate-limit is classified as `host_api_unreadable`.
- A3: permission failures are classified separately as `permission`.
- A4: merge/check/closeout/readback host API paths consume the same helper/classifier behavior.
