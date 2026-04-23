# Validation: Complex-Existing Second-Sample Counterevidence

## 1. 样本标识

- 第一复杂既有样本：`hotcp`
  - 归档记录：历史复杂既有仓库验证
- 第二复杂既有样本：
  - `Syvert`：`/Users/mc/dev/syvert`
  - `WebEnvoy`：`/Users/mc/dev/WebEnvoy`
- 验证日期：`2026-04-23`
- 对应 Loom issue：`#275`

本记录只做只读验证，不对 `Syvert` / `WebEnvoy` 执行 `--write`。

## 2. 目标

`#275` 在复杂既有仓库这一半要回答的不是“再找一个仓库重复支持 `hotcp`”，而是：

- 是否存在独立于 `hotcp` 的第二复杂既有仓库样本
- 它到底支持“更完整装配”，还是反证并继续支持 `deep-existing-repo` attach-only

## 3. 当前仓库事实与默认判断

### 3.1 `Syvert`

执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert
```

结果：

- `scenario_key = complex-existing`
- `recommended_adoption.path = full-bootstrap`
- `github_control_plane.repository = MC-and-his-Agents/Syvert`

说明：

- Loom 当前自动探测依然保守
- 它不会把成熟治理重仓直接伪装成“已经 live attach-only”

### 3.2 `WebEnvoy`

执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/WebEnvoy
```

结果：

- `scenario_key = complex-existing`
- `recommended_adoption.path = full-bootstrap`
- `github_control_plane.repository = MC-and-his-Agents/WebEnvoy`

说明：

- `WebEnvoy` 同样先被保守判到 `full-bootstrap`
- 这证明 Loom 当前不会仅凭“复杂”自动跳到 attach-only

## 4. 显式成熟治理信号下的 attach-only 结果

为了验证第二样本在成熟治理条件下的真实落点，本次对两个仓库都使用同一类显式 intake：

- `repository_type = existing`
- `root_boundary_docs = clear`
- `ci_or_basic_tests = true`
- `repository_level_validation_entry = true`
- `shared_contract_or_high_risk_boundary = true`
- `merge_review_semantic_overload = true`

执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert --intake /tmp/loom-275-syvert-intake.json
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/WebEnvoy --intake /tmp/loom-275-webenvoy-intake.json
```

两仓共同结果：

- `scenario_key = complex-existing`
- `recommended_adoption.path = deep-existing-repo`
- `project_judgment.primary_structural_problem = the repo already has a mature governance stack`
- `fact_chain.mode = repo-native attach-only`
- `initial_work_items[0].execution_path = recognize-and-attach`

attach-only 输出边界也保持一致：

- 会生成：
  - `.loom/README.md`
  - `.loom/bootstrap/*`
  - `.loom/companion/README.md`
  - `.loom/companion/checkpoints.md`
  - `.loom/companion/review.md`
  - `.loom/companion/merge-ready.md`
  - `.loom/companion/closeout.md`
  - repo-local `.loom/bin/*`
- 不会生成：
  - `.loom/work-items/*`
  - `.loom/progress/*`
  - `.loom/status/current.md`

## 5. 这组第二样本实际说明了什么

它们证明两件事：

1. `Syvert` / `WebEnvoy` 确实是独立于 `hotcp` 的复杂既有仓库第二样本
2. 这组第二样本不支持把 `complex-existing` 或“历史入口并存”直接升级成默认 `full-bootstrap`

更精确地说：

- `hotcp` 继续支撑：
  - 某些复杂既有仓库确实需要更完整装配
- `Syvert` / `WebEnvoy` 共同反证：
  - 对已有稳定根规则、统一验证入口、成熟宿主动作与 repo-native carriers 的重仓，第一轮更合理的默认值仍然是 `deep-existing-repo`
  - 也就是先 `recognize-and-attach`，而不是立刻生成 Loom-owned recovery/status carriers

## 6. 对 `EXT-0046` / `EXT-0047` 的影响

### 6.1 `EXT-0046`

本次不升为 `core`，继续停在 `adapt/candidate`。

原因：

- `hotcp` 证明“某类复杂既有仓库需要更完整装配”
- `Syvert` / `WebEnvoy` 证明“复杂既有仓库”并不是足以自动触发 `full-bootstrap` 的充分条件

因此，`EXT-0046` 当前只能表达为：

- 一组候选升级信号
- 需要继续靠更多 live adopted repo 区分“该 attach-only”还是“该 full-bootstrap”

### 6.2 `EXT-0047`

本次同样不升为 `core`，继续停在 `adapt/candidate`。

原因：

- `hotcp` 支撑“现行入口与历史入口并存”可能是恢复与状态升级信号
- `Syvert` / `WebEnvoy` 反证说明：如果成熟根规则、统一验证入口和 attach-only 读面已经足够稳定，这个信号本身还不足以强制生成 Loom-owned recovery/status carriers

## 7. 结论

`#275` 在“复杂既有仓库第二样本”这一半的正式结论是：

- 第二样本已存在
- 它是反证，不是重复支持
- `EXT-0046` / `EXT-0047` 继续保留 `candidate`
- `deep-existing-repo` 的 attach-only 默认值得到再次补强，但不改变其现有 `keep/core` 状态
