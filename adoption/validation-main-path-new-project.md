# Real Adoption Validation: New-Project Main Path

## 1. 样本标识

- 样本真相来源：`loom-adoption-new-project`
- 仓库类型：`新项目`
- 源仓库位置：`/Users/mc/dev/loom-adoption-new-project`
- 主验证副本：`/tmp/loom-168-clean-path`
- 观察副本：
  - `/tmp/loom-168-new-main-path`
  - `/tmp/loom-168-init-path`
- 验证日期：`2026-04-18`
- 对应 Loom issue：`#168`

## 2. 本次验证为什么采用 `Split Path`

当前新项目样本仍然没有远端、issue / PR 承接面，也没有可解析的 GitHub control-plane。

因此，本次不强行把同一个样本升级成 host-backed closeout 样本，而是固定分成两段：

1. 在临时副本里验证 `adopt -> execute -> review -> merge-ready`
2. 只验证它进入 `closeout` 时会把宿主缺口显式报出，而不是伪装成通过

这条边界与 [validation-new-project.md](./validation-new-project.md) 中“新项目首轮缺的是最小入口，不是现成宿主控制面”的结论一致。

## 3. 复验路径

### 3.1 进入 adopt

先在空仓副本上验证路由：

```bash
python3 tools/loom_init.py route --target /tmp/loom-168-new-main-path --task "请初始化这个新项目并接入 Loom"
```

结果：

- `selected_skill = loom-adopt`
- `result = pass`

这复用了 [validation-skill-loom-adopt.md](./validation-skill-loom-adopt.md) 的场景路由结论，但把目标切换成真实新项目样本副本。

### 3.2 bootstrap 与 baseline commit

在空仓副本上直接执行：

```bash
python3 tools/loom_init.py bootstrap --target /tmp/loom-168-new-main-path --write --force --install-pr-template
git -C /tmp/loom-168-new-main-path commit -m "bootstrap baseline for #168 validation"
python3 tools/loom_init.py verify --target /tmp/loom-168-new-main-path
```

结果：

- `bootstrap --write` 成功写出 Loom 首批工件
- 在空仓阶段直接附带 `--verify` 会把 `state-check block` 暴露出来，因此不能把“尚无稳定 `HEAD`”伪装成可继续执行
- 写入后补一条 baseline commit，再执行 `verify`，结果为 `ok: true`

这一步把 [validation-new-project.md](./validation-new-project.md) 里的“需要首个稳定提交或等价回退边界”落实为真实脚本行为。

### 3.3 execute / review / merge-ready

在干净副本 `/tmp/loom-168-clean-path` 上执行：

```bash
python3 tools/loom_flow.py recovery writeback --target /tmp/loom-168-clean-path --item INIT-0001 --current-stop "Bootstrap execution has started." --next-step "Record the first formal review conclusion." --latest-validation-summary "Bootstrap baseline committed and ready for review validation."
python3 tools/loom_flow.py flow review --target /tmp/loom-168-clean-path --item INIT-0001
python3 tools/loom_flow.py review record --target /tmp/loom-168-clean-path --item INIT-0001 --decision fallback --kind code_review --summary "The new-project sample is ready for review consumption but still lacks host-backed merge approval." --reviewer codex --fallback-to admission --findings-file /tmp/loom-168-clean-findings.json
python3 tools/loom_flow.py flow merge-ready --target /tmp/loom-168-clean-path --item INIT-0001
python3 tools/loom_flow.py checkpoint merge --target /tmp/loom-168-clean-path --item INIT-0001
```

结果：

- `recovery writeback`
  - `result = pass`
- `flow review`
  - `state-check = pass`
  - `runtime-evidence = pass`
  - `build checkpoint = fallback`
  - 顶层 `result = fallback`
- `review record`
  - `result = pass`
  - review finding 明确记录“当前样本仍缺 host-backed merge approval”
- `flow merge-ready`
  - 顶层 `result = fallback`
  - `fallback_to = admission`
- `checkpoint merge`
  - `result = fallback`
  - `fallback_to = admission`

这里没有把 bootstrap 新项目硬写成“已经 merge-ready”，而是稳定返回 `fallback`，并把回退点保持在 admission/build 一侧。

### 3.4 closeout 边界

继续在同一副本执行：

```bash
python3 tools/loom_flow.py closeout check --target /tmp/loom-168-clean-path --skip-gate
```

结果：

- `result = block`
- `summary = closeout could not determine the GitHub repository`
- `missing_inputs = ["owner/repo"]`
- `fallback_to = merge`

这证明当前新项目样本在没有 GitHub control-plane 时，会显式停在 host closeout 入口之前，不会把缺失宿主事实伪装成 `pass`。

## 4. 与既有验证记录的消费关系

本记录不重写已有主合同，而是把先前分散验证收成一条新项目主路径：

- [validation-new-project.md](./validation-new-project.md)
  - 承接“为什么是新项目最小起步，而不是 retrofit”
- [validation-complete-kernel-new-project.md](./validation-complete-kernel-new-project.md)
  - 承接 bootstrap 后的完整入口链路可读性
- [validation-skill-loom-adopt.md](./validation-skill-loom-adopt.md)
  - 承接 adopt 场景路由与 root bootstrap 消费关系
- [validation-review-and-authoring.md](./validation-review-and-authoring.md)
  - 承接 `recovery writeback`、`review record` 的 authored 写回语义
- [validation-host-lifecycle-and-closeout.md](./validation-host-lifecycle-and-closeout.md)
  - 承接 host lifecycle / closeout 的正式合同；本记录只证明新项目样本会在缺少 host truth 时受控阻断

## 5. 结论

- `#168` 要求的新项目主路径现在已有单条版本化记录承接
- 这条主路径已经证明：
  - 新项目可从 `loom-adopt` 进入 bootstrap
  - baseline commit 形成后，`verify`、`recovery writeback`、`review record` 可被同一条事实链消费
  - `merge-ready` / `checkpoint merge` 在当前样本阶段稳定返回 `fallback`
  - `closeout check` 在缺少 GitHub control-plane 时稳定返回 `block`
- 本次没有把新项目样本升级成新的宿主控制面样本，也没有改写 `closeout` / `reconciliation` 合同
