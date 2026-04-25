# Validation: Syvert Reverse-Consumption Smoke

## 1. Scope

本记录归档 Loom `#330` 的 Syvert 反向消费 smoke validation。

本轮目标不是替换 Syvert 治理栈，而是证明 Loom 能在只读基线和受控 smoke branch 中消费 Syvert 级治理面。

## 2. Baseline: Syvert main

样本仓库：`/Users/mc/dev/syvert`

只读命令：

```bash
python3 tools/loom_init.py bootstrap --target /Users/mc/dev/syvert --verify
python3 tools/loom_flow.py governance-profile status --target /Users/mc/dev/syvert
python3 tools/loom_flow.py runtime-parity validate --target /Users/mc/dev/syvert
python3 tools/loom_flow.py shadow-parity --target /Users/mc/dev/syvert
```

结果：

- `loom_init bootstrap --verify`
  - scenario: `复杂既有仓库`
  - recommended path: `full-bootstrap`
  - integration mode: `companion`
  - maturity: `unadopted`
  - next: `light`
- `governance-profile status`
  - result: `pass`
  - maturity: `unadopted`
  - next: `light`
- `runtime-parity validate`
  - result: `block`
  - fallback: `admission`
  - blocker: missing `.loom/bootstrap/init-result.json`
- `shadow-parity`
  - result: `warn`
  - blocker: repo interop contract absent

结论：Syvert `main` 保持未接入状态；Loom 能识别它是复杂既有仓库，但不能在未安装 companion / interop 时声称 runtime parity 已完成。

## 3. Controlled Smoke Worktree

受控 smoke worktree：`/Users/mc/dev/syvert-loom-phase-d-smoke`

Syvert smoke branch：`chore/loom-phase-d-smoke-companion`

Syvert smoke commit：`9a7b2923b6ab39631d8a3eafc1be8e5090709b9d`

该分支只用于 Phase D smoke，不合并到 Syvert `main`。

Smoke branch 中新增：

- `.loom/bootstrap/init-result.json`
- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`
- `.loom/companion/interop.json`
- `.loom/shadow/*`

Syvert 原生治理入口保持 repo-owned：

- `AGENTS.md`
- `WORKFLOW.md`
- `docs/process/delivery-funnel.md`
- `code_review.md`
- `spec_review.md`
- `scripts/pr_guardian.py`
- `docs/exec-plans/`

## 4. Smoke Results

Smoke 命令：

```bash
python3 /Users/mc/dev/Loom/tools/loom_flow.py governance-profile status --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 /Users/mc/dev/Loom/tools/loom_flow.py governance-profile upgrade-plan --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 /Users/mc/dev/Loom/tools/loom_flow.py runtime-parity validate --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 /Users/mc/dev/Loom/tools/loom_flow.py shadow-parity --target /Users/mc/dev/syvert-loom-phase-d-smoke
python3 /Users/mc/dev/Loom/tools/loom_flow.py shadow-parity --target /Users/mc/dev/syvert-loom-phase-d-smoke --blocking
python3 /Users/mc/dev/Loom/tools/loom_flow.py flow resume --target /Users/mc/dev/syvert-loom-phase-d-smoke --item INIT-0001
```

结果：

- `governance-profile status`
  - result: `pass`
  - maturity: `strong`
- `governance-profile upgrade-plan`
  - result: `pass`
  - summary: already at `strong`
- `runtime-parity validate`
  - result: `pass`
  - summary: Work Item、status、gates、controlled merge、closeout、shadow boundary 均可机读
- `shadow-parity`
  - result: `pass`
  - admission / review / merge_ready / closeout 均为 `match`
- `shadow-parity --blocking`
  - result: `pass`
  - 证明显式 blocking 消费能读取同一 surface，但不会改变默认 validation-only 边界
- `flow resume`
  - result: `pass`
  - maturity: `strong`

## 5. Boundary

本轮没有替换 Syvert 治理栈，也没有合并 Syvert smoke branch。

Loom 已证明可以消费 Syvert 的强治理形态，但 Syvert 是否正式迁入 `.loom/companion`，应由后续 Syvert migration issue 决定。
