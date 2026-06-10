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
- The prepared fixture clone helper uses `git clone --no-local`, removes `origin`, applies local git author config, and verifies target `HEAD`.
- Fake Codex review fixtures now drain prompt stdin and use explicit invalid JSON for the schema-drift negative case, avoiding prompt-pipe deadlocks and ambiguous schema fixtures as the prepared baseline reuse changes prompt/context size.
- Review-run fixture subprocesses use fixture-private `HOME` and `TMPDIR` so Codex App host discovery cannot read workstation `.codex` sessions or default `codex-ipc` sockets while validating fallback behavior.
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

Rejected approaches:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result with raw `shutil.copytree()` of prepared git baselines:

```text
elapsed=387.45s failures=2
real 389.20
```

Classification: unsafe/insufficient reuse. Raw copying a prepared git worktree caused review-run fixture failures and was not used.

Result with local `git clone --no-hardlinks` from the prepared baseline:

```text
loom_check: end source surface=review-run step=review-run elapsed=201.60s failures=0
real 203.59
```

Classification: locally fast, but hosted Linux `make loom-check` failed in `review-run-fixture` with `fatal: update_ref failed for ref 'HEAD': cannot update ref 'refs/heads/master': trying to write ref ... with nonexistent object ...`. This was rejected because it was not cross-platform stable.

After implementation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result:

```text
loom_check: end source surface=review-run step=review-run elapsed=302.30s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 303.78
```

Installed runtime validation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface installed-runtime .
```

Result:

```text
loom_check: end source surface=installed-runtime step=installed-runtime elapsed=128.40s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 129.86
```

Current-main base sync validation after rebasing onto `origin/main` `cd6a6760fd348648c8b9372ac21c5fe4029686b4`:

```text
git merge-base HEAD origin/main
```

Result:

```text
cd6a6760fd348648c8b9372ac21c5fe4029686b4
```

The first post-rebase `review-run` check exposed mutable host-state drift from workstation Codex App discovery:

```text
loom_check: end source surface=review-run step=review-run elapsed=323.95s failures=3
```

Classification: fixture environment drift. The failing payloads showed discovery of a real default Codex App control socket/session outside the fixture target. The fixture now sets private `HOME` and `TMPDIR`, and debug readback showed host discovery searching only the fixture-owned `hostless-home` and `hostless-tmp` paths.

Post-fix `review-run` validation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .
```

Result:

```text
loom_check: end source surface=review-run step=review-run elapsed=152.95s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 154.14
```

Post-rebase installed runtime validation:

```text
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface installed-runtime .
```

Result:

```text
loom_check: end source surface=installed-runtime step=installed-runtime elapsed=115.00s failures=0
loom_check: OK (/Users/mc/.codex/worktrees/edaa/Loom)
real 116.28
```

## Isolation Evidence

The final reuse helper uses:

```text
git clone --quiet --no-local <baseline> <target>
git remote remove origin
git config user.email loom-check@example.com
git config user.name loom-check
git rev-parse --verify HEAD
```

This preserves isolation because each scenario target receives its own working tree and pack-generated object store, the temporary baseline is not retained as a remote truth source, and later scenario mutations happen only inside that target clone. `--no-local` avoids local clone hardlinks/alternates and avoids the hosted Linux local-object/ref failure observed with `--no-hardlinks`.

The reusable baselines live under `loom_check_temporary_directory(...)` and are deleted with the same temporary directory cleanup as the previous per-scenario targets.

Review-run subprocesses additionally run with fixture-owned `HOME` and `TMPDIR`. That keeps Codex App fallback tests from consuming workstation/session truth while still allowing scenarios that pass explicit `--codex-app-review-*` proof to exercise the intended host-bound paths.

## Static Validation

```text
git diff --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py skills/*/.loom-runtime/shared/scripts/loom_check.py examples/new-project/.loom/bin/loom_check.py
```

Result:

```text
py_compile_clean: OK (14 files)
```

Additional parity/demo checks:

```text
python3 tools/skills_surface.py check
make loom-demo-new-project-check
make repo-local-cli-fast GROUP=setup-demo-bootstrap
```

Result:

```text
skills surface check: OK
demo bootstrap fixture: OK (examples/new-project)
demo bootstrap fixture: OK (examples/new-project)
```
