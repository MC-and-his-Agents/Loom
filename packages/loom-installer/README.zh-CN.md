# @mc-and-his-agents/loom-installer

这个包已退役。

它现在是 tombstone package：任何 CLI 调用都会 fail closed，并指向当前 Loom 安装路径。

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host verify --host codex --scope user --json
```

不要再用 `loom-installer` 安装 plugin、安装单 skill、执行 `upgrade-plan` 或
`verify-upgrade`。这些活跃 installer 入口已经移除。

`npm deprecate @mc-and-his-agents/loom-installer` 是 release closeout 动作，
执行前必须单独确认。

[English version](./README.md)
