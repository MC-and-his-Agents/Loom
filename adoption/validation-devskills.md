# Real Adoption Validation: DevSkills

## 1. 样本标识

- 样本仓库：`DevSkills`
- 仓库类型：`既有仓库（轻量路径反例）`
- 仓库位置：`/Users/mc/dev/DevSkills`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#29`

## 2. 仓库事实

- 已有清晰根级边界文档：`AGENTS.md`
- 已有根级 `README.md` 与模块级 `README.md` / `AGENTS.md`
- 仓库目标、目录职责、复用结构与文档约束都已可读
- 当前没有可见 `.github/workflows/`、显式 CI 配置、统一测试目录或仓库级验证入口
- 仓库内存在局部 helper scripts，但它们服务的是子能力校验，不构成统一仓库级验证面
- 仓库主产物是共享治理语义和 skill 包，本身已经带有共享 contract / shared skill 风险信号
- 当前缺口不只是 Loom 风格的治理入口，也包括如何为共享方法库建立正式验证与状态入口

## 3. `loom-init` 判断

- 场景判断：`复杂既有仓库`
- 装配强度：`标准`
- 推荐路径：不继续采用 `lightweight retrofit default`，而是按更重路径补正式验证入口与共享 contract 边界
- 不是 `新项目`：因为仓库已经有稳定边界、模块结构与复用规则
- 不是 `小型既有仓库`：因为它不满足轻量路径的硬前提，也带有共享 contract / shared skill 风险信号
- 接入方式：`companion docs`
- 恢复形态：若引入 Loom，应从明确验证入口和正式事项入口开始，不把 `checkpoint-lite` 当作默认前提

## 4. 首批装配结果

### 本轮启用

- `companion docs` 接入
- 更明确的正式事项入口与验证入口
- 对共享 contract / shared skill 变更的正式规约路径
- 统一的 review / closeout 合同

### 本轮暂不启用

- 重写现有根规则
- profile 分层
- 宿主特定 adapter 实现

### 首批工件与入口

- 规则入口：保留现有 `AGENTS.md`，新增 companion docs 承接 Loom 规则
- 验证入口：必须先补统一仓库级验证入口，否则无法满足 Loom 输出合同中的验证与 clean state 要求
- 恢复主入口：不默认寄存在 issue / PR；先建立正式事项承载面
- 初始 clean state：不重写现有根规则，但必须能回答验证入口、状态读取入口和共享 contract 变更的正式路径

## 5. 摩擦、失效点与升级信号

### 当前路径失效的证据

- 该仓库没有可见 CI / 测试入口，也没有统一仓库级验证面
- 仓库主产物是共享治理语义与 skill 包，本身已经超出“只补最小治理包”的轻量语义
- 若继续按轻量路径处理，验证入口、状态读取入口和 clean state 都需要依赖口头解释补齐

### 升级信号

- 无可见 CI / workflow 且无统一验证入口
- 仓库主产物本身是共享 contract、shared skill 或 governance module
- merge 前 review 仍承担第一次系统性高质量判断

## 6. 台账回写结果

- 新增 `EXT-0045`
- 修正 `EXT-0031`
- 受影响落点：`adoption/lightweight-retrofit-default.md`、`skills/loom-init/references/intake-signals.md`、`skills/loom-init/SKILL.md`
- 本次结论为：`DevSkills` 不应作为轻量路径正例，它提供的是一条负例边界

## 7. 关闭依据

- `#29` 的完成标准已满足：已有 `mail-listener` 之外的第二个真实既有仓库样本，并把轻量路径的失效边界写回版本控制
- 本次验证没有新增第二个轻量正例，而是收紧了 `lightweight retrofit default` 的适用边界
- 当前继续保留在候选区的部分：共享方法库是否需要进一步独立出专门 adoption 路径，仍需更多样本
