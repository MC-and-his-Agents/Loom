# Implementation Contract

## Owned Surface

- `src/skills/shared/scripts/loom_check.py`
- generated/runtime copies of `loom_check.py`
- `.loom/specs/WI-1151/*`
- `.loom/work-items/WI-1151.md`
- `.loom/progress/WI-1151.md`
- `.loom/progress/WI-1149.md` terminal fact-chain sync only, because PR #1186 is already merged/closed but `origin/main` still carries a merge checkpoint carrier that blocks single-active-WI purity after #1151 rebase.
- `.loom/reviews/WI-1151.spec.json`
- `.loom/reviews/WI-1151.json`
- generated hash carriers for changed `loom_check.py`
- `.loom/shadow/merge-ready-loom.json` and `.loom/shadow/closeout-loom.json` status hash parity only, when `.loom/status/current.md` changes for the #1151 active carrier.

## Behavior Contract

- Scaffold dry-run fixture must not mutate the target tree.
- Scaffold apply fixture must create only contracted full suite scaffold artifacts.
- Host truth negative fixture must prove forbidden truth surfaces are unchanged after scaffold apply.
- The fixture may use temporary targets only; it must not write host truth or generated skill truth in the real repository.

## Non-Goals

- No new scaffold artifact types.
- No scaffold implementation behavior change unless required by failing fixture evidence.
- No parent FR or phase closeout.

## Validation Contract

- Focused CLI contract and source-surface checks are required before PR.
- Source/generated/runtime copies must stay synchronized.
