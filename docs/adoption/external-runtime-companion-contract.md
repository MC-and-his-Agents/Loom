# External Runtime Companion Contract

本文定义从 vendored `.loom/bin` runtime 迁移到 versioned external Loom runtime 的路径。

本轮只冻结合同和迁移纪律，不要求任何 adopted repo 立即 de-vendor。

## 1. 目标

external-runtime 的目标是让成熟 adopted repo 最终可以：

- 保留 `.loom/companion`、status、work item、review、shadow evidence 等仓内治理载体
- 停止长期提交 vendored `.loom/bin/*` runtime 文件
- 通过版本化 Loom runtime locator 执行同一组 Loom 命令
- 在迁移失败时可回滚到 vendored `.loom/bin` carrier

## 2. 当前默认

当前用户入口默认使用根 `loom` CLI，但仓库必须显式声明 runtime provider
mode：

- `global-cli` repo 依赖已安装的根 `loom` 命令作为 runtime provider，不期望
  提交 `.loom/bin` carrier；
- `repo-local-wrapper` repo 有意保留 `.loom/bin` 或等价 wrapper carrier；
  这些 carrier 只在 installed-state 明确声明时才是有效仓库 runtime
  carrier。

历史 strong-governance adopted repo 可能仍需要本地可审计 runtime provenance。
在这类 repo 中，vendored `.loom/bin/**` 仍可作为
[.loom surfaces 版本控制策略](./loom-surfaces-version-control.md) 下的稳定
carrier 保留，但它不再由文件存在本身证明 active provider。manifest
provenance、installed-state 与 provider requirements 必须共同说明它是
current、retained、audit-only、obsolete 还是 compatibility-only。

因此，external-runtime 迁移是一条显式迁移路径；它不得把 workstation
provider state 写成仓库 truth，也不得把未声明的 `.loom/bin` residue 当成
当前 runtime provider。

## 3. Companion 保留面

迁移到 external-runtime 时，以下仓内载体必须保持稳定，不得因为 runtime locator 改变而重写语义：

- `.loom/companion/manifest.json`
- `.loom/companion/repo-interface.json`
- `.loom/companion/interop.json`
- `.loom/status/current.md`
- `.loom/work-items/*`
- `.loom/progress/*`
- `.loom/reviews/*`
- `.loom/shadow/*`

这些文件继续是 repo-local governance carrier。external runtime 只能替换执行入口，不能替代仓内治理真相。

## 4. External runtime locator

external-runtime companion 必须显式声明 runtime locator，而不是依赖环境变量猜测。

最小字段：

```json
{
  "schema_version": "loom-external-runtime/v1",
  "runtime_locator": "loom://github/MC-and-his-Agents/Loom@v1.3",
  "runtime_version": "v1.3",
  "fallback_runtime": ".loom/bin",
  "companion_manifest": ".loom/companion/manifest.json",
  "interop_contract": ".loom/companion/interop.json",
  "rollback_mode": "vendored-runtime"
}
```

稳定约束：

- `runtime_locator` 必须是版本化 locator，不能是浮动 `main`
- `fallback_runtime` 必须指向可恢复的 vendored `.loom/bin` 或明确声明需要 rebootstrap
- `companion_manifest` 与 `interop_contract` 必须继续指向仓内相对路径
- external-runtime 不得通过 `LOOM_SOURCE_REPO_ROOT` 覆盖 bootstrapped target runtime 的判定

## 5. Migration sequence

推荐迁移顺序：

1. 保持 vendored `.loom/bin`，先确认 runtime provenance hash 全部通过
2. 记录 external runtime locator 与版本
3. 在 rehearsal 中运行：
   - `runtime-state`
   - `governance-profile status`
   - `runtime-parity validate`
   - `shadow-parity`
   - `shadow-parity --blocking`，仅限显式 strong profile smoke
4. 确认 `.loom/companion`、status、work item、review、shadow evidence 均未因 runtime locator 改变而漂移
5. 只在以上检查通过后删除或停止提交 vendored `.loom/bin`

停止提交 vendored `.loom/bin` 时，不得引入 blanket `.loom/` ignore；`.loom/companion`、`interop.json` 与其他已启用治理载体必须继续 Git 可见。

## 6. Rollback

任一条件失败时必须回滚到 vendored runtime 或 rebootstrap：

- external runtime locator 不可解析
- runtime version 与期望不一致
- `.loom/companion` 或 `interop.json` 不可读
- shadow evidence source hash 漂移
- active item、review head binding 或 metadata parsing 出现不一致

Rollback 操作必须：

- 保留 evidence
- 恢复 `.loom/bin` 或重新运行 `loom_init bootstrap --write --force --verify`
- 回到 `advisory` gate rollout mode
- 重新运行 adversarial adoption checks 后才允许恢复 blocking 消费

## 7. 边界

external-runtime 迁移不改变：

- repo companion 的 repo-specific residue ownership
- repo interop 的只读 locator 语义
- host action ownership
- review / merge-ready / closeout 的 gate 语义
- shadow parity 默认 validation-only 的边界

它只改变 Loom runtime 的执行来源。
