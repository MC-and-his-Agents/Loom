# Skills Distribution And Adapter Contract

## 定位

本文定义 Loom skills 的发布与宿主适配合同。

Loom 当前唯一的 skills 发布形态是 Codex 用户级 plugin payload：

- manifest：`plugins/loom/.codex-plugin/plugin.json`
- skills payload：`plugins/loom/skills/`
- root entry：`loom-init`
- scenario skills：`loom-adopt`、`loom-resume`、`loom-build`、`loom-story`、`loom-pre-review`、`loom-review`、`loom-spec-review`、`loom-handoff`、`loom-retire`、`loom-merge-ready`

`src/skills/` 是可编辑源码真相。根 `skills/` 是 checked-in mirror，用于本仓库检查、阅读与过渡兼容；它不是目标仓库安装面，也不是 single-skill package 发布面。

## 分发边界

当前发布合同固定为：

- 发布物必须包含完整 plugin payload，而不是每个 skill 的自包含包。
- `plugins/loom/skills/registry.json` 是 plugin payload 的版本与入口索引。
- `plugins/loom/skills/install-layout.json` 定义完整 payload 的最小文件布局。
- `plugins/loom/skills/upgrade-contract.json` 定义完整 payload 的升级判断。
- 每个 scenario skill 可以按目录组织源码和资源，但不得声明为可单独安装的 Loom 发布产物。

当前发布物不得包含：

- `skills/<skill-id>/loom-package.json`
- `plugins/loom/skills/<skill-id>/loom-package.json`
- `skills/<skill-id>/.loom-runtime/`
- `plugins/loom/skills/<skill-id>/.loom-runtime/`
- 目标仓库内 `plugins/loom/skills/`、`.agents/skills/` 或顶层 `skills/` 安装语义

## 宿主适配器职责

宿主适配器只负责把用户级 plugin payload 映射到宿主的发现、安装、启用和升级机制。

适配器应保证：

- 宿主能发现 `loom-init` 作为唯一 root entry。
- 宿主能发现全部 scenario skills。
- 用户级 plugin 安装不写目标仓库。
- 目标仓库采用 Loom 时只写 adoption metadata 和工作事实载体。
- 缺失 manifest、registry、root entry、scenario skill、shared scripts、shared references 或 shared assets 时 fail closed。
- 升级比较 plugin manifest version、host adapter version、plugin payload `registry_version` 与各 skill `contract_version`。

适配器不得：

- 把单个 skill 伪装成完整 Loom 安装。
- 把目标仓库内的 plugin/skills/runtime payload 当作当前安装成功证据。
- 在 adapter 内复制 Loom 治理规则并长期维护第二份事实真相。
- 把 repo-local `loom` CLI 或 repo-local payload 升格成用户级 plugin provider。

## 公开接口

Loom skills 对外只承诺三类接口：

- root entry：`loom-init` 负责初始化入口和场景路由。
- scenario skills：每个 scenario skill 负责一个稳定执行场景。
- shared runtime/resources：`shared/scripts`、`shared/assets`、`shared/references` 为完整 plugin payload 的共享执行与知识层。

`skills/registry.json` 和 `plugins/loom/skills/registry.json` 必须保持一致。`skills/` mirror 只服务本仓库检查和源码阅读；发布、安装、升级、host registration 应消费 `plugins/loom/skills/`。

## 验证

最小验证面：

- `python3 tools/skills_surface.py check`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`

这些检查必须证明：

- `plugins/loom/skills` 与 `src/skills` 同步。
- root entry 为 `loom-init`。
- scenario skills 完整。
- plugin payload 不含 single-skill package artifacts。
- npm package 包含完整 `plugins/loom` payload。
