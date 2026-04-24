# GitHub Governance Profile Funnel Validation

本文件归档 `#287` 及其子事项 `#288` 到 `#295` 的验证结果、release judgment 与 closeout basis。

## 1. 验证目标

验证 Loom 是否已经把以下交付漏斗收成可执行、可检查、可安装的主干真相：

- `Roadmap / 阶段目标`
- `GitHub Phase`
- `GitHub FR`
- `GitHub Work Item`
- `spec / contract`
- `spec review`
- `implementation PR`
- `PR review`
- `squash merge`

## 2. 本轮收口范围

- `#288`
  - 冻结 `GitHub delivery funnel` 与 `item context` 合同
- `#289`
  - 建立统一 `status surface` 读取面与 repo-local `loom_status`
- `#290`
  - 冻结 `spec / implementation` 分离规则与最小模板
- `#291`
  - 新增独立 `loom-spec-review`
- `#292`
  - 让 review 与 merge-ready 消费 `spec_review` 与 `head_sha`
- `#293`
  - 把 GitHub governance profile 与 adoption 升级路径落盘
- `#294`
  - 让 GitHub host 最小读取与受控 merge 链路进入可消费状态
- `#295`
  - 固定验证记录、release judgment 与 residue

## 3. 正向链验证

已验证以下正向链可以被 Loom 的技能、脚本和 installer 同时消费：

1. `loom-init route` 能把 formal spec 审查信号稳定路由到 `loom-spec-review`
2. `loom-spec-review flow spec-review` 能在 installed runtime 中通过
3. `loom_flow.py review run --review-file .loom/reviews/<item>.spec.json` 能产出标准化 `review_record_input`
4. `loom-review flow review` 能消费 `spec_review` gate
5. `loom_flow.py review run` 能产出 implementation review 草稿
6. `loom-merge-ready flow merge-ready` 与 `checkpoint merge` 能消费前序 `spec_review` / implementation review / `head_sha`
7. `tools/loom_status.py` 能把 item、checkpoint、recovery、spec review、review、merge-ready、governance surface 与 GitHub 信号收成单一读取面

## 4. 负样本验证

已验证以下阻断会 fail-closed：

- 缺 formal spec review 记录
- `spec_review` 未批准
- implementation review 未批准
- review 记录与当前 `head_sha` 不一致
- runtime layout 与 `install-layout.json` 漂移
- installer payload 并发构建导致的目录竞态

## 5. 本轮命令验证

以下命令在本轮收口中通过：

```bash
python3 tools/loom_check.py
python3 -m py_compile \
  tools/loom.py \
  tools/loom_init.py \
  tools/loom_flow.py \
  tools/loom_status.py \
  skills/shared/scripts/loom_init.py \
  skills/shared/scripts/loom_flow.py \
  skills/shared/scripts/loom_status.py \
  skills/shared/scripts/loom_check.py \
  skills/shared/scripts/runtime_state.py \
  skills/shared/scripts/governance_surface.py \
  skills/loom-spec-review/scripts/loom-spec-review.py
npm --prefix packages/loom-installer test
npm --prefix packages/loom-installer run check:payload
cd packages/loom-installer && npm pack --dry-run
git ls-files plugins/loom packages/skills packages/loom-installer/payload
python3 tools/loom_status.py --target examples/new-project --item INIT-0001
python3 tools/loom_init.py route --target examples/new-project --task '请做 formal spec review，判断 spec 是否可以进入实现'
```

## 6. Release Judgment

本轮 judgment：

- `GitHub governance profile funnel` 已进入主干可消费状态
- 可以关闭 `#287` 与 `#288` 到 `#295`
- 当前能力属于 Loom core + GitHub default profile 的最小稳定版本，不再只是讨论稿

支撑理由：

- 合同、模板、skills、repo-local wrapper、installer payload、self-check 已全部对齐
- 正向链和负样本都已有版本控制内的验证依据
- `spec review` 不再只是文档概念，而是独立 skill 与 gate

## 7. Residue

本轮仍未收的 residue：

- 更强的 GitHub object automation 仍停留在“最小读取与受控 merge”层，不包含更重的 project/issue orchestration
- 非 GitHub 宿主的 profile 仍需后续验证，当前只冻结语义，不提供等强度实现
- `shadow parity` 仍保持 validation-only，不在本轮升级为 blocking merge gate

## 8. Closeout Basis

可以直接用于 parent closeout 的 basis：

- `GitHub delivery funnel`、`item context`、`status surface contract`、`spec separation` 已冻结
- `loom-spec-review` 已成为正式 skill
- review / merge-ready 已消费 `spec_review` 与 `head_sha`
- GitHub host 的最小读取与 closeout 链路已可被 Loom 工具消费
- installer 已从 canonical `skills/` 与 `.codex-plugin/` 动态构建，并对 layout drift fail-closed
