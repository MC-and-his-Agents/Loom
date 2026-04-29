# Evidence Boundary

Loom keeps evidence when it is part of upstream auditability, acceptance, or regression coverage. It does not keep local installation state or generated runtime output as repository truth.

## Versioned Evidence

Keep these files in git:

- `extraction-ledger.md`: the audit ledger for upstreamable lessons, sources, and decisions.
- `landing-map.md`: the map from extracted lessons to current Loom owners.
- Current validation records that are consumed by gates, fixtures, or active methodology contracts.
- Small fixtures that prove a cross-repo behavior without requiring another repository to be present.

Historical source names such as downstream repository names may appear in these files when they identify audit provenance. They must not become generic Loom rule names or default path assumptions.

## Archived Evidence

Move evidence to an archive when it is still useful for audit history but no longer acts as current product truth, gate input, or methodology contract.

Archived evidence should explain:

- what decision it supported;
- which current contract replaced the process narrative;
- whether any gate or fixture still consumes it.

## Non-Versioned Evidence

Do not commit:

- repo-local plugin marketplace state such as `.agents/plugins/marketplace.json`;
- local Codex or Claude installation state such as `.codex/` or `.claude/marketplaces/`;
- generated payloads, generated skill packages, caches, `__pycache__`, or `.pyc` files;
- one-off command transcripts that belong in PR or issue comments.

If a generated artifact becomes necessary for regression coverage, convert it into a minimal fixture with a stable owner and document why it is no longer treated as generated output.
