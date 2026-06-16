# WI-1296 Plan

## Implementation Steps

1. Confirm #1235/#1236/#1237 closeout and #1519 merge are consumed from GitHub and origin/main.
2. Select v0.14.1 and verify the remote tag, GitHub Release, and npm package are absent before merge.
3. Bump `VERSION`, `package.json`, and every generated `skills/loom-*/loom-package.json` `repo_version` surface to v0.14.1 / 0.14.1.
4. Record WI-1296 Work Item, progress, spec, evidence map, task carrier, build evidence, status, init-result, and shadow carriers for review and gate consumption.
5. Run local release/version/package/CLI/skills/suite/fact-chain/shadow validation, then author review for the current release PR head.
6. Create PR metadata, push branch, create/read back PR, wait for hosted checks and release-judgment, and merge only after controlled merge passes.
7. After merge, wait for the `loom-cli-release` push run on main, then verify v0.14.1 tag, GitHub Release, npm package, and installed/global CLI smoke.
8. Terminalize WI-1296 carriers, close issue #1296 as completed, then hand parent #1228 closeout to the final Round 9 parent step.

## Validation

- `git diff --check`
- `cat VERSION`
- `jq -r '.version' package.json`
- `find skills -name loom-package.json -maxdepth 4 -print | sort | xargs -I{} jq -r '.repo_version' {}`
- `git ls-remote --tags origin "refs/tags/v0.14.1" "refs/tags/v0.14.1^{}"`
- `gh release view v0.14.1 --repo MC-and-his-Agents/Loom --json tagName,name,publishedAt,targetCommitish,url`
- `npm view @mc-and-his-agents/loom@0.14.1 version time --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1296 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1296 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1296 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target .`
- PR metadata preflight/readback, hosted checks, release-judgment, pr-gate, controlled merge, post-merge release workflow, tag/GitHub Release/npm/global CLI smoke, and terminal closeout readback.

## Dependencies

- Hard dependency consumed: #1235 closeout PR #1506 merged as `703feadf46162d7937ede040a098a013093b2c39`.
- Hard dependency consumed: #1236 closeout PR #1517 merged as `47083d932490b76a49f97d9a0cb307134582282b`.
- Hard dependency consumed: #1237 implementation PR #1518 merged as `864e12ace9090ba38cf55d6456726d7d291d5aae`.
- Hard dependency consumed: #1237 closeout PR #1519 merged as `a840bfa2dab65fa46c254d1eae7f6069afcd8b84`.
- Parent dependency: #1228 remains open until #1296 terminal release evidence is consumed.

## Scope Guard

- Do not manually publish from the local machine, manually create tags, or manually create GitHub Releases.
- Do not alter release workflow semantics, npm package payload policy, installer legacy release line, runtime behavior, schema, parser, failure vocabulary, Round 10/11, Deferred roadmap, parent #1228 closeout before #1296 completion, or unrelated files.
