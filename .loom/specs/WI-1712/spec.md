# Spec

- Suite path: not_applicable

- Formal-suite not_applicable:
  - rationale: WI-1712 is a docs-governance contract freeze that defines version authority, payload freshness terminology, and the hash decision boundary without implementing runtime behavior.
  - consumer boundary: suite validate, spec review, implementation review, merge-ready, PR gate, hosted CI, and closeout consume this only as the formal suite decision while fact-chain, current-head review, PR metadata, no-release judgment, controlled merge, and closeout remain required.
  - recheck condition: require a full or minimal suite if scope expands into CLI behavior, payload hash implementation, metadata generation, host source/cache readback, legacy installer behavior, fixtures, version bump, release mechanics, AGENTS root rules, or external-visible behavior.
  - scope proof: PR #1723 changes version authority docs, install-surface docs, the skills distribution contract mirrors, `version_surface_check`, and WI-1712 fact-chain carriers only.
  - review requirement: current_head_review_required.
