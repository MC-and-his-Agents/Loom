# WI-1514 Spec

- Suite path: not_applicable
- Rationale: WI-1514 is a docs/skills/evidence inventory convergence slice. It does not change executable runtime behavior, host mutation behavior, or formal suite semantics.
- Consumer boundary: #1514 consumers may use this slice for gate freeze docs/skills and regression inventory wording only. Runtime behavior remains governed by existing gate freeze, hosted admission, PR metadata, and classifier contract tests.
- Recheck condition: Recheck if gate freeze command names, failure classifier vocabulary, hosted admission metadata contract, or PR metadata render/readback behavior changes.
- Scope proof: The implementation diff is limited to skill protocol docs, CLI command matrix troubleshooting, regression inventory, and WI-1514 carrier/review evidence.
- Review requirement: current_head_review_required

## Acceptance

- Skills route PR-bound pre-review, review, and merge-ready flows back through gate freeze repair paths when freeze inputs block.
- CLI command matrix documents `unsupported_command_surface` as the stable classifier for unsupported freeze next actions.
- Regression surface inventory names existing gate-freeze and hosted-admission coverage without moving closeout terminal behavior into #1514.
