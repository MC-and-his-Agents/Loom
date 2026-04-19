# Skills

`skills/` 负责 Loom 的入口层。

当前 `skills/` 的核心职责，是把 Loom 已有能力装配成可直接使用的入口，并把执行者导向正确场景。

当前稳定结构为：

- 1 个 root entry
  - `loom-init`
- 7 个场景 skills
  - `loom-adopt`
  - `loom-resume`
  - `loom-pre-review`
  - `loom-review`
  - `loom-handoff`
  - `loom-retire`
  - `loom-merge-ready`

当前已落以下入口合同与分发工件：

- [registry.json](./registry.json)
  - 仓库内机读入口注册表，声明 root 入口、场景入口与合同版本
- [upgrade-contract.json](./upgrade-contract.json)
  - 仓库内机读升级协议，声明显式升级、多 entry 版本可见与刷新要求
- [install-layout.json](./install-layout.json)
  - 仓库内机读安装布局合同，声明 installed-skills 最小必须面
- [route-matrix.md](./route-matrix.md)
  - root entry 的显式 / 隐式路由矩阵，声明任务信号与目标 skill 的稳定对应关系
- [loom-init/SKILL.md](./loom-init/SKILL.md)
  - Loom 的唯一 root entry，负责初始化与场景路由
- [loom-init/contract.json](./loom-init/contract.json)
  - `loom-init` 的机读 root 合同，声明输入 / 输出合同、路由引用与安装关系
- 各场景 skill 的 `SKILL.md` / `contract.json` / `agents/openai.yaml` / `references/*`
  - 声明对应场景的触发信号、输出合同与底层 CLI 编排
- 各场景 skill 的 `scripts/*`
  - 作为 installed-skills 的正式入口脚本
- [shared/scripts/](./shared/scripts/)
  - 共享 deterministic runtime，供所有 skill-local scripts 复用
- [shared/assets/](./shared/assets/)
  - bootstrap 写入目标仓库所需的模板和 PR 资产
- [shared/references/](./shared/references/)
  - installed-skills 必需的 Loom 真相读面
- [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)
  - 约束 `skills/` 作为入口层时的最小分发、发现、升级、版本识别与宿主适配边界

当前 `skills/` 的职责包括：

- 读取 `shared/references/` 中镜像的 adoption / governance / harness / templates 真相读面
- 将这些能力装配成初始化、执行、审查与收口入口
- 暴露可被宿主直接调用的执行入口，例如各 skill 的 `scripts/*.py` 与 `shared/scripts/*.py`
- 让 root entry 在显式调用与隐式信号下，都能导向正确场景 skill

对入口层自身，Loom 当前至少要求能表达以下验证面：

- 显式触发是否正确
- 隐式触发是否正确
- 行为是否出现退化
- adapter 失败是否可见
- 版本变化是否可见

这些验证面的最小边界由 [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md) 承接；宿主完整测试矩阵与 CI 产品细节不进入 Loom 内核。

当前 `skills/` 的直接输入主要来自：

- [shared/references/adoption/routing-and-checkpoints.md](./shared/references/adoption/routing-and-checkpoints.md)
- [shared/references/adoption/lightweight-retrofit-default.md](./shared/references/adoption/lightweight-retrofit-default.md)
- [shared/references/governance/review-model.md](./shared/references/governance/review-model.md)
- [shared/references/harness/daily-entry-matrix.md](./shared/references/harness/daily-entry-matrix.md)
- [shared/references/harness/recovery-model.md](./shared/references/harness/recovery-model.md)
- [shared/references/templates/spec-suite.md](./shared/references/templates/spec-suite.md)
- [route-matrix.md](./route-matrix.md)
- [loom-init/references/input-signals.md](./loom-init/references/input-signals.md)
- [loom-init/references/output-contract.md](./loom-init/references/output-contract.md)

其中 `loom-init` 负责两件事：

- 做初始化 bootstrap
- 在未显式指定 skill 时，基于任务信号路由到正确场景

场景 skill 负责：

- 解释什么时候该用这个入口
- 明确应该读取哪些 Loom 真相载体
- 编排对应 CLI 或 flow
- 输出该场景的最小稳定结果

其中 `loom-init` 负责把以下入口合同转成实际判断与输出：

- 输入信号合同
  - [loom-init/references/input-signals.md](./loom-init/references/input-signals.md)
- 输出合同
  - [loom-init/references/output-contract.md](./loom-init/references/output-contract.md)
- 场景路由矩阵
  - [route-matrix.md](./route-matrix.md)
- 小型既有仓库默认策略
  - [shared/references/adoption/lightweight-retrofit-default.md](./shared/references/adoption/lightweight-retrofit-default.md)
- `skills` 分发与适配合同
  - [distribution-and-adapter-contract.md](./distribution-and-adapter-contract.md)
