# Loom Review Output Contract

输出是 host-attested review 摘要，至少包含：

- `result`: `pass | block`
- `summary`
- `missing_inputs`
- `fallback_to`
- `review`
  - GitHub PR、current head、review policy、verifier 与 verdict
- `semantic_tree`
  - commit 与 semantic digest
- `workflow_run`
  - trusted path、run id、event、status、conclusion 与 head binding
- `artifact`
  - GitHub artifact id、run id 与 host digest
- `failure_envelope`
  - 恰好一个 primary cause；其他缺口是 consequence

固定步骤为 `semantic-review-run -> GitHub review/assertion -> host-attestation-readback`。
输出只内联 agent-safe 摘要和 locator，不复制 raw engine output。

普通路径不得包含 `.loom/reviews/**`、progress/status/shadow、authored head、
`review record` 或 carrier fallback。Review 只负责语义审查与 host attestation，
不替代 merge-ready 或宿主 merge。
