# Story Intake Template Boundary

本文件定义 templates 层如何承接 story intake。

权威 story intake 合同在 [../governance/story-intake.md](../governance/story-intake.md)。本文件只说明模板层边界，避免在 templates 下复制第二份 story truth。

本文件当前承接：

- `#1015`
- `#1029`

## 模板层职责

templates 层只提供可投放骨架和字段约束：

- User Story 最小骨架
- Story Readiness verdict 字段
- Story Business Confirmation 字段
- Delivery Consumption Boundary 字段

模板层不得重新定义 story 的 authority boundary。若字段语义、verdict 词汇或 formal spec 消费规则与治理合同冲突，以 [../governance/story-intake.md](../governance/story-intake.md) 为准。

## 当前骨架

- [scaffold/user-story.md](./scaffold/user-story.md)

该 scaffold 必须保持四个产物分离：

- `User Story`
- `Story Readiness`
- `Story Business Confirmation`
- `Delivery Consumption Boundary`

Story intake 只能作为 `spec.md` / `plan.md` 的上游语义来源。它不能替代 Work Item、recovery、review、merge-ready 或 closeout truth。
