# v0.10.0 Live Smoke Foundation

本记录归档 `#597` 的 live smoke foundation 验证结果。

它证明：

- `python3 tools/loom_flow.py live-smoke run --target <repo>` 能产出 `loom-live-smoke/v1`
- target 不存在时会产出 explicit unavailable evidence
- `python3 tools/loom_flow.py live-smoke replay --prior-evidence <path>` 能消费 versioned prior-pass evidence
- `orchestration-live` 仍保持 validation-only / confidence-input 边界

## Commands

```bash
python3 tools/loom_flow.py live-smoke run --target /tmp/loom-missing-live-target --item INIT-0001
python3 tools/loom_flow.py live-smoke replay --prior-evidence docs/evidence/validations/validation-v0.7-live-orchestration-smoke.md
python3 tools/loom_flow.py live-smoke run --target /Users/mc/dev/syvert --item INIT-0001
python3 tools/skills_surface.py check
python3 tools/loom_check.py
make check
```

## Result

- Date: 2026-05-09
- Missing target run result: `warn`
- Missing target evidence:
  - target path unavailable
  - `fallback_to: live-smoke-retry-or-record-unavailable`
  - release interpretation: explicit unavailable evidence is a non-blocking confidence input and does not silently pass
- Replay result: `pass`
- Replay evidence:
  - prior evidence path: `docs/evidence/validations/validation-v0.7-live-orchestration-smoke.md`
  - prior status: `versioned-prior-pass`
  - replay does not rerun adopted-repo commands
- Local adopted repo run result: `warn`
- Local adopted repo target: `/Users/mc/dev/syvert`
- Local adopted repo warnings:
  - `governance-profile upgrade-plan` reports missing `basic_host_binding` and `closeout_reconciliation_read`
  - `runtime-parity validate` reports `.loom/progress/INIT-0001.md` missing `Execution Ledger`
  - `shadow-parity` reports unreadable repo interop carrier fields
  - `flow resume` reports the same fact-chain gap
- `python3 tools/skills_surface.py check`: `pass`
- `python3 tools/loom_check.py`: `pass`
- `make check`: `pass`
- Release interpretation: profile-local live smoke failure lowers release confidence but does not replace `orchestration-core` gate results.
- Remaining risk:
  - current live target still exposes repo-local adoption gaps, so v0.10.0 currently proves real feedback wiring, not a full adopted-repo green path
