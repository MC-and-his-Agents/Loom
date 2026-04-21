# Loom v0.5.0 Release

本文是 Loom `v0.5.0` 的正式发布与升级说明。

发布日期：`2026-04-21`

变更分类：`minor`

受影响交付面：

- `repo-local plugin`
- repo-local `loom CLI`
- `scenario skills`
- `single-skill standard-skill packages`
- `harness`
- `templates`
- `adoption`

下游是否需要动作：否。
已接入 `v0.4.0` 的下游可以继续沿用既有 authored review 路径；若要消费本次默认 Codex-backed review 主路径，应刷新 repo-local `loom` plugin、repo-local `loom CLI` 或对应 single-skill package 安装物。

对应 Loom issue：`#248`、`#249`、`#250`、`#251`、`#252`、`#253`

## 1. 本次发布收敛的默认 review 主路径

`v0.5.0` 在不改写既有四层 repo-local 交付形态的前提下，把 Loom 的正式 review 默认路径收敛为：

1. `flow review`
   - 继续只读，负责 formal review 的机械基线、进入条件与 blocking companion requirements
2. `review run`
   - 新增默认 engine 执行层
   - 固定调用 Codex-backed reviewer
   - 把 raw output 落为 `.loom/runtime/review/<item>/<head>/...` evidence
   - 产出 Loom-owned normalized findings，并在 engine 不可用、schema 漂移、runtime 冲突或 repo tracked diff 时 fail-closed
3. `review record`
   - 继续作为唯一正式 authored truth
   - 把 decision / findings / reviewed_head 写回单一 review record
   - 只记录 `engine_adapter`、`engine_evidence`、`normalized_findings` 这类 consumed inputs，而不创建第二 authored artifact

用户首层路径仍保持不变：

- `loom-pre-review -> loom-review -> loom-merge-ready`

内部正式 review 执行链现在固定为：

- `flow review -> review run -> review record`

## 2. 为什么这是 `minor`

本次按 `minor` 管理，原因是：

- 这次新增的是既有执行面内的稳定能力扩展，而不是安装面或角色边界重写
- 用户仍从相同的 scenario skill 进入，不需要重新理解四层 repo-local 交付形态
- `merge-ready` / `checkpoint merge` 继续只消费单一 authored `review record`
- 既有 manual review 路径保持可用；engine 失败时只是 fail-closed 回到同一 review record 写回路径

本次没有进入 `major` 的原因是：

- 没有引入新的 root entry、scenario skill、默认安装对象或新的事实真相源
- 没有把 Loom 扩写成 multi-engine marketplace
- 没有改写 checkpoint、closeout、route priority 或 review record 的唯一真相边界

## 3. 下游升级路径

### 3.1 完整 Loom 消费方

1. 重新读取根 `README.md`、`adoption/versioning-and-upgrades.md` 与本文
2. 刷新 repo-local `loom` plugin 的安装物，确保 plugin 镜像里的 `loom-review` contract、shared runtime 与 review schema 已同步到当前版本
3. 若希望使用默认 engine-backed review，确认宿主环境可调用 `codex`
4. 若 `review run` fail-closed，继续按 manual review 路径把正式结论写回同一 `review record`

### 3.2 repo-local `loom CLI` / 自动化消费方

1. 在 formal review 自动化里显式采用 `loom review run`
2. 不直接消费 engine raw output、prompt 或日志，把它们视为 evidence 而不是 merge gate truth
3. 继续让 `loom review record` 成为唯一正式写回入口

### 3.3 单 skill package 消费方

1. 刷新 `loom-review` package 与共享 runtime 资源
2. 确认安装布局包含 `shared/assets/review/loom-review-result-schema.json`
3. 不把默认 Codex-backed path 理解成新的 package 边界；它仍属于 `loom-review` 既有场景合同内的扩展

### 3.4 兼容原则

- `flow review` 保持只读，不承担 engine 执行或 authored writeback
- engine 输出只作为 evidence 存在，不形成第二 authored truth
- `merge-ready` / `checkpoint merge` 不直接读取 engine raw output
- 仅补 Loom runtime/status carriers 的提交不应把 review 判成 stale；非 carrier 漂移仍必须 stale/block

详见：[adoption/execution-entry-compatibility.md](../adoption/execution-entry-compatibility.md)

## 4. 版本化公开面的对齐结果

本次 release 已把以下文档统一到同一条仓库真相：

- 根 `README.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- `adoption/execution-entry-compatibility.md`
- `harness/review-execution.md`
- `harness/merge-checkpoint.md`
- `skills/loom-review/SKILL.md`
- `skills/loom-review/contract.json`
- `templates/review-record.md`
- `VERSION`
- plugin 镜像下的 `plugins/loom/skills/**`

这些文档共同回答：

- 默认 formal review 主路径是什么
- engine evidence、authored truth 与 merge 消费的边界是什么
- 为什么本轮是 `v0.5.0` 的 `minor`
- plugin / installed runtime 需要刷新哪些镜像文件

## 5. 延续有效的验证与收口依据

本次 release 除了沿用既有完整内核验证外，还新增并固定了以下 review 主路径验证：

- repo-local `python3 tools/loom_check.py`
- repo-local `python3 -m py_compile skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py`
- repo-local `git diff --check`
- GitHub PR `#254` 的 `py-compile`、`demo-bootstrap`、`repo-local-cli` 与 `loom-check`
- 版本控制内的 review 验证记录：
  - `adoption/validation-review-and-authoring.md`
  - `adoption/validation-installed-skills-pre-merge-chain.md`

负样本也已进入验证记录：

- engine unavailable
- schema drift
- repo tracked diff detected
- review stale / head drift
- validation summary drift

## 6. 本次不进入发布面的内容

以下内容本次明确不进入 `v0.5.0` 的稳定发布面：

- multi-engine marketplace 或 engine selector
- 第二 authored review artifact
- 把 `codex exec` 之类宿主命令名提升为 Loom core 对外合同
- 让 `merge-ready` 或 `checkpoint merge` 充当第一次正式语义审查
- guardian / merge gate 语义提前混入 reviewer rubric
