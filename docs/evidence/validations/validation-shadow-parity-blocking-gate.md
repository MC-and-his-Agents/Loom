# Validation: Optional Shadow Parity Blocking Gate

## 1. 样本标识

- 验证目标：`#320`
- 验证日期：`2026-04-25`
- 验证范围：Loom core candidate shadow parity consumption

## 2. 验证目标

本记录证明 `shadow parity` 可以被 strong governance profile 显式消费成 blocking gate，同时保持默认 validation-only 行为。

## 3. Runtime Contract

默认入口保持 validation-only：

```bash
python3 tools/loom_flow.py shadow-parity --target <repo>
```

默认结果只允许：

- `pass`
- `warn`

blocking 模式必须显式开启：

```bash
python3 tools/loom_flow.py shadow-parity --target <repo> --blocking
```

或：

```bash
python3 tools/loom_flow.py shadow-parity --target <repo> --mode blocking
```

blocking 模式结果只允许：

- `pass`
- `block`

## 4. Taxonomy

`reports[*].result` 继续保持兼容词表：

- `match`
- `mismatch`
- `unreadable`

新增并行字段：

- `classification`
  - `drift` 用于 `mismatch`
  - `gate_failure` 用于 `unreadable`
- `blocking`
- `recommended_action`

## 5. 边界

`interop.json` 仍然只描述读取入口，不声明 blocking owner、override decision 或 final verdict。

blocking enablement、fallback、owner、authority-of-truth 必须落在 strong governance profile 或其他权威合同中。

## 6. Release Judgment

`#320` 完成后，Loom core 支持 optional shadow parity blocking gate，但默认仓库不会因为存在 shadow parity mismatch 自动阻断 merge 或 closeout。
