# Demo: New Project Bootstrap

本文件提供一条可复验的 Loom 下游接入演示链路。

## 目标

验证 `tools/loom_init.py` 能把一个空的新项目目录初始化为最小可执行 Loom 工作现场，而不只是输出说明文字。

## 演示目录

- `examples/new-project/`

它应保持接近空仓状态，只作为下游目标目录承接初始化结果。

## 运行方式

在 Loom 仓库根目录执行：

```bash
make loom-demo-new-project
```

等价命令：

```bash
python3 tools/loom_init.py bootstrap \
  --target examples/new-project \
  --write \
  --force \
  --verify \
  --install-pr-template
```

## 预期结果

执行完成后，至少应能读取以下工件：

- `examples/new-project/.loom/bootstrap/init-result.json`
- `examples/new-project/.loom/bootstrap/manifest.json`
- `examples/new-project/.loom/work-items/INIT-0001.md`
- `examples/new-project/.loom/progress/INIT-0001.md`
- `examples/new-project/.loom/status/current.md`
- `examples/new-project/.loom/bin/loom_flow.py`
- `examples/new-project/.loom/specs/INIT-0001/spec.md`
- `examples/new-project/.loom/specs/INIT-0001/plan.md`
- `examples/new-project/.github/PULL_REQUEST_TEMPLATE.md`

随后可继续执行：

```bash
cd examples/new-project
python3 .loom/bin/loom_init.py verify --target .
python3 .loom/bin/loom_init.py fact-chain --target .
python3 .loom/bin/loom_flow.py fact-chain --target . --item INIT-0001
python3 .loom/bin/loom_flow.py runtime-evidence --target . --item INIT-0001
python3 .loom/bin/loom_flow.py checkpoint admission --target . --item INIT-0001
python3 .loom/bin/loom_flow.py workspace locate --target . --item INIT-0001
python3 .loom/bin/loom_flow.py purity-check --target . --item INIT-0001
```

## 收口判断

只有当以下条件同时满足时，这条 demo 才算成立：

- `bootstrap` 命令退出码为 `0`
- `verify` 命令退出码为 `0`
- `fact-chain` 命令退出码为 `0`
- `loom_flow.py` 的 `fact-chain`、`runtime-evidence`、`checkpoint admission`、`workspace locate`、`purity-check` 命令都可读取当前样例
- `init-result.json` 含有 7 个必需区块
- 首批 work item、recovery entry、状态面与 spec/plan 工件都已落位
