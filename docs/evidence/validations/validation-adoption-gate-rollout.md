# Validation: adoption gate rollout

本记录证明 `#355` 把 adoption gate rollout 从说明收成机器可读合同。

## Scope

本轮只定义 adoption gate 的 rollout / rollback 消费语义，不把任何 adopted repo 默认切到 blocking。

稳定模式固定为：

- `advisory`
- `blocking`
- `rollback`

## Runtime contract

`governance-profile status` 与 `governance-profile upgrade-plan` 必须通过 `governance_control_plane.maturity.gate_rollout` 暴露：

- `schema_version: loom-adoption-gate-rollout/v1`
- `default_mode: advisory`
- `current_mode`
- `recommended_mode`
- `allowed_modes`
- `blocking_allowed`
- `blocking_preconditions`
- `rollback`

`governance-profile upgrade --dry-run` 必须输出同一 `gate_rollout`，让 adoption 工具和后续 gate 消费同一个 rollout 判断。

## Blocking preconditions

进入 `blocking` 前必须同时满足：

- `strong_maturity`
- `adversarial_adoption_checks`
- `rollback_switch`

新下游仓库默认仍是 `advisory`。只有 adversarial adoption checks 有版本控制内证据后，profile 才允许显式启用 blocking。

## Rollback rule

`rollback` 必须切回 `advisory`，并保留 evidence。rollback 的目标不是删除 Loom，而是在 runtime、evidence、host binding、review head 或 metadata parsing 漂移时暂停 blocking 消费。

## Validation commands

```bash
python3 tools/loom_flow.py governance-profile status --target examples/new-project
python3 tools/loom_flow.py governance-profile upgrade-plan --target examples/new-project
python3 tools/loom_flow.py governance-profile upgrade --target examples/new-project --to standard --dry-run
python3 tools/loom_check.py .
```

## Result

`loom_check` 现在验证 `gate_rollout` 的 schema、三态模式、blocking 前置条件、rollback switch 和 upgrade 输出一致性。
