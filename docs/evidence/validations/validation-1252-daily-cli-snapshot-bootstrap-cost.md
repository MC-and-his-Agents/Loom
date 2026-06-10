# Validation: WI-1252 daily CLI snapshot/bootstrap cost

Date: 2026-06-10

Worksite: `/Users/mc/.codex/worktrees/edaa/Loom`

Branch: `work/1252-daily-cli-snapshot-bootstrap-cost`

Head before commit: `9a9705b83e1942caf2a5b55533ec840d64b5dd44`

## Scope

Issue #1252 reduces repeated source snapshot and bootstrap setup cost without weakening fixture isolation or repository truth boundaries.

Changed surface:

- `check_review_run_fixture()` now prepares one `review-run-baseline`, then clones independent per-scenario targets from it.
- `check_installed_runtime_fixture()` now prepares one installed pre-merge baseline, then clones independent `positive_target` and `review_fallback_target` copies from it.
- Generated runtime copies are synchronized with `src/skills/shared/scripts/loom_check.py`.

Unchanged boundary:

- No `daily-execution-cli` progress/timing/failure label ownership was changed.
- No review-run fixture group names were split or renamed.
- No Codex App fallback truth boundary was redefined.
- No fast/full validation entrypoint was added.

## Timing Evidence

Before implementation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result: the run stayed inside the single `review-run` step and was terminated after `ps` showed `etime=13:53`. It had only emitted:

```text
loom_check: start source surface=review-run step=review-run
```

Classification: focused `review-run` baseline was too expensive to complete before modification; this is a lower bound of more than 833 seconds.

Intermediate rejected approach:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result with raw `shutil.copytree()` of prepared git baselines:

```text
elapsed=387.45s failures=2
real 389.20
```

Classification: unsafe/insufficient reuse. Raw copying a prepared git worktree caused review-run fixture failures, so the final implementation switched to `git clone --no-hardlinks` from the prepared baseline.

After implementation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result:

```text
loom_check: end source surface=review-run step=review-run elapsed=201.60s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 203.59
```

Installed runtime validation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface installed-runtime .
```

Result:

```text
loom_check: end source surface=installed-runtime step=installed-runtime elapsed=124.64s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 127.20
```

## Isolation Evidence

The final reuse helper uses:

```text
git clone --quiet --no-hardlinks <baseline> <target>
git remote remove origin
git config user.email loom-check@example.com
git config user.name loom-check
```

This preserves isolation because each scenario target receives its own working tree and object store, the temporary baseline is not retained as a remote truth source, and later scenario mutations happen only inside that target copy.

The reusable baselines live under `loom_check_temporary_directory(...)` and are deleted with the same temporary directory cleanup as the previous per-scenario targets.

## Static Validation

```text
git diff --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py skills/*/.loom-runtime/shared/scripts/loom_check.py
```

Result:

```text
py_compile_clean: OK (13 files)
```
