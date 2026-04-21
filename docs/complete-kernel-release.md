# Loom v0.6.0 Release

本文是 Loom `v0.6.0` 的正式发布与升级说明。

发布日期：`2026-04-21`

变更分类：`minor`

受影响交付面：

- repo-local `loom CLI`
- `scenario skills`
- `harness`
- `adoption`

下游是否需要动作：否。
已接入 `v0.5.0` 的下游可以继续沿用既有路径；只有需要消费成熟治理重仓 attach-only adoption、`repo-interface v2`、`interop.json` 或 `shadow parity` 的仓库，才需要显式刷新对应 Loom 资产与 companion 合同。

对应 Loom issue：`#243`、`#244`、`#245`、`#246`、`#247`

## 1. 本次发布收敛的成熟治理重仓接入面

`v0.6.0` 在不改写既有四层 repo-local 交付形态的前提下，正式收敛以下能力：

1. `deep-existing-repo`
   - 仍属于 `complex-existing`
   - 作为 attach-only adoption path，保留 root rules、retained host actions 与 repo-native carriers
2. `repo-interface v2`
   - 保持 `v1` 继续可读
   - 新增 typed `specialized_gates`
   - 新增可选 `metadata_contract`
   - 新增可选 `context_schema`
3. `interop.json`
   - 独立承接 retained host action result、repo-native carriers 与 `shadow parity` 的 read-only 入口
4. `shadow parity`
   - 固定四个 compare surface：`admission`、`review`、`merge_ready`、`closeout`
   - 只做 validation / parity，不成为新的默认 merge gate

用户首层路径仍保持不变：

- `loom-pre-review -> loom-review -> loom-merge-ready`

## 2. 为什么这是 `minor`

本次按 `minor` 管理，原因是：

- 新增的是既有执行面内的稳定能力扩展，而不是安装面或角色边界重写
- `repository_mode` 枚举保持不变
- root entry、scenario skill 角色、checkpoint 语义与 closeout 语义保持不变
- `repo-interface v2` 保持 `v1` 可读
- `interop.json` 与 `shadow parity` 仍是 read-only / validation-only surface

本次没有进入 `major` 的原因是：

- 没有新增第四种 scenario / repository mode
- 没有改写 root contract、必备工件或既有 CLI 顶层结果语义
- 没有让 `shadow parity` 直接充当 blocking merge gate

## 3. 下游升级路径

### 3.1 既有 `v0.5.0` 消费方

1. 重新读取根 `README.md`、`adoption/versioning-and-upgrades.md` 与本文
2. 若当前仓库继续使用 `full-bootstrap` 或 `repo-interface v1`，可以保持不动
3. 若当前仓库是成熟治理重仓，且希望第一轮只做 attach-only adoption，则改为显式消费 `deep-existing-repo`
4. 若当前 companion 需要 typed gates、repo-specific context 或 metadata declaration，则升级到 `repo-interface v2`
5. 若当前仓库需要 Loom 读取 retained host action result、repo-native carriers 或 `shadow parity`，再新增 `interop.json`

### 3.2 repo-local `loom CLI` / 自动化消费方

1. 接受 `loom-init` 现在可能返回 `recommended_adoption.path = deep-existing-repo`
2. 接受 `governance_surface.repo_interface` 读取 `v1` / `v2`
3. 接受 `governance_surface.repo_interop`
4. 若需要 parity compare，可显式调用 `python3 tools/loom_flow.py shadow-parity --target <repo>`

### 3.3 companion 维护者

1. 继续保持 `.loom/companion/manifest.json` locator-only
2. 不把 runtime state、review summary、validation status 写回 `repo-interface.json`
3. 只在需要 Loom 读取 retained host actions / repo-native carriers / parity surfaces 时新增 `interop.json`
4. 不因为引入 `interop.json` 就把 branch / PR / worktree / merge 的宿主实现迁进 Loom

### 3.4 兼容原则

- `deep-existing-repo` 不是第四种 `repository_mode`
- `repo-interface v2` 不破坏 `v1` 仓库
- `interop.json` 不改写 `repo-interface.json` 的职责
- `shadow parity` 的结果只用于 compare，不决定“哪一方自动获胜”

详见：[adoption/repo-companion-migration.md](../adoption/repo-companion-migration.md)

## 4. 版本化公开面的对齐结果

本次 release 已把以下文档统一到同一条仓库真相：

- `adoption/deep-existing-repo-default.md`
- `adoption/deep-existing-repo-workflow.md`
- `adoption/repo-companion-contract.md`
- `adoption/repo-companion-migration.md`
- `adoption/repo-interop-contract.md`
- `adoption/validation-deep-existing-repo-syvert-webenvoy.md`
- `adoption/upstream-delivery-surface.md`
- `adoption/versioning-and-upgrades.md`
- `VERSION`
- plugin 镜像下的 `plugins/loom/skills/**`

这些文档共同回答：

- 成熟治理重仓应该如何 attach
- companion / interop 的边界是什么
- 为什么本轮是 `v0.6.0 / minor`
- 哪些能力已进入稳定交付面，哪些仍停在 `adapt` / `needs_validation`

## 5. 验证与收口依据

本次 release 固定采用以下验证入口：

- repo-local `python3 tools/loom_check.py`
- repo-local `python3 -m py_compile skills/shared/scripts/governance_surface.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/governance_surface.py plugins/loom/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_check.py tools/loom_flow.py tools/loom_check.py`
- repo-local `git diff --check`
- 对 `Syvert` / `WebEnvoy` 的 live scan：
  - `python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert`
  - `python3 tools/loom_init.py bootstrap --target /Users/mc/dev/WebEnvoy`
- 对 `Syvert` / `WebEnvoy` 的 mature-governance positive path 复验：
  - `python3 tools/loom_init.py bootstrap --target <repo> --intake <override>`

对应版本化记录：

- `adoption/validation-repo-companion-interface.md`
- `adoption/validation-deep-existing-repo-syvert-webenvoy.md`

## 6. 本次不进入发布面的内容

以下内容本次明确不进入 `v0.6.0` 的稳定发布面：

- 第四种 `repository_mode`
- branch / PR / worktree / merge / ruleset 的底层宿主实现接管
- repo-specific metadata field 的跨仓默认 taxonomy
- 把 `shadow parity` mismatch 自动提升为 blocking merge gate
- 把 carrier 迁移与入口迁移绑定成一次性动作
