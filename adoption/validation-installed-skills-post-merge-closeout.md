# Validation: Installed-Skills Post-Merge Closeout

本文记录 `#210` 的 installed-skills post-merge `closeout -> cleanup/retire` 验收。

## 样本

- `installed-skills 安装根`
  - 临时目录中只复制 `skills/`
  - 不复制 repo root `tools/`、`harness/`、`governance/`、`templates/`、`adoption/`
- `post-merge closeout 验证现场`
  - Loom 仓库主干上的真实 host merge 结果
  - 历史对照样本：`#131` / `#138` / `project 5`
  - 当前链路样本：`#210` 合入主干后的 issue / PR / project 状态
- `retire 验证现场`
  - 由 installed-skills 驱动的隔离临时 target repo
  - 不复用源工作树，不在主干 dogfood 现场直接退休当前工作树
- `repo-local 源码现场`
  - 只用于开发回归与 `make loom-check`
  - 不计入 `#210` 验收结论

## 正向链

### 1. installed closeout 历史主干样本

在 installed-skills 安装根中执行：

```bash
python3 shared/scripts/loom_flow.py reconciliation audit --target <loom-main> --issue 131 --pr 138 --project 5
python3 shared/scripts/loom_flow.py reconciliation sync --target <loom-main> --issue 131 --pr 138 --project 5 --dry-run
python3 shared/scripts/loom_flow.py closeout check --target <loom-main> --issue 131 --pr 138 --project 5 --skip-gate
python3 shared/scripts/loom_flow.py closeout sync --target <loom-main> --issue 131 --pr 138 --project 5 --skip-gate
```

结果：

- installed `reconciliation audit = pass`
- installed `reconciliation sync --dry-run = pass`
- installed `closeout check = pass`
- installed `closeout sync = pass`
- 输出都显式携带 `runtime_state`
- 结论发生在 `installed-skills 验证现场`，不是 repo-local `tools/` 成功伪装

### 2. installed retire 隔离样本

在 installed-skills 安装根中，对隔离 target repo 执行：

```bash
python3 loom-retire/scripts/loom-retire.py purity-check --target <retire-target> --item INIT-0001
python3 loom-retire/scripts/loom-retire.py workspace cleanup --target <retire-target> --item INIT-0001
python3 loom-retire/scripts/loom-retire.py workspace retire --target <retire-target> --item INIT-0001
```

结果：

- `purity-check = pass`
- 当 target repo 只有 Loom-owned `.loom/.tmp` 残留时，`workspace cleanup = pass`
- `workspace retire = pass`
- recovery 主入口最终回写为 `current_checkpoint: retired`
- 这里的结论发生在 `installed-skills 验证现场` 的隔离 target repo，不是 Loom 主干 dogfood 现场

## Fail-Closed 负样本

### 1. 安装态 runtime/layout 漂移

- 删除 installed `install-layout.json`
- 期望：
  - `closeout check` 直接 `block`
  - `purity-check` 直接 `block`
  - 两者都把阻断来源暴露在 `runtime_state`

### 2. 宿主事实缺失

- 不提供 `issue` / `pr` / `project` 目标执行 `reconciliation audit`
- 期望：
  - 返回 `block`
  - 不伪装成 `pass` 或 `fallback`

### 3. 非 Loom residue

- 在隔离 target repo 中引入非 Loom 脏改动
- 期望：
  - `purity-check = block`
  - `workspace cleanup = block`
  - `workspace retire = block`
  - 不自动丢弃用户改动

## 主干 dogfood closeout

`#210` 自身的正式 closeout 发生在主干 host merge 之后，由 installed-skills 消费真实 merge 结果完成：

- installed `reconciliation audit` 先证明 `absorbed_but_open` / project drift 是否存在
- installed `reconciliation sync` 在可同步条件下关闭 `#210` 并同步 project 状态
- installed `closeout check` / `closeout sync` 最终确认主干、issue、PR、project 与仓内结果对齐

这一步的最终结果写回 GitHub issue / PR / parent issue comment，不在本记录里伪装成 merge 前已经发生。

## 结论

- `#210` 要求的 installed post-merge closeout 与 retire 链已经具备可重复、可隔离、可 fail-closed 的执行基础
- closeout / reconciliation / purity / workspace cleanup / workspace retire 现在都会先消费 `runtime_state`
- 历史主干样本与隔离 retire 样本进入版本控制；`#210` 自身的 merge 后 closeout 则由 GitHub 状态与 parent issue comment 消费
