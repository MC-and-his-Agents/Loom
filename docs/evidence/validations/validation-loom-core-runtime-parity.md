# Validation: Loom Core Runtime Parity

## 1. 样本标识

- 验证目标：`#318`
- 验证日期：`2026-04-25`
- 样本仓库：`examples/new-project`

## 2. 验证目标

本记录把 Syvert strong governance parity 从文档层推进到最小 runtime parity。

它不证明 GitHub profile 已完成完整宿主编排，也不把 Syvert repo-local 文件名提升为 Loom core。它只证明 Loom core 能用机器可读 runtime surface 表达以下能力：

- `Work Item` 作为唯一执行入口
- `status control plane`
- `gate chain`
- `controlled merge` 合同
- `closeout / reconciliation` 前置关系
- `shadow parity` 默认 validation-only 边界

## 3. Runtime Entry

新增 runtime parity 验证入口：

```bash
python3 tools/loom_flow.py runtime-parity validate --target examples/new-project --item INIT-0001
```

该入口输出 `loom-runtime-parity/v1` JSON，并由 `loom_check` 消费。

## 4. Runtime Parity 边界

本验证明确区分两层：

- 文档层 parity
  - 由 `docs/methodology/**`、`docs/adoption/**` 与既有 Syvert parity validation 证明语义落点完整。
- runtime parity
  - 由 `runtime-parity validate` 证明核心治理路径可被工具读取、归类并 fail-closed。

本阶段仍不覆盖：

- ProjectV2 / native sub-issues 的完整自动编排
- GitHub profile 的重宿主动作
- Syvert 反向消费 Loom 的 release judgment

这些进入后续 `#321` 与 `#329`。

## 5. Release Judgment

`#318` 完成后，Loom core 不再只声称具备 strong governance parity，而是拥有可运行、可检查、可安装回归的 runtime parity 入口。

`#317` 仍不能关闭，直到 `#319` 与 `#320` 继续补齐 closeout/reconciliation 阻断和可选 shadow parity blocking gate。
