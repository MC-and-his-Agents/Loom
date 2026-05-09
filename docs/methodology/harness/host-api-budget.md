# Host API Budget

Loom 的宿主读取必须有明确预算、快照与降级语义。

`github_control_plane.api_snapshot` 的 `budget` 字段必须使用 `loom-execution-budget/v1`，且不得直接暴露供应商专属字段名。

## execution budget Contract

固定字段：

- `schema_version: loom-execution-budget/v1`
- `status`
- `enforcement`
- `summary`
- `dimensions`
- `provenance`
- `adapter_evidence_locator`

其中：

- `status` 为以下之一：
  - `present`
  - `not_applicable`
  - `unavailable`
- `enforcement` 固定为 `advisory`
- `summary` 必须说明预算输出是否来自 host header、adapter evidence，或说明不可用原因
- `dimensions` 每项是标准化维度 `unit/used/limit/remaining/risk/source` 集合中的元素
  - `id` 只允许：`turns`、`tokens`、`requests`、`retries`、`time_window`
  - 不允许出现供应商原始字段名（例如 `x-ratelimit-...`、`rateLimit` 等）
- `provenance` 记录读取来源（host header 或 adapter evidence）
- `adapter_evidence_locator` 只保留适配器 evidence locator，不承载原始供应商字段

读取规则（与 `github_control_plane.api_snapshot` 一致）：

- 非合并展示、status、upgrade-plan、precheck 使用 `cached_non_merge`。
- merge-ready / controlled merge 所需宿主事实使用 `uncached_live_gate`。
- `cached_non_merge` 只允许进程内缓存，返回对象必须是 copy，不能暴露共享可变状态。
- 非合并路径远端读取失败时输出 `unverified`、`stale` 或 `host_unavailable`，不能伪装成 pass。
- 合并前 live recheck 失败必须 fail-closed。
- REST 优先；GraphQL 只在 REST 无法表达对象关系时使用，并且必须声明 scope、cost 与 fallback。
- 不在热路径使用 search endpoint 或 polling。
- 不为了查看额度额外调用 `/rate_limit`；只消费自然响应中的 header 信息（当可读到时）。
- GitHub Actions 默认按 `GITHUB_TOKEN` 每 repo 每小时 1,000 requests 级别预算设计。

读取失败必须留在 `errors` / `missing_inputs` / `host_enforcement.verification_status` 中，由调用路径决定 advisory 降级或 merge fail-closed。
