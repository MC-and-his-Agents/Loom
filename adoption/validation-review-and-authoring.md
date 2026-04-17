# Validation: Review Execution And Authored Writeback

本文记录 `#131` / `#132` 的最小复验。

## 样本

- 仓内下游样本：`examples/new-project`
- 样本副本：临时目录中的 `examples/new-project` 副本

## 复验命令

在 Loom 仓库中执行：

```bash
python3 tools/loom_flow.py flow review --target examples/new-project --item INIT-0001
python3 tools/loom_flow.py review read --target examples/new-project --item INIT-0001
python3 tools/loom_check.py
```

在样本副本中执行：

```bash
python3 tools/loom_flow.py recovery writeback --target <temp-copy> --item INIT-0001 --current-stop "Bootstrap review has started." --next-step "Record the first formal review conclusion." --latest-validation-summary "Bootstrap artifacts verified and ready for semantic review."
python3 tools/loom_flow.py work-item create --target <temp-copy> --item NEXT-0001 --goal "Validate work item authoring" --scope "Limit changes to `.loom/` artifacts for this temp check" --execution-path execution/support --workspace-entry . --validation-entry "python3 .loom/bin/loom_init.py verify --target ." --closing-condition "The authored work item can be activated and read mechanically." --init-recovery --activate
python3 tools/loom_flow.py work-item update --target <temp-copy> --item NEXT-0001 --scope "Keep the temp authoring check constrained to `.loom/` files"
cat > <temp-copy>/.loom/review-findings.json <<'JSON'
[
  {
    "id": "block-1",
    "summary": "Formal review has not approved the item yet.",
    "severity": "block",
    "rebuttal": null,
    "disposition": {
      "status": "rejected",
      "summary": "The missing approval signal still blocks the review."
    }
  },
  {
    "id": "warn-1",
    "summary": "Re-run formal review after the missing approval signal is resolved.",
    "severity": "warn",
    "rebuttal": "The follow-up review will be recorded after the blocking item is cleared.",
    "disposition": {
      "status": "deferred",
      "summary": "This follow-up remains open until the next formal review."
    }
  }
]
JSON
python3 tools/loom_flow.py review record --target <temp-copy> --item NEXT-0001 --decision fallback --kind code_review --summary "Formal review has not approved the item yet." --reviewer loom-check --fallback-to admission --findings-file .loom/review-findings.json
```

## 结果

- `flow review`
  - 能稳定读取 `fact-chain -> state-check -> runtime-evidence -> checkpoint-build -> review-entry`
  - 在 bootstrap 样本上按预期返回 `fallback_to: admission`
- `review read`
  - 能稳定读取 `.loom/reviews/INIT-0001.json`
- `recovery writeback`
  - 只写 recovery 主入口，再同步状态面，不引入第二 authored 真相
- `work-item create/update`
  - 只写静态字段；`--activate` 才切换当前 locator truth
- `review record`
  - 能在单一 `review_entry` 中写出 merge checkpoint 可机械消费的正式 review 结论
  - `findings` 成为权威数组，逐条承接 `id`、`severity`、`rebuttal`、`disposition`
  - `blocking_issues` / `follow_ups` 只保留兼容投影
- `loom_check`
  - 已把 `flow review`、`review read|record`、`recovery writeback`、`work-item create|update` 纳入 gate

## 结论

`pre-review -> review -> merge-ready -> merge checkpoint` 已形成明确分层；同时 recovery writeback 与 work item authoring 也已有稳定脚本面，不再只停留在规则层。
