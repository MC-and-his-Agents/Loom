# Validation: Installed-Skills Pre-Merge Chain

本文记录 `#209` 的 installed-skills pre-merge 验收。

## 样本

- `installed-skills 安装根`
  - 临时目录中只复制 `skills/`
- `target repo 验证现场`
  - 当前 Loom 仓库快照的临时副本
  - 不复用源工作树
- `repo-local 源码现场`
  - 只用于开发回归与 `make loom-check`
  - 不计入 `#209` 验收结论

## 正向链

在 installed-skills 安装根中执行：

```bash
python3 loom-init/scripts/loom-init.py bootstrap --target <target-repo> --write --force --verify --install-pr-template
git -C <target-repo> add .
git -C <target-repo> commit -m "bootstrap baseline for #209"

python3 loom-init/scripts/loom-init.py route --target <target-repo> --task "请接手当前事项并恢复上下文后继续推进"
python3 loom-resume/scripts/loom-resume.py flow resume --target <target-repo> --item INIT-0001

python3 loom-init/scripts/loom-init.py route --target <target-repo> --task "请在进入 review 前做统一检查"
python3 loom-pre-review/scripts/loom-pre-review.py flow pre-review --target <target-repo> --item INIT-0001

python3 loom-init/scripts/loom-init.py route --target <target-repo> --task "请对当前事项做正式 review 并给出审查结论"
python3 loom-review/scripts/loom-review.py flow review --target <target-repo> --item INIT-0001
python3 shared/scripts/loom_flow.py review run --target <target-repo> --item INIT-0001
python3 loom-review/scripts/loom-review.py review record --target <target-repo> --item INIT-0001 --decision allow --kind code_review --summary "Installed pre-merge chain is ready for merge checkpoint consumption." --reviewer loom/default-codex --findings-file .loom/runtime/review/INIT-0001/<head>/normalized-findings.json --engine-adapter loom/default-codex --engine-evidence .loom/runtime/review/INIT-0001/<head>/engine-result.json --normalized-findings .loom/runtime/review/INIT-0001/<head>/normalized-findings.json
python3 shared/scripts/loom_flow.py recovery writeback --target <target-repo> --item INIT-0001 --current-checkpoint "merge checkpoint" --current-stop "Installed review completed and merge-ready validation is next." --next-step "Run merge-ready and checkpoint merge from installed skills." --latest-validation-summary "<resume latest_validation_summary>"
git -C <target-repo> add .loom/reviews/INIT-0001.json .loom/progress/INIT-0001.md .loom/status/current.md
git -C <target-repo> commit -m "author installed pre-merge carriers for #209"

python3 loom-init/scripts/loom-init.py route --target <target-repo> --task "请做 merge-ready 最终放行前预检并确认是否可以合并"
python3 loom-merge-ready/scripts/loom-merge-ready.py flow merge-ready --target <target-repo> --item INIT-0001
python3 shared/scripts/loom_flow.py checkpoint merge --target <target-repo> --item INIT-0001
```

结果：

- `route(resume|pre-review|review|merge-ready)` 全部命中对应 installed skill
- `flow resume` / `flow pre-review` / `flow review` / `flow merge-ready` 全部 `pass`
- `review run` 以默认 Codex reviewer 产出 normalized findings，并 fail-closed 地保留 manual review 回退口径
- `review record` 以 `allow` 写入单一 `review_entry`
- `checkpoint merge = pass`
- 允许 review 之后只新增 Loom 自身的 `review_entry`、recovery、status carriers 提交；否则仍视为 stale

## Fail-Closed 负样本

### 1. 安装态 layout 漂移

- 删除 installed `install-layout.json`
- 期望：
  - `loom-init route` 直接 `block`
  - `loom-pre-review flow pre-review` 直接 `block`

### 2. review 基线缺失

- 将 recovery `Current Checkpoint` 降回 `admission checkpoint`
- 期望：
  - `flow review` 返回 `fallback`
  - `review run` 不启动默认 reviewer，而是沿用 `flow review` 的 `fallback`
  - `flow merge-ready` 返回 `fallback` 或 `block`

### 3. merge-ready 条件漂移

- 在 allow review 和 merge carriers 提交之后，再提交非 Loom carrier 改动
- 期望：
  - `checkpoint merge` 明确 `block`
  - 原因保留为 review stale / reviewed head drift，而不是伪装成 `pass`

### 4. default engine fail-closed

- 缺少 `codex` CLI、schema 漂移或 engine 修改 tracked repo 内容
- 期望：
  - `review run` 明确 `block`
  - `fallback_to = null`
  - formal review 仍只能回写到同一 `review record`

## 结论

- `#209` 的 installed-skills pre-merge 链已经可在隔离安装根和隔离 target repo 上完整复验
- 正向链必须包含显式 authored 推进：`review record` 与 `recovery writeback`
- 本记录只覆盖 pre-merge readiness，不宣称 `#210` 的 host merge 后 closeout 已完成
