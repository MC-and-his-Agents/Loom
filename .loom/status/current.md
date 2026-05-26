# Current Status

## Derived Fact Chain View

- Item ID: WI-1027
- Goal: Define the GitHub profile mapping for delivery planning outputs so Loom can distinguish Phase, FR, Work Item, Project item, sub-issue, blocked-by/blocks, checklist, PR, and closeout carriers.
- Scope: #1027 GitHub Phase / FR / Work Item / Project mapping only; update the GitHub profile contract and synchronized reference surfaces, plus repo-local carriers. Do not implement GitHub API automation, task carrier contracts (#1017), skills routing (#1028), gate-chain behavior (#1019), or CLI automation (#1052).
- Execution Path: issue #1027 -> branch work/1027-github-planning-mapping -> worktree /Users/mc/dev/Loom.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1027.md
- Review Entry: .loom/reviews/WI-1027.json
- Validation Entry: git diff --check; rg -n "Phase|FR|Work Item|Project item|implementation PR|唯一默认执行入口" docs/adoption docs/methodology skills src .loom; rg -n "Project.*不替代|FR.*不直接|locator|provenance" docs/adoption docs/methodology skills src .loom; rg -n "Project Status|Todo|In Progress|Done|completed truth|closeout" docs/adoption docs/methodology skills src .loom; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1027 --write; python3 tools/skills_surface.py check; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1027 defines GitHub host mapping for Phase / FR / Work Item / Project / PR authority boundaries, locator/provenance, forbidden use, Project Status semantics, native parent/sub-issue and blocked-by/blocks synchronization, and closeout evidence consumption without implementing automation.
- Current Checkpoint: implementation
- Current Stop: GitHub mapping contract and synchronized reference surfaces drafted and locally validated.
- Next Step: Open PR, consume checks, then merge and close out #1027 if green.
- Blockers: None recorded.
- Latest Validation Summary: Passed: `git diff --check`; focused `rg` checks for Phase / FR / Work Item / Project / PR mapping, Project forbidden use, locator/provenance, Project Status, completed truth, and closeout; `python3 .loom/bin/loom_init.py verify --target .`; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1027 --write`; `python3 tools/skills_surface.py check`; `python3 tools/check_npm_package.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Recovery Boundary: #1027 owns GitHub Phase / FR / Work Item / Project / PR mapping only. Do not expand into GitHub API automation, #1028 skills routing, #1017 task carrier contracts, #1019 gate-chain behavior, or #1052 CLI automation.
- Current Lane: github-planning-mapping

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; rg -n "Phase|FR|Work Item|Project item|implementation PR|唯一默认执行入口" docs/adoption docs/methodology skills src .loom; rg -n "Project.*不替代|FR.*不直接|locator|provenance" docs/adoption docs/methodology skills src .loom; rg -n "Project Status|Todo|In Progress|Done|completed truth|closeout" docs/adoption docs/methodology skills src .loom; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1027 --write; python3 tools/skills_surface.py check; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1027.md
- Dynamic Truth: .loom/progress/WI-1027.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
