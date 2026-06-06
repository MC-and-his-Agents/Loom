# Governance

`governance/` 负责 Loom 的制度层。

它回答：

- 真相源如何划分
- 工作如何进入执行
- 审查职责如何拆分
- 事项成熟度与关闭语义如何定义

当前承接的核心条目：

- [issue-model.md](./issue-model.md)
  - `#175`
- [principles.md](./principles.md)
  - `EXT-0001` `EXT-0002` `EXT-0006` `EXT-0023`
- [change-governance-intensity.md](./change-governance-intensity.md)
  - `#1315`
- [loom-governance-intensity-mapping.md](./loom-governance-intensity-mapping.md)
  - `#1316`
- [review-model.md](./review-model.md)
  - `EXT-0004` `EXT-0014` `EXT-0018`
- [github-delivery-funnel.md](./github-delivery-funnel.md)
  - `#299` `#300` `#304` `#305`
- [story-intake.md](./story-intake.md)
  - `#649`
- [spec-implementation-separation.md](./spec-implementation-separation.md)
  - `#290`
- [governance-maturity-model.md](./governance-maturity-model.md)
  - `#307`
- [maturity-and-closing.md](./maturity-and-closing.md)
  - `EXT-0026`
- [state-machine.md](./state-machine.md)
  - `#157`
- [truth-and-sync-boundary.md](./truth-and-sync-boundary.md)
  - `#158`
- [host-object-taxonomy.md](./host-object-taxonomy.md)
  - `#153`
- [goal-schema.md](./goal-schema.md)
  - `#821`

`Project / Phase / FR / Work Item / /goal / delegated goal` 的字段、缺失语义与校验失败分类以 [goal-schema.md](./goal-schema.md) 为主落点。其他执行、subagent 或 adoption 文档只引用该 schema，不再各自定义第二套 goal truth。
