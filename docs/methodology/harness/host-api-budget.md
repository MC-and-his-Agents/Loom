# Host API Budget

Loom 的宿主读取必须有明确预算、快照与降级语义。

默认规则：

- 非合并展示、status、upgrade-plan、precheck 使用 `cached_non_merge`。
- merge-ready / controlled merge 所需宿主事实使用 `uncached_live_gate`。
- `cached_non_merge` 只允许进程内缓存，返回对象必须是 copy，不能暴露共享可变状态。
- 非合并路径远端读取失败时输出 `unverified`、`stale` 或 `host_unavailable`，不能伪装成 pass。
- 合并前 live recheck 失败必须 fail-closed。
- REST 优先；GraphQL 只在 REST 无法表达对象关系时使用，并且必须声明 scope、cost 与 fallback。
- 不在热路径使用 search endpoint 或 polling。
- 不为了查看额度额外调用 `/rate_limit`；只消费自然响应中的 `x-ratelimit-*` header。
- GitHub Actions 默认按 `GITHUB_TOKEN` 每 repo 每小时 1,000 requests 级别预算设计。

## Snapshot Contract

`github_control_plane.api_snapshot` 使用：

- `schema_version: loom-host-api-snapshot/v1`
- `read_mode: cached_non_merge | uncached_live_gate`
- `verification_status: verified | unverified | stale | host_unavailable`
- `fallback_status`
- `cache_scope`
- `requests`
- `errors`
- `budget`

读取失败不得投影为：

- empty required checks
- disabled branch protection
- empty rulesets
- host enforcement pass

缺失或失败必须留在 `errors` / `missing_inputs` / `host_enforcement.verification_status` 中，由调用路径决定 advisory 降级或 merge fail-closed。
