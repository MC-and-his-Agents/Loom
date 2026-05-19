# Loom Surfaces Version Control Policy

本文冻结目标仓库中 `.loom` surfaces 的版本控制策略。

它回答两个问题：

- 哪些 `.loom` 文件是稳定治理载体，应当进入 Git
- 哪些 `.loom` 文件是运行态 scratch，不应进入 Git

本策略不改变 [repo companion](./repo-companion-contract.md)、[repo interop](./repo-interop-contract.md)、[target repo version](./target-repo-version-contract.md) 或 [external runtime](./external-runtime-companion-contract.md) 的 ownership 边界。

## 1. 稳定载体必须 Git 可见

以下路径一旦由当前 adoption profile 生成或启用，必须能被 `git status` 看见并可被提交：

- `.loom/bootstrap/manifest.json`
- `.loom/bootstrap/init-result.json`
- `.loom/README.md`
- `.loom/companion/manifest.json`
- `.loom/companion/README.md`
- `.loom/companion/repo-interface.json`
- `.loom/companion/interop.json`
- `.loom/companion/**` 下由 repo companion 合同允许的 repo-specific locator 文档
- `.loom/bin/**`，仅限当前采用 vendored repo-local runtime 阶段
- `.loom/work-items/**`，仅限显式启用 execution-control 或 strong-governance 后
- `.loom/progress/**`，仅限显式启用 execution-control 或 strong-governance 后
- `.loom/reviews/**`，仅限显式启用 execution-control、strong-governance 或 Loom-authored review carrier 后
- `.loom/status/current.md`，仅限显式启用 Loom-owned status surface 后
- `.loom/specs/**`，仅限显式启用 Loom-authored spec truth 后
- `.loom/shadow/**`，仅限显式启用 shadow evidence 并由 Loom 合同要求版本化后

`attach-only` profile 默认只提交 attach metadata、repo companion / interop read surfaces、repo-local verify entry 与必要 vendored runtime。它不得生成 Loom-authored work item、progress、status、review 或 spec truth，除非 adoption intent 显式升级到 execution-control。

## 2. 运行态残留必须保持未版本化

以下路径是运行态 scratch、缓存或本地尝试残留，不应提交：

- `.loom/runtime/**`
- `.loom/tmp/**`
- `.loom/cache/**`
- `.loom/attempts/**/raw-logs/**`
- `.loom/attempts/**/scratch/**`
- `.loom/local/**`
- host token、local credential、machine cache 或一次性调试输出

若某个 profile 需要把 attempt evidence 版本化，必须先定义稳定 evidence schema 与 locator；不能直接提交 raw logs 或 scratch 目录。

## 3. `.gitignore` 纪律

目标仓库不得用 blanket ignore 隐藏整个 `.loom/`。

禁止：

```gitignore
.loom/
.loom/**
```

推荐只忽略运行态目录：

```gitignore
.loom/runtime/
.loom/tmp/
.loom/cache/
.loom/attempts/**/raw-logs/
.loom/attempts/**/scratch/
.loom/local/
```

如果目标仓库已经存在 blanket `.loom/` ignore，bootstrap 和 verify 必须 fail closed。dry-run / blocked write 必须输出可审查的 ignore 修复方案；显式选择自动修复时，只能把 blanket ignore 收敛为 `.loom/runtime/`、`.loom/tmp/`、`.loom/cache/` 等运行态路径。不要用 `git add -f .loom` 粗粒度绕过，因为这会同时掩盖稳定载体和运行态残留的边界。

## 4. Verify failure guidance

当 verify 发现稳定 carrier 被忽略、缺失或不可见时，输出必须包含：

- 具体路径
- 该路径属于哪个 profile 或 capability
- 当前失败原因：`missing`、`ignored`、`untracked` 或 `unexpected runtime path`
- 建议动作：移除 blanket ignore、改成细粒度 ignore、显式升级 adoption intent，或删除 forbidden authored carrier

运行态路径如 `.loom/runtime/`、`.loom/tmp/`、`.loom/cache/` 不得被误报为必须提交。

## 5. External runtime 迁移

在 vendored repo-local runtime 阶段，`.loom/bin/**` 是可审计 runtime provenance，必须 Git 可见。

迁移到 versioned external runtime 后，`.loom/bin/**` 可以停止提交，但必须同时满足 [external runtime companion contract](./external-runtime-companion-contract.md)：

- external runtime locator 已版本化
- fallback runtime 或 rebootstrap 路径明确
- `.loom/companion` 与 `interop.json` 继续保持 Git 可见
- rollback 能恢复到可信 runtime

external runtime 只替换执行来源，不能替代仓内治理真相。
