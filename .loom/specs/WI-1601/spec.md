# WI-1601 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1601 is a focused release readback and resume classification slice with deterministic CLI contract coverage, release-state fixtures, and docs/runtime parity checks; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1598 convergence, and milestone closeout may consume this minimal suite only for release readback/resume behavior; recheck condition: require broader suite artifacts if scope expands into GitHub Actions publishing, v0.15.0 release closeout, closeout PR role modeling, issue dependency parsing, host auth, or PR metadata rendering.

## Objective

Make release status resumable by reading tag, GitHub Release, npm, and workflow state and classifying partial publish cases.

## Acceptance Scenarios

### S1: Release state can be read back

Given a release intent, the CLI reports tag, GitHub Release, npm, and workflow state without performing a publish.

### S2: Partial publish state is classified for resume

Given a partial publish state, the CLI classifies the resume posture and exposes the next action without replacing the existing GitHub Actions publishing path.

## Acceptance Criteria

- A1: release readback accepts release intent inputs and reports tag, GitHub Release, npm, and workflow status.
- A2: resume classification distinguishes complete, unpublished, partial, and conflicting release states.
- A3: next actions are machine-readable and preserve GitHub Actions as the publishing authority.
- A4: fixtures cover partial publish and conflict/readback cases.
