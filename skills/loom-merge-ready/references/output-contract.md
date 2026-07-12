# Loom Merge Ready Output Contract

输出至少包含：

- `result`: `pass | block`
- `summary`
- `missing_inputs`
- `fallback_to`
- `host_attestation`
  - PR/current head、review/verifier、semantic tree、workflow run 与 artifact digest
- `pr_gate`
  - 同一 PR head 的 metadata/required-check verdict
- `merge_check`
  - base branch、mergeability、required checks 与 merge method
- `suite_path_consumption`
  - full suite locators，或有效 minimal `not_applicable`
- `failure_envelope`
  - 一个 primary cause；其余是 consequences

固定步骤为 `host-attestation-readback -> pr-gate -> merge-check`。输出只包含
agent-safe 摘要与 GitHub/artifact locator，不包含 repo review/current/status/shadow
carrier，也不执行 merge。
