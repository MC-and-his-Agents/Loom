# Current Status

## Derived Fact Chain View

- Item ID: WI-1883
- Goal: 精简宿主 AGENTS 执行入口指引，避免宿主 agent 先实现、门禁失败后再补 spec 的返工路径。
- Scope: Generated host AGENTS.md managed block, root-entry generator, example new-project fixture, contract tests, plugin payload metadata, and issue/PR carrier evidence for #1883. Excludes unrelated release mechanics except marking #1884 as the release follow-up.
- Execution Path: issue #1883 -> branch work/1883-host-agents-execution-guidance -> PR #1885 -> review/gate -> merge -> #1884 release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1883.md
- Review Entry: .loom/reviews/WI-1883.json
- Validation Entry: git diff --check; skills surface checks; adoption-host-metadata and aggregate CLI contract; demo fixture drift/generation/canonicalization; release surface/version/package checks; make npm-package-check; make loom-check
- Closing Condition: PR #1885 merged, #1883 closed, #1884 release path completed or explicitly handed off with release evidence.
- Current Checkpoint: review
- Current Stop: Implementation commit `d3743a42cf1c16dc393c7284c47efbd4e52c7b2a` is validated locally and PR #1885 is open; hosted `loom-pr-merge-gate` failed because WI-1883 carrier/review inputs were missing and is being repaired by this carrier sync.
- Next Step: Record current-head review for WI-1883, update PR metadata to the repaired head, rerun PR gate, merge, then continue #1884 release.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-02T11:17:46Z implementation validation passed at PR head `d3743a42cf1c16dc393c7284c47efbd4e52c7b2a`: `git diff --check`, `python3 tools/skills_surface.py check`, `python3 tools/skills_surface.py check --surface cache-artifacts`, `python3 tools/check_cli_contract.py --surface adoption-host-metadata`, `python3 tools/check_cli_contract.py --surface aggregate`, demo fixture drift/generation/canonicalization checks, `make loom-demo-new-project-check`, release surface/version/package checks, `make npm-package-check`, and full `make loom-check` all passed. PR #1885 metadata render/readback passed with body hash `c45461a82af5c428385af031fc359d237339907b52849921aeba7a39af57e805`. Hosted `loom-pr-merge-gate` run `28585813263` failed before this sync because fact-chain still pointed at WI-1876 and WI-1883 review was unavailable.
- Recovery Boundary: WI-1883 owns generated host AGENTS execution guidance, root-entry generator parity, fixture/test updates, plugin payload metadata, PR #1885 carrier evidence, and release handoff to #1884. It does not change unrelated release mechanics or reopen WI-1876/v0.26.2 closeout.
- Current Lane: implementation-pr-gate-repair

## Runtime Evidence

- Run Entry: 2026-07-02 WI-1883 work is active in `/Users/mc/dev/Loom` on branch `work/1883-host-agents-execution-guidance`.
- Logs Entry: Local validation output and hosted gate classification are retained in this Codex thread; PR #1885 body readback hash is `c45461a82af5c428385af031fc359d237339907b52849921aeba7a39af57e805`.
- Diagnostics Entry: Hosted `loom-pr-merge-gate` run `28585813263` failed before this carrier sync because PR metadata expected WI-1883 while repo fact-chain still selected WI-1876 and review entry was unavailable.
- Verification Entry: fact-chain now reads WI-1883; local implementation validation passed at `d3743a42cf1c16dc393c7284c47efbd4e52c7b2a` with the commands listed in `.loom/progress/WI-1883.md`.
- Lane Entry: implementation-pr-gate-repair

## Sources

- Static Truth: .loom/work-items/WI-1883.md
- Dynamic Truth: .loom/progress/WI-1883.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
