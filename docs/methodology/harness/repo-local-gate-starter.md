# Local Gate Entry

Loom source repo 的默认本地聚合入口是：

```bash
make loom-check
```

它只运行 host-native lifecycle contracts：PR binding、FR/Phase closure guard、字段权威、host attestation、product acceptance、failure envelope、light profile、delivery gate 与 composite action contract。它不读取或生成 committed current、progress、review、shadow、closeout carrier，也不物化 repo-local runtime。

GitHub `main` push 使用同一个 aggregate；feature PR 只运行 `py-compile`、targeted `loom-delivery-gate`，以及 release workflow 中的短 host-native aggregate。full CLI contract 只在 `main`/release 收敛时运行，不在同一 feature head 重复。

## Retired aliases

以下入口已退出产品与 CI surface，不得作为当前验证建议：

- `make repo-local-cli-fast GROUP=<group>`
- `make repo-local-cli-full`
- `make repo-local-cli-*`
- `.loom/bin/loom_init.py` / `.loom/bin/loom_flow.py` lifecycle replay

历史 evidence 中的同名命令只描述当时的验证，不构成当前入口。旧 `daily-execution-cli-*`、`loom-check-runtime-regression` 与 `tools/loom_check.py` surface 仅保留到 compatibility removal boundary，必须显式调用，且不得作为默认 merge-ready 或产品完成证明。

## Authority boundary

本地通过只能证明候选 contract 在当前 checkout 中成立。它不能证明：

- GitHub workflow 已运行；
- required checks 已配置并强制；
- branch protection/ruleset 已启用；
- PR head、review、merge 与 release host facts 一致。

这些事实必须由 GitHub live readback 与 hosted checks 证明。Loom 不从本地 aggregate、CI green 或 PR merged 推导 product acceptance。
