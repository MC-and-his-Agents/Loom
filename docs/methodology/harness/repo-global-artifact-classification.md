# Repo / Global Artifact Classification

本合同定义 adopted repository、GitHub host 与 workstation cache 的事实边界。

## Authority matrix

| Fact / artifact | Owner | Default location |
| --- | --- | --- |
| adoption profile、companion policy | repository | `.loom/installed-state.json` 与小型 companion manifest |
| goal、scope、dependencies、closing condition | GitHub Issue / Work Item | GitHub |
| PR、branch、head、checks、merge facts | GitHub PR / Actions | GitHub |
| semantic review、delivery closeout | host attestation | GitHub check run / Actions artifact |
| product acceptance | product acceptance adapter | trusted host artifact |
| formal source/spec/test assets | target repository | repository-native paths |
| current session、MRU、diagnostics、runtime output | workstation | `~/.loom/` 或 ignored cache |

Committed current、status、progress、review、shadow 与 ordinary closeout carrier
不属于默认 repository authority。light profile 出现这些路径时应 fail closed，并由
`loom repair plan` 指向删除/迁移，而不是要求同步或 terminalize。

## Workstation path

可再生的本地状态使用稳定 repository id 放在：

```text
~/.loom/repos/<repo-id>/
```

可包含 runtime output、临时文件、diagnostic readback、hash-addressed artifact copy
与 locator index。repository id 是 workstation-local key，不得提交为仓库身份。

## Consumer boundary

workstation cache 只能加速发现、resume 与诊断。consumer 必须：

- 重新读取 GitHub/Git/repository owner 的权威事实；
- 验证 artifact digest、head/run binding 与 freshness；
- 在 cache 缺失时仍能从权威来源工作；
- 在 cache 与 host facts 冲突时 fail closed；
- 不因 cache 声称安全而修改 repo 或 GitHub。

tracked legacy residue 是 migration input，不是当前 truth。默认公共入口不得把长日志、
runtime payload、plugin cache 或 workstation registry 写回 repository。

## Validation

实现必须证明：

- source/adopted repo role 不会混淆 canonical payload 与 legacy surface；
- `doctor`、`workspace check`、`pre-review`、`merge-ready` 与 `closeout` 不依赖
  repo-local runtime cache；
- cache mismatch 返回一个精确 primary cause；
- package 与 plugin payload 不包含 workstation cache 或 Python bytecode。
