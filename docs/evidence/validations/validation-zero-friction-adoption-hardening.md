# Validation: zero-friction downstream adoption hardening

本记录归档 `#367` 这一轮 zero-friction downstream adoption hardening 的验证结论。

## 目标

本轮目标不是继续修 Syvert PR #259，而是把 Syvert strong-governance adoption 暴露出的通用阻力 upstream 到 Loom。

完成后，下游仓库接入 Loom 时应能依靠 Loom 自身能力完成以下动作：

- 验证 downstream producer / consumer round-trip。
- 统一刷新 Loom-owned carrier metadata。
- 校验 host binding 的 branch / issue / PR / SHA 推断边界。
- 在 Loom 仓内复现 Syvert-style 强治理接入压力。

## 合并记录

- `#374` / `#368`: `feat(runtime): harden repo-relative carrier path boundaries`
- `#375` / `#369`: `feat(adoption): add downstream adopt verify round-trip contract`
- `#376` / `#370`: `feat(carrier): add unified Loom carrier refresh`
- `#377` / `#371`: `feat(host-binding): validate SHA branch issue and PR inference`
- `#378` / `#372`: `test(adoption): extend Syvert-style zero-friction fixture`
- `#373`: 本 evidence closeout

## Runtime Interfaces

本轮新增或固化的 public runtime entry：

```bash
python3 tools/loom_flow.py adopt verify --target examples/new-project --item INIT-0001
python3 tools/loom_flow.py carrier refresh --target examples/new-project --dry-run
python3 tools/loom_flow.py host-binding validate --target . --owner MC-and-his-Agents --repo Loom --branch main
python3 tools/loom_flow.py host-binding validate --target . --owner MC-and-his-Agents --repo Loom --head-sha <sha>
```

稳定输出 schema：

- `loom-adoption-verify/v1`
- `loom-carrier-refresh/v1`
- `loom-host-binding/v1`

## 已覆盖的风险

- repo locator 必须是 target-root 内的 repo-relative path。
- 绝对路径、`..` escape、target-root 外 locator 必须返回 `block`。
- `Review Artifacts` required section 被删除时，consumer 必须返回 `block`。
- manifest 与 init-result 的 `.loom/bin/*` artifact hash 漂移可由 `carrier refresh --dry-run` 报告，并由 `--write` 修复。
- shadow evidence 的 `source_files` 与 `source_sha256` 必须闭包一致。
- missing hash、partial hash、hash drift、undeclared evidence 都进入 adversarial fixture。
- carrier-only review metadata 可以刷新；implementation drift 或 mixed drift 必须 `block`，要求重新 review。
- SHA-only host binding 无法通过 REST 证明 issue / PR 归属时必须 fail closed。
- CI 无 `GH_TOKEN` 时，公开 GitHub REST 读取可以 fallback 到 HTTPS REST，不重新引入高频 GraphQL。

## 验证命令

每个 Work Item PR 合并前均通过：

```bash
make py-compile
python3 tools/loom_check.py .
make loom-check
npm --prefix packages/loom-installer test
```

本轮新增接口的显式验证包括：

```bash
python3 tools/loom_flow.py adopt verify --target examples/new-project --item INIT-0001
python3 tools/loom_flow.py carrier refresh --target examples/new-project --dry-run
python3 tools/loom_flow.py host-binding validate --target . --owner MC-and-his-Agents --repo Loom --branch main
GH_CONFIG_DIR=/tmp/loom-empty-gh-config python3 tools/loom_flow.py host-binding validate --target . --owner MC-and-his-Agents --repo Loom --branch main
```

## 剩余边界

- 本轮不把 Syvert guardian、integration contract、release / sprint 语义迁入 Loom core。
- 本轮不恢复或修改 Syvert PR #259。
- Syvert official adoption 的下一步应先刷新 vendored `.loom/bin/*` 到包含本轮 hardening 的 Loom `main`，再运行上述 Loom-on-downstream 验证。
- ProjectV2 与 native sub-issues 仍属于 GitHub profile 的 GraphQL-only 路径，只允许在明确预算边界内使用。

## 结论

Loom 已经把 Syvert PR #259 暴露的接入阻力收成 upstream runtime 能力与 Loom-owned fixture。

后续恢复 Syvert official adoption 时，预期流程应是：

1. refresh Loom runtime carrier。
2. run `adopt verify`、`carrier refresh --dry-run`、`host-binding validate`、`loom_check`。
3. 只修复这些命令明确报告的问题。
4. 再进入 Syvert guardian 与 controlled merge。
