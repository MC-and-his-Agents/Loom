# Tiered Gate Consumption Contract

本文件定义 `light`、`standard` 与 `reinforced` 如何调整验证强度。强度只改变
检查深度，不改变字段 owner，也不得恢复已退役 repo execution carrier。

## 1. 最小 PR policy

PR machine block 只承载 GitHub 无法自行推导的 policy claim：

- typed `work_item_locator`；
- `governance_intensity`、`governance_mode`、`governance_assurance`；
- `change_class`、`suite_path`、`review_requirement`；
- `pr_gate_required`、`release_judgment`、`closeout_required`；
- `upgrade_triggers` 与明确 excluded scope。

branch、head、checks、merge state 与 merge commit 始终由 GitHub live readback
拥有。兼容字段 `fact_chain_required` 表示是否要求 host-native delivery binding，
不授权读取 committed current/status/progress/review/shadow 文件。

## 2. 分级语义

| Intensity | Typical change | Required validation |
| --- | --- | --- |
| `light` | 局部文档、低风险配置 | diff/static/targeted checks + current-head attestation + required host checks |
| `standard` | 公共合同、跨模块行为 | targeted matrix + 一次稳定-head aggregate + host attestation/readback |
| `reinforced` | security、permission、runtime、release、external action | specialized review、hosted negatives、runtime/release evidence 与受控 merge |

升级治理强度不得隐式改变仓库 profile。高风险 PR 可提高本 PR 的检查强度，但
light 仓库仍禁止 committed current、status、progress、review、shadow、suite 与
普通 closeout carrier。

## 3. 绑定优先级

字段 owner 固定为：

1. GitHub Issue：goal、scope、dependency、closing condition；
2. GitHub PR/Checks：branch、head、checks、mergeability、merge facts；
3. Git worktree：当前正式执行路径与 checkout；
4. host attestation：semantic review 与 delivery closeout；
5. acceptance adapter：独立 product acceptance verdict；
6. PR policy block：仅补充强度、change class、review/release policy。

两个权威来源冲突时 fail closed。人类摘要缺失不能覆盖 host facts；机器不得把
authoritative conflict 自动修成某一方。

## 4. Gate consumption

所有强度都必须保留：

- Work Item admission；
- formal worktree / branch / PR / live head binding；
- current-head semantic review；
- repository-native targeted checks 与适用 required checks；
- `loom pr gate`、retained result 与 `loom merge-ready` readback；
- release/no-release judgment；
- host-derived delivery closeout；
- 适用时独立 product acceptance。

`suite_path: not_applicable` 只说明正式规格工件对当前 scope 不适用。其 rationale、
consumer boundary、recheck condition、scope proof 与 review requirement 保存在 PR
policy 中；不得为此生成 repo-local spec、progress、review 或 closeout carrier。

## 5. Failure semantics

分类器至少输出 effective intensity、upgrade reasons、consumed host locators 与一个
primary cause。常见 domain 包括 governance metadata、git history、environment、
permission、host service 与 product acceptance；不同 domain 不得折叠成不可执行的
通用错误。

`light` 声明与 runtime/release/permission/external-action diff 冲突、PR policy 不可
解析、host head/readback 不一致或 required check 失败时必须 block。补救只能指向
30 个公共命令、GitHub/Git 手工动作或 external provider action。

强度映射见
[loom-governance-intensity-mapping.md](../governance/loom-governance-intensity-mapping.md)。
