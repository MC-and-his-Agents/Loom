# Runtime Regression Surface Closeout Evidence

This record preserves the aggregate `loom_check` runtime regression entrypoint
and names the focused runtime validation surfaces that parent #1263 and umbrella
#1255 can consume after #1405, #1406, and #1407 terminalization.

## Scope

- Work Item: WI-1408 / issue #1408
- Parent consumer: #1263
- Umbrella consumer: #1255
- Branch: `work/1408-aggregate-runtime-closeout`
- Change class: docs and repo carrier evidence only
- Release required: no

WI-1408 does not change runtime checker behavior, Makefile command behavior,
shared contract/schema/parser vocabulary, release/package output, VERSION,
tags, GitHub Releases, npm publishing, live external systems, or parent
closeout state. It records the current validation surface map and the aggregate
entrypoint that remains authoritative for merge-ready and parent closeout
evidence.

## Named Runtime Surfaces

| Surface label | Direct command | Make target | Source Work Item |
| --- | --- | --- | --- |
| `single-flight-locking` | `python3 tools/check_loom_check_runtime_regressions.py --surface single-flight-locking` | `make loom-check-runtime-single-flight-locking` | #1405 |
| `worktree-local-lock-paths` | `python3 tools/check_loom_check_runtime_regressions.py --surface worktree-local-lock-paths` | `make loom-check-runtime-worktree-local-lock-paths` | #1405 |
| `installer-regression-lock-output` | `python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output` | `make loom-check-runtime-installer-regression-lock-output` | #1405 |
| `subprocess-env-purity` | `python3 tools/check_loom_check_runtime_regressions.py --surface subprocess-env-purity` | `make loom-check-runtime-subprocess-env-purity` | #1406 |
| `temp-dir-cleanup` | `python3 tools/check_loom_check_runtime_regressions.py --surface temp-dir-cleanup` | `make loom-check-runtime-temp-dir-cleanup` | #1407 |
| `demo-fixture-cleanliness` | `python3 tools/check_loom_check_runtime_regressions.py --surface demo-fixture-cleanliness` | `make loom-check-runtime-demo-fixture-cleanliness` | #1407 |

The internal `runtime-purity-helpers` fixture group remains aggregate-only. It is
not a separately selectable parent closeout surface and must not be cited as an
independent surface label.

## Aggregate Entrypoint

The aggregate runtime regression path remains:

```bash
python3 tools/check_loom_check_runtime_regressions.py
make loom-check-runtime-regression
make loom-check
```

The checker has no `--surface aggregate` selector. Evidence summaries must cite
the no-filter command or Make target for aggregate proof, then list the named
surfaces covered by that aggregate run.

## Parent Consumption Rule

Parent #1263 and umbrella #1255 may consume this record only together with:

- the current PR/head or merge commit that carried the evidence;
- focused surface command results or an aggregate runtime regression result;
- review and PR gate evidence bound to the current head;
- retained issue and PR readback for #1405, #1406, #1407, and #1408;
- an explicit no_release rationale.

This record does not close #1263 or #1255. Those closeouts require separate
watcher authorization, current carrier readback, and parent-specific terminal
metadata.
