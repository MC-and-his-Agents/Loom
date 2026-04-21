# Validation: Deep-Existing Repo With Syvert And WebEnvoy

## 1. 样本标识

- 样本仓库：
  - `Syvert`：`/Users/mc/dev/syvert`
  - `WebEnvoy`：`/Users/mc/dev/WebEnvoy`
- 仓库类型：`复杂既有仓库`
- 验证日期：`2026-04-21`
- 对应 Loom issue：`#247`

本记录分两层取证：

1. 直接读取 `Syvert` / `WebEnvoy` 当前仓库事实，验证 Loom 为什么必须保留 root rules、retained host actions 与 repo-native carriers
2. 使用 `loom-init` 的显式 intake override 与 `loom_check` synthetic fixtures，验证 `deep-existing-repo`、typed `repo companion`、`repo interop` 与 `shadow parity` 的正式合同

本次没有对源仓库执行 `--write`。所有正向 bootstrap 结论都来自无写入验证或 Loom 仓内 synthetic fixtures。

## 2. 样本事实

### 2.1 `Syvert`

- 已有清晰根级边界文档：`AGENTS.md`、`WORKFLOW.md`
- 已有成熟执行面脚本：`scripts/create_worktree.py`、`scripts/open_pr.py`、`scripts/merge_pr.py`、`scripts/sync_repo_settings.py`
- 已有 repo-native truth / carrier：
  - `docs/exec-plans/**`
  - `scripts/governance_status.py`
  - 仓库本地 integration / policy 输出
- 当前复杂度不在“缺最小治理入口”，而在“已有治理栈很重、host actions 很重、repo-native carriers 很重”

直接执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert
```

结果：

- `scenario_key = complex-existing`
- 默认 `recommended_adoption.path = full-bootstrap`
- 当前自动探测没有把该仓库识别成 `deep-existing-repo` 正样本

这说明 Loom 当前对真实重仓样本仍保持保守；它不会仅凭“仓库很复杂”就擅自切到 attach-only 路径。

### 2.2 `WebEnvoy`

- 已有清晰根级边界文档与治理入口
- 已有统一 PR 元数据承载面，例如：
  - `integration_check`
  - `gate_applicability`
  - `live_evidence_record`
- 已有 repo-specific review / guardian 负担与较重的条件化 gate
- 当前复杂度主要来自 metadata contract、typed gates、host adapter result consumption 与 overload 前移，而不是缺基本规则文档

直接执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/WebEnvoy
```

结果：

- `scenario_key = complex-existing`
- 默认 `recommended_adoption.path = full-bootstrap`
- 当前自动探测同样没有把该仓库直接判成 `deep-existing-repo`

因此，`WebEnvoy` 也证明了同一件事：Loom 当前保持保守 attach 口径，不会把 reference sample 自动伪装成 live adopted repo。

## 3. `deep-existing-repo` Validation

为了验证正向 attach-only 路径，本次对两个样本都使用同一组显式 mature-governance intake 信号：

- `repository_type = existing`
- `root_boundary_docs = clear`
- `repository_level_validation_entry = true`
- `shared_contract_or_high_risk_boundary = true`
- `merge_review_semantic_overload = true`

执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert --intake <override>
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/WebEnvoy --intake <override>
python3 tools/loom_check.py
```

结果：

- 两个样本都稳定返回：
  - `scenario_key = complex-existing`
  - `governance_surface.repository_mode = complex-existing`
  - `recommended_adoption.path = deep-existing-repo`
  - `fact_chain.mode = repo-native attach-only`
- `deep-existing-repo` 的 initial artifacts 只包含 attach metadata、`.loom/companion/*` 与 repo-local `.loom/bin/*`
- 正向路径不生成 `.loom/work-items`、`.loom/progress`、`.loom/status`
- `loom_check` 同时复验：
  - 正向 `deep-existing-repo` attach-only sample
  - 缺少成熟治理信号时回退到 `full-bootstrap`

结论：

- `deep-existing-repo` 已可作为 `complex-existing` 下的正式 adoption path 进入 `keep`
- 它不是新的 `repository_mode`
- 真实 live repo 的 auto-detection 仍保持保守，不应把这点误写成“Loom 已经自动接管 Syvert/WebEnvoy”

## 4. Typed `repo companion` Validation

本次 companion 合同验证同时消费：

- [reference-companion-spec-syvert.md](./reference-companion-spec-syvert.md)
- [reference-companion-spec-webenvoy.md](./reference-companion-spec-webenvoy.md)
- [validation-repo-companion-interface.md](./validation-repo-companion-interface.md)
- `python3 tools/loom_check.py`

结果：

- `repo-interface v2` 在保持 `v1` 继续可读的前提下，已经可以稳定承接：
  - typed `specialized_gates[*].gate_type`
  - `context_schema`
  - 可选 `metadata_contract`
- `Syvert` 样本证明：
  - `admission` / `build` typed gates
  - `review` / `merge_ready` / `closeout` blocking requirements
  - `issue`、`item_key`、`item_type`、`release`、`sprint` 这类 repo-specific context fields
- `WebEnvoy` 样本证明：
  - `pre_review` / `review` typed gates
  - `guardian_lane`、`evidence_window` 这类 repo-specific context fields
  - `integration_check`、`gate_applicability`、`live_evidence_record` 这类 repo-specific metadata fields
- `loom_check` synthetic fixtures 已覆盖：
  - `v1` / `v2` 并存读取
  - 非法 `gate_type`
  - 非法 `metadata_contract`
  - 非法 `context_schema`

结论：

- 进入 `keep`
  - typed `specialized_gates`
  - locator-first 的 `context_schema`
- 继续停在 `adapt`
  - `metadata_contract` 的字段 taxonomy
  - 哪些 metadata field 应该成为跨仓复用的稳定集合

## 5. `repo interop` Validation

本次 interop 验证消费：

- [repo-interop-contract.md](./repo-interop-contract.md)
- [host-action-contract.md](../harness/host-action-contract.md)
- `python3 tools/loom_check.py`

样本结论：

- `Syvert`
  - retained host actions 继续由宿主脚本承接
  - `docs/exec-plans/**`、`governance_status.py` 等仍保留为 repo-native carriers
- `WebEnvoy`
  - guardian verdict、integration / evidence verdict 继续保留在 repo-local host / carrier 层
  - Loom 需要的是统一 read surface，而不是重写 PR / worktree / merge 生命周期动作

`loom_check` synthetic fixtures 已覆盖：

- `interop.json` 缺失 / 非法 / 完整输入
- `governance_surface.repo_interop` 的 `absent | incomplete | present`
- `host_adapters`
- `repo_native_carriers`
- `shadow_surfaces`

结论：

- 进入 `keep`
  - companion-owned `interop.json`
  - retained host action result / repo-native carrier 的 read-only consumption boundary
- 继续停在 `adapt`
  - host adapter payload taxonomy
  - repo-native carrier 的细字段与具体 locator 形状

## 6. `shadow parity` Validation

本次 parity 验证消费：

- [repo-interop-contract.md](./repo-interop-contract.md)
- `python3 tools/loom_flow.py shadow-parity --target examples/new-project`
- `python3 tools/loom_check.py`

结果：

- `python3 tools/loom_flow.py shadow-parity --target examples/new-project`
  - 当前样本因不存在 `interop.json`，按合同返回 `warn`，并把四个 surface 都标成 `unreadable`
- parity compare 的固定 surfaces 已冻结为：
  - `admission`
  - `review`
  - `merge_ready`
  - `closeout`
- parity compare 结果固定为：
  - `match`
  - `mismatch`
  - `unreadable`
- `loom_check` synthetic fixtures 已覆盖：
  - present / match sample
  - mismatch sample
  - 缺失或非法 `interop.json`

样本归纳：

- `Syvert` 证明 Loom 需要能对照 admission / review / merge-ready / closeout 的 repo-native结论
- `WebEnvoy` 证明 parity compare 必须允许把 guardian / metadata / evidence 结果留在 repo-local truth，而不是写进 Loom core gate

结论：

- 进入 `keep`
  - `shadow parity` 作为 validation-only compare surface
- 继续停在 `needs_validation`
  - 把 parity mismatch 自动提升为 blocking merge gate

## 7. 摩擦、失效点与升级信号

### 当前成立的证据

- 成熟治理重仓的第一步需求，确实是 attach path、typed companion、repo interop 与 shadow validation
- `deep-existing-repo` 能在不引入第四种 `repository_mode` 的前提下，稳定表达 attach-only adoption
- `repo-interface v2` 与 `interop.json` 已把 machine contract 与 read surface 分开

### 当前仍存在的摩擦

- 真实 `Syvert` / `WebEnvoy` 仓库扫描仍然保守，当前 auto-detection 不应被夸大为“已经 live dogfood”
- `metadata_contract` 目前主要仍由 `WebEnvoy` 样本支持
- `shadow parity` 的 compare 面已经稳定，但“何时应自动阻断 merge”还没有足够 live adopted repo 证据

### 下一轮升级信号

- 第二批 live adopted repo 完成 `interop.json` 与 shadow parity dogfood
- 出现第二个独立仓库证明 `metadata_contract` 需要更稳定的跨仓字段 taxonomy
- 出现真实仓库证明 parity mismatch 可以安全提升为 merge / closeout gate，而不是仅做 validation surface

## 8. Release Judgment

本树按 `v0.6.0 / minor` 收口。

原因：

- `repository_mode` 枚举没有变化
- root contract 没有变化
- 既有 CLI 顶层结果语义没有被破坏
- attach-only 路径没有改写既有 full-bootstrap 路径
- `repo-interface v2` 保持 `v1` 可读
- `interop.json` 与 `shadow parity` 仍是 read-only / validation-only surface，没有被抬成新的默认 merge gate

## 9. 台账回写结果

- 新增 `EXT-0048`
  - `keep`
  - `deep-existing-repo` 成为 `complex-existing` 下的正式 attach-only adoption path
- 新增 `EXT-0049`
  - `keep`
  - typed `specialized_gates` 与 locator-first `context_schema` 成为稳定 companion 合同
- 新增 `EXT-0050`
  - `adapt`
  - `metadata_contract` 作为可选 `v2` 扩展保留，但字段 taxonomy 继续候选
- 新增 `EXT-0051`
  - `keep`
  - retained host action result / repo-native carrier 的 read-only interop 合同已稳定
- 新增 `EXT-0052`
  - `keep`
  - `shadow parity` 作为 validation-only compare surface 已稳定
- 新增 `EXT-0053`
  - `needs_validation`
  - parity mismatch 自动升级为 blocking merge gate 仍待更多 live adopted repo 证明

受影响落点：

- `adoption/deep-existing-repo-default.md`
- `adoption/deep-existing-repo-workflow.md`
- `adoption/repo-companion-contract.md`
- `adoption/repo-companion-migration.md`
- `adoption/repo-interop-contract.md`
- `adoption/versioning-and-upgrades.md`
- `adoption/upstream-delivery-surface.md`
- `docs/complete-kernel-release.md`

## 10. Closeout Basis

`#247` 关闭时，父树 `#242` 已具备直接消费的正式依据：

- `#243`
  - 边界、PR slices 与 release judgment 口径已冻结
- `#244`
  - `deep-existing-repo` attach-only adoption path 已进入正式合同
- `#245`
  - `repo-interface v2`、typed gates、metadata/context contract 已进入正式合同
- `#246`
  - `interop.json`、repo-native carrier read surface 与 `shadow parity` 已进入正式合同
- `#247`
  - `Syvert` / `WebEnvoy` validation、`v0.6.0 / minor` release judgment 与 parent closeout basis 已进入版本控制

因此，`#242` 的 closeout comment 不再需要依赖会话补充解释：

- 为什么 `deep-existing-repo` 不是第四个 scenario
- 为什么 Loom 仍不接管 branch / PR / worktree / merge 的宿主实现
- 为什么 `shadow mode` 目前只做 validation，而不是新的 merge gate
