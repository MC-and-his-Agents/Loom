# Real Adoption Validation: Second New-Project Sample

## 1. 样本标识

- 第一新项目样本：`loom-adoption-new-project`
  - 归档记录：历史 `#168` 验证
- 第二新项目样本：`loom-adoption-new-project-2`
  - 源仓库位置：`/Users/mc/dev/loom-adoption-new-project-2`
  - 仓库类型：`新项目`
  - 初始状态：只有 `.git/`，没有 `HEAD`、远端、规则入口或宿主承接面
- 验证日期：`2026-04-23`
- 对应 Loom issue：`#275`

本记录只消费一个全新隔离空仓，不接远端，也不接触任何真实业务仓库。

## 2. 为什么它是独立第二样本

- 它不是 `#168` 使用过的 `loom-adoption-new-project`
- 它不是 [examples/new-project](../../../examples/new-project) 这类仓内夹具
- 它有独立 `.git/`、独立 bootstrap 输出和独立 baseline commit

因此，它满足“独立于 `#168` 的第二新项目样本”要求。

## 3. 路由与 bootstrap 结果

### 3.1 root route

执行：

```bash
python3 tools/loom_init.py route --target /Users/mc/dev/loom-adoption-new-project-2 --task "请初始化这个新项目并接入 Loom"
```

结果：

- `result = pass`
- `selected_skill = loom-adopt`
- `mode = implicit`
- `governance_surface.repository_mode = new`
- `fallback_to = loom-init`

这说明第二样本继续稳定消费同一条 root entry / route 语义。

### 3.2 bootstrap

执行：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/loom-adoption-new-project-2 --write --force --install-pr-template
```

结果：

- `run.scenario_key = new`
- `recommended_adoption.path = minimal-bootstrap`
- `integration_mode = root`
- `recovery_mode = checkpoint-lite`
- `validation_entry = python3 .loom/bin/loom_init.py verify --target .`
- `write.written_files = 21`

关键输出形状：

- 根入口：`AGENTS.md`
- Loom 入口：`.loom/README.md`
- bootstrap metadata：
  - `.loom/bootstrap/intake.snapshot.json`
  - `.loom/bootstrap/init-result.json`
  - `.loom/bootstrap/manifest.json`
  - `.loom/bootstrap/capability-map.md`
- runtime / verify 入口：
  - `.loom/bin/loom_init.py`
  - `.loom/bin/loom_flow.py`
  - `.loom/bin/loom_check.py`
- 初始治理 carriers：
  - `.loom/work-items/INIT-0001.md`
  - `.loom/progress/INIT-0001.md`
  - `.loom/reviews/INIT-0001.json`
  - `.loom/status/current.md`
- 规格与模板：
  - `.loom/specs/INIT-0001/spec.md`
  - `.loom/specs/INIT-0001/plan.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`

这与 `#168` 的新项目主路径记录保持同一类最小输出形状，而不是漂移成新模板族或新入口族。

## 4. baseline 之后的验证链

先建立独立 baseline：

```bash
git -C /Users/mc/dev/loom-adoption-new-project-2 branch -m main
git -C /Users/mc/dev/loom-adoption-new-project-2 add .
git -C /Users/mc/dev/loom-adoption-new-project-2 commit -m "bootstrap baseline for #275 validation"
```

得到：

- `HEAD = c4899c9`

随后执行：

```bash
cd /Users/mc/dev/loom-adoption-new-project-2
python3 .loom/bin/loom_init.py verify --target .
python3 .loom/bin/loom_init.py fact-chain --target .
python3 .loom/bin/loom_flow.py state-check --target . --item INIT-0001
python3 .loom/bin/loom_flow.py flow review --target . --item INIT-0001
python3 .loom/bin/loom_flow.py flow merge-ready --target . --item INIT-0001
python3 .loom/bin/loom_flow.py checkpoint merge --target . --item INIT-0001
python3 .loom/bin/loom_flow.py closeout check --target . --skip-gate
```

结果：

- `verify`
  - `ok = true`
- `fact-chain`
  - `mode = work-item + recovery-entry + derived status-surface`
  - `current_item_id = INIT-0001`
  - `validation_entry = python3 .loom/bin/loom_init.py verify --target .`
- `state-check`
  - `result = pass`
- `flow review`
  - `result = fallback`
  - `fallback_to = admission`
- `flow merge-ready`
  - `result = fallback`
  - `fallback_to = admission`
  - review 仍停在 bootstrap placeholder，不会伪装成已进入正式 merge judgment
- `checkpoint merge`
  - `result = fallback`
  - `fallback_to = admission`
- `closeout check`
  - `result = block`
  - `missing_inputs = ["owner/repo"]`
  - `fallback_to = merge`

## 5. 这个第二样本实际证明了什么

它稳定复验了新项目默认路径的四个核心边界：

1. root route 仍由 `loom-adopt` 承接
2. bootstrap 仍输出同一类最小治理结构，而不是漂移成新的 scaffold 族
3. baseline commit 形成后，`verify` / `fact-chain` / `state-check` 可以进入统一入口
4. `review` / `merge-ready` / `closeout` 仍 fail-closed：
   - 没有正式 review 时回退到 `admission`
   - 没有 GitHub control-plane 时阻断 `closeout`

这说明对“空仓新项目先建立根入口、最小治理、首批事项与升级入口，而不是预装重 harness”的结论，当前已经有两个独立真实样本支撑，而且输出形状没有继续漂移。

## 6. 对台账与落点的影响

- `EXT-0044`
  - 从 `adapt/candidate` 升为 `keep/core`
  - 理由：`#168` 与 `#275` 现在已经共同提供两个独立新项目样本，覆盖 root route、bootstrap 输出形状、验证入口和 fail-closed upgrade boundary
- 本次不改变：
  - `repository_mode` 枚举
  - `loom-init-output/v1` schema
  - 新项目默认恢复形态仍为 `checkpoint-lite`

## 7. 关闭依据

`#275` 在“新项目第二样本”这一半的 done condition 已满足：

- 已有独立于 `#168` 的第二新项目样本
- 证据已进入版本控制
- 结论已足够支撑 `EXT-0044` 升级，而不是继续停留在“只有一个真实样本”
