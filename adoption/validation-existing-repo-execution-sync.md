# Real Adoption Validation: Existing-Repo Execution And Sync Companion

## 1. 样本标识

- 轻量既有样本：`mail-listener`
  - 源仓库：`/Users/mc/dev/mail-listener`
  - adopted 副本：`/tmp/loom-170-mail`
- 复杂既有样本：`hotcp`
  - 源仓库：`/Users/mc/dev/hotcp`
  - adopted 副本：`/tmp/loom-170-hotcp`
- Loom companion control-plane 样本：
  - 目标仓库：`/Users/mc/dev/Loom`
  - issue：`#131`
  - PR：`#138`
  - Project：`5`
- 验证日期：`2026-04-18`
- 对应 Loom issue：`#170`

## 2. 这次验证如何分段

`#170` 不把外部 adopted existing repo 样本扩成新的 GitHub fixture。

本次固定分成两段：

1. 在 `mail-listener` / `hotcp` 的 adopted 副本上验证：
   - `flow resume`
   - `flow handoff`
   - `recovery writeback`
2. 在 Loom 仓内继续复用已存在的 control-plane 样本，验证：
   - `reconciliation audit`
   - `reconciliation sync --dry-run`
   - `closeout check`
   - `closeout sync`

因此，本记录证明的是“既有仓库执行/回写可稳定消费”，以及“truth sync 有 companion evidence”，而不是“外部样本已经独立证明了 GitHub truth sync”。

## 3. adopted existing repo 执行 / 回写复验

### 3.1 bootstrap 与 baseline

在两个 adopted 副本上都先执行：

```bash
python3 tools/loom_init.py bootstrap --target /tmp/loom-170-mail --write --force --verify --install-pr-template
python3 tools/loom_init.py bootstrap --target /tmp/loom-170-hotcp --write --force --verify --install-pr-template
git -C /tmp/loom-170-mail commit -m "bootstrap baseline for #170 mail validation"
git -C /tmp/loom-170-hotcp commit -m "bootstrap baseline for #170 hotcp validation"
```

结果：

- `bootstrap --write` 成功写入 Loom 工件
- 两个副本上的 `bootstrap --verify` 都显式暴露 `state-check block`，因此不能把“刚写入但尚未形成干净 baseline”的现场伪装成验证通过
- 补 baseline commit 后，后续 `resume/handoff/writeback` 可在同一 adopted 副本上继续进行

### 3.2 `mail-listener`

执行：

```bash
python3 tools/loom_flow.py flow resume --target /tmp/loom-170-mail --item INIT-0001
python3 tools/loom_flow.py flow handoff --target /tmp/loom-170-mail --item INIT-0001
python3 tools/loom_flow.py recovery writeback --target /tmp/loom-170-mail --item INIT-0001 --current-stop "mail-listener validation reached authored writeback." --next-step "Review the updated recovery entry from the resumed existing-repo sample." --latest-validation-summary "mail-listener adopted copy passed resume and handoff."
```

结果：

- `flow resume`
  - `result = pass`
  - `state-check = pass`
  - `workspace-locate = pass`
- `flow handoff`
  - `result = pass`
  - 能稳定返回 `writeback_fields`
- `recovery writeback`
  - `result = pass`
  - 只改 recovery 主入口并同步状态面

额外观察：

- 本次 bootstrap 读取到的 `github_control_plane.repository = MC-and-his-Agents/mail-listener`
- 该 adopted 副本当前被脚本判断为 `complex-existing`
- 本记录不据此回写新的 adoption 结论；它只记录当前执行面已经可以稳定消费这类既有样本

### 3.3 `hotcp`

执行：

```bash
python3 tools/loom_flow.py flow resume --target /tmp/loom-170-hotcp --item INIT-0001
python3 tools/loom_flow.py flow handoff --target /tmp/loom-170-hotcp --item INIT-0001
python3 tools/loom_flow.py recovery writeback --target /tmp/loom-170-hotcp --item INIT-0001 --current-stop "hotcp validation reached authored writeback." --next-step "Review the updated recovery entry from the complex existing-repo sample." --latest-validation-summary "hotcp adopted copy passed resume and handoff."
```

结果：

- `flow resume`
  - `result = pass`
- `flow handoff`
  - `result = pass`
- `recovery writeback`
  - `result = pass`

因此，复杂既有仓库样本也能消费同一条 `resume -> handoff -> recovery writeback` 执行链，不需要额外发明第二套 authored truth。

## 4. Loom companion truth-sync 复验

在 Loom 仓库当前主工作树上执行：

```bash
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 131 --pr 138 --project 5
python3 tools/loom_flow.py reconciliation sync --target /Users/mc/dev/Loom --issue 131 --pr 138 --project 5 --dry-run
python3 tools/loom_flow.py closeout check --target /Users/mc/dev/Loom --issue 131 --pr 138 --project 5 --skip-gate
python3 tools/loom_flow.py closeout sync --target /Users/mc/dev/Loom --issue 131 --pr 138 --project 5 --skip-gate
```

结果：

- `reconciliation audit`
  - `result = pass`
- `reconciliation sync --dry-run`
  - `result = pass`
  - `applied_actions = []`
- `closeout check`
  - `result = pass`
- `closeout sync`
  - `result = pass`

这里继续使用 `#131/#138/project 5` 这一已收敛样本，证明 Loom 当前的 control-plane sync 语义仍可被实际命令复验。

## 5. 与既有验证记录的消费关系

本记录只把既有证据收成 `#170` 所需的单条 closeout 依据：

- [validation-complete-kernel-existing-repos.md](./validation-complete-kernel-existing-repos.md)
  - 承接既有仓库完整入口链路已可消费
- [validation-skill-loom-resume.md](./validation-skill-loom-resume.md)
  - 承接 `resume` 场景读面与顺序
- [validation-skill-loom-handoff.md](./validation-skill-loom-handoff.md)
  - 承接 `handoff` 只输出最小回写清单
- [validation-fact-chain-mail-listener.md](./validation-fact-chain-mail-listener.md)
  - 承接 `mail-listener` 的既有事实链消费背景
- [validation-host-lifecycle-and-closeout.md](./validation-host-lifecycle-and-closeout.md)
  - 承接 `reconciliation` / `closeout` 的主合同与负样本纪律

## 6. 结论

- `#170` 现在已有单条版本化记录承接“既有仓库执行 / 回写 / sync companion 验证”
- adopted existing repo 样本已经证明：
  - `resume` 可恢复当前执行上下文
  - `handoff` 可产出最小回写清单
  - `recovery writeback` 可更新 authored recovery truth 而不生成第二状态源
- Loom companion sample 继续证明：
  - `reconciliation audit`
  - `reconciliation sync --dry-run`
  - `closeout check`
  - `closeout sync`
  仍然能对齐同一组 issue / PR / Project 真相
- 本次没有宣称外部 adopted existing repo 已经独立证明 GitHub truth sync，也没有新增 GitHub fixture 管理规则
