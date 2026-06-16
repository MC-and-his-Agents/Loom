# WI-1232 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1232 is a narrow CLI/runtime read-surface Work Item with issue-scoped requirements, focused behavior fixtures, and no new external API, data model, security, privacy, or product discovery contract; consumer boundary: suite validate, review, merge-ready, PR gate, and closeout may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence without separate full-path discovery artifacts; recheck condition: author the full suite if #1232 expands into #1233 host-truth diagnostics, #1234 retained lookup, #1235 repair/apply, broad #1236 fixture inventory, #1237 docs/help finalization, #1296 release, external host mutation, shared schema/vocabulary changes, security/privacy behavior, or new product/API contracts.

## Acceptance Scenarios

### S1: idle fact-chain is consumable

Given `.loom/bootstrap/init-result.json` declares `fact_chain.mode = idle`, `current_item_id = no_active_item`, inactive carrier locators using the frozen idle literal, and `.loom/status/current.md` as the status surface, the fact-chain reader returns a structured pass for a fresh idle status surface.

### S2: idle status is non-blocking

Given a valid idle fact-chain, `loom status --target <repo>` reports `item.status = idle`, `item.id = no_active_item`, active-only item fields as the frozen idle literal, and does not classify the absence of active carriers as a broken fact-chain.

### S3: governance summaries do not invent bootstrap carriers

Given a valid idle fact-chain, governance surface and carrier summaries do not default the current item, spec, plan, recovery, review, execution entry, or merge surface to `INIT-0001`.

### S4: active item validation remains fail-closed

Given an active fact-chain, mismatched `current_item_id` locator values and stale derived status fields still return blocking structured failures.
