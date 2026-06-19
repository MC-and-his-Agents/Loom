# WI-1621-1622-1623-1628-1638 Suite Path Decision

- Suite path: not_applicable
- Rationale: This Work Item freezes adoption/install contract semantics for #1621, #1622, #1623, #1628, and #1638. It does not introduce product behavior, runtime code, CLI implementation, package contents, release mechanics, or generated skills payloads.
- Consumer boundary: Formal spec, plan, and implementation-contract artifacts are not required for this docs-only contract freeze. Review, fact-chain, PR metadata, targeted checks, release/no-release judgment, merge-ready, and closeout remain required.
- Recheck condition: Reopen the formal suite decision if the change starts implementing CLI behavior, mutating install outputs, changing package/release surfaces, changing generated skills/plugin payloads, or widening beyond adoption/install contract docs and Work Item carriers.
- Scope proof: Changed files are limited to adoption docs and Loom Work Item carrier files; `VERSION`, `package.json`, release evidence/docs, `tools/check_cli_contract.py`, generated skills, and package surfaces are intentionally untouched.
- Review requirement: current-head review required before merge-ready.
