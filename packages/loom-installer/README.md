# @mc-and-his-agents/loom-installer

This package is retired.

It is now a tombstone package: every CLI invocation fails closed and points to
the current Loom install path.

```bash
npm install -g @mc-and-his-agents/loom
loom host install --host codex --scope user --apply --json
loom host verify --host codex --scope user --json
```

Do not use `loom-installer` for plugin install, single-skill install,
`upgrade-plan`, or `verify-upgrade`. Those active installer surfaces are gone.

`npm deprecate @mc-and-his-agents/loom-installer` is a release closeout action
and must be confirmed separately before execution.

[中文版本](./README.zh-CN.md)
