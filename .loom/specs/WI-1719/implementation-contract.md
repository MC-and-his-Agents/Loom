# Implementation Contract

## Scope

- Owns `packages/loom-installer` behavior that emits, reads, and compares single-skill version context.
- Owns installer regression tests proving `skill_package_version` is not current freshness authority.
- Owns WI-1719 fact-chain, progress, suite, evidence, task-carrier, review, status, and bootstrap carriers.

## Non-goals

- Do not restore or recommend single SKILL install as the current install path.
- Do not make per-skill package versions participate in freshness or upgrade success.
- Do not change plugin payload hash generation, host command boundaries, root release versions, npm publish, installer tags/releases, or v0.19.0 release mechanics.

## Invariants

- `contract_version` / `skill_contract_version` remain compatibility metadata.
- Legacy installed `skill_package_version` may be read only as migration diagnostic context.
- Current upgrade/freshness decisions must not compare `skill_package_version`.
- Missing or inconsistent installed state still fails closed.
- The installer package metadata version may advance only as CI admission evidence for changed `packages/loom-installer/src/**` behavior; it must not imply npm publish or installer release restoration.

## Validation Contract

- `npm --prefix packages/loom-installer test`
- `npm --prefix packages/loom-installer run check:docs`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `git diff --check`
- `python3 tools/loom.py fact-chain --target . --item WI-1719 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1719 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json`

## Review Boundary

- Review must consume the current PR head, PR metadata readback, installer test results, suite evidence, and forbidden-surface diff.
- Re-run review if installer source/tests, WI-1719 carriers, PR metadata, or head SHA changes after the review record is written.
