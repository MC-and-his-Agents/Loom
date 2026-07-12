#!/usr/bin/env python3
"""CLI-first Loom control-plane entry.

The command surface is intentionally broader than the implementation surface.
Commands that are not implemented in this phase fail closed with a structured
JSON block instead of silently falling back to legacy wrappers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

import build_distribution

try:
    import tomllib as _tomllib
except ModuleNotFoundError:
    _tomllib = None
    try:
        import tomli as _tomli
    except ModuleNotFoundError:
        _tomli = None
else:
    _tomli = None


class TomlDecodeError(ValueError):
    pass


def parse_toml_text(raw: str) -> dict[str, Any]:
    if _tomllib is not None:
        return _tomllib.loads(raw)
    if _tomli is not None:
        return _tomli.loads(raw)
    raise TomlDecodeError("TOML parsing requires Python 3.11+ tomllib or the tomli package")


REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_ROOT = REPO_ROOT / "tools"
VERSION_FILE = REPO_ROOT / "VERSION"
SKILLS_ROOT = REPO_ROOT / "skills"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json"
PLUGIN_SKILLS_ROOT = REPO_ROOT / "plugins" / "loom" / "skills"
SHARED_SCRIPTS_ROOT = SKILLS_ROOT / "shared" / "scripts"
SHARED_SCRIPT_CANDIDATES = (
    SHARED_SCRIPTS_ROOT,
    REPO_ROOT / "src" / "skills" / "shared" / "scripts",
    PLUGIN_SKILLS_ROOT / "shared" / "scripts",
)
for shared_scripts_root in reversed(SHARED_SCRIPT_CANDIDATES):
    if shared_scripts_root.is_dir() and str(shared_scripts_root) not in sys.path:
        sys.path.insert(0, str(shared_scripts_root))
from runtime_paths import global_runtime_path, is_global_runtime_locator
from authority_contract import parse_typed_locator, typed_locator
from failure_envelope import public_cli_failure_envelope
from github_host import github_lifecycle_subject_readback
from host_attestation import _artifact_id as host_attestation_artifact_id
from host_attestation import main as host_attestation_main
from host_attestation import readback as host_attestation_readback
from product_acceptance import main as product_acceptance_main

LOOM_BOOTSTRAP_START = "<!-- LOOM_BOOTSTRAP_START -->"
LOOM_BOOTSTRAP_END = "<!-- LOOM_BOOTSTRAP_END -->"
LOOM_BOOTSTRAP_BLOCK = f"""{LOOM_BOOTSTRAP_START}
## Loom Execution

本仓库使用 Loom 管理 Work Item、admission/spec、build、review、merge-ready 和 closeout。Loom 是执行控制面，不替代仓库自身业务事实源。

开始改文件前：

1. 先用 `loom route --target . --task "<request>" --json` 判断入口；接手已有事项时先用 `loom resume --target . --json`。
2. 一次只推进一个明确 Work Item；不要把无关修复、后续想法或新范围塞进同一 PR。
3. 命中 formal spec path 时，缺 `spec.md`、`plan.md` 或 `spec_review approved` 不得进入实现。
4. 按 Loom 返回的 `next_action` / `fallback_to` 执行；`block` 表示回退修前序事实，不表示绕过门禁。
5. 验证证据必须写清命令、结果、时间或 head sha；不要只把结论留在会话里。
6. 改了代码、PR body、review 输入或 carrier 后，重新确认 review/gate evidence 是否仍 fresh。
7. merge 后不等于完成；按 Loom closeout 同步 issue、PR、主干和事实载体状态。

环境或插件问题交给 `loom doctor --target . --json` 的输出处理。
{LOOM_BOOTSTRAP_END}
"""

OUTPUT_SCHEMA = "loom-cli-output/v1"
OUTPUT_ENVELOPE_SCHEMA = "loom-agent-output-envelope/v1"
OUTPUT_ARTIFACT_SCHEMA = "loom-output-artifact/v1"
DEFAULT_OUTPUT_ARTIFACT_DIR = Path(".loom/tmp/output-artifacts")
DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES = 16 * 1024
DEFAULT_AGENT_SAFE_SUMMARY_TARGET_BYTES = 4 * 1024
DEFAULT_ACTIONABLE_FINDINGS_LIMIT = 5
INSTALLED_STATE_SCHEMA = "loom-installed-state/v2"
DETECT_SCHEMA = "loom-installed-surface-detect/v1"
DOCTOR_SCHEMA = "loom-installed-surface-doctor/v1"
REPAIR_PLAN_SCHEMA = "loom-installed-surface-repair-plan/v1"
WORKSPACE_SCHEMA = "loom-workspace-control/v1"
HOST_OBJECT_SCHEMA = "loom-host-object-control/v1"
HOST_SCHEMA = "loom-host-orchestration/v1"
WORKSTATION_SCHEMA = "loom-workstation-registration/v1"
WORKSTATION_CONTROL_SCHEMA = "loom-workstation-control/v1"
WORKSTATION_REPOSITORIES_SCHEMA = "loom-workstation-repositories/v1"
WORKSTATION_CURRENT_SCHEMA = "loom-workstation-current/v1"
WORKSTATION_UPGRADE_PLAN_SCHEMA = "loom-workstation-upgrade-plan/v1"
GLOBAL_CACHE_MIGRATION_SCHEMA = "loom-global-cache-migration/v1"
SKILLS_SCHEMA = "loom-skills-surface/v1"
SCENARIO_SCHEMA = "loom-scenario-control/v1"
PROFILE_SCHEMA = "loom-governance-profile-control/v1"
GATE_SCHEMA = "loom-gate-control/v1"
DELIVERY_SCHEMA = "loom-delivery-control/v1"
RELEASE_READBACK_SCHEMA = "loom-release-readback/v1"
RUNTIME_UPGRADE_SCHEMA = "loom-runtime-upgrade/v1"
CLOSEOUT_PR_ROLES = (
    "implementation_pr",
    "release_pr",
    "carrier_sync_pr",
    "final_closeout_pr",
)

RUNTIME_PROVIDER_GLOBAL_CLI = "global-cli"
RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER = "repo-local-wrapper"
GLOBAL_CLI_PROVIDER_LAYER = "global-cli-runtime-provider"
GLOBAL_CLI_REQUIRED_COMMANDS = [
    "installed-state validate",
    "detect",
    "doctor",
    "verify",
    "fact-chain",
    "status",
    "shadow-parity",
    "story",
    "workstation current",
]


COMMANDS: list[dict[str, Any]] = [
    {
        "command": "version",
        "domain": "core",
        "status": "implemented",
        "json": True,
        "summary": "Show Loom CLI and distribution version context.",
    },
    {
        "command": "help",
        "domain": "core",
        "status": "implemented",
        "json": True,
        "summary": "Show task-oriented guidance plus the frozen CLI command matrix.",
    },
    {
        "command": "acceptance validate",
        "domain": "acceptance",
        "status": "implemented",
        "json": True,
        "summary": "Structurally validate a product acceptance record without authorizing a trusted passed verdict.",
    },
    {
        "command": "acceptance resolve",
        "domain": "acceptance",
        "status": "implemented",
        "json": True,
        "summary": "Resolve a trusted product acceptance verdict from authenticated GitHub host facts.",
    },
    {
        "command": "attestation readback",
        "domain": "host-attestation",
        "status": "implemented",
        "json": True,
        "summary": "Read an approved PR review, semantic tree, and workflow artifact from GitHub only.",
    },
    {
        "command": "attestation closeout",
        "domain": "host-attestation",
        "status": "implemented",
        "json": True,
        "summary": "Read a host-native Work Item closeout without creating repository carriers.",
    },
    {
        "command": "installed-state show",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Read the target repository loom-installed-state/v2 object.",
    },
    {
        "command": "installed-state validate",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Validate installed-state schema, layers, graph, runtime-provider declarations, and fail-closed metadata.",
    },
    {
        "command": "installed-state export",
        "domain": "installation",
        "status": "implemented",
        "json": True,
        "summary": "Export installed-state plus its installation graph for upgrade consumers.",
    },
    {
        "command": "detect",
        "domain": "diagnostics",
        "status": "implemented",
        "json": True,
        "summary": "Detect installed Loom surfaces, legacy layouts, symlinks, and mixed installations.",
    },
    {
        "command": "doctor",
        "domain": "diagnostics",
        "status": "implemented",
        "json": True,
        "summary": "Diagnose metadata-only adoption, global CLI provider, user-level plugin provider, and unsupported legacy residue.",
    },
    {
        "command": "repair plan",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Emit a non-mutating repair plan for legacy, drifted, runtime-provider, or host-complete active carrier surfaces; it does not mutate host state.",
    },
    {
        "command": "repair apply",
        "domain": "repair",
        "status": "implemented",
        "json": True,
        "summary": "Apply explicit safe repo carrier closeout repairs for host-complete active carriers; fail closed for installed-surface repair actions and do not close host objects.",
    },
    {
        "command": "install",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Install metadata-only repository adoption; does not write runtime, plugin, or skills payload into the repository.",
    },
    {
        "command": "upgrade-plan",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Plan non-mutating upgrades across installed-state, legacy surfaces, and runtime-provider carriers.",
    },
    {
        "command": "runtime-upgrade status",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Inspect a single repository Loom runtime workflow pin and current upgrade context.",
    },
    {
        "command": "runtime-upgrade prepare",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Plan or explicitly apply a single repository Loom runtime workflow pin update with maintenance PR guidance.",
    },
    {
        "command": "runtime-upgrade check",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Fail-closed readback for single repository Loom runtime upgrade maintenance PR readiness.",
    },
    {
        "command": "runtime-upgrade pr",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Render, create, update, and read back a single repository Loom runtime upgrade maintenance PR.",
    },
    {
        "command": "runtime-upgrade closeout",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Read merged runtime upgrade PR/issue facts and orchestrate carrier-only closeout sync.",
    },
    {
        "command": "migrate-global-cache plan",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Plan explicit migration of legacy repo-local Loom cache/residue to workstation global cache.",
    },
    {
        "command": "migrate-global-cache apply",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Move ignored repo-local Loom runtime/tmp cache to workstation global cache and register the repository.",
    },
    {"command": "upgrade", "domain": "delivery", "status": "implemented", "json": True},
    {"command": "rollback", "domain": "delivery", "status": "implemented", "json": True},
    {
        "command": "verify",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Verify the same readiness boundary as doctor for metadata-only adoption and global providers.",
    },
    {"command": "init", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "adopt", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "adopt adversarial-test", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "route", "domain": "scenario", "status": "implemented", "json": True},
    {
        "command": "carrier closeout-sync",
        "domain": "harness",
        "status": "compatibility",
        "json": True,
        "summary": "Retired carrier backend; available only through an explicit reinforced, expiring compatibility exception.",
    },
    {"command": "status", "domain": "harness", "status": "implemented", "json": True},
    {"command": "fact-chain", "domain": "harness", "status": "implemented", "json": True},
    {
        "command": "shadow-parity",
        "domain": "harness",
        "status": "implemented",
        "json": True,
        "summary": "Compare Loom and repo-native parity surfaces through the global CLI agent-safe output boundary.",
    },
    {"command": "profile status", "domain": "profile", "status": "implemented", "json": True},
    {"command": "profile upgrade-plan", "domain": "profile", "status": "implemented", "json": True},
    {"command": "profile upgrade", "domain": "profile", "status": "implemented", "json": True},
    {
        "command": "profile light-migration-plan",
        "domain": "profile",
        "status": "implemented",
        "json": True,
        "summary": "Read the light-profile carrier invariant and emit a non-mutating profile-migration plan.",
    },
    {
        "command": "profile light-migration-reconcile",
        "domain": "profile",
        "status": "implemented",
        "json": True,
        "summary": "Reconcile light-profile GitHub required checks and verify the migrated main tree through host readback.",
    },
    {"command": "governance-profile status", "domain": "profile", "status": "implemented", "json": True},
    {"command": "governance-profile upgrade-plan", "domain": "profile", "status": "implemented", "json": True},
    {"command": "governance-profile upgrade", "domain": "profile", "status": "implemented", "json": True},
    {"command": "governance-profile binding", "domain": "profile", "status": "implemented", "json": True},
    {"command": "story", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "spec", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "plan", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "build", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "pre-review", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "spec-review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "review", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "merge-ready", "domain": "scenario", "status": "delegated", "json": True},
    {
        "command": "closeout",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Check closeout readiness; bare `loom closeout` remains a compatibility alias for closeout check.",
    },
    {
        "command": "closeout status",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Read closeout metadata, host reconciliation, carrier terminal state, and cleanup status with a short diagnostic.",
    },
    {
        "command": "closeout sync",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Plan or apply host reconciliation, consume host closeout attestation, and report local cleanup without repository mutations.",
    },
    {
        "command": "closeout run",
        "domain": "host-control",
        "status": "compatibility",
        "json": True,
        "summary": "Plan or apply a single post-merge closeout run across host reconciliation, terminal carrier metadata, recovery status, shadow refresh, and final closeout check.",
    },
    {
        "command": "closeout batch",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Plan or apply host-only batch issue closeout comments for a merged implementation PR without writing repo carrier state or creating a closeout PR.",
    },
    {
        "command": "closeout queue status",
        "domain": "scenario",
        "status": "implemented",
        "json": True,
        "summary": "Read retained post-merge closeout residue queue status and suggest the next read-only command.",
    },
    {"command": "resume", "domain": "scenario", "status": "delegated", "json": True},
    {"command": "handoff", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "retire", "domain": "scenario", "status": "implemented", "json": True},
    {"command": "checkpoint admission", "domain": "gate", "status": "implemented", "json": True},
    {"command": "checkpoint build", "domain": "gate", "status": "implemented", "json": True},
    {"command": "checkpoint merge", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate pre-review", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate spec-review", "domain": "gate", "status": "implemented", "json": True},
    {"command": "gate review", "domain": "gate", "status": "implemented", "json": True},
    {
        "command": "gate pr",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Alias for pr-gate check; proves the current PR head has authored Loom semantic review approval.",
    },
    {
        "command": "gate merge",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Alias for controlled-merge check; reads host merge readiness without executing a merge.",
    },
    {
        "command": "gate freeze check",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Read-only validation of hosted loom-gate-freeze/v1 or closeout loom-closeout-freeze/v1 admission snapshots.",
    },
    {
        "command": "gate freeze write",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Write a repo-local hosted or closeout freeze snapshot under .loom/runtime/gate-freeze without mutating host truth.",
    },
    {
        "command": "gate closeout",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Run the closeout gate over host readback, release/no-release evidence, and repo carrier consistency without performing host writes.",
    },
    {
        "command": "gate repair-pr",
        "domain": "gate",
        "status": "implemented",
        "json": True,
        "summary": "Record and validate audited repair PR evidence under .loom/companion without mutating GitHub rulesets or replacing semantic review.",
    },
    {
        "command": "release readback",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Read target package surface, tag, GitHub Release, npm, workflow, and carrier terminal state into a publish/missing/drifted/blocked verdict without publishing.",
    },
    {
        "command": "release resume",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Classify release recovery state from readback evidence without triggering publish or closeout.",
    },
    {
        "command": "release closeout-sync",
        "domain": "delivery",
        "status": "compatibility",
        "json": True,
        "summary": "Retired release carrier backend; stable release aftercare ends at host readback.",
    },
    {"command": "workspace create", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace locate", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "workspace check", "domain": "host-control", "status": "implemented", "json": True},
    {
        "command": "workspace audit",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Read active carrier drift before starting a Work Item; does not mutate host state or repo carriers.",
    },
    {
        "command": "workspace retire",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Emit local-only worksite retirement evidence; does not close host objects or write versioned terminal carriers.",
    },
    {"command": "issue inspect", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "issue bind", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "issue reconcile", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "project status", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "project reconcile", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr inspect", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr metadata-render", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr metadata-readback", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr metadata-update", "domain": "host-control", "status": "implemented", "json": True},
    {"command": "pr metadata-preflight", "domain": "host-control", "status": "implemented", "json": True},
    {
        "command": "pr-intent prepare",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Prepare the minimal carrier set for a declared PR intent profile without replacing review or gate truth.",
    },
    {
        "command": "pr-intent check",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Check suite, metadata, head binding, scope proof, and carrier-set consistency for a declared PR intent profile.",
    },
    {
        "command": "docs-pr prepare",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Shortcut for `pr-intent prepare --intent docs-governance-only`.",
    },
    {
        "command": "docs-pr check",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Shortcut for `pr-intent check --intent docs-governance-only`.",
    },
    {
        "command": "pr gate",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Check `loom pr gate <pr> --head-sha <sha> --work-item <WI> --json` before merge; CI/checks cannot replace the authored review record.",
    },
    {
        "command": "merge check",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Read-only controlled merge preflight; consumes PR gate, required checks, triggered checks, host enforcement, and mergeability.",
    },
    {
        "command": "merge run",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Execute host merge only with `--apply` after `merge check` passes for the same PR head and Work Item.",
    },
    {
        "command": "ship",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Dry-run the delivery path across PR metadata, PR gate, controlled merge, changed-path validation profile, and closeout policy.",
    },
    {
        "command": "ship status",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Read the ship control-plane status across host issue, release, checkout, and carrier surfaces without mutating state.",
    },
    {
        "command": "ship preflight",
        "domain": "delivery",
        "status": "implemented",
        "json": True,
        "summary": "Alias for ship status; emits the short blocked/fixed/next_action diagnostic before delivery work starts.",
    },
    {
        "command": "reconcile",
        "domain": "host-control",
        "status": "implemented",
        "json": True,
        "summary": "Read or align host closeout control-plane state; repo carrier closeout-sync remains a separate versioned-carrier write.",
    },
    {"command": "host list", "domain": "host", "status": "implemented", "json": True},
    {"command": "host doctor", "domain": "host", "status": "implemented", "json": True},
    {"command": "host install", "domain": "host", "status": "implemented", "json": True},
    {"command": "host verify", "domain": "host", "status": "implemented", "json": True},
    {
        "command": "host register",
        "domain": "host",
        "status": "implemented",
        "json": True,
        "summary": "Inspect or explicitly register a Codex Loom plugin provider with the local workstation.",
    },
    {"command": "host upgrade", "domain": "host", "status": "implemented", "json": True},
    {"command": "host remove", "domain": "host", "status": "implemented", "json": True},
    {
        "command": "workstation register",
        "domain": "workstation",
        "status": "implemented",
        "json": True,
        "summary": "Register the target repository in ~/.loom/repositories.json without mutating the repository.",
    },
    {
        "command": "workstation list",
        "domain": "workstation",
        "status": "implemented",
        "json": True,
        "summary": "List machine-local Loom repository registry entries.",
    },
    {
        "command": "workstation unregister",
        "domain": "workstation",
        "status": "implemented",
        "json": True,
        "summary": "Remove or opt out a target repository entry from ~/.loom/repositories.json.",
    },
    {
        "command": "workstation upgrade",
        "domain": "workstation",
        "status": "implemented",
        "json": True,
        "summary": "Plan a machine-level Loom CLI/plugin refresh plus per-repository adoption classifications without mutating state.",
    },
    {
        "command": "workstation current",
        "domain": "workstation",
        "status": "implemented",
        "json": True,
        "summary": "Read or update ~/.loom/repos/<repo-id>/current.json without mutating the repository.",
    },
    {
        "command": "skills list",
        "domain": "skills",
        "status": "implemented",
        "json": True,
        "summary": "List the Loom source skills registry used to generate the Codex plugin payload.",
    },
    {
        "command": "skills generate",
        "domain": "skills",
        "status": "implemented",
        "json": True,
        "summary": "Regenerate the Loom source repository skills mirror and Codex plugin payload; source repo only.",
    },
    {
        "command": "skills check",
        "domain": "skills",
        "status": "implemented",
        "json": True,
        "summary": "Verify source plugin payload parity or metadata-only target repository adoption.",
    },
    {"command": "skills doctor", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills package", "domain": "skills", "status": "implemented", "json": True},
    {"command": "skills release-check", "domain": "skills", "status": "implemented", "json": True},
    {
        "command": "suite inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect suite path decision and repo-relative artifact inventory.",
    },
    {
        "command": "suite scaffold",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Plan or explicitly apply repo-local minimal or full spec suite scaffold writes.",
    },
    {
        "command": "suite validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate the current suite path decision and core readiness envelope without mutating files.",
    },
    {
        "command": "suite evidence inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect evidence-map locator, rows, freshness, and repo-local evidence bindings.",
    },
    {
        "command": "suite evidence scaffold",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Plan or explicitly apply repo-local evidence-map scaffold writes without marking evidence present.",
    },
    {
        "command": "suite evidence validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate behavior, test, and fresh verification evidence-map freshness without mutating files.",
    },
    {
        "command": "suite carrier inspect",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Inspect task-carrier locators, normalized status, relationships, and Work Item backlinks.",
    },
    {
        "command": "suite carrier validate",
        "domain": "suite",
        "status": "implemented",
        "json": True,
        "summary": "Validate task-carrier locator/status/backlink consistency without promoting carrier truth.",
    },
]

HELP_TASK_ROUTES: list[dict[str, Any]] = [
    {
        "task": "resume",
        "summary": "Take over the current Work Item from repository facts.",
        "first_command": "loom resume --target <repo> --item <WI> --json",
        "next_step": "Continue with build, review, merge-ready, or closeout based on the resume checkpoint.",
    },
    {
        "task": "prepare-pr",
        "summary": "Prepare or verify a known PR intent carrier set before review/gate.",
        "first_command": "loom pr-intent prepare --intent <intent> --target <repo> --item <WI> --apply --json",
        "next_step": "Run pr-intent check after the PR body metadata is updated and read back.",
    },
    {
        "task": "review",
        "summary": "Consume the current semantic review from GitHub host attestation.",
        "first_command": "loom attestation readback --repo <owner/repo> --pr <n> --work-item <n> --artifact-input <file> --json",
        "next_step": "Only continue when GitHub binds the review, semantic tree, workflow run, artifact digest, and current PR head.",
    },
    {
        "task": "merge-ready",
        "summary": "Check final readiness before host merge.",
        "first_command": "loom merge-ready --target <repo> --item <WI> --json",
        "next_step": "Run pr gate and merge check against the same PR head.",
    },
    {
        "task": "post-merge-closeout",
        "summary": "Consume merged PR and Work Item completion from GitHub without repository aftercare carriers.",
        "first_command": "loom attestation closeout --repo <owner/repo> --pr <merged-pr> --work-item <issue> --artifact-input <file> --json",
        "next_step": "A passing host readback is terminal; retire only the local workspace and do not create a closeout PR.",
    },
    {
        "task": "release",
        "summary": "Read back release surfaces without publishing or republishing.",
        "first_command": "loom release readback --target <repo> --version <version> --commit <sha> --json",
        "next_step": "Publish only through the repository release workflow; a passing host readback is terminal and creates no closeout PR.",
    },
    {
        "task": "release-closeout",
        "summary": "Read back published release host facts without repository aftercare carriers.",
        "first_command": "loom release readback --target <repo> --version <version> --commit <sha> --json",
        "next_step": "Consume the readback in GitHub closeout; do not create a release closeout PR.",
    },
    {
        "task": "runtime-upgrade",
        "summary": "Update one repository's Loom workflow pin through a maintenance PR.",
        "first_command": "loom runtime-upgrade status --target <repo> --json",
        "next_step": "Use prepare/check/closeout; do not mix repo workflow mutation with user plugin cache mutation.",
    },
    {
        "task": "host-plugin-doctor",
        "summary": "Diagnose local Codex plugin/cache freshness.",
        "first_command": "loom host doctor --host codex --scope user --json",
        "next_step": "Run host install/register with --apply only when refreshing the user workstation surface is intended.",
    },
    {
        "task": "workstation-registry",
        "summary": "List or update the machine-local Loom repository registry.",
        "first_command": "loom workstation list --json",
        "next_step": "Use register/unregister to update ~/.loom/repositories.json; each repo still owns adoption truth.",
    },
]

HELP_COMMAND_TIERS: dict[str, list[str]] = {
    "common_path": [
        "resume",
        "pr-intent prepare",
        "pr-intent check",
        "review",
        "merge-ready",
        "pr gate",
        "merge check",
        "merge run",
        "attestation readback",
        "attestation closeout",
        "closeout sync",
    ],
    "maintenance_path": [
        "runtime-upgrade status",
        "runtime-upgrade prepare",
        "runtime-upgrade pr",
        "runtime-upgrade check",
        "runtime-upgrade closeout",
        "release readback",
        "host doctor",
        "workstation list",
    ],
    "advanced_debug_path": [
        "carrier closeout-sync",
        "closeout run",
        "release closeout-sync",
        "pr metadata-render",
        "pr metadata-readback",
        "pr metadata-update",
        "pr metadata-preflight",
        "suite validate",
        "suite evidence validate",
        "suite carrier validate",
    ],
}

COMMAND_INDEX = {entry["command"]: entry for entry in COMMANDS}
IMPLEMENTED_SUITE_COMMANDS = tuple(
    entry["command"]
    for entry in COMMANDS
    if entry.get("domain") == "suite" and entry.get("status") == "implemented"
)
SUITE_SUPPORT_MARKERS = {
    "suite-command-surface",
    "suite-commands",
    "loom-suite-commands",
    "full-spec-suite-cli",
    "full-spec-suite-cli-surface",
}

COMMAND_ROUTES: dict[str, tuple[str, tuple[str, ...]]] = {
    "acceptance": ("product_acceptance.py", ()),
    "init": ("loom_init.py", ()),
    "adopt": ("loom_flow.py", ("adopt",)),
    "route": ("loom_init.py", ("route",)),
    "flow": ("loom_flow.py", ()),
    "resume": ("loom_flow.py", ("flow", "resume")),
    "merge-ready": ("loom_flow.py", ("flow", "merge-ready")),
    "spec-review": ("loom_flow.py", ("flow", "spec-review")),
    "review": ("loom_flow.py", ("review",)),
    "check": ("loom_check.py", ()),
    "status": ("loom_status.py", ()),
    "fact-chain": ("loom_init.py", ("fact-chain",)),
}

STATE_FILENAMES = (
    ".loom/installed-state.json",
    ".loom/installed-state.v2.json",
    ".loom/installed-state/installed-state.json",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return read_json(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_readback_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def release_normalize_tag(version: str) -> str:
    return version if version.startswith("v") else f"v{version}"


def release_npm_version(version: str) -> str:
    return version[1:] if version.startswith("v") else version


def release_package_context(target: Path, *, version: str | None, package_name: str | None) -> dict[str, Any]:
    package_path = target / "package.json"
    package_data: dict[str, Any] = {}
    if package_path.exists():
        try:
            loaded = json.loads(package_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                package_data = loaded
        except (OSError, json.JSONDecodeError):
            package_data = {}
    resolved_version = version
    if not resolved_version and (target / "VERSION").exists():
        resolved_version = (target / "VERSION").read_text(encoding="utf-8").strip()
    if not resolved_version and isinstance(package_data.get("version"), str):
        resolved_version = release_normalize_tag(package_data["version"])
    if not resolved_version:
        resolved_version = "unknown"
    resolved_package = package_name or package_data.get("name") or "@mc-and-his-agents/loom"
    return {
        "version": resolved_version,
        "tag": release_normalize_tag(resolved_version),
        "npm_version": release_npm_version(resolved_version),
        "npm_package": resolved_package,
        "package_json_version": package_data.get("version"),
    }


def infer_github_repo(target: Path) -> str | None:
    completed = run_readback_command(["git", "remote", "get-url", "origin"], cwd=target)
    if completed.returncode != 0:
        return None
    remote = completed.stdout.strip()
    patterns = (
        re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$"),
        re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$"),
    )
    for pattern in patterns:
        match = pattern.search(remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def release_target_commit(target: Path, explicit_commit: str | None) -> str | None:
    if explicit_commit:
        return explicit_commit
    completed = run_readback_command(["git", "rev-parse", "HEAD"], cwd=target)
    if completed.returncode == 0:
        return completed.stdout.strip()
    return None


def release_tag_readback(target: Path, *, tag: str, target_commit: str | None) -> dict[str, Any]:
    completed = run_readback_command(["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], cwd=target)
    if completed.returncode != 0:
        return {
            "kind": "git_tag",
            "tag": tag,
            "exists": False,
            "source": f"git rev-parse -q --verify refs/tags/{tag}",
        }
    commit = run_readback_command(["git", "rev-list", "-n", "1", tag], cwd=target)
    resolved_commit = commit.stdout.strip() if commit.returncode == 0 else None
    return {
        "kind": "git_tag",
        "tag": tag,
        "exists": True,
        "object": completed.stdout.strip(),
        "commit": resolved_commit,
        "target_commit": target_commit,
        "matches_target_commit": bool(target_commit and resolved_commit == target_commit),
        "source": f"git rev-list -n 1 {tag}",
    }


def github_release_readback(target: Path, *, repo: str | None, tag: str) -> dict[str, Any]:
    if not repo:
        return {
            "kind": "github_release",
            "tag": tag,
            "exists": None,
            "read_error": "missing GitHub repo locator",
            "failure_kind": "host_api_unreadable",
        }
    completed = run_readback_command(
        [
            "gh",
            "release",
            "view",
            tag,
            "--repo",
            repo,
            "--json",
            "tagName,name,url,isDraft,isPrerelease,createdAt,publishedAt,targetCommitish",
        ],
        cwd=target,
    )
    if completed.returncode != 0:
        error = completed.stderr.strip()
        lowered = error.lower()
        if "not found" in lowered or "404" in lowered:
            return {
                "kind": "github_release",
                "tag": tag,
                "repo": repo,
                "exists": False,
                "source": f"gh release view {tag} --repo {repo}",
            }
        return {
            "kind": "github_release",
            "tag": tag,
            "repo": repo,
            "exists": None,
            "read_error": error or "gh release view failed",
            "failure_kind": "host_api_unreadable",
            "source": f"gh release view {tag} --repo {repo}",
        }
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "kind": "github_release",
            "tag": tag,
            "repo": repo,
            "exists": None,
            "read_error": "gh release view returned non-JSON output",
            "failure_kind": "host_api_unreadable",
        }
    payload.update({"kind": "github_release", "repo": repo, "exists": True})
    return payload


def npm_package_readback(target: Path, *, package_name: str, npm_version: str) -> dict[str, Any]:
    package_spec = f"{package_name}@{npm_version}"
    completed = run_readback_command(["npm", "view", package_spec, "version", "dist-tags", "--json"], cwd=target)
    if completed.returncode != 0:
        error = completed.stderr.strip()
        lowered = error.lower()
        if "e404" in lowered or "404 not found" in lowered or "is not in this registry" in lowered:
            latest = run_readback_command(["npm", "view", package_name, "version", "--json"], cwd=target)
            latest_version = None
            if latest.returncode == 0:
                try:
                    latest_version = json.loads(latest.stdout)
                except json.JSONDecodeError:
                    latest_version = latest.stdout.strip().strip('"') or None
            return {
                "kind": "npm_package",
                "package": package_name,
                "version": npm_version,
                "version_exists": False,
                "latest": latest_version,
                "source": f"npm view {package_spec} version dist-tags --json",
            }
        return {
            "kind": "npm_package",
            "package": package_name,
            "version": npm_version,
            "version_exists": None,
            "read_error": error or "npm view failed",
            "failure_kind": "host_api_unreadable",
            "source": f"npm view {package_spec} version dist-tags --json",
        }
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "kind": "npm_package",
            "package": package_name,
            "version": npm_version,
            "version_exists": None,
            "read_error": "npm view returned non-JSON output",
            "failure_kind": "host_api_unreadable",
        }
    if isinstance(payload, dict):
        observed_version = payload.get("version")
        dist_tags = payload.get("dist-tags", {})
    else:
        observed_version = payload
        dist_tags = {}
    return {
        "kind": "npm_package",
        "package": package_name,
        "version": npm_version,
        "observed_version": observed_version,
        "version_exists": observed_version == npm_version,
        "dist_tags": dist_tags if isinstance(dist_tags, dict) else {},
        "source": f"npm view {package_spec} version dist-tags --json",
    }


def release_package_surface_readback(target: Path, *, context: dict[str, Any]) -> dict[str, Any]:
    version_path = target / "VERSION"
    package_path = target / "package.json"
    version_text = None
    package_name = None
    package_version = None
    errors: list[str] = []
    if version_path.exists():
        try:
            version_text = version_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            errors.append(f"VERSION unreadable: {exc}")
    else:
        errors.append("VERSION missing")
    if package_path.exists():
        try:
            package_data = json.loads(package_path.read_text(encoding="utf-8"))
            if isinstance(package_data, dict):
                package_name = package_data.get("name")
                package_version = package_data.get("version")
            else:
                errors.append("package.json is not an object")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"package.json unreadable: {exc}")
    else:
        errors.append("package.json missing")
    expected_tag = context.get("tag")
    expected_npm_version = context.get("npm_version")
    expected_package = context.get("npm_package")
    version_matches = version_text == expected_tag
    package_version_matches = package_version == expected_npm_version
    package_name_matches = package_name == expected_package
    gaps: list[str] = []
    if not version_matches:
        gaps.append("version_file_mismatch")
    if not package_version_matches:
        gaps.append("package_json_version_mismatch")
    if not package_name_matches:
        gaps.append("package_name_mismatch")
    return {
        "kind": "package_surface",
        "exists": package_path.exists() and version_path.exists(),
        "version_file": version_text,
        "package_json_name": package_name,
        "package_json_version": package_version,
        "expected_tag": expected_tag,
        "expected_npm_version": expected_npm_version,
        "expected_package": expected_package,
        "result": "pass" if not errors and not gaps else "block",
        "gaps": gaps,
        "errors": errors,
        "source": "VERSION + package.json",
    }


def release_carrier_status_readback(target: Path) -> dict[str, Any]:
    status = ship_status_surface(target)
    return {
        "kind": "carrier_status",
        "path": status.get("path"),
        "state": status.get("state"),
        "current_checkpoint": status.get("current_checkpoint"),
        "current_stop": status.get("current_stop"),
        "next_step": status.get("next_step"),
        "blockers": status.get("blockers"),
    }


def workflow_run_readback(target: Path, *, repo: str | None, workflow: str, target_commit: str | None) -> dict[str, Any]:
    if not repo:
        return {
            "kind": "workflow_run",
            "workflow": workflow,
            "exists": None,
            "read_error": "missing GitHub repo locator",
            "failure_kind": "host_api_unreadable",
        }
    completed = run_readback_command(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            workflow,
            "--limit",
            "20",
            "--json",
            "databaseId,displayTitle,event,headSha,headBranch,status,conclusion,createdAt,updatedAt,url",
        ],
        cwd=target,
    )
    if completed.returncode != 0:
        return {
            "kind": "workflow_run",
            "workflow": workflow,
            "repo": repo,
            "exists": None,
            "read_error": completed.stderr.strip() or "gh run list failed",
            "failure_kind": "host_api_unreadable",
            "source": f"gh run list --repo {repo} --workflow {workflow}",
        }
    try:
        runs = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "kind": "workflow_run",
            "workflow": workflow,
            "repo": repo,
            "exists": None,
            "read_error": "gh run list returned non-JSON output",
            "failure_kind": "host_api_unreadable",
        }
    if not isinstance(runs, list):
        runs = []
    matching = [run for run in runs if isinstance(run, dict) and target_commit and run.get("headSha") == target_commit]
    selected = matching[0] if matching else (runs[0] if runs else None)
    return {
        "kind": "workflow_run",
        "workflow": workflow,
        "repo": repo,
        "exists": bool(selected),
        "target_commit": target_commit,
        "selected": selected,
        "matching_target_commit_count": len(matching),
        "source": f"gh run list --repo {repo} --workflow {workflow}",
    }


def release_read_errors(readbacks: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for name, readback in readbacks.items():
        if isinstance(readback, dict) and readback.get("read_error"):
            errors.append(
                {
                    "surface": name,
                    "failure_kind": readback.get("failure_kind") or "host_api_unreadable",
                    "summary": readback.get("read_error"),
                    "source": readback.get("source"),
                }
            )
    return errors


def classify_release_readback(*, release_judgment: str, readbacks: dict[str, Any]) -> dict[str, Any]:
    if release_judgment == "no_release":
        return {
            "verdict": "no_release",
            "classification": "no_release",
            "reason": "release judgment declares no release required",
            "gaps": [],
            "resume_action": "record no-release rationale evidence; do not publish",
            "next_action": "record no-release rationale evidence; do not publish",
        }

    tag = readbacks.get("tag", {})
    release = readbacks.get("github_release", {})
    npm = readbacks.get("npm_package", {})
    workflow = readbacks.get("workflow_run", {})
    package_surface = readbacks.get("package_surface", {})
    merge_fallback = readbacks.get("merge_fallback", {})
    tag_exists = tag.get("exists") is True
    tag_matches = tag.get("matches_target_commit") is True
    release_exists = release.get("exists") is True
    npm_exists = npm.get("version_exists") is True
    npm_latest = npm.get("dist_tags", {}).get("latest") if isinstance(npm.get("dist_tags"), dict) else npm.get("latest")
    npm_latest_matches = not npm_exists or npm_latest in (None, npm.get("version"))
    package_surface_pass = not isinstance(package_surface, dict) or package_surface.get("result") in (None, "pass")
    workflow_selected = workflow.get("selected") if isinstance(workflow.get("selected"), dict) else None
    workflow_target_commit = workflow.get("target_commit")
    workflow_matches_target = (
        workflow_selected is not None
        and (
            not workflow_target_commit
            or workflow.get("matching_target_commit_count", 0) > 0
            or workflow_selected.get("headSha") == workflow_target_commit
        )
    )
    workflow_success = (
        workflow.get("exists") is True
        and workflow_selected is not None
        and workflow_matches_target
        and workflow_selected.get("status") == "completed"
        and workflow_selected.get("conclusion") == "success"
    )

    present_count = sum(1 for present in (tag_exists, release_exists, npm_exists) if present)
    gaps: list[str] = []
    if not tag_exists:
        gaps.append("tag_missing")
    elif not tag_matches:
        gaps.append("tag_target_commit_mismatch")
    if not release_exists:
        gaps.append("github_release_missing")
    if not npm_exists:
        gaps.append("npm_version_missing")
    if not workflow.get("exists"):
        gaps.append("workflow_run_missing")
    elif not workflow_matches_target:
        gaps.append("workflow_run_target_commit_missing")
    elif not workflow_success:
        gaps.append("workflow_run_not_success")
    if not npm_latest_matches:
        gaps.append("npm_latest_dist_tag_mismatch")
    if not package_surface_pass and isinstance(package_surface, dict):
        gaps.extend(str(gap) for gap in package_surface.get("gaps", []) if gap)
    if isinstance(merge_fallback, dict) and merge_fallback.get("main_worktree_busy"):
        same_head = merge_fallback.get("same_head_sha") is True
        gate_passed = merge_fallback.get("gate_passed") is True
        action = merge_fallback.get("host_api_action") or (
            "use host merge API for the same head SHA after gate readback" if same_head and gate_passed else "free the main worktree, then rerun controlled merge"
        )
        return {
            "verdict": "blocked",
            "classification": "blocked",
            "reason": "main worktree is busy during controlled merge readback",
            "gaps": ["main_worktree_busy"],
            "resume_action": action,
            "next_action": action,
        }

    if not package_surface_pass:
        return {
            "verdict": "blocked",
            "classification": "blocked",
            "reason": "local package release surface does not match the requested release target",
            "gaps": gaps,
            "resume_action": "align VERSION and package.json with the release target before publishing",
            "next_action": "align VERSION and package.json with the release target before publishing",
        }

    if present_count == 0:
        return {
            "verdict": "missing",
            "classification": "missing",
            "legacy_classification": "unpublished",
            "reason": "release-required readback found no tag, GitHub Release, or npm version",
            "gaps": gaps,
            "resume_action": "publish path is still unoccupied; use the release workflow only after the release intent is authorized",
            "next_action": "publish path is still unoccupied; use the release workflow only after the release intent is authorized",
        }
    if tag_exists and tag_matches and release_exists and npm_exists and workflow_success:
        return {
            "verdict": "published",
            "classification": "published",
            "reason": "tag, GitHub Release, npm package, and workflow run read back consistently",
            "gaps": [],
            "resume_action": "consume release closeout evidence; do not republish",
            "next_action": "consume release closeout evidence; do not republish",
        }
    if "workflow_run_not_success" in gaps:
        return {
            "verdict": "blocked",
            "classification": "blocked",
            "reason": "release workflow run exists but did not complete successfully",
            "gaps": gaps,
            "resume_action": "inspect the failed release workflow before repairing or rerunning publication",
            "next_action": "inspect the failed release workflow before repairing or rerunning publication",
        }
    drift_gaps = {"tag_target_commit_mismatch", "workflow_run_target_commit_missing", "npm_latest_dist_tag_mismatch"}
    if any(gap in drift_gaps for gap in gaps):
        return {
            "verdict": "drifted",
            "classification": "drifted",
            "legacy_classification": "partial_published",
            "reason": "release evidence exists but at least one artifact is bound to a different target",
            "gaps": gaps,
            "resume_action": "repair release drift without overwriting existing tag, release, or npm version",
            "next_action": "repair release drift without overwriting existing tag, release, or npm version",
        }
    return {
        "verdict": "missing",
        "classification": "missing",
        "legacy_classification": "partial_published",
        "reason": "at least one release artifact exists but the release evidence set is incomplete or mismatched",
        "gaps": gaps,
        "resume_action": "repair only the missing release evidence; do not overwrite existing tag, release, or npm version",
        "next_action": "repair only the missing release evidence; do not overwrite existing tag, release, or npm version",
    }


def release_closeout_head_hint(
    *,
    target: Path,
    context: dict[str, Any],
    release_judgment: str,
    readbacks: dict[str, Any],
    classification: dict[str, Any],
) -> dict[str, Any]:
    gaps = set(classification.get("gaps", [])) if isinstance(classification.get("gaps"), list) else set()
    if not {"tag_target_commit_mismatch", "workflow_run_target_commit_missing"} & gaps:
        return classification
    tag = readbacks.get("tag") if isinstance(readbacks.get("tag"), dict) else {}
    workflow = readbacks.get("workflow_run") if isinstance(readbacks.get("workflow_run"), dict) else {}
    selected = workflow.get("selected") if isinstance(workflow.get("selected"), dict) else {}
    release_commit = tag.get("commit")
    target_commit = tag.get("target_commit") or workflow.get("target_commit")
    if not isinstance(release_commit, str) or release_commit == target_commit:
        return classification
    if selected.get("headSha") not in {None, release_commit}:
        return classification
    version = context.get("version") or context.get("tag") or "<version>"
    command = f"loom release readback --target {target} --version {version} --commit {release_commit} --release-judgment {release_judgment} --json"
    return {
        **classification,
        "resume_action": command,
        "next_action": command,
        "closeout_head_hint": "release artifacts are bound to the published release commit; rerun readback with --commit when checking from a later closeout carrier head.",
    }


def release_fixture_payload(fixture_file: Path, fixture_name: str) -> dict[str, Any] | None:
    try:
        data = json.loads(fixture_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fixtures = data.get("fixtures") if isinstance(data, dict) else None
    if not isinstance(fixtures, list):
        return None
    for fixture in fixtures:
        if isinstance(fixture, dict) and fixture.get("name") == fixture_name:
            return fixture
    return None


def release_readback_payload(
    *,
    command: str,
    target: Path,
    release_judgment: str,
    version: str | None,
    package_name: str | None,
    repo: str | None,
    commit: str | None,
    workflow: str,
    fixture_file: Path | None,
    fixture_name: str | None,
) -> dict[str, Any]:
    fixture: dict[str, Any] | None = None
    if fixture_file or fixture_name:
        if not fixture_file or not fixture_name:
            return output(
                command,
                "block",
                schema=RELEASE_READBACK_SCHEMA,
                summary="Release readback fixture mode requires both --fixture-file and --fixture.",
                target=str(target),
                mutates=False,
                failed_layer="release-readback-input",
                fail_closed_reason="missing_fixture_input",
                fallback_to=["loom release readback --target <repo> --json"],
            )
        fixture = release_fixture_payload(fixture_file, fixture_name)
        if fixture is None:
            return output(
                command,
                "block",
                schema=RELEASE_READBACK_SCHEMA,
                summary="Release readback fixture was not found or unreadable.",
                target=str(target),
                mutates=False,
                failed_layer="release-readback-fixture",
                fail_closed_reason=f"missing fixture: {fixture_name}",
                fallback_to=["docs/evidence/fixtures/release-readback-fixtures.json"],
            )
        fixture_target = fixture.get("target") if isinstance(fixture.get("target"), dict) else {}
        context = {
            "version": fixture_target.get("version") or version or "unknown",
            "tag": fixture_target.get("tag") or release_normalize_tag(fixture_target.get("version") or version or "unknown"),
            "npm_version": fixture_target.get("npm_version") or release_npm_version(fixture_target.get("version") or version or "unknown"),
            "npm_package": fixture_target.get("npm_package") or package_name or "@mc-and-his-agents/loom",
            "package_json_version": fixture_target.get("package_json_version"),
        }
        target_commit = fixture_target.get("target_commit") or commit
        resolved_repo = fixture_target.get("repo") or repo
        readbacks = fixture.get("readbacks") if isinstance(fixture.get("readbacks"), dict) else {}
    else:
        context = release_package_context(target, version=version, package_name=package_name)
        target_commit = release_target_commit(target, commit)
        resolved_repo = repo or infer_github_repo(target)
        readbacks = {
            "tag": release_tag_readback(target, tag=context["tag"], target_commit=target_commit),
            "github_release": github_release_readback(target, repo=resolved_repo, tag=context["tag"]),
            "npm_package": npm_package_readback(target, package_name=context["npm_package"], npm_version=context["npm_version"]),
            "workflow_run": workflow_run_readback(target, repo=resolved_repo, workflow=workflow, target_commit=target_commit),
            "package_surface": release_package_surface_readback(target, context=context),
            "carrier": release_carrier_status_readback(target),
        }

    errors = release_read_errors(readbacks)
    classification = classify_release_readback(release_judgment=release_judgment, readbacks=readbacks)
    classification = release_closeout_head_hint(
        target=target,
        context=context,
        release_judgment=release_judgment,
        readbacks=readbacks,
        classification=classification,
    )
    if errors:
        classification = {
            "verdict": "blocked",
            "classification": "blocked",
            "reason": "one or more release readback surfaces are unreadable",
            "gaps": [error["surface"] for error in errors],
            "resume_action": "restore host/npm readback access before deciding release closeout state",
            "next_action": "restore host/npm readback access before deciding release closeout state",
        }
    result = "block" if errors else "pass"
    summary = (
        f"Release readback verdict: {classification['verdict']}."
        if result == "pass"
        else "Release readback could not read one or more host surfaces."
    )
    payload = output(
        command,
        result,
        schema=RELEASE_READBACK_SCHEMA,
        summary=summary,
        target=str(target),
        mutates=False,
        host_mutations=False,
        carrier_mutations=False,
        release_judgment=release_judgment,
        release_target={
            **context,
            "target_commit": target_commit,
            "repo": resolved_repo,
            "workflow": workflow,
        },
        classification=classification,
        readbacks=readbacks,
        read_errors=errors,
        diagnostic={
            "verdict": classification.get("verdict"),
            "blocked": classification.get("verdict") == "blocked" or bool(errors),
            "gaps": classification.get("gaps", []),
            "next_action": classification.get("next_action") or classification.get("resume_action"),
        },
        next_action=classification.get("next_action") or classification.get("resume_action"),
        failed_layer="release-readback" if errors else None,
        fail_closed_reason="host_readback_unavailable" if errors else None,
        fallback_to=["resolve host readback/auth via #1597 before retrying"] if errors else None,
    )
    if fixture is not None:
        payload["fixture"] = {
            "file": str(fixture_file),
            "name": fixture_name,
            "story": fixture.get("story"),
            "expected_classification": fixture.get("expected_classification"),
        }
    return payload


def release_closeout_step(name: str, payload: dict[str, Any], *, mutates: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "result": payload.get("result"),
        "summary": payload.get("summary"),
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "mutates": mutates,
        "payload": payload,
    }


def release_closeout_readback_allows_sync(readback: dict[str, Any]) -> tuple[bool, str]:
    classification = readback.get("classification") if isinstance(readback.get("classification"), dict) else {}
    verdict = str(classification.get("verdict") or "")
    gaps = {str(gap) for gap in classification.get("gaps", []) if gap}
    if verdict == "published":
        return True, "release readback is already published; closeout-sync is idempotent."
    if verdict == "blocked" and gaps == {"carrier_not_terminal"}:
        return True, "release artifacts are published; repo carrier terminalization is the only remaining gap."
    return False, f"release readback verdict `{verdict or 'unknown'}` is not eligible for closeout-sync"


RELEASE_CLOSEOUT_PR_READBACK_FALLBACK = [
    "loom pr inspect <pr> --json --full-output",
    "pass --pr-payload-file <path> with a saved PR readback payload",
]


def release_closeout_repo_flow_args(repo: str | None) -> list[str]:
    if not repo or "/" not in repo:
        return []
    owner, repo_name = repo.split("/", 1)
    if not owner or not repo_name:
        return []
    return ["--owner", owner, "--repo", repo_name]


def release_closeout_pr_from_binding_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    chain = payload.get("binding_chain") if isinstance(payload.get("binding_chain"), dict) else {}
    nodes = chain.get("nodes") if isinstance(chain.get("nodes"), dict) else {}
    pr_node = nodes.get("pr") if isinstance(nodes.get("pr"), dict) else nodes.get("implementation_pr")
    if not isinstance(pr_node, dict):
        return None
    pr_value = pr_node.get("value") if isinstance(pr_node.get("value"), dict) else {}
    if not pr_value:
        return None
    pr = dict(pr_value)
    merge_node = nodes.get("merge_commit") if isinstance(nodes.get("merge_commit"), dict) else {}
    merge_value = merge_node.get("value") if isinstance(merge_node.get("value"), dict) else {}
    merge_sha = merge_value.get("sha")
    if merge_sha and not isinstance(pr.get("mergeCommit"), dict):
        pr["mergeCommit"] = {"oid": str(merge_sha)}
    return pr


def release_closeout_normalize_pr_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    pr = payload.get("pr") if isinstance(payload.get("pr"), dict) else payload
    if any(key in pr for key in ("number", "state", "mergeCommit", "merge_commit_sha")):
        normalized = dict(pr)
    else:
        binding_pr = release_closeout_pr_from_binding_payload(payload)
        if binding_pr is None:
            return None
        normalized = binding_pr
    if "mergeCommit" not in normalized and normalized.get("merge_commit_sha"):
        normalized["mergeCommit"] = {"oid": str(normalized.get("merge_commit_sha"))}
    if "mergedAt" not in normalized and normalized.get("merged_at"):
        normalized["mergedAt"] = normalized.get("merged_at")
    if "url" not in normalized and normalized.get("html_url"):
        normalized["url"] = normalized.get("html_url")
    state = str(normalized.get("state") or "").upper()
    if state == "CLOSED" and normalized.get("mergedAt"):
        normalized["state"] = "MERGED"
    return normalized


def release_closeout_pr_readback_payload(
    *,
    target: Path,
    pr_number: str,
    repo: str | None,
    target_commit: str | None,
    pr_payload_file: str | None,
) -> dict[str, Any]:
    command = "release closeout-sync pr-readback"
    if pr_payload_file:
        path = Path(pr_payload_file)
        if not path.is_absolute():
            path = target / path
        try:
            loaded = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            return output(command, "block", summary="PR readback fixture is unreadable.", missing_inputs=[str(exc)], fallback_to=RELEASE_CLOSEOUT_PR_READBACK_FALLBACK)
        pr = release_closeout_normalize_pr_payload(loaded) if isinstance(loaded, dict) else None
    else:
        inspect_args = [
            "host-binding",
            "inspect",
            "--target",
            str(target),
            "--pr",
            str(pr_number),
            *release_closeout_repo_flow_args(repo),
        ]
        inspected = flow_payload(
            command,
            inspect_args,
            fallback_to=RELEASE_CLOSEOUT_PR_READBACK_FALLBACK,
        )
        pr = release_closeout_normalize_pr_payload(inspected)

    if not isinstance(pr, dict):
        return output(command, "block", summary="PR readback payload is invalid.", missing_inputs=["PR payload must expose PR number, state, and merge commit"], fallback_to=RELEASE_CLOSEOUT_PR_READBACK_FALLBACK)
    missing: list[str] = []
    if str(pr.get("number")) != str(pr_number):
        missing.append("PR number mismatch")
    if str(pr.get("state", "")).upper() != "MERGED":
        missing.append("PR is not merged")
    merge_commit = pr.get("mergeCommit") if isinstance(pr.get("mergeCommit"), dict) else {}
    merge_sha = merge_commit.get("oid")
    if not merge_sha:
        missing.append("PR merge commit is missing")
    if target_commit and merge_sha and merge_sha != target_commit:
        missing.append("release target commit does not match PR merge commit")
    if missing:
        return output(command, "block", summary="Release closeout PR readback is not merge-complete for the release target.", missing_inputs=missing, pr=pr, fallback_to=["verify --pr points at the merged release PR for this version"])
    return output(command, "pass", summary="Release PR readback is merge-complete and bound to the release target.", pr=pr)


def release_closeout_next_commands(args: argparse.Namespace, target: Path, head_sha: str | None) -> dict[str, str]:
    branch = args.branch or "<closeout-sync-branch>"
    stable_head = head_sha or "<post-commit-head-sha>"
    pr = args.closeout_pr or "<closeout-sync-pr>"
    return {
        "metadata_render": f"loom pr metadata-render --target {target} --surface closeout --item {args.item} --branch {branch} --head-sha {stable_head} --release-judgment no_release --json",
        "metadata_update": f"loom pr metadata-update {pr} --target {target} --surface closeout --item {args.item} --branch {branch} --head-sha {stable_head} --release-judgment no_release --apply --json",
        "gate": f"loom pr gate {pr} --target {target} --surface closeout --work-item {args.item} --head-sha {stable_head} --json",
        "merge": f"loom merge check {pr} --target {target} --work-item {args.item} --head-sha {stable_head} --json",
        "post_merge_readback": f"loom release readback --target {target} --version {args.version or '<version>'} --commit {args.commit or '<release-commit>'} --release-judgment release_required --json",
    }


def release_closeout_issue(args: argparse.Namespace) -> str:
    if args.issue:
        return str(args.issue)
    match = re.search(r"\d+", str(args.item))
    return match.group(0) if match else "not_applicable"


def handle_release_closeout_sync(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom release closeout-sync")
    parser.add_argument("--target", default=".")
    parser.add_argument("--version")
    parser.add_argument("--package", dest="package_name")
    parser.add_argument("--repo")
    parser.add_argument("--commit")
    parser.add_argument("--workflow", default="loom-cli-release.yml")
    parser.add_argument("--item", required=True)
    parser.add_argument("--pr", required=True, help="Merged release PR number used as release evidence.")
    parser.add_argument("--closeout-pr", help="Optional carrier-sync PR number for next-step metadata/gate commands.")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--branch")
    parser.add_argument("--head-sha")
    parser.add_argument("--target-branch")
    parser.add_argument("--closed-at")
    parser.add_argument("--evidence-locator")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--fixture-file")
    parser.add_argument("--fixture")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    add_legacy_carrier_compatibility_args(parser)
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("release closeout-sync", target, "target path does not exist"))
    compatibility = legacy_carrier_compatibility(args)
    if compatibility["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    "release closeout-sync",
                    "block",
                    schema_version="loom-legacy-carrier-command/v1",
                    summary=compatibility["summary"],
                    mutates=False,
                    target=str(target),
                    compatibility=compatibility,
                    missing_inputs=compatibility["missing_inputs"],
                    fallback_to="loom release readback --target <repo> --version <version> --commit <sha> --json",
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )

    release_readback = release_readback_payload(
        command="release closeout-sync release-readback",
        target=target,
        release_judgment="release_required",
        version=args.version,
        package_name=args.package_name,
        repo=args.repo,
        commit=args.commit,
        workflow=args.workflow,
        fixture_file=Path(args.fixture_file).resolve() if args.fixture_file else None,
        fixture_name=args.fixture,
    )
    steps = [release_closeout_step("release-readback", release_readback)]
    allowed, reason = release_closeout_readback_allows_sync(release_readback)
    if not allowed:
        payload = output(
            "release closeout-sync",
            "block",
            schema_version="loom-release-closeout-sync/v1",
            summary="release closeout-sync stopped before carrier writes.",
            target=str(target),
            item={"id": args.item},
            release_pr={"number": args.pr},
            apply=args.apply,
            dry_run=not args.apply,
            steps=steps,
            missing_inputs=[reason],
            readiness=readiness_payload(
                ready=False,
                reasons=["release_readback_mismatch"],
                next_command="loom release readback --target <repo> --json",
            ),
            fallback_to=["loom release readback --target <repo> --json"],
            next_action="Resolve release readback drift/missing artifacts before carrier terminalization.",
        )
        return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))

    release_target = release_readback.get("release_target") if isinstance(release_readback.get("release_target"), dict) else {}
    readbacks = release_readback.get("readbacks") if isinstance(release_readback.get("readbacks"), dict) else {}
    github_release = readbacks.get("github_release") if isinstance(readbacks.get("github_release"), dict) else {}
    resolved_repo = args.repo or release_target.get("repo") or infer_github_repo(target)
    target_commit = args.commit or release_target.get("target_commit")
    pr_readback = release_closeout_pr_readback_payload(
        target=target,
        pr_number=args.pr,
        repo=str(resolved_repo) if resolved_repo else None,
        target_commit=str(target_commit) if target_commit else None,
        pr_payload_file=args.pr_payload_file,
    )
    steps.append(release_closeout_step("release-pr-readback", pr_readback))
    if pr_readback.get("result") != "pass":
        payload = output(
            "release closeout-sync",
            "block",
            schema_version="loom-release-closeout-sync/v1",
            summary="release closeout-sync stopped before carrier writes.",
            target=str(target),
            item={"id": args.item},
            release_pr={"number": args.pr},
            apply=args.apply,
            dry_run=not args.apply,
            steps=steps,
            missing_inputs=pr_readback.get("missing_inputs", []),
            readiness=readiness_payload(
                ready=False,
                reasons=readiness_reasons_from_text(pr_readback.get("missing_inputs", [])) or ["release_readback_mismatch"],
                next_command="loom pr inspect <pr> --json --full-output",
            ),
            fallback_to=pr_readback.get("fallback_to"),
            next_action="Bind --pr to the merged release PR before carrier terminalization.",
        )
        return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))

    pr = pr_readback.get("pr") if isinstance(pr_readback.get("pr"), dict) else {}
    merge_commit = pr.get("mergeCommit") if isinstance(pr.get("mergeCommit"), dict) else {}
    merge_sha = str(merge_commit.get("oid") or target_commit or "not_applicable")
    target_branch = str(args.target_branch or pr.get("baseRefName") or "main")
    closed_at = str(args.closed_at or pr.get("mergedAt") or now_iso())
    evidence_locator = str(args.evidence_locator or ";".join(str(value) for value in (github_release.get("url"), pr.get("url")) if value) or "release-readback")
    issue_number = release_closeout_issue(args)

    carrier_args = [
        "carrier",
        "closeout-sync",
        "--target",
        str(target),
        "--item",
        args.item,
        "--terminal-state",
        "closed_out",
        "--issue",
        issue_number,
        "--pr",
        str(args.pr),
        "--merge-commit",
        merge_sha,
        "--target-branch",
        target_branch,
        "--closed-at",
        closed_at,
        "--evidence-locator",
        evidence_locator,
        "--apply" if args.apply else "--dry-run",
    ]
    carrier = flow_payload("release closeout-sync", carrier_args, fallback_to=["loom carrier closeout-sync --target <repo> --item <item> --apply --json"])
    steps.append(release_closeout_step("carrier-closeout-sync", carrier, mutates=args.apply))

    if args.apply and carrier.get("result") == "pass":
        stop = (
            f"{args.item} release closeout synced for {release_target.get('version') or args.version}: "
            f"release PR #{args.pr} merged at {merge_sha}; published release readback consumed into terminal repo carrier state."
        )
        recovery_args = [
            "recovery",
            "writeback",
            "--target",
            str(target),
            "--item",
            args.item,
            "--current-checkpoint",
            "closed_out",
            "--current-stop",
            stop,
            "--next-step",
            "None.",
            "--blockers",
            "None recorded.",
            "--current-lane",
            "release-closeout-sync",
        ]
        recovery = flow_payload("release closeout-sync", recovery_args, fallback_to=["loom recovery writeback --target <repo> --item <item>"])
        steps.append(release_closeout_step("recovery-writeback", recovery, mutates=True))
        if recovery.get("result") == "pass":
            for surface in ("closeout", "merge_ready"):
                refresh_args = ["carrier", "refresh", "--target", str(target), "--item", args.item, "--surface", surface, "--write"]
                refresh = flow_payload("release closeout-sync", refresh_args, fallback_to=["loom carrier refresh --target <repo> --write"])
                steps.append(release_closeout_step(f"carrier-refresh-{surface}", refresh, mutates=True))

    blocker = next((step for step in steps if step.get("result") == "block"), None)
    result = "block" if blocker else "pass"
    next_commands = release_closeout_next_commands(args, target, args.head_sha)
    payload = output(
        "release closeout-sync",
        result,
        schema_version="loom-release-closeout-sync/v1",
        summary="release closeout-sync applied terminal carrier updates." if args.apply and result == "pass" else "release closeout-sync produced a terminal carrier plan." if result == "pass" else "release closeout-sync stopped at a blocking step.",
        target=str(target),
        item={"id": args.item},
        release_pr={"number": args.pr},
        release_target=release_target,
        terminal_metadata={
            "terminal_state": "closed_out",
            "issue": issue_number,
            "pr": str(args.pr),
            "merge_commit": merge_sha,
            "target_branch": target_branch,
            "closed_at": closed_at,
            "evidence_locator": evidence_locator,
        },
        apply=args.apply,
        dry_run=not args.apply,
        mutates=args.apply,
        host_mutations=False,
        carrier_mutations=args.apply,
        steps=steps,
        first_blocker=blocker,
        missing_inputs=blocker.get("missing_inputs", []) if blocker else [],
        readiness=readiness_payload(
            ready=False,
            reasons=readiness_reasons_from_text(blocker.get("missing_inputs", []) if blocker else []) if blocker else [],
            next_command=next_commands["metadata_update"] if args.apply and result == "pass" else "loom release closeout-sync --target <repo> --item <item> --pr <release-pr> --apply --json",
            summary=(
                "Release carrier sync is written; update/read back the closeout PR metadata before hosted gate."
                if args.apply and result == "pass"
                else "Review the release closeout-sync dry-run before applying carrier writes."
                if result == "pass"
                else "Release closeout-sync stopped before hosted gate readiness."
            ),
        ),
        fallback_to=blocker.get("fallback_to") if blocker else None,
        next_commands=next_commands,
        next_action=next_commands["metadata_update"] if args.apply and result == "pass" else "Review the dry-run plan, then rerun with --apply.",
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def handle_release(argv: list[str]) -> int:
    if not argv:
        return emit(output("release", "block", schema=RELEASE_READBACK_SCHEMA, summary="Release requires an operation.", failed_layer="release-input", fail_closed_reason="missing release operation", fallback_to=["loom release readback --target <repo> --json"]))
    operation = argv[0]
    if operation == "closeout-sync":
        return handle_release_closeout_sync(argv[1:])
    if operation not in {"readback", "resume"}:
        return emit(output("release", "block", schema=RELEASE_READBACK_SCHEMA, summary="Unsupported release operation.", failed_layer="release-input", fail_closed_reason=f"unsupported release operation: {operation}", fallback_to=["loom release readback --target <repo> --json"]))
    parser = argparse.ArgumentParser(prog=f"loom release {operation}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--version")
    parser.add_argument("--package", dest="package_name")
    parser.add_argument("--repo")
    parser.add_argument("--commit")
    parser.add_argument("--workflow", default="loom-cli-release.yml")
    parser.add_argument("--release-judgment", choices=("release_required", "no_release"), default="release_required")
    parser.add_argument("--fixture-file")
    parser.add_argument("--fixture")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv[1:])
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(f"release {operation}", target, "target path does not exist"))
    payload = release_readback_payload(
        command=f"release {operation}",
        target=target,
        release_judgment=args.release_judgment,
        version=args.version,
        package_name=args.package_name,
        repo=args.repo,
        commit=args.commit,
        workflow=args.workflow,
        fixture_file=Path(args.fixture_file).resolve() if args.fixture_file else None,
        fixture_name=args.fixture,
    )
    if operation == "resume":
        payload["resume_contract"] = {
            "mutates": False,
            "summary": "Release resume is a readback classifier; it does not trigger workflow_dispatch, create tags, publish npm, create GitHub Releases, or write closeout carriers.",
            "next_action": payload.get("classification", {}).get("resume_action"),
        }
    return emit(payload)


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"__pycache__", ".DS_Store"} or name.endswith(".pyc")}

    shutil.copytree(source, target, ignore=ignore)


def repo_version() -> str:
    if not VERSION_FILE.exists():
        return "unknown"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def version_context() -> dict[str, Any]:
    registry = read_optional_json(PLUGIN_SKILLS_ROOT / "registry.json") or {}
    plugin = read_optional_json(PLUGIN_MANIFEST) or {}
    x_loom = plugin.get("x-loom", {}) if isinstance(plugin.get("x-loom"), dict) else {}
    return {
        "repo_version": repo_version(),
        "skills_registry_version": registry.get("registry_version", "unknown"),
        "plugin_surface_version": x_loom.get("plugin_surface_version", plugin.get("version", "unknown")),
        "host_adapter_version": x_loom.get("host_adapter_version", "unknown"),
        "plugin_payload_root": "plugins/loom/skills",
        "plugin_payload_version": x_loom.get("plugin_payload_version", "unknown"),
        "plugin_payload_hash": x_loom.get("plugin_payload_hash", "unknown"),
        "source_package": x_loom.get("source_package", "unknown"),
        "source_package_version": x_loom.get("source_package_version", "unknown"),
        "source_git_sha": x_loom.get("source_git_sha", "unknown"),
        "version_authority": "docs/adoption/version-authority-map.md",
    }


def semver_tuple(value: str) -> tuple[int, ...] | None:
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def npm_latest_version(package_name: str = "@mc-and-his-agents/loom") -> dict[str, Any]:
    override = os.environ.get("LOOM_TEST_NPM_LATEST_VERSION")
    if override:
        if override == "__unreadable__":
            return {"status": "unreadable", "version": None, "source": "test-override", "error": "simulated npm read failure"}
        return {"status": "readable", "version": override, "source": "test-override"}
    if os.environ.get("LOOM_SKIP_NPM_LATEST") == "1":
        return {"status": "unreadable", "version": None, "source": "disabled", "error": "npm latest lookup disabled"}
    try:
        completed = subprocess.run(
            ["npm", "view", package_name, "version", "--json"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=4,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unreadable", "version": None, "source": "npm", "error": str(exc)}
    if completed.returncode != 0:
        return {"status": "unreadable", "version": None, "source": "npm", "error": (completed.stderr or completed.stdout).strip()}
    try:
        version = json.loads(completed.stdout)
    except json.JSONDecodeError:
        version = completed.stdout.strip().strip('"')
    if not isinstance(version, str) or not version:
        return {"status": "unreadable", "version": None, "source": "npm", "error": "npm returned no version"}
    return {"status": "readable", "version": version, "source": "npm"}


def plugin_payload_refresh_guidance(plugin_readback: dict[str, Any]) -> dict[str, Any]:
    action = plugin_readback.get("action")
    freshness = plugin_readback.get("freshness")
    readback_command = "loom host doctor --host codex --scope user --json"
    install_command = "loom host install --host codex --scope user --apply --json"
    register_command = "loom host register --host codex --scope user --apply --json"
    reload_note = "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded."

    apply_commands: list[str] = []
    next_steps: list[str]
    reload_required = False
    status = "required"
    summary = "Codex plugin payload refresh is required."

    if action == "install_cli":
        apply_commands = [
            "npm install -g @mc-and-his-agents/loom@latest",
            install_command,
            register_command,
        ]
        next_steps = [*apply_commands, readback_command]
        summary = "Install the current root Loom CLI, then refresh and register the Codex user plugin payload."
    elif action == "install_plugin":
        apply_commands = [install_command, register_command]
        next_steps = [*apply_commands, readback_command]
        summary = "Refresh the Codex user plugin source from the root Loom CLI, then register it."
    elif action == "reload_host":
        reload_required = True
        next_steps = [reload_note, readback_command]
        summary = "The Codex-owned runtime cache is stale; reload Codex, then read back host doctor."
    elif action == "already_current" or freshness == "already_current":
        status = "current"
        next_steps = [readback_command]
        summary = "Codex plugin payload is already current."
    else:
        command = plugin_readback.get("command") if isinstance(plugin_readback.get("command"), str) else readback_command
        next_steps = [command, readback_command] if command != readback_command else [readback_command]

    return {
        "schema": "loom-plugin-payload-refresh-guidance/v1",
        "status": status,
        "freshness": freshness,
        "action": action,
        "summary": summary,
        "apply_commands": apply_commands,
        "readback_command": readback_command,
        "reload_required": reload_required,
        "reload_note": reload_note if reload_required else None,
        "next_steps": next_steps,
        "authority_boundary": {
            "provider": "codex-user-plugin",
            "managed_by": "loom host doctor|install|register --host codex --scope user",
            "target_install_upgrade_scope": "repository installed-state only",
            "legacy_installer": "not_primary_path",
        },
    }


def version_freshness(source: Path | None = None, plugin_readback: dict[str, Any] | None = None) -> dict[str, Any]:
    versions = version_context()
    installed_cli = versions["repo_version"]
    latest = npm_latest_version()
    installed_tuple = semver_tuple(installed_cli)
    latest_tuple = semver_tuple(str(latest.get("version") or ""))
    if latest["status"] != "readable" or latest_tuple is None:
        cli_freshness = "npm_unreadable"
        cli_action = "check_cli_latest"
    elif installed_tuple is None:
        cli_freshness = "installed_version_unknown"
        cli_action = "upgrade_cli"
    elif installed_tuple is not None and installed_tuple < latest_tuple:
        cli_freshness = "stale"
        cli_action = "upgrade_cli"
    else:
        cli_freshness = "current"
        cli_action = "already_current"

    try:
        plugin_readback = plugin_readback or codex_plugin_payload_readback(source or global_codex_plugin_source(), codex_workstation_paths())
    except Exception as exc:  # pragma: no cover - defensive host boundary guard.
        plugin_readback = {
            "schema": "loom-codex-plugin-payload-readback/v1",
            "result": "block",
            "freshness": "host_api_unreadable",
            "action": "refresh_plugin",
            "command": "loom host doctor --host codex --scope user --json",
            "error": f"{type(exc).__name__}: {exc}",
            "layers": [],
        }
    plugin_freshness = plugin_readback.get("freshness")
    plugin_action = "already_current" if plugin_freshness == "already_current" else "refresh_plugin"
    if plugin_readback.get("action") == "install_cli":
        plugin_action = "upgrade_cli"
    refresh_guidance = plugin_payload_refresh_guidance(plugin_readback)
    source_surface = next((layer.get("plugin_surface_version") for layer in plugin_readback.get("layers", []) if layer.get("layer") == "source-payload"), None)
    surface_versions = {
        layer.get("layer"): layer.get("plugin_surface_version")
        for layer in plugin_readback.get("layers", [])
        if layer.get("plugin_surface_version")
    }
    incompatible_surfaces = [
        layer
        for layer, surface in surface_versions.items()
        if source_surface and surface != source_surface
    ]
    if cli_action == "upgrade_cli" or plugin_action == "upgrade_cli":
        action = "upgrade_cli"
        command = "npm install -g @mc-and-his-agents/loom@latest"
    elif plugin_action == "refresh_plugin":
        action = "refresh_plugin"
        command = plugin_readback.get("command") or "loom host install --host codex --scope user --apply --json"
    elif cli_action == "check_cli_latest":
        action = "check_cli_latest"
        command = "npm view @mc-and-his-agents/loom version --json"
    else:
        action = "already_current"
        command = None
    return {
        "schema": "loom-version-freshness/v1",
        "action": action,
        "command": command,
        "cli": {
            "package": "@mc-and-his-agents/loom",
            "installed_version": installed_cli,
            "latest_version": latest.get("version"),
            "freshness": cli_freshness,
            "latest_status": latest.get("status"),
            "latest_source": latest.get("source"),
            "error": latest.get("error"),
        },
        "plugin_payload": {
            "freshness": plugin_freshness,
            "action": plugin_action,
            "installed": next((layer for layer in plugin_readback.get("layers", []) if layer.get("layer") == "runtime-cache"), None),
            "latest": next((layer for layer in plugin_readback.get("layers", []) if layer.get("layer") == "source-payload"), None),
            "readback": plugin_readback,
            "refresh_guidance": refresh_guidance,
        },
        "surface_compatibility": {
            "status": "incompatible" if incompatible_surfaces else "compatible",
            "source_surface_version": source_surface,
            "surface_versions": surface_versions,
            "incompatible_layers": incompatible_surfaces,
        },
    }


def version_freshness_action(freshness: dict[str, Any]) -> dict[str, Any]:
    action = freshness.get("action")
    guidance = freshness.get("plugin_payload", {}).get("refresh_guidance", {})
    return {
        "id": "cli-plugin-freshness",
        "kind": "version-freshness",
        "status": "current" if action == "already_current" else "required",
        "action": action,
        "command": freshness.get("command") or "loom version --json",
        "apply_commands": guidance.get("apply_commands", []),
        "readback_command": guidance.get("readback_command"),
        "reload_required": guidance.get("reload_required", False),
        "reload_note": guidance.get("reload_note"),
        "next_steps": guidance.get("next_steps", []),
    }


def emit(payload: dict[str, Any], *, stream: Any | None = None) -> int:
    failure_envelope = public_cli_failure_envelope(payload)
    if failure_envelope is not None:
        payload["failure_envelope"] = failure_envelope
        if "primary_cause" in payload:
            payload["primary_cause"] = failure_envelope["primary_cause"]
    if stream is None:
        stream = sys.stdout
    stream.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0 if payload.get("result") in {"pass", "not_applicable"} else 1


def output(command: str, result: str, **fields: Any) -> dict[str, Any]:
    return {
        "schema_version": OUTPUT_SCHEMA,
        "command": command,
        "result": result,
        "generated_at": now_iso(),
        **fields,
    }


def output_key_gaps(payload: dict[str, Any], *, limit: int = 10) -> list[Any]:
    for field in ("key_gaps", "blocking_gaps", "gaps", "missing_inputs", "blocking_failures"):
        value = payload.get(field)
        if isinstance(value, list):
            return value[:limit]
    reason = payload.get("fail_closed_reason")
    return [reason] if reason else []


def output_diagnostic_counts(payload: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for field in ("key_gaps", "blocking_gaps", "gaps", "missing_inputs", "blocking_failures"):
        value = payload.get(field)
        if isinstance(value, list):
            counts[field] = len(value)
    reports = payload.get("reports")
    if isinstance(reports, list):
        counts["reports"] = len(reports)
        counts["non_passing_reports"] = sum(
            1
            for report in reports
            if isinstance(report, dict) and report.get("result") not in {None, "pass", "match"}
        )
    return counts


def output_key_locators(payload: dict[str, Any], *, limit: int = 10) -> list[str]:
    locators: list[str] = []

    def visit(value: Any) -> None:
        if len(locators) >= limit:
            return
        if isinstance(value, dict):
            for key, nested in value.items():
                lowered = str(key).lower()
                if isinstance(nested, str) and (
                    lowered.endswith("locator")
                    or lowered.endswith("path")
                    or lowered.endswith("entrypoint")
                    or lowered in {"target", "read_entry", "current_runtime_entrypoint"}
                ):
                    if nested and nested not in locators:
                        locators.append(nested)
                        if len(locators) >= limit:
                            return
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)
                if len(locators) >= limit:
                    return

    visit(payload)
    return locators


def compact_action_text(value: Any, *, budget: int = 240) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return truncate_utf8(text, budget) if text else None


def actionable_finding(entry: Any, *, source: str) -> dict[str, Any] | None:
    if isinstance(entry, str):
        summary = compact_action_text(entry)
        return {"source": source, "summary": summary} if summary else None
    if not isinstance(entry, dict):
        return None
    finding: dict[str, Any] = {"source": source}
    for key in ("kind", "failure_kind", "classifier", "subject"):
        value = compact_action_text(entry.get(key))
        if value:
            finding[key] = value
    for source_key, target_key in (
        ("summary", "summary"),
        ("recommended_action", "next_action"),
        ("next_action", "next_action"),
        ("next_command", "next_command"),
        ("fallback_to", "fallback_to"),
        ("action", "action"),
        ("description", "summary"),
    ):
        value = entry.get(source_key)
        if isinstance(value, list):
            value = " | ".join(str(item) for item in value[:3])
        compacted = compact_action_text(value)
        if compacted and target_key not in finding:
            finding[target_key] = compacted
    if "summary" not in finding:
        for key in ("subject", "kind", "failure_kind", "classifier"):
            if key in finding:
                finding["summary"] = finding[key]
                break
    return finding if any(key in finding for key in ("summary", "next_action", "next_command", "fallback_to")) else None


def budget_actionable_finding(finding: dict[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {"source": finding["source"]}
    for key in ("summary", "next_action", "next_command", "fallback_to"):
        value = compact_action_text(finding.get(key), budget=160)
        if value:
            compacted[key] = value
    if len(compacted) > 1:
        return compacted
    for key in ("kind", "failure_kind", "classifier", "subject"):
        value = compact_action_text(finding.get(key), budget=160)
        if value:
            compacted["summary"] = value
            return compacted
    return compacted


def output_actionable_findings(payload: dict[str, Any], *, limit: int = DEFAULT_ACTIONABLE_FINDINGS_LIMIT) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(entry: Any, *, source: str) -> None:
        if len(findings) >= limit:
            return
        finding = actionable_finding(entry, source=source)
        if not finding:
            return
        key = json.dumps(finding, sort_keys=True, ensure_ascii=False)
        if key in seen:
            return
        seen.add(key)
        findings.append(finding)

    for field in ("findings", "blocking_inputs", "blocking_gaps", "gaps", "missing_inputs", "blocking_failures"):
        value = payload.get(field)
        if isinstance(value, list):
            for entry in value:
                add(entry, source=field)

    repair_plan = payload.get("repair_plan")
    if isinstance(repair_plan, dict) and isinstance(repair_plan.get("actions"), list):
        for entry in repair_plan["actions"]:
            add(entry, source="repair_plan.actions")

    sync_plan = payload.get("sync_plan")
    if isinstance(sync_plan, dict) and isinstance(sync_plan.get("actions"), list):
        for entry in sync_plan["actions"]:
            add(entry, source="sync_plan.actions")

    for field in ("next_command", "next_action", "fallback_to"):
        value = payload.get(field)
        entries = value if isinstance(value, list) else [value]
        for entry in entries:
            if entry is None:
                continue
            if field == "fallback_to":
                add({"fallback_to": entry, "summary": "Run the suggested fallback command."}, source=field)
            else:
                add({field: entry}, source=field)

    return findings


def should_use_actionable_envelope(payload: dict[str, Any], actionable_findings: list[dict[str, Any]]) -> bool:
    result = str(payload.get("result") or "")
    return result not in {"", "pass"} and bool(actionable_findings)


def positive_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def truncate_utf8(text: str, budget_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= budget_bytes:
        return text
    marker = "…"
    marker_bytes = marker.encode("utf-8")
    if budget_bytes <= len(marker_bytes):
        return ""
    return encoded[: budget_bytes - len(marker_bytes)].decode("utf-8", errors="ignore") + marker


def output_envelope(
    command: str,
    result: str,
    *,
    summary: str,
    key_gaps: list[Any] | None = None,
    failed_layer: str | None = None,
    fail_closed_reason: str | None = None,
    artifact_locator: str | None = None,
    artifact_sha256: str | None = None,
    full_output_available: bool = False,
    full_output_truncated: bool = False,
    sensitive: bool = False,
    **fields: Any,
) -> dict[str, Any]:
    failure_classification = {
        key: value
        for key, value in {
            "failed_layer": failed_layer,
            "fail_closed_reason": fail_closed_reason,
        }.items()
        if value
    }
    return output(
        command,
        result,
        envelope_schema=OUTPUT_ENVELOPE_SCHEMA,
        summary=summary,
        failure_classification=failure_classification,
        key_gaps=key_gaps or [],
        full_output={
            "available": full_output_available,
            "artifact_locator": artifact_locator,
            "artifact_sha256": artifact_sha256,
            "truncated": full_output_truncated,
            "sensitive": sensitive,
        },
        **fields,
    )


def write_output_artifact_metadata(
    payload: dict[str, Any],
    *,
    artifact_dir: Path | None = None,
    target_root: Path | None = None,
    sensitive: bool = False,
) -> dict[str, str]:
    configured = artifact_dir or Path(os.environ.get("LOOM_OUTPUT_ARTIFACT_DIR", DEFAULT_OUTPUT_ARTIFACT_DIR))
    configured_locator = configured.as_posix()
    if configured.is_absolute() or target_root is None or not is_global_runtime_locator(configured_locator):
        root = configured if configured.is_absolute() else ((target_root or Path.cwd()) / configured)
    else:
        root = global_runtime_path(target_root, configured_locator)
    root.mkdir(parents=True, exist_ok=True)
    command = str(payload.get("command", "loom-output"))
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", command).strip("-") or "loom-output"
    rendered = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:12]
    path = root / f"{now_iso().replace(':', '').replace('+', 'Z')}-{slug}-{digest}.json"
    artifact = {
        "schema_version": OUTPUT_ARTIFACT_SCHEMA,
        "generated_at": now_iso(),
        "command": command,
        "sensitive": sensitive,
        "payload": payload,
    }
    artifact_bytes = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(artifact_bytes)
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    locator = str(path)
    if target_root is not None and not configured.is_absolute():
        if is_global_runtime_locator(configured_locator):
            locator = f"{configured_locator.rstrip('/')}/{path.name}"
            return {"artifact_locator": locator, "artifact_sha256": artifact_sha256}
        try:
            locator = str(path.relative_to(target_root))
        except ValueError:
            pass
    return {"artifact_locator": locator, "artifact_sha256": artifact_sha256}


def write_output_artifact(
    payload: dict[str, Any],
    *,
    artifact_dir: Path | None = None,
    target_root: Path | None = None,
    sensitive: bool = False,
) -> str:
    return write_output_artifact_metadata(
        payload,
        artifact_dir=artifact_dir,
        target_root=target_root,
        sensitive=sensitive,
    )["artifact_locator"]


def agent_safe_payload(
    payload: dict[str, Any],
    *,
    stdout_budget_bytes: int | None = None,
    summary_target_bytes: int | None = None,
    artifact_dir: Path | None = None,
    target_root: Path | None = None,
    sensitive: bool = False,
    full_output: bool = False,
) -> dict[str, Any]:
    if full_output:
        return payload
    stdout_budget_bytes = stdout_budget_bytes or positive_int_env(
        "LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES",
        DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES,
    )
    summary_target_bytes = summary_target_bytes or positive_int_env(
        "LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES",
        DEFAULT_AGENT_SAFE_SUMMARY_TARGET_BYTES,
    )
    actionable_findings = output_actionable_findings(payload)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    over_budget = len(rendered.encode("utf-8")) > stdout_budget_bytes
    if not over_budget and not should_use_actionable_envelope(payload, actionable_findings):
        return payload
    artifact_metadata = write_output_artifact_metadata(
        payload,
        artifact_dir=artifact_dir,
        target_root=target_root,
        sensitive=sensitive,
    )
    summary = truncate_utf8(
        str(payload.get("summary") or "Full output exceeded the agent-safe stdout budget."),
        summary_target_bytes,
    )
    envelope_actionable_findings = (
        [budget_actionable_finding(finding) for finding in actionable_findings[:3]]
        if over_budget
        else actionable_findings
    )
    envelope_fields = {
        "actionable_findings": envelope_actionable_findings,
        "diagnostic_counts": output_diagnostic_counts(payload),
        "key_locators": output_key_locators(payload),
        "stdout_budget_bytes": stdout_budget_bytes,
        "summary_target_bytes": summary_target_bytes,
    }
    readiness = payload.get("readiness")
    if isinstance(readiness, dict):
        envelope_fields["readiness"] = readiness
    return output_envelope(
        str(payload.get("command", "loom-output")),
        str(payload.get("result", "block")),
        summary=summary,
        key_gaps=output_key_gaps(payload),
        failed_layer=payload.get("failed_layer"),
        fail_closed_reason=payload.get("fail_closed_reason"),
        artifact_locator=artifact_metadata["artifact_locator"],
        artifact_sha256=artifact_metadata["artifact_sha256"],
        full_output_available=True,
        full_output_truncated=True,
        sensitive=sensitive,
        **envelope_fields,
    )


def add_closeout_pr_role_args(flow_args: list[str], args: argparse.Namespace) -> None:
    for flag, value in (
        ("--pr-role", getattr(args, "pr_role", None)),
        ("--implementation-pr", getattr(args, "implementation_pr", None)),
        ("--release-pr", getattr(args, "release_pr", None)),
        ("--carrier-sync-pr", getattr(args, "carrier_sync_pr", None)),
        ("--final-closeout-pr", getattr(args, "final_closeout_pr", None)),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])


def closeout_pr_role_numbers_from_args(args: argparse.Namespace) -> dict[str, int]:
    roles: dict[str, int] = {}
    for role in CLOSEOUT_PR_ROLES:
        value = getattr(args, role, None)
        if value is not None:
            roles[role] = int(value)
    return roles


def closeout_current_pr_input(args: argparse.Namespace) -> int | None:
    requested_role = getattr(args, "pr_role", None)
    role_numbers = closeout_pr_role_numbers_from_args(args)
    if requested_role is not None:
        return role_numbers.get(requested_role, getattr(args, "pr", None))
    for role in ("final_closeout_pr", "carrier_sync_pr", "release_pr", "implementation_pr"):
        if role in role_numbers:
            return role_numbers[role]
    return getattr(args, "pr", None)


def normalize_subprocess_argv(args: list[object] | tuple[object, ...]) -> list[str]:
    """Normalize supported CLI argv scalars and reject ambiguous internal values."""
    normalized: list[str] = []
    for index, value in enumerate(args):
        if value is None or isinstance(value, bool):
            raise TypeError(f"subprocess argv[{index}] must not be {type(value).__name__}")
        if isinstance(value, str):
            normalized.append(value)
            continue
        if isinstance(value, int):
            normalized.append(str(value))
            continue
        if isinstance(value, os.PathLike):
            path_value = os.fspath(value)
            normalized.append(os.fsdecode(path_value) if isinstance(path_value, bytes) else path_value)
            continue
        raise TypeError(
            f"subprocess argv[{index}] has unsupported type {type(value).__name__}; "
            "expected str, int, or os.PathLike"
        )
    return normalized


def run_capture(args: list[object] | tuple[object, ...], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        normalize_subprocess_argv(args),
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_json_or_block(command: str, completed: subprocess.CompletedProcess[str], *, failed_layer: str, fallback_to: list[str]) -> dict[str, Any]:
    raw = completed.stdout or completed.stderr
    if raw:
        try:
            payload = json.loads(raw)
            if payload.get("command") and payload.get("command") != command:
                payload["wrapped_command"] = payload.get("command")
            payload["command"] = command
            return payload
        except json.JSONDecodeError:
            pass
    if completed.returncode != 0:
        return output(
            command,
            "block",
            summary="Delegated command failed.",
            failed_layer=failed_layer,
            fail_closed_reason=raw.strip() if raw else f"{completed.args} failed",
            fallback_to=fallback_to,
        )
    return output(
        command,
        "block",
        summary="Delegated command did not emit JSON.",
        failed_layer=failed_layer,
        fail_closed_reason="invalid JSON from delegated command",
        fallback_to=fallback_to,
    )


def flow_payload(command: str, flow_args: list[str], *, fallback_to: list[str]) -> dict[str, Any]:
    completed = run_capture([sys.executable, str(TOOLS_ROOT / "loom_flow.py"), *flow_args])
    return parse_json_or_block(command, completed, failed_layer="loom-flow", fallback_to=fallback_to)


def host_lifecycle_admission_payload(
    *,
    target: Path,
    issue: int | None,
    fr: int | None = None,
    owner: str | None,
    repo_name: str | None,
    intent: str,
    pr: int | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Use the shared host admission evaluator before a lifecycle entrypoint."""

    target_repo_slug = infer_github_repo(target)
    target_owner, target_repo = target_repo_slug.split("/", 1) if target_repo_slug and "/" in target_repo_slug else (None, None)
    effective_owner = owner or target_owner
    effective_repo = repo_name or target_repo
    if not target_owner or not target_repo or not effective_owner or not effective_repo:
        return {
            "result": "block",
            "lifecycle_state": "missing_subject",
            "primary_remediation": "restore a readable target origin GitHub owner/repo binding before entering execution",
            "carrier_mutations": False,
            "missing_inputs": ["target origin GitHub owner/repo"],
        }
    subject_readback = github_lifecycle_subject_readback(
        target,
        effective_owner,
        effective_repo,
        issue_number=issue,
        fr_number=fr,
        pr_number=pr,
        branch_name=branch or (git_branch_for_target(target) if issue is None and fr is None and pr is None else None),
        intent=intent,
        target_owner=target_owner,
        target_repo=target_repo,
    )
    issue = subject_readback.get("issue_number") if isinstance(subject_readback.get("issue_number"), int) else None
    if subject_readback.get("result") != "pass" or issue is None:
        return {
            "result": "block",
            "lifecycle_state": "missing_subject",
            "primary_remediation": "provide --issue <work-item-or-fr> or bind the branch to one PR with exactly one native closing Work Item",
            "carrier_mutations": False,
            "subject_readback": subject_readback,
            "missing_inputs": list(subject_readback.get("errors") or ["host lifecycle subject"]),
        }
    flow_args = ["github-intake", "admission", "--target", str(target), "--issue", str(issue), "--intent", intent, "--lifecycle-only"]
    flow_args.extend(["--owner", effective_owner, "--repo", effective_repo])
    payload = flow_payload(
        "host-lifecycle-admission",
        flow_args,
        fallback_to=["loom route --target <repo> --issue <fr> --task <work-item scope> --intent build --apply --json"],
    )
    verdict = payload.get("lifecycle_verdict")
    if isinstance(verdict, dict):
        return {**verdict, "subject_readback": subject_readback, "admission": payload}
    return {
        "result": "block",
        "lifecycle_state": "host_unreadable",
        "primary_remediation": "loom route --target <repo> --issue <fr> --task <work-item scope> --intent build --apply --json",
        "carrier_mutations": False,
        "subject_readback": subject_readback,
        "admission": payload,
    }


def emit_flow(command: str, flow_args: list[str], *, fallback_to: list[str]) -> int:
    forwarded_args, full_output = split_agent_output_args(flow_args)
    target = target_root_from_explicit_arg(forwarded_args)
    payload = flow_payload(command, forwarded_args, fallback_to=fallback_to)
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def delegated_payload(command: str, tool_name: str, delegated_args: list[str], *, failed_layer: str, fallback_to: list[str]) -> dict[str, Any]:
    completed = run_capture([sys.executable, str(TOOLS_ROOT / tool_name), *delegated_args])
    return parse_json_or_block(command, completed, failed_layer=failed_layer, fallback_to=fallback_to)


def emit_delegated(command: str, tool_name: str, delegated_args: list[str], *, failed_layer: str, fallback_to: list[str]) -> int:
    forwarded_args, full_output = split_agent_output_args(delegated_args)
    target = target_root_from_explicit_arg(forwarded_args)
    payload = delegated_payload(command, tool_name, forwarded_args, failed_layer=failed_layer, fallback_to=fallback_to)
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def strip_json_flag(argv: list[str]) -> list[str]:
    return [arg for arg in argv if arg != "--json"]


def split_agent_output_args(argv: list[str]) -> tuple[list[str], bool]:
    forwarded: list[str] = []
    full_output = False
    for arg in argv:
        if arg == "--full-output":
            full_output = True
            continue
        forwarded.append(arg)
    return forwarded, full_output


def append_full_output_flag(flow_args: list[str], args: argparse.Namespace) -> None:
    if getattr(args, "full_output", False):
        flow_args.append("--full-output")


def target_root_from_explicit_arg(argv: list[str]) -> Path | None:
    if "--target" in argv or any(arg.startswith("--target=") for arg in argv):
        return target_from_args(argv)
    return None


def target_from_args(argv: list[str]) -> Path:
    for index, arg in enumerate(argv):
        if arg == "--target" and index + 1 < len(argv):
            return resolve_target(argv[index + 1])
        if arg.startswith("--target="):
            return resolve_target(arg.split("=", 1)[1])
    return resolve_target(".")


def global_cli_command_entry(command: str, target: Path, argv: list[str]) -> str:
    forwarded = strip_json_flag(split_agent_output_args(argv)[0])
    if "--target" not in forwarded and not any(arg.startswith("--target=") for arg in forwarded):
        forwarded = [*forwarded, "--target", str(target)]
    return " ".join(["loom", command, *forwarded, "--json"])


def annotate_global_cli_runtime_entrypoint(payload: dict[str, Any], *, command: str, target: Path, argv: list[str]) -> None:
    if target_runtime_provider(target) != RUNTIME_PROVIDER_GLOBAL_CLI:
        return
    entry = global_cli_command_entry(command, target, argv)
    payload["runtime_provider"] = RUNTIME_PROVIDER_GLOBAL_CLI
    payload["current_runtime_entrypoint"] = entry
    if command == "fact-chain":
        fact_chain = payload.get("fact_chain")
        if isinstance(fact_chain, dict):
            old_read_entry = fact_chain.get("read_entry")
            if isinstance(old_read_entry, str) and old_read_entry and old_read_entry != entry:
                payload.setdefault("retained_provenance", []).append(
                    {
                        "kind": "historical-runtime-entrypoint",
                        "locator": old_read_entry,
                        "classification": "retained-provenance",
                        "reason": "installed-state declares global-cli as the current runtime provider",
                    }
                )
            fact_chain["read_entry"] = entry
    elif command == "status":
        payload["status_entrypoint"] = entry
    elif command == "shadow-parity":
        payload["shadow_parity_entrypoint"] = entry
    elif command == "story":
        payload["story_carrier_entrypoint"] = entry


def command_matrix() -> list[dict[str, Any]]:
    return [
        {
            "command": entry["command"],
            "domain": entry["domain"],
            "status": entry["status"],
            "json": entry.get("json", True),
            "summary": entry.get("summary", ""),
            "output_policy": command_output_policy(entry["command"]),
        }
        for entry in COMMANDS
    ]


def command_output_policy(command: str) -> dict[str, Any]:
    full_output_supported = (
        command
        in {
            "init",
            "adopt",
            "route",
            "flow",
            "status",
            "fact-chain",
            "shadow-parity",
            "story",
            "build",
            "pre-review",
            "handoff",
            "retire",
            "closeout",
            "closeout queue status",
            "resume",
            "merge-ready",
            "spec-review",
            "review",
            "check",
            "reconcile",
            "carrier closeout-sync",
        }
        or command.startswith("profile ")
        or command.startswith("checkpoint ")
        or command.startswith("gate ")
        or command.startswith("pr ")
        or command.startswith("merge ")
    )
    return {
        "default_stdout": "agent_safe_summary_or_json_within_budget" if full_output_supported else "direct_json",
        "artifact_on_over_budget": full_output_supported,
        "full_output_flag": "--full-output" if full_output_supported else None,
        "stdout_budget_env": "LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES",
        "summary_target_env": "LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES",
        "artifact_dir_env": "LOOM_OUTPUT_ARTIFACT_DIR",
        "relative_artifact_dir_base": "resolved --target root for target-aware commands; process cwd otherwise",
    }


def normalize_support_marker(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    marker = value.strip().lower().replace("_", "-")
    return marker or None


def extract_declared_support_entries(raw: Any) -> tuple[list[str], list[str]]:
    markers: list[str] = []
    suite_commands: list[str] = []
    if raw is None:
        return markers, suite_commands
    if isinstance(raw, str):
        marker = normalize_support_marker(raw)
        if marker:
            markers.append(marker)
        return markers, suite_commands
    if isinstance(raw, list):
        for item in raw:
            item_markers, item_commands = extract_declared_support_entries(item)
            markers.extend(item_markers)
            suite_commands.extend(item_commands)
        return markers, suite_commands
    if isinstance(raw, dict):
        for key in ("suite_commands", "suite-command-surface", "suite_command_surface"):
            commands = raw.get(key)
            if isinstance(commands, list):
                suite_commands.extend(command for command in commands if isinstance(command, str) and command.strip())
        for key in ("surface", "support", "id", "name"):
            marker = normalize_support_marker(raw.get(key))
            if marker:
                markers.append(marker)
        for key in ("supports", "declared_support", "provided_surfaces"):
            item_markers, item_commands = extract_declared_support_entries(raw.get(key))
            markers.extend(item_markers)
            suite_commands.extend(item_commands)
    return markers, suite_commands


def suite_support_declaration(state: Any) -> tuple[bool, list[str], list[str]]:
    declarations: list[str] = []
    declared_commands: list[str] = []
    if not isinstance(state, dict):
        return False, declarations, declared_commands
    for key in ("declared_support", "supported_surfaces", "provides"):
        markers, commands = extract_declared_support_entries(state.get(key))
        declarations.extend(markers)
        declared_commands.extend(commands)
    layers = state.get("layers", [])
    if isinstance(layers, list):
        for layer in layers:
            if not isinstance(layer, dict):
                continue
            for key in ("declared_support", "supported_surfaces", "provides"):
                markers, commands = extract_declared_support_entries(layer.get(key))
                declarations.extend(markers)
                declared_commands.extend(commands)
    declaration_set = set(declarations)
    declares_surface = bool(declaration_set & SUITE_SUPPORT_MARKERS) or bool(declared_commands)
    required_commands = sorted(set(declared_commands)) if declared_commands else list(IMPLEMENTED_SUITE_COMMANDS)
    return declares_surface, sorted(declaration_set), required_commands


def suite_command_surface_check(state: Any) -> dict[str, Any]:
    declared, declarations, required_commands = suite_support_declaration(state)
    matrix = {entry["command"]: entry for entry in command_matrix()}
    exposed_suite_commands = sorted(command for command, entry in matrix.items() if entry.get("domain") == "suite")
    if not declared:
        return {
            "name": "suite-command-surface",
            "result": "pass",
            "summary": "Suite command support is not declared for this installed-state; doctor does not require the suite surface.",
            "declared_support": False,
            "declarations": declarations,
            "required_commands": [],
            "exposed_commands": exposed_suite_commands,
        }

    schema_errors: list[dict[str, str]] = []
    for command in required_commands:
        entry = matrix.get(command)
        if entry is None:
            schema_errors.append({"command": command, "reason": "missing from loom help --json command matrix"})
            continue
        if entry.get("domain") != "suite":
            schema_errors.append({"command": command, "reason": "command matrix domain is not suite"})
        if entry.get("status") != "implemented":
            schema_errors.append({"command": command, "reason": "declared suite command is not implemented"})
        if entry.get("json") is not True:
            schema_errors.append({"command": command, "reason": "declared suite command does not expose json=true"})
    result = "pass" if not schema_errors else "block"
    return {
        "name": "suite-command-surface",
        "result": result,
        "summary": "Declared suite command surface matches loom help --json." if result == "pass" else "Declared suite command surface disagrees with loom help --json.",
        "declared_support": True,
        "declarations": declarations,
        "required_commands": required_commands,
        "exposed_commands": exposed_suite_commands,
        "help_schema": "loom help --json",
        "schema_errors": schema_errors,
        **({} if result == "pass" else {
            "failed_layer": "suite-command-surface",
            "fallback_to": ["loom repair plan", "loom help --json", "loom suite inspect --target <repo> --item <item> --json"],
        }),
    }


def suite_verify_requirement(state: Any, item: str | None) -> dict[str, Any]:
    required = bool(item)
    sources: list[str] = ["work-item-gate"] if item else []
    configured_item: str | None = None

    def consume(raw: Any, source: str) -> None:
        nonlocal required, configured_item
        if not isinstance(raw, dict):
            return
        suite_value = raw.get("suite_validation", raw.get("suite"))
        if isinstance(suite_value, str) and suite_value.strip().lower() in {"required", "blocking", "full"}:
            required = True
            sources.append(source)
        elif suite_value is True:
            required = True
            sources.append(source)
        candidate_item = raw.get("suite_item") or raw.get("work_item") or raw.get("item")
        if isinstance(candidate_item, str) and candidate_item.strip() and configured_item is None:
            configured_item = candidate_item.strip()

    if isinstance(state, dict):
        for key in ("verify_requirements", "profile_requirements", "gate_requirements"):
            consume(state.get(key), f"installed-state.{key}")
        profile = state.get("profile")
        if isinstance(profile, dict):
            consume(profile.get("requirements"), "installed-state.profile.requirements")
        layers = state.get("layers", [])
        if isinstance(layers, list):
            for index, layer in enumerate(layers, start=1):
                if not isinstance(layer, dict):
                    continue
                layer_id = layer.get("id") if isinstance(layer.get("id"), str) else f"layer[{index}]"
                for key in ("verify_requirements", "profile_requirements", "gate_requirements"):
                    consume(layer.get(key), f"installed-state.{layer_id}.{key}")

    return {
        "required": required,
        "item_id": item or configured_item,
        "sources": sorted(set(sources)),
        "summary": "suite validation is required for this verify invocation." if required else "suite validation is not required for this verify invocation.",
    }


def suite_validation_check(target: Path, item: str | None) -> dict[str, Any]:
    if not item:
        return {
            "name": "suite-validation",
            "result": "block",
            "summary": "Suite validation is required but no Work Item was provided.",
            "missing_inputs": ["suite_validation_item"],
            "failed_layer": "suite-verify-requirement",
            "fail_closed_reason": "suite validation requires --item or installed-state suite_item",
            "fallback_to": ["loom verify --target <repo> --item <item> --json", "loom suite validate --target <repo> --item <item> --json"],
        }
    summary, result, payload, failed_layer, fail_closed_reason, fallback_to = suite_validate_payload(target, item)
    return {
        "name": "suite-validation",
        "result": result,
        "summary": summary,
        "item_id": item,
        "command": "loom suite validate",
        "mutates": False,
        "failed_layer": failed_layer,
        "fail_closed_reason": fail_closed_reason,
        "missing_inputs": payload.get("missing_inputs", []),
        "blocking_gaps": payload.get("blocking_gaps", []),
        "advisory_gaps": payload.get("advisory_gaps", []),
        "fallback_to": fallback_to,
        "payload": payload,
    }


def print_usage(stream) -> None:
    stream.write(
        "usage: loom <command> [args ...]\n\n"
        "CLI-first Loom control-plane entry.\n\n"
        "core commands:\n"
        "  version [--json]\n"
        "  help [--json]\n"
        "  installed-state show|validate|export --target <repo> [--json]\n\n"
        "install, provider, and repair commands:\n"
        "  install, doctor, verify, upgrade-plan, repair plan\n"
        "  global-cli repos use the root loom provider and do not expect .loom/bin\n"
        "  repo-local runtime, plugin, and skills payloads are unsupported legacy surfaces\n\n"
        "scenario and gate commands:\n"
        "  init, adopt, route, status, fact-chain, profile, checkpoint, gate\n"
        "  resume, spec-review, review, merge-ready, check\n"
        "  suite inspect --target <repo> --item <item> [--json]\n"
        "  suite scaffold --target <repo> --item <item> [--suite minimal|full] [--apply] [--json]\n\n"
        "  suite validate --target <repo> --item <item> [--json]\n\n"
        "  suite evidence inspect|scaffold|validate --target <repo> --item <item> [--apply] [--json]\n\n"
        "Use `loom help --json` for the full frozen command matrix, including reserved commands.\n"
    )


def handle_version(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom version")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = output(
        "version",
        "pass",
        summary="Loom CLI version context resolved.",
        versions=version_context(),
        version_freshness=version_freshness(),
        command_contract="docs/methodology/harness/cli-command-matrix.md",
    )
    if args.json:
        return emit(payload)
    versions = payload["versions"]
    print(f"loom repo {versions['repo_version']}")
    print(f"skills registry {versions['skills_registry_version']}")
    print(f"plugin surface {versions['plugin_surface_version']}")
    freshness = payload["version_freshness"]
    print(f"action {freshness['action']}")
    if freshness.get("command"):
        print(f"next {freshness['command']}")
    return 0


def handle_help(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom help")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = output(
        "help",
        "pass",
        summary="Task-oriented guidance plus the frozen CLI command matrix.",
        command_count=len(COMMANDS),
        task_routes=HELP_TASK_ROUTES,
        command_tiers=HELP_COMMAND_TIERS,
        commands=command_matrix(),
        output_modes={
            "default": "Use `loom ... --json` for normal agent workflows; JSON is emitted directly only when it fits the effective stdout budget, otherwise stdout contains an agent-safe summary envelope and an artifact locator.",
            "artifact_locator": "Share artifact locators for complete diagnostics instead of pasting full JSON, status tables, or long logs into threads, handoff, review, or closeout text.",
            "full_output": "Pass --full-output on supported command families only for explicit debugging, audit, or blocker classification that requires full JSON diagnostics on stdout.",
            "stdout_budget_bytes_default": DEFAULT_AGENT_SAFE_STDOUT_BUDGET_BYTES,
            "summary_target_bytes_default": DEFAULT_AGENT_SAFE_SUMMARY_TARGET_BYTES,
            "configuration": {
                "stdout_budget_env": "LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES",
                "summary_target_env": "LOOM_AGENT_SAFE_SUMMARY_TARGET_BYTES",
                "artifact_dir_env": "LOOM_OUTPUT_ARTIFACT_DIR",
                "artifact_dir_default": str(DEFAULT_OUTPUT_ARTIFACT_DIR),
                "relative_artifact_dir_base": "resolved --target root for target-aware commands; process cwd otherwise",
            },
            "artifact_lifecycle": "Artifacts are local diagnostic files under the configured artifact directory; they are diagnostic evidence locators, not authored truth carriers.",
        },
        fail_closed_on=[
            "unknown command",
            "reserved command invoked before implementation",
            "delegated wrapper missing",
            "installed-state metadata missing or invalid",
        ],
        fallback_to=[
            "loom help --json",
            "loom installed-state validate --target <repo> --json",
            "legacy delegated wrapper only when command status is delegated",
        ],
    )
    if args.json:
        return emit(payload)
    print_usage(sys.stdout)
    print("\ntask routes:")
    for route in HELP_TASK_ROUTES:
        print(f"  {route['task']:<22} {route['first_command']}")
    print("\ncommands:")
    for entry in COMMANDS:
        print(f"  {entry['command']:<32} {entry['status']:<11} {entry['domain']}")
    return 0


def resolve_target(raw_target: str) -> Path:
    target = Path(raw_target).expanduser()
    if target.is_absolute():
        return target.resolve()
    invocation_cwd = os.environ.get("LOOM_INVOCATION_CWD")
    base = Path(invocation_cwd).expanduser() if invocation_cwd else Path.cwd()
    return (base / target).resolve()


def installed_state_path(target: Path) -> Path | None:
    for filename in STATE_FILENAMES:
        path = target / filename
        if path.exists():
            return path
    return None


def build_installed_state(target: Path, *, host: str, mode: str, skill_id: str | None = None) -> dict[str, Any]:
    if mode != "metadata-only":
        raise ValueError("loom install only supports metadata-only adoption")
    versions = version_context()
    minimum_contract = versions["repo_version"]
    layers: list[dict[str, Any]] = []
    graph_layers: list[str] = []
    graph_edges: list[dict[str, str]] = []
    runtime_provider = RUNTIME_PROVIDER_GLOBAL_CLI
    layers.extend(
        [
            {
                "id": "adoption-metadata",
                "layer_type": "repository-adoption-metadata",
                "installed_path": ".loom/installed-state.json",
                "version_context": {
                    "minimum_loom_contract": minimum_contract,
                    "installed_state_schema": INSTALLED_STATE_SCHEMA,
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["repository adoption truth"],
                "consumes": ["user-skills-provider", "global-cli-provider"],
            },
            {
                "id": "user-skills-provider",
                "layer_type": "user-level-skills-provider",
                "installed_path": "workstation:codex-loom-plugin",
                "version_context": {
                    "minimum_plugin_contract": versions["plugin_surface_version"],
                    "minimum_host_adapter_contract": versions["host_adapter_version"],
                },
                "runtime_state": "ready",
                "upgrade_eligibility": "current",
                "provides": ["Loom scenario skills from user-level Codex plugin"],
                "consumes": [],
            },
            {
                "id": "global-cli-provider",
                "layer_type": GLOBAL_CLI_PROVIDER_LAYER,
                "installed_path": "workstation:loom-cli",
                "version_context": {
                    "package": "@mc-and-his-agents/loom",
                    "minimum_version": minimum_contract,
                },
                "runtime_state": "unknown",
                "upgrade_eligibility": "unknown",
                "provides": ["loom command semantics", "runtime provider"],
                "declared_support": {"commands": list(GLOBAL_CLI_REQUIRED_COMMANDS)},
                "consumes": [],
            },
        ]
    )
    graph_layers.extend(["adoption-metadata", "user-skills-provider", "global-cli-provider"])
    graph_edges.append({"from": "adoption-metadata", "to": "user-skills-provider", "relationship": "requires-external-provider"})
    graph_edges.append({"from": "adoption-metadata", "to": "global-cli-provider", "relationship": "requires-runtime-provider"})
    return {
        "schema_version": INSTALLED_STATE_SCHEMA,
        "installation_id": f"loom-{target.name or 'repo'}",
        "installing_command": "loom install",
        "upgrade_eligibility": "current",
        "runtime_provider": runtime_provider,
        "contract": {
            "minimum_loom_version": minimum_contract,
            "installed_state_schema": INSTALLED_STATE_SCHEMA,
        },
        "provider_requirements": {
            "global_cli": {
                "required": runtime_provider == RUNTIME_PROVIDER_GLOBAL_CLI,
                "provider": "loom-cli",
                "authority": "workstation",
                "package": "@mc-and-his-agents/loom",
                "executable": "loom",
                "version_requirement": minimum_contract,
                "required_commands": list(GLOBAL_CLI_REQUIRED_COMMANDS),
                "compatibility_mode_allowed": False,
            }
        },
        "repo_payload": {
            "mode": "metadata-only",
            "adoption_mode": "light-governance",
            "intentional_absent_paths": [
                ".loom/bin",
                ".loom/runtime",
                ".loom/tmp",
                ".loom/shadow",
                ".loom/status/current.md",
                ".loom/work-items",
                ".loom/progress",
                ".loom/specs",
                ".loom/reviews",
                "plugins/loom/.codex-plugin/plugin.json",
                "plugins/loom/skills",
                ".agents/skills",
                "skills",
            ],
        },
        "skills_provider": {
            "provider": "codex-loom-plugin",
            "scope": "user",
            "required": True,
            "registration_authority": "workstation",
        },
        "layers": layers,
        "installation_graph": {
            "layers": graph_layers,
            "edges": graph_edges,
        },
    }


def installed_layer_paths(target: Path) -> set[str]:
    path = installed_state_path(target)
    if path is None:
        return set()
    try:
        state = read_json(path)
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(state, dict) or state.get("schema_version") != INSTALLED_STATE_SCHEMA:
        return set()
    paths: set[str] = set()
    for layer in state.get("layers", []):
        if not isinstance(layer, dict):
            continue
        installed_path = layer.get("installed_path")
        if isinstance(installed_path, str) and installed_path:
            paths.add(installed_path.rstrip("/"))
    return paths


def installed_state_runtime_provider(state: Any) -> str | None:
    if not isinstance(state, dict):
        return None
    provider = state.get("runtime_provider")
    if isinstance(provider, str) and provider.strip():
        return provider.strip()
    layers = state.get("layers", [])
    if isinstance(layers, list):
        if any(isinstance(layer, dict) and layer.get("layer_type") == GLOBAL_CLI_PROVIDER_LAYER for layer in layers):
            return RUNTIME_PROVIDER_GLOBAL_CLI
        if any(isinstance(layer, dict) and layer.get("installed_path") == ".loom/bin" for layer in layers):
            return RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER
    return None


def target_runtime_provider(target: Path) -> str | None:
    path = installed_state_path(target)
    if path is None:
        return None
    try:
        return installed_state_runtime_provider(read_json(path))
    except (OSError, json.JSONDecodeError):
        return None


def target_adoption_mode(target: Path) -> str | None:
    path = installed_state_path(target)
    if path is None:
        return None
    try:
        state = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict):
        return None
    repo_payload = state.get("repo_payload") if isinstance(state.get("repo_payload"), dict) else {}
    adoption_mode = repo_payload.get("adoption_mode")
    if isinstance(adoption_mode, str) and adoption_mode.strip():
        return adoption_mode.strip()
    if repo_payload.get("mode") == "metadata-only":
        return "light-governance"
    return None


def target_uses_light_governance(target: Path) -> bool:
    return target_adoption_mode(target) in {"light-governance", "attach-only"}


def global_cli_provider_requirement(state: Any) -> dict[str, Any] | None:
    if not isinstance(state, dict):
        return None
    requirements = state.get("provider_requirements")
    if not isinstance(requirements, dict):
        return None
    global_cli = requirements.get("global_cli")
    return global_cli if isinstance(global_cli, dict) else None


def global_cli_provider_check(state: Any) -> dict[str, Any]:
    requirement = global_cli_provider_requirement(state)
    if installed_state_runtime_provider(state) != RUNTIME_PROVIDER_GLOBAL_CLI and not (
        requirement and requirement.get("required") is True
    ):
        return {
            "name": "global-cli-runtime-provider",
            "result": "pass",
            "summary": "Global CLI runtime provider is not required by this installed-state.",
            "required": False,
        }
    command_names = {entry["command"] for entry in COMMANDS if entry.get("status") == "implemented"}
    required_commands = requirement.get("required_commands") if isinstance(requirement, dict) else None
    missing_commands = [
        command
        for command in (required_commands if isinstance(required_commands, list) else GLOBAL_CLI_REQUIRED_COMMANDS)
        if not isinstance(command, str) or command not in command_names
    ]
    return {
        "name": "global-cli-runtime-provider",
        "result": "pass" if not missing_commands else "block",
        "summary": (
            "Global CLI runtime provider requirement is declared and the current CLI exposes the required command surface."
            if not missing_commands
            else "Global CLI runtime provider requirement is declared but required commands are missing."
        ),
        "required": True,
        "authority": "workstation",
        "runtime_provider": RUNTIME_PROVIDER_GLOBAL_CLI,
        "required_commands": required_commands if isinstance(required_commands, list) else GLOBAL_CLI_REQUIRED_COMMANDS,
        "missing_commands": missing_commands,
        "failed_layer": None if not missing_commands else "global-cli-runtime-provider",
        "fallback_to": None if not missing_commands else ["loom help --json", "loom installed-state validate --target <repo> --json"],
    }


def is_managed_path(relative: str, managed_paths: set[str]) -> bool:
    relative = relative.rstrip("/")
    for managed in managed_paths:
        if relative == managed or relative.startswith(f"{managed}/"):
            return True
    return False


def legacy_surface_hints(target: Path) -> list[dict[str, str]]:
    candidates = [
        (".loom/bin", "repo-local-runtime-bin"),
        (".loom/companion/manifest.json", "repo-companion"),
        (".agents/skills", "repo-local-skills"),
        ("skills/registry.json", "full-repo-skills"),
        ("plugins/loom/.codex-plugin/plugin.json", "codex-plugin"),
        ("plugins/loom/.loom-install-status.json", "legacy-installed-surface-status"),
        ("packages/loom-installer/package.json", "legacy-installer-package"),
    ]
    hints = []
    for relative, kind in candidates:
        if (target / relative).exists():
            hints.append({"kind": kind, "path": relative})
    return hints


def relative_to_target(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def surface(path: Path, target: Path, *, kind: str, layer: str, authority: str, migration: str, summary: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "layer": layer,
        "path": relative_to_target(path, target),
        "authority": authority,
        "migration_status": migration,
        "is_symlink": path.is_symlink(),
        "summary": summary,
    }


def detect_surfaces(target: Path) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    state_path = installed_state_path(target)
    managed_paths = installed_layer_paths(target)
    runtime_provider = target_runtime_provider(target)
    if state_path is not None:
        surfaces.append(
            surface(
                state_path,
                target,
                kind="installed-state-v2",
                layer="installation-metadata",
                authority="loom-cli",
                migration="current",
                summary="Versioned installed-state metadata is present.",
            )
        )

    candidates = (
        (
            ".loom/bin",
            "legacy-loom-bin",
            "runtime",
            "repo-local-runtime",
            "legacy",
            "Legacy bootstrapped runtime wrappers are present.",
        ),
        (
            ".loom/bootstrap/manifest.json",
            "bootstrap-manifest",
            "runtime",
            "repo-local-runtime",
            "legacy",
            "Bootstrap manifest is present without being authoritative installed-state metadata.",
        ),
        (
            ".loom/companion/manifest.json",
            "repo-companion",
            "governance-residue",
            "repo-companion",
            "read-only",
            "Repo companion residue is present and must remain repo-owned.",
        ),
        (
            ".agents/skills",
            "repo-local-agents-skills",
            "skills",
            "repo-local",
            "legacy",
            "Repo-local .agents/skills layout is present.",
        ),
        (
            "skills/registry.json",
            "full-repo-skills",
            "skills",
            "target-repo-namespace",
            "legacy",
            "Top-level skills registry is present in the target repository namespace.",
        ),
        (
            "plugins/loom/.codex-plugin/plugin.json",
            "codex-plugin",
            "plugin",
            "codex-plugin",
            "legacy",
            "Codex plugin manifest is present.",
        ),
        (
            "plugins/loom/.loom-install-status.json",
            "legacy-installed-surface-status",
            "installation-metadata",
            "installer-shim",
            "legacy",
            "Legacy installer status file is present.",
        ),
        (
            "packages/loom-installer/package.json",
            "legacy-installer-package",
            "installer",
            "installer-shim",
            "legacy",
            "Legacy installer package surface is present.",
        ),
        (
            "SKILL.md",
            "single-skill",
            "skills",
            "single-skill",
            "legacy",
            "Single-skill installation surface is present.",
        ),
    )
    for relative, kind, layer, authority, migration, summary in candidates:
        path = target / relative
        if path.exists():
            if is_managed_path(relative, managed_paths):
                migration = "current"
                authority = "loom-cli"
                summary = f"CLI-managed {summary[0].lower()}{summary[1:]}"
            surfaces.append(surface(path, target, kind=kind, layer=layer, authority=authority, migration=migration, summary=summary))

    skill_dirs = target / "skills"
    if skill_dirs.exists() and skill_dirs.is_dir():
        for skill_path in sorted(skill_dirs.glob("*/SKILL.md")):
            relative = relative_to_target(skill_path, target)
            managed = is_managed_path(relative, managed_paths)
            surfaces.append(
                surface(
                    skill_path,
                    target,
                    kind="single-skill",
                    layer="skills",
                    authority="loom-cli" if managed else "skill-package",
                    migration="current" if managed else "legacy",
                    summary="CLI-managed skill package is present under skills/." if managed else "Standalone skill package is present under skills/.",
                )
            )

    for entry in surfaces:
        if entry["is_symlink"]:
            entry["kind"] = f"symlink-{entry['kind']}"
            entry["migration_status"] = "legacy"
            entry["summary"] = f"Symlinked {entry['summary'][0].lower()}{entry['summary'][1:]}"
    return surfaces


def classify_installation(surfaces: list[dict[str, Any]]) -> tuple[str, str]:
    if not surfaces:
        return "uninstalled", "No Loom installation surfaces were detected."
    has_current = any(item["kind"] == "installed-state-v2" for item in surfaces)
    legacy = [item for item in surfaces if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")]
    authorities = {item.get("authority") for item in surfaces if item.get("authority")}
    if has_current and not legacy:
        return "current", "Versioned installed-state is present and no legacy surface was detected."
    if has_current and legacy:
        return "mixed", "Versioned installed-state and legacy surfaces are both present."
    if len(authorities) > 1 or len(legacy) > 1:
        return "mixed-legacy", "Multiple legacy Loom surface families are present."
    return "legacy", "Only legacy Loom installation surfaces were detected."


def block_target(command: str, target: Path, reason: str) -> dict[str, Any]:
    return output(
        command,
        "block",
        summary="Target cannot be inspected.",
        target=str(target),
        failed_layer="target",
        fail_closed_reason=reason,
        fallback_to=["loom help --json"],
    )


def detect_payload(target: Path) -> dict[str, Any]:
    surfaces = detect_surfaces(target)
    classification, summary = classify_installation(surfaces)
    return output(
        "detect",
        "pass",
        schema=DETECT_SCHEMA,
        summary=summary,
        target=str(target),
        classification=classification,
        surface_count=len(surfaces),
        surfaces=surfaces,
        installed_state_path=str(installed_state_path(target)) if installed_state_path(target) else None,
        fallback_to=None if surfaces else ["loom install"],
    )


def handle_detect(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom detect")
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("detect", target, "target path does not exist"))
    return emit(detect_payload(target))


def doctor_payload(target: Path) -> dict[str, Any]:
    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    freshness = version_freshness()
    checks: list[dict[str, Any]] = [
        {
            "name": "surface-detection",
            "result": "pass" if detection["surface_count"] else "block",
            "summary": detection["summary"],
        }
    ]
    if installed_error is not None:
        checks.append(
            {
                "name": "installed-state",
                "result": "block",
                "summary": installed_error["fail_closed_reason"],
                "failed_layer": "installed-state",
                "fallback_to": ["loom repair plan"],
            }
        )
    elif validation_errors:
        checks.append(
            {
                "name": "installed-state",
                "result": "block",
                "summary": "Installed-state metadata is present but invalid.",
                "errors": validation_errors,
                "failed_layer": "installed-state",
                "fallback_to": ["loom repair plan"],
            }
        )
    else:
        checks.append(
            {
                "name": "installed-state",
                "result": "pass",
                "summary": "Installed-state metadata is valid.",
                "installed_state_path": str(path),
            }
        )
        checks.append(global_cli_provider_check(state))
        checks.append(suite_command_surface_check(state))
    has_codex_plugin_payload = (target / "plugins" / "loom" / ".codex-plugin" / "plugin.json").exists()
    declares_host_adapter = any(isinstance(layer, dict) and layer.get("layer_type") == "host-adapter-plugin" for layer in (state or {}).get("layers", [])) if isinstance(state, dict) else False
    if has_codex_plugin_payload or declares_host_adapter:
        provider_source = global_codex_plugin_source()
        codex_registration = codex_workstation_registration_status(provider_source)
        checks.append(
            {
                "name": "codex-workstation-registration",
                "result": codex_registration["result"],
                "summary": "Codex Desktop workstation registration is present." if codex_registration["result"] == "pass" else "Codex Desktop workstation registration is missing or incomplete.",
                "workstation_registration": codex_registration,
                "failed_layer": None if codex_registration["result"] == "pass" else "workstation-registration",
                "fallback_to": None if codex_registration["result"] == "pass" else ["loom host install --host codex --scope user --apply --json", "loom host register --host codex --scope user --apply --json"],
            }
        )
    legacy_surfaces = [item for item in detection["surfaces"] if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")]
    if legacy_surfaces:
        checks.append(
            {
                "name": "legacy-surfaces",
                "result": "block",
                "summary": "Unsupported legacy Loom surfaces must be removed or migrated before this repository can pass current install diagnostics.",
                "surfaces": legacy_surfaces,
                "fallback_to": ["docs/adoption/codex-install.md", "loom install --target <repo> --apply --json"],
            }
        )
    blocking_checks = [check for check in checks if check["result"] != "pass"]
    result = "pass" if not blocking_checks else "block"
    failed_layer = None if result == "pass" else next((check.get("failed_layer") for check in blocking_checks if check.get("failed_layer")), "installed-surface")
    return output(
        "doctor",
        result,
        schema=DOCTOR_SCHEMA,
        summary="Installed surface diagnostics passed." if result == "pass" else "Installed surface diagnostics found blocking repair inputs.",
        target=str(target),
        detection=detection,
        version_freshness=freshness,
        checks=checks,
        failed_layer=failed_layer,
        fail_closed_reason=None if result == "pass" else "doctor found blocking checks: " + ", ".join(check["name"] for check in blocking_checks),
        fallback_to=None if result == "pass" else ["loom repair plan"],
    )


def handle_doctor(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom doctor")
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("doctor", target, "target path does not exist"))
    return emit(doctor_payload(target))


RUNTIME_CARRIER_BLOCKER_LOCATORS = {
    ".loom/bootstrap/init-result.json",
    ".loom/status/current.md",
    "Makefile",
}

RUNTIME_CARRIER_SCAN_DIRS = (
    ".loom/bootstrap",
    ".loom/status",
    ".loom/work-items",
    ".loom/progress",
    ".loom/specs",
    ".github/workflows",
    "docs",
)

RUNTIME_CARRIER_SCAN_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def runtime_carrier_reference_records(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    matches: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if "python3 .loom/bin/" not in line:
            continue
        matches.append(
            {
                "line": line_number,
                "locator": line.strip(),
            }
        )
    if not matches:
        return []
    relative = relative_to_target(path, target)
    classification = "repo-local-gate-blocker" if relative in RUNTIME_CARRIER_BLOCKER_LOCATORS or relative.startswith(".github/workflows/") else "runtime-carrier-guidance"
    return [
        {
            "path": relative,
            "classification": classification,
            "references": matches,
        }
    ]


def runtime_carrier_reference_scan(target: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocker_records: list[dict[str, Any]] = []
    guidance_records: list[dict[str, Any]] = []
    seen: set[str] = set()
    explicit_files = [target / locator for locator in sorted(RUNTIME_CARRIER_BLOCKER_LOCATORS) if locator != "Makefile"]
    explicit_files.append(target / "Makefile")
    for candidate in explicit_files:
        if not candidate.exists() or not candidate.is_file():
            continue
        relative = relative_to_target(candidate, target)
        seen.add(relative)
        for record in runtime_carrier_reference_records(candidate, target):
            (blocker_records if record["classification"] == "repo-local-gate-blocker" else guidance_records).append(record)
    for relative_dir in RUNTIME_CARRIER_SCAN_DIRS:
        root = target / relative_dir
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else sorted(path for path in root.rglob("*") if path.is_file())
        for candidate in candidates:
            relative = relative_to_target(candidate, target)
            if relative in seen:
                continue
            if candidate.suffix.lower() not in RUNTIME_CARRIER_SCAN_SUFFIXES:
                continue
            seen.add(relative)
            for record in runtime_carrier_reference_records(candidate, target):
                (blocker_records if record["classification"] == "repo-local-gate-blocker" else guidance_records).append(record)
    return blocker_records, guidance_records


def global_cli_runtime_carrier_migration_actions(
    target: Path,
    detection: dict[str, Any],
    *,
    installed_ready: bool,
    state_path: Path | None,
) -> list[dict[str, Any]]:
    if not installed_ready or target_runtime_provider(target) != RUNTIME_PROVIDER_GLOBAL_CLI:
        return []
    retained_surfaces = [
        item for item in detection["surfaces"]
        if item.get("kind") == "retained-loom-bin" and item.get("migration_status") == "repairable-residue"
    ]
    if not retained_surfaces:
        return []
    blocker_records, guidance_records = runtime_carrier_reference_scan(target)
    carrier_update_paths = sorted({record["path"] for record in [*blocker_records, *guidance_records]})
    tracked_runtime_paths = sorted({item.get("path") for item in retained_surfaces if isinstance(item.get("path"), str) and item.get("path")})
    action: dict[str, Any] = {
        "id": "plan-global-cli-runtime-carrier-migration",
        "kind": "runtime-carrier-migration",
        "status": "blocked" if blocker_records else "recommended",
        "reason": (
            "repo-local gate carriers still reference .loom/bin; rewrite those entrypoints before proposing retained runtime deletion."
            if blocker_records
            else "installed-state already declares global-cli as the active runtime provider; retained .loom/bin can only be removed through an explicit apply/confirmation flow."
        ),
        "runtime_provider": RUNTIME_PROVIDER_GLOBAL_CLI,
        "installed_state_path": relative_to_target(state_path, target) if state_path is not None else None,
        "tracked_runtime_paths": tracked_runtime_paths,
        "carrier_update_paths": carrier_update_paths,
        "blocking_references": blocker_records,
        "guidance_references": guidance_records,
        "deletes": tracked_runtime_paths,
        "requires_confirmation": True,
        "command": (
            "rewrite listed repo-local gate carriers to `loom ... --json` entrypoints before planning deletion"
            if blocker_records
            else "review retained runtime residue and require explicit apply/confirmation language before deleting .loom/bin"
        ),
        "mutates": False,
    }
    actions = [action]
    if blocker_records:
        actions.append(
            {
                "id": "block-retained-loom-bin-deletion",
                "kind": "repo-local-gate-blocker",
                "status": "required",
                "blocked_paths": tracked_runtime_paths,
                "blocking_references": blocker_records,
                "reason": "retained .loom/bin cannot be proposed for deletion while repo-local gate carriers still point to repo-local runtime wrappers",
                "command": "rewrite the listed blockers first; keep deletion proposal-only until an explicit apply contract is approved",
                "mutates": False,
            }
        )
    return actions


def repair_actions(target: Path, detection: dict[str, Any], installed_errors: list[dict[str, str]], state_path: Path | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if installed_errors:
        actions.append(
            {
                "id": "repair-installed-state-v2",
                "kind": "write-installed-state",
                "status": "planned",
                "writes": [".loom/installed-state.json"],
                "reason": "installed-state metadata is missing or invalid",
                "command": "loom installed-state validate --target <repo> --json",
            }
        )
    legacy = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]
    repairable = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "repairable-residue"
    ]
    for index, item in enumerate(legacy, start=1):
        actions.append(
            {
                "id": f"classify-legacy-surface-{index}",
                "kind": "manual-migration-judgment",
                "status": "planned",
                "surface": item,
                "reason": "legacy surface must be classified before Loom can apply mutating repair",
                "command": "loom doctor --target <repo> --json",
            }
        )
    if repairable:
        actions.extend(
            global_cli_runtime_carrier_migration_actions(
                target,
                detection,
                installed_ready=not installed_errors,
                state_path=state_path,
            )
        )
    return actions


def repair_plan_payload(target: Path) -> dict[str, Any]:
    return repair_plan_payload_with_carrier(target, item=None, issue=None, output_relative=".loom/bootstrap/init-result.json")


def carrier_repair_flow_payload(
    target: Path,
    action: str,
    *,
    item: str | None,
    issue: int | None,
    output_relative: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    flow_args = ["repair", action, "--target", str(target), "--output", output_relative]
    if item:
        flow_args.extend(["--item", item])
    if issue is not None:
        flow_args.extend(["--issue", str(issue)])
    if dry_run:
        flow_args.append("--dry-run")
    return flow_payload(f"repair {action}", flow_args, fallback_to=["loom carrier closeout-sync --target <repo> --json"])


def repair_plan_payload_with_carrier(
    target: Path,
    *,
    item: str | None,
    issue: int | None,
    output_relative: str,
) -> dict[str, Any]:
    detection = detect_payload(target)
    state_path, state, installed_error = load_installed_state(target)
    installed_errors = [{"path": "installed-state", "reason": installed_error["fail_closed_reason"]}] if installed_error else validate_installed_state(state)
    actions = repair_actions(target, detection, installed_errors, state_path)
    migration_action = downstream_top_level_skills_migration_action(target)
    if migration_action:
        actions.append(migration_action)
    registration_action = workstation_registration_action(target)
    if registration_action:
        actions.append(registration_action)
    has_installed_surface_actions = bool(actions)
    carrier_repair = carrier_repair_flow_payload(
        target,
        "plan",
        item=item,
        issue=issue,
        output_relative=output_relative,
    )
    carrier_missing_inputs = carrier_repair.get("missing_inputs")
    carrier_missing_issue_only = (
        item is None
        and issue is None
        and isinstance(carrier_missing_inputs, list)
        and carrier_missing_inputs == ["issue selector is required for safe carrier repair"]
    )
    carrier_actions = carrier_repair.get("actions") if isinstance(carrier_repair.get("actions"), list) else []
    if not (has_installed_surface_actions and carrier_missing_issue_only):
        actions.extend(action for action in carrier_actions if isinstance(action, dict))
    carrier_blocks_plan = carrier_repair.get("result") == "block" and not (has_installed_surface_actions and carrier_missing_issue_only)
    result = "block" if carrier_blocks_plan else "pass" if detection["surface_count"] or actions else "block"
    return output(
        "repair plan",
        result,
        schema=REPAIR_PLAN_SCHEMA,
        summary=(
            "Repair plan generated without mutating target state."
            if result == "pass"
            else "Repair planning is blocked until installed-surface or carrier ownership is unambiguous."
            if carrier_blocks_plan
            else "No installed surface exists to repair."
        ),
        target=str(target),
        mutates=False,
        detection=detection,
        carrier_repair=carrier_repair,
        actions=actions,
        failed_layer=None if result == "pass" else "carrier-repair" if carrier_blocks_plan else "installed-surface",
        fail_closed_reason=None
        if result == "pass"
        else "; ".join(str(message) for message in carrier_repair.get("missing_inputs", []))
        if carrier_blocks_plan
        else "target has no detectable Loom surface",
        fallback_to=None if result == "pass" else ["loom install"],
    )


def handle_repair(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom repair")
    parser.add_argument("action", choices=("plan", "apply"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--output", default=".loom/bootstrap/init-result.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(f"repair {args.action}", target, "target path does not exist"))
    plan = repair_plan_payload_with_carrier(
        target,
        item=args.item,
        issue=args.issue,
        output_relative=args.output,
    )
    if args.action == "plan":
        return emit(plan)
    non_carrier_actions = [
        action
        for action in plan.get("actions", [])
        if isinstance(action, dict) and action.get("kind") != "carrier_closeout_sync"
    ]
    planned_carrier_repair = plan.get("carrier_repair") if isinstance(plan.get("carrier_repair"), dict) else {}
    planned_carrier_updates = planned_carrier_repair.get("versioned_carrier_updates")
    has_planned_carrier_apply = isinstance(planned_carrier_updates, list) and bool(planned_carrier_updates)
    if non_carrier_actions and has_planned_carrier_apply:
        return emit(
            output(
                "repair apply",
                "block",
                schema=REPAIR_PLAN_SCHEMA,
                summary="Safe carrier repair apply is blocked until installed-surface repair actions are resolved.",
                target=str(target),
                mutates=False,
                dry_run=args.dry_run,
                plan=plan,
                carrier_repair=planned_carrier_repair,
                unapplied_actions=non_carrier_actions,
                failed_layer="installed-surface",
                fail_closed_reason="repair apply cannot combine carrier closeout writes with installed-surface repair actions",
                fallback_to=["loom repair plan", "loom installed-state validate --target <repo> --json", "loom doctor"],
            )
        )
    carrier_apply = carrier_repair_flow_payload(
        target,
        "apply",
        item=args.item,
        issue=args.issue,
        output_relative=args.output,
        dry_run=args.dry_run,
    )
    carrier_updates = carrier_apply.get("versioned_carrier_updates")
    has_carrier_apply = isinstance(carrier_updates, list) and bool(carrier_updates)
    if carrier_apply.get("result") == "pass" and has_carrier_apply:
        return emit(
            output(
                "repair apply",
                "pass",
                schema=REPAIR_PLAN_SCHEMA,
                summary=(
                    "Safe carrier repair applied versioned carrier updates."
                    if carrier_apply.get("mutates")
                    else "Safe carrier repair apply dry-run generated versioned carrier updates without mutating target state."
                ),
                target=str(target),
                mutates=bool(carrier_apply.get("mutates")),
                dry_run=bool(carrier_apply.get("dry_run")),
                plan=plan,
                carrier_repair=carrier_apply,
                host_mutations=False,
                host_actions=[],
                versioned_carrier_updates=carrier_updates,
                unapplied_actions=non_carrier_actions,
                failed_layer=None,
                fail_closed_reason=None,
                fallback_to=None,
            )
        )
    if carrier_apply.get("result") == "block":
        return emit(
            output(
                "repair apply",
                "block",
                schema=REPAIR_PLAN_SCHEMA,
                summary="Safe carrier repair apply is blocked until host-complete carrier ownership is unambiguous.",
                target=str(target),
                mutates=False,
                dry_run=args.dry_run,
                plan=plan,
                carrier_repair=carrier_apply,
                failed_layer="carrier-repair",
                fail_closed_reason="; ".join(str(message) for message in carrier_apply.get("missing_inputs", [])),
                fallback_to=["loom repair plan", "loom carrier closeout-sync --target <repo> --json"],
            )
        )
    return emit(
        output(
            "repair apply",
            "block",
            schema=REPAIR_PLAN_SCHEMA,
            summary="Mutating installed-surface repair apply remains disabled; no safe carrier closeout repair action was available.",
            target=str(target),
            mutates=False,
            dry_run=args.dry_run,
            plan=plan,
            failed_layer="repair-apply",
            fail_closed_reason="repair apply is currently limited to safe carrier closeout sync actions",
            fallback_to=["loom repair plan", "loom doctor"],
        )
    )


def global_codex_plugin_source() -> Path:
    return REPO_ROOT / "plugins" / "loom"


def resolve_codex_plugin_source(raw_source: str | None) -> tuple[Path, str]:
    if raw_source:
        return resolve_target(raw_source), "explicit-source"
    return global_codex_plugin_source(), "global-loom-package"


def generate_source_skills_payload(target: Path) -> list[str]:
    if target.resolve() != REPO_ROOT.resolve():
        raise RuntimeError("skills generate is source-repo only and never writes downstream repository skills payload")
    completed = run_capture([sys.executable, str(TOOLS_ROOT / "skills_surface.py"), "generate"])
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "skills generation failed")
    return ["skills", "plugins/loom/skills"]


def ensure_agents_bootstrap(target: Path) -> str:
    agents_path = target / "AGENTS.md"
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    block = LOOM_BOOTSTRAP_BLOCK.rstrip() + "\n"
    if LOOM_BOOTSTRAP_START in existing and LOOM_BOOTSTRAP_END in existing:
        pattern = re.compile(
            rf"{re.escape(LOOM_BOOTSTRAP_START)}.*?{re.escape(LOOM_BOOTSTRAP_END)}",
            re.DOTALL,
        )
        updated = pattern.sub(block.rstrip(), existing)
    elif existing.strip():
        updated = existing.rstrip() + "\n\n" + block
    else:
        updated = block
    agents_path.write_text(updated, encoding="utf-8")
    return relative_to_target(agents_path, target)


def verify_cli_managed_surfaces(target: Path, *, host: str) -> tuple[bool, list[dict[str, str]]]:
    checks: list[dict[str, str]] = []

    def check(relative: str, kind: str) -> None:
        path = target / relative
        checks.append({"kind": kind, "path": relative, "status": "pass" if path.exists() else "missing"})

    check(".loom/installed-state.json", "installed-state")
    if host != "codex":
        checks.append({"kind": "host-provider", "path": host, "status": "unsupported"})
    for relative in ("plugins/loom", "plugins/loom/skills", ".agents/skills", "skills", ".loom/bin", ".loom/bootstrap"):
        path = target / relative
        checks.append(
            {
                "kind": "intentional-absent-surface",
                "path": relative,
                "status": "unexpected" if path.exists() else "pass",
            }
        )
    return all(item["status"] == "pass" for item in checks), checks


def installed_state_declared_mode(target: Path) -> str | None:
    state_path = installed_state_path(target)
    if state_path is None:
        return None
    try:
        state = read_json(state_path)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict):
        return None
    repo_payload = state.get("repo_payload")
    if isinstance(repo_payload, dict):
        mode = repo_payload.get("mode")
        if mode in {"metadata-only", "embedded", "plugin", "full-repo", "skill"}:
            return "plugin" if mode == "embedded" else str(mode)
    layers = state.get("layers", []) if isinstance(state, dict) else []
    if any(
        isinstance(layer, dict)
        and layer.get("layer_type") == "user-level-skills-provider"
        and str(layer.get("installed_path", "")).startswith("workstation:")
        for layer in layers
    ):
        return "metadata-only"
    if any(
        isinstance(layer, dict)
        and layer.get("layer_type") in {"plugin-embedded-skills", "host-adapter-plugin"}
        and str(layer.get("installed_path", "")).startswith("plugins/loom")
        for layer in layers
    ):
        return "plugin"
    return None


def declares_plugin_mode(target: Path) -> bool:
    return installed_state_declared_mode(target) == "plugin"


def declares_metadata_only_mode(target: Path) -> bool:
    return installed_state_declared_mode(target) == "metadata-only"


def top_level_skills_assessment(target: Path) -> dict[str, Any] | None:
    skills_root = target / "skills"
    registry_path = skills_root / "registry.json"
    if not registry_path.exists():
        return None
    expected_registry = read_optional_json(PLUGIN_SKILLS_ROOT / "registry.json") or {}
    actual_registry = read_optional_json(registry_path) or {}
    expected_ids = {
        entry.get("id")
        for entry in expected_registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    actual_ids = {
        entry.get("id")
        for entry in actual_registry.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    skill_dirs = {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }
    unknown_ids = sorted((actual_ids | skill_dirs) - expected_ids)
    missing_ids = sorted(expected_ids - actual_ids)
    if actual_ids == expected_ids and skill_dirs <= expected_ids:
        ownership = "loom-generated"
        result = "migration-recommended"
        summary = "Top-level skills appears to be Loom-generated residue from the old downstream plugin layout."
    else:
        ownership = "mixed-or-target-owned"
        result = "manual-review-required"
        summary = "Top-level skills cannot be proven Loom-owned and must not be removed automatically."
    return {
        "path": "skills",
        "ownership": ownership,
        "result": result,
        "unknown_skill_ids": unknown_ids,
        "missing_loom_skill_ids": missing_ids,
        "summary": summary,
    }


def downstream_top_level_skills_migration_action(target: Path) -> dict[str, Any] | None:
    if not declares_plugin_mode(target):
        return None
    assessment = top_level_skills_assessment(target)
    if assessment is None:
        return None
    if assessment["ownership"] == "loom-generated":
        return {
            "id": "plan-top-level-loom-skills-migration",
            "kind": "legacy-plugin-layout-migration",
            "status": "recommended",
            "surface": assessment,
            "reason": "plugin mode now uses plugins/loom/skills; downstream top-level Loom skills is legacy residue",
            "command": "review target-owned skills/ before any explicit removal; do not delete automatically",
            "mutates": False,
        }
    return {
        "id": "review-top-level-skills-ownership",
        "kind": "manual-migration-judgment",
        "status": "required",
        "surface": assessment,
        "reason": "target repository skills/ ownership is mixed or unknown",
        "command": "inspect skills/ before planning any migration",
        "mutates": False,
    }


def codex_workstation_paths(home: Path | None = None, codex_home: Path | None = None) -> dict[str, Path | str]:
    resolved_home = (home or Path.home()).expanduser().resolve()
    resolved_codex_home = Path(os.environ.get("CODEX_HOME", str(resolved_home / ".codex"))).expanduser().resolve()
    if codex_home is not None:
        resolved_codex_home = codex_home.expanduser().resolve()
    marketplace_name = "local-user-plugins"
    return {
        "home": resolved_home,
        "codex_home": resolved_codex_home,
        "marketplace_name": marketplace_name,
        "marketplace_root": resolved_home,
        "marketplace_path": resolved_home / ".agents" / "plugins" / "marketplace.json",
        "plugin_cache_path": resolved_home / "plugins" / "loom",
        "config_path": resolved_codex_home / "config.toml",
        "config_plugin_key": f"loom@{marketplace_name}",
    }


def codex_marketplace_plugin_entry() -> dict[str, Any]:
    return {
        "name": "loom",
        "source": {
            "source": "local",
            "path": "./plugins/loom",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }


def codex_payload_metadata(path: Path, *, layer: str) -> dict[str, Any]:
    manifest_path = path / ".codex-plugin" / "plugin.json"
    parse_error = None
    try:
        manifest = read_optional_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        manifest = None
        parse_error = f"{type(exc).__name__}: {exc}"
    x_loom = manifest.get("x-loom", {}) if isinstance(manifest, dict) and isinstance(manifest.get("x-loom"), dict) else {}
    version = x_loom.get("plugin_payload_version")
    digest = x_loom.get("plugin_payload_hash")
    payload = {
        "layer": layer,
        "path": str(path),
        "manifest": str(manifest_path),
        "status": "present" if manifest_path.exists() else "missing",
        "plugin_surface_version": x_loom.get("plugin_surface_version"),
        "plugin_payload_version": version,
        "plugin_payload_hash": digest,
        "source_package": x_loom.get("source_package"),
        "source_package_version": x_loom.get("source_package_version"),
        "source_git_sha": x_loom.get("source_git_sha"),
        "metadata_complete": isinstance(version, str) and bool(version) and isinstance(digest, str) and bool(digest),
    }
    if parse_error:
        payload["error"] = parse_error
    return payload


def latest_codex_runtime_cache(paths: dict[str, Path | str], *, surface_version: str | None = None) -> Path | None:
    root = Path(paths["codex_home"]) / "plugins" / "cache" / str(paths["marketplace_name"]) / "loom"
    if not root.exists():
        return None
    if surface_version:
        candidate = root / surface_version
        if (candidate / ".codex-plugin" / "plugin.json").exists():
            return candidate
    candidates = [path for path in root.iterdir() if (path / ".codex-plugin" / "plugin.json").exists()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def codex_plugin_payload_readback(source: Path, paths: dict[str, Path | str]) -> dict[str, Any]:
    source_payload = codex_payload_metadata(source, layer="source-payload")
    marketplace_payload = codex_payload_metadata(Path(paths["plugin_cache_path"]), layer="marketplace-source")
    surface_version = (
        marketplace_payload.get("plugin_surface_version")
        if isinstance(marketplace_payload.get("plugin_surface_version"), str)
        else source_payload.get("plugin_surface_version")
    )
    runtime_path = latest_codex_runtime_cache(paths, surface_version=surface_version if isinstance(surface_version, str) else None)
    runtime_payload = codex_payload_metadata(runtime_path, layer="runtime-cache") if runtime_path else {
        "layer": "runtime-cache",
        "path": str(Path(paths["codex_home"]) / "plugins" / "cache" / str(paths["marketplace_name"]) / "loom"),
        "status": "missing",
        "metadata_complete": False,
    }
    layers = [source_payload, marketplace_payload, runtime_payload]

    missing_metadata = [layer["layer"] for layer in layers if layer.get("status") == "present" and not layer.get("metadata_complete")]
    if source_payload["status"] != "present" or not source_payload["metadata_complete"]:
        freshness = "source_metadata_missing"
        action = "install_cli"
        command = "npm install -g @mc-and-his-agents/loom"
    elif marketplace_payload["status"] != "present":
        freshness = "marketplace_source_missing"
        action = "install_plugin"
        command = "loom host install --host codex --scope user --apply --json"
    elif not marketplace_payload["metadata_complete"]:
        freshness = "marketplace_source_metadata_missing"
        action = "install_plugin"
        command = "loom host install --host codex --scope user --apply --json"
    elif (
        marketplace_payload.get("plugin_payload_version") != source_payload.get("plugin_payload_version")
        or marketplace_payload.get("plugin_payload_hash") != source_payload.get("plugin_payload_hash")
    ):
        freshness = "marketplace_source_stale"
        action = "install_plugin"
        command = "loom host install --host codex --scope user --apply --json"
    elif runtime_payload["status"] != "present":
        freshness = "runtime_cache_missing"
        action = "reload_host"
        command = "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded."
    elif not runtime_payload.get("metadata_complete"):
        freshness = "runtime_cache_metadata_missing"
        action = "reload_host"
        command = "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded."
    elif (
        runtime_payload.get("plugin_payload_version") != marketplace_payload.get("plugin_payload_version")
        or runtime_payload.get("plugin_payload_hash") != marketplace_payload.get("plugin_payload_hash")
    ):
        freshness = "runtime_cache_stale"
        action = "reload_host"
        command = "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded."
    else:
        freshness = "already_current"
        action = "already_current"
        command = None

    return {
        "schema": "loom-codex-plugin-payload-readback/v1",
        "result": "pass" if freshness == "already_current" else "block",
        "freshness": freshness,
        "action": action,
        "command": command,
        "layers": layers,
        "missing_metadata": missing_metadata,
        "authority_boundary": {
            "source_payload": "Loom package payload selected by --source or the global Loom package",
            "marketplace_source": "Codex local user marketplace source managed by `loom host install`",
            "runtime_cache": "Codex-owned loaded plugin cache; Loom only reads it and asks the user to reload Codex when stale",
        },
    }


def codex_workstation_plugin_install_status(source: Path | None = None) -> dict[str, Any]:
    source = source or global_codex_plugin_source()
    paths = codex_workstation_paths()
    plugin_cache_path = paths["plugin_cache_path"]
    source_manifest = source / ".codex-plugin" / "plugin.json"
    plugin_cache_manifest = Path(plugin_cache_path) / ".codex-plugin" / "plugin.json"
    checks: list[dict[str, Any]] = [
        {
            "name": "source-payload",
            "result": "pass" if source_manifest.exists() else "block",
            "path": str(source_manifest),
            "summary": "Codex plugin payload source is readable." if source_manifest.exists() else "Codex plugin payload source is missing.",
        }
    ]
    cache_ok = plugin_cache_manifest.exists()
    checks.append(
        {
            "name": "user-plugin-cache",
            "result": "pass" if cache_ok else "block",
            "path": str(plugin_cache_path),
            "summary": "User plugin cache contains a Loom plugin payload." if cache_ok else "User plugin cache is missing the Loom plugin payload.",
        }
    )
    blocking = [check for check in checks if check["result"] != "pass"]
    payload_readback = codex_plugin_payload_readback(source, paths)
    return {
        "schema": WORKSTATION_SCHEMA,
        "host": "codex",
        "scope": "user",
        "source": str(source),
        "source_kind": "global-loom-package" if source.resolve() == global_codex_plugin_source().resolve() else "explicit-source",
        "status": "installed" if not blocking else "missing",
        "result": "pass" if not blocking else "block",
        "paths": {key: str(value) for key, value in paths.items() if isinstance(value, Path)},
        "checks": checks,
        "plugin_payload_readback": payload_readback,
        "authority_boundary": {
            "kind": "developer-workstation-plugin-cache",
            "does_not_write_repo_truth": True,
        },
    }


def codex_workstation_registration_status(source: Path | None = None) -> dict[str, Any]:
    source = source or global_codex_plugin_source()
    paths = codex_workstation_paths()
    marketplace_path = paths["marketplace_path"]
    config_path = paths["config_path"]
    marketplace_name = str(paths["marketplace_name"])
    config_plugin_key = str(paths["config_plugin_key"])
    expected_source = codex_marketplace_plugin_entry()["source"]
    install_status = codex_workstation_plugin_install_status(source)
    checks: list[dict[str, Any]] = list(install_status["checks"])

    marketplace_entry = None
    marketplace_error = None
    marketplace = None
    if Path(marketplace_path).exists():
        try:
            marketplace = read_json(Path(marketplace_path))
            plugins = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
            marketplace_entry = next((entry for entry in plugins if isinstance(entry, dict) and entry.get("name") == "loom"), None)
        except (OSError, json.JSONDecodeError) as exc:
            marketplace_error = str(exc)
    marketplace_ok = (
        isinstance(marketplace, dict)
        and marketplace.get("name") == marketplace_name
        and isinstance(marketplace_entry, dict)
        and marketplace_entry.get("source") == expected_source
    )
    checks.append(
        {
            "name": "user-marketplace-entry",
            "result": "pass" if marketplace_ok else "block",
            "path": str(marketplace_path),
            "marketplace_name": marketplace.get("name") if isinstance(marketplace, dict) else None,
            "entry": marketplace_entry,
            "summary": "Codex personal marketplace contains the Loom plugin entry." if marketplace_ok else "Codex personal marketplace is missing the Loom plugin entry.",
            "error": marketplace_error,
        }
    )

    config_data = None
    config_error = None
    if Path(config_path).exists():
        try:
            config_data = parse_toml_text(Path(config_path).read_text(encoding="utf-8"))
        except (OSError, TomlDecodeError, ValueError) as exc:
            config_error = str(exc)
    marketplaces = config_data.get("marketplaces", {}) if isinstance(config_data, dict) else {}
    plugins = config_data.get("plugins", {}) if isinstance(config_data, dict) else {}
    marketplace_config = marketplaces.get(marketplace_name) if isinstance(marketplaces, dict) else None
    plugin_config = plugins.get(config_plugin_key) if isinstance(plugins, dict) else None
    config_enabled = isinstance(plugin_config, dict) and plugin_config.get("enabled") is True
    config_marketplace_ok = isinstance(marketplace_config, dict) and marketplace_config.get("source_type") == "local" and str(marketplace_config.get("source")) == str(paths["marketplace_root"])
    checks.append(
        {
            "name": "codex-config-marketplace",
            "result": "pass" if config_marketplace_ok else "block",
            "path": str(config_path),
            "marketplace": marketplace_name,
            "summary": "Codex config points at the local user plugin marketplace." if config_marketplace_ok else "Codex config is missing the local user plugin marketplace.",
            "error": config_error,
        }
    )
    checks.append(
        {
            "name": "codex-config-enabled",
            "result": "pass" if config_enabled else "block",
            "path": str(config_path),
            "plugin": config_plugin_key,
            "enabled": config_enabled,
            "summary": "Codex config enables the Loom plugin." if config_enabled else "Codex config does not enable the Loom plugin.",
            "error": config_error,
        }
    )

    blocking = [check for check in checks if check["result"] != "pass"]
    return {
        "schema": WORKSTATION_SCHEMA,
        "host": "codex",
        "scope": "user",
        "source": str(source),
        "source_kind": install_status["source_kind"],
        "status": "registered" if not blocking else "missing",
        "result": "pass" if not blocking else "block",
        "paths": {key: str(value) for key, value in paths.items() if isinstance(value, Path)},
        "marketplace_name": marketplace_name,
        "config_plugin_key": config_plugin_key,
        "checks": checks,
        "plugin_payload_readback": install_status.get("plugin_payload_readback"),
        "reload_required": True,
        "reload_guidance": "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded.",
        "authority_boundary": {
            "kind": "developer-workstation-registration-state",
            "does_not_write_repo_truth": True,
            "repo_payload_verify_command": "loom host verify --host codex --target <repo> --json",
        },
    }


def update_codex_marketplace(marketplace_path: Path) -> None:
    if marketplace_path.exists():
        marketplace = read_json(marketplace_path)
        if not isinstance(marketplace, dict):
            raise RuntimeError(f"marketplace is not a JSON object: {marketplace_path}")
    else:
        marketplace = {
            "name": "local-user-plugins",
            "interface": {
                "displayName": "Local User Plugins",
            },
            "plugins": [],
        }
    marketplace.setdefault("name", "local-user-plugins")
    marketplace.setdefault("interface", {"displayName": "Local User Plugins"})
    plugins = marketplace.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise RuntimeError(f"marketplace plugins must be an array: {marketplace_path}")
    entry = codex_marketplace_plugin_entry()
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == "loom":
            plugins[index] = entry
            break
    else:
        plugins.append(entry)
    write_json(marketplace_path, marketplace)


def set_toml_table_value(text: str, table: str, assignments: dict[str, str]) -> str:
    lines = text.splitlines()
    header = f"[{table}]"
    start = next((index for index, line in enumerate(lines) if line.strip() == header), None)
    rendered = [f"{key} = {value}" for key, value in assignments.items()]
    if start is None:
        prefix = lines + ([""] if lines and lines[-1] else [])
        return "\n".join([*prefix, header, *rendered]) + "\n"
    end = start + 1
    while end < len(lines) and not (lines[end].startswith("[") and lines[end].endswith("]")):
        end += 1
    body = lines[start + 1 : end]
    remaining = dict(assignments)
    updated_body = []
    for line in body:
        stripped = line.strip()
        key = stripped.split("=", 1)[0].strip() if "=" in stripped else None
        if key in remaining:
            updated_body.append(f"{key} = {remaining.pop(key)}")
        else:
            updated_body.append(line)
    updated_body.extend(f"{key} = {value}" for key, value in remaining.items())
    return "\n".join([*lines[: start + 1], *updated_body, *lines[end:]]) + "\n"


def update_codex_config(config_path: Path, marketplace_root: Path, marketplace_name: str, plugin_key: str) -> None:
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    text = set_toml_table_value(
        text,
        f"marketplaces.{marketplace_name}",
        {
            "last_updated": json.dumps(now_iso()),
            "source_type": json.dumps("local"),
            "source": json.dumps(str(marketplace_root)),
        },
    )
    text = set_toml_table_value(text, f'plugins."{plugin_key}"', {"enabled": "true"})
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text, encoding="utf-8")


def install_codex_workstation_plugin(source: Path) -> list[str]:
    paths = codex_workstation_paths()
    if not (source / ".codex-plugin" / "plugin.json").exists():
        raise RuntimeError(f"Codex plugin source is missing .codex-plugin/plugin.json: {source}")
    plugin_cache_path = Path(paths["plugin_cache_path"])
    if source.resolve() == global_codex_plugin_source().resolve():
        with tempfile.TemporaryDirectory(prefix="loom-plugin-install-") as tmp:
            output = Path(tmp) / "distribution"
            build_distribution.build(output)
            copy_tree(output / "plugins" / "loom", plugin_cache_path)
    else:
        copy_tree(source, plugin_cache_path)
    return [str(plugin_cache_path)]


def register_codex_workstation(source: Path) -> list[str]:
    paths = codex_workstation_paths()
    writes = install_codex_workstation_plugin(source)
    update_codex_marketplace(Path(paths["marketplace_path"]))
    update_codex_config(Path(paths["config_path"]), Path(paths["marketplace_root"]), str(paths["marketplace_name"]), str(paths["config_plugin_key"]))
    writes.extend([str(paths["marketplace_path"]), str(paths["config_path"])])
    return writes


def workstation_registration_action(target: Path, source: Path | None = None) -> dict[str, Any] | None:
    plugin_source = source or global_codex_plugin_source()
    repo_ok, _ = verify_cli_managed_surfaces(target, host="codex")
    registration = codex_workstation_registration_status(plugin_source)
    if repo_ok and registration["result"] != "pass":
        return {
            "id": "register-codex-workstation-plugin",
            "kind": "workstation-registration",
            "status": "recommended",
            "reason": "repository adoption metadata is current, but Codex Desktop workstation registration is missing",
            "command": "loom host register --host codex --scope user --dry-run --json",
            "apply_command": "loom host register --host codex --scope user --apply --json",
            "mutates": False,
            "apply_mutates": True,
            "reload_required": registration["reload_required"],
            "reload_note": registration["reload_guidance"],
        }
    return None


def host_plugin_refresh_boundary_action(host: str = "codex") -> dict[str, Any] | None:
    if host != "codex":
        return None
    return {
        "id": "host-plugin-refresh-boundary",
        "kind": "host-provider-guidance",
        "status": "separate-command",
        "reason": (
            "target install/upgrade manages repository installed-state and adoption metadata only; "
            "it does not refresh the Codex workstation plugin cache"
        ),
        "command": "loom host doctor --host codex --scope user --json",
        "apply_commands": [
            "loom host install --host codex --scope user --apply --json",
            "loom host register --host codex --scope user --apply --json",
        ],
    }


def workflow_files(target: Path) -> list[Path]:
    workflow_root = target / ".github" / "workflows"
    if not workflow_root.exists() or not workflow_root.is_dir():
        return []
    return sorted(
        path
        for pattern in ("*.yml", "*.yaml")
        for path in workflow_root.glob(pattern)
        if path.is_file()
    )


def normalize_workflow_version_value(raw: str) -> str:
    value = raw.strip()
    if "#" in value:
        value = value.split("#", 1)[0].strip()
    return value.strip().strip("'\"")


def extract_loom_package_specs(line: str) -> list[str]:
    specs: list[str] = []
    marker = "@mc-and-his-agents/loom@"
    start = 0
    while True:
        index = line.find(marker, start)
        if index == -1:
            return specs
        value = line[index + len(marker):].strip()
        if value.startswith("${{"):
            end = value.find("}}")
            spec = value[: end + 2] if end != -1 else value
        else:
            spec = re.split(r"[\s'\"`]", value, maxsplit=1)[0]
        specs.append(normalize_workflow_version_value(spec))
        start = index + len(marker)


def runtime_upgrade_workflow_pins(target: Path) -> dict[str, Any]:
    pins: list[dict[str, Any]] = []
    direct_specs: list[dict[str, Any]] = []
    for path in workflow_files(target):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            version_match = re.match(r"^(\s*LOOM_VERSION\s*:\s*)(.+?)\s*$", line)
            if version_match:
                pins.append(
                    {
                        "locator": f"{relative_to_target(path, target)}:{index}",
                        "file": relative_to_target(path, target),
                        "line": index,
                        "version": normalize_workflow_version_value(version_match.group(2)),
                        "source": "LOOM_VERSION",
                        "updatable": True,
                    }
                )
            for package_spec in extract_loom_package_specs(line):
                direct_specs.append(
                    {
                        "locator": f"{relative_to_target(path, target)}:{index}",
                        "file": relative_to_target(path, target),
                        "line": index,
                        "version": package_spec,
                        "source": "npm_package_spec",
                        "updatable": False,
                    }
                )
    versions = sorted({pin["version"] for pin in pins})
    return {
        "workflow_files": [relative_to_target(path, target) for path in workflow_files(target)],
        "pins": pins,
        "direct_package_specs": direct_specs,
        "versions": versions,
        "pin_count": len(pins),
        "updatable_pin_count": sum(1 for pin in pins if pin.get("updatable")),
    }


def runtime_upgrade_apply_workflow_pin_update(target: Path, target_version: str) -> list[dict[str, Any]]:
    writes: list[dict[str, Any]] = []
    for path in workflow_files(target):
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        changed = False
        updated_lines: list[str] = []
        for line in raw.splitlines(keepends=True):
            newline = "\n" if line.endswith("\n") else ""
            body = line[:-1] if newline else line
            match = re.match(r"^(\s*LOOM_VERSION\s*:\s*)(.+?)(\s*(#.*)?)$", body)
            if match:
                suffix = match.group(3)
                body = f"{match.group(1)}{target_version}{suffix}"
                changed = True
            updated_lines.append(f"{body}{newline}")
        if changed:
            path.write_text("".join(updated_lines), encoding="utf-8")
            writes.append({"file": relative_to_target(path, target), "version": target_version})
    return writes


def runtime_upgrade_artifact_path(target: Path, item: str | None, suffix: str) -> str:
    safe_item = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(item or "runtime-upgrade")).strip("-") or "runtime-upgrade"
    if not suffix.endswith(".md"):
        suffix = f"{suffix}.md"
    return f".loom/runtime/pr/{safe_item}-{suffix}"


def runtime_upgrade_effective_branch(args: argparse.Namespace, target: Path) -> str | None:
    return args.branch or git_branch_for_target(target)


def runtime_upgrade_effective_head(args: argparse.Namespace, target: Path) -> str | None:
    return args.head_sha or git_head_sha_for_target(target)


def runtime_upgrade_version_label(version: str | None) -> str:
    return str(version or "<version>")


def runtime_upgrade_github_work_item_locator(args: argparse.Namespace) -> str | None:
    issue = str(args.issue or "").strip()
    if re.fullmatch(r"[1-9][0-9]*", issue):
        return f"work_item:{issue}"
    item = str(args.item or "").strip()
    if re.fullmatch(r"work_item:[1-9][0-9]*", item):
        return item
    return None


def runtime_upgrade_pr_metadata_command(args: argparse.Namespace) -> str | None:
    if not args.item:
        return None
    parts = [
        "loom pr metadata-render",
        "--surface merge_ready",
        f"--item {args.item}",
        "--change-class runtime_upgrade",
        "--suite-path not_applicable",
        "--review-requirement current_head_review_required",
        "--release-judgment no_release",
        "--upgrade-trigger runtime_upgrade",
        "--suite-na-rationale workflow-only Loom runtime version pin maintenance",
        "--suite-na-consumer-boundary CI workflow installs the pinned @mc-and-his-agents/loom runtime",
        "--suite-na-recheck-condition workflow pin, PR metadata, head SHA, hosted checks, and carrier closeout change",
        "--suite-na-scope-proof only Loom runtime workflow pin and maintenance carrier surfaces changed",
        "--suite-na-review-requirement current_head_review_required",
    ]
    if args.issue:
        parts.append(f"--issue {args.issue}")
    if args.branch:
        parts.append(f"--branch {args.branch}")
    if args.head_sha:
        parts.append(f"--head-sha {args.head_sha}")
    return " ".join(parts)


def runtime_upgrade_pr_metadata_flow_args(
    args: argparse.Namespace,
    target: Path,
    *,
    action: str,
    surface: str,
    pr: str | None = None,
    output_file: str | None = None,
    readback_file: str | None = None,
) -> list[str]:
    branch = runtime_upgrade_effective_branch(args, target)
    head_sha = runtime_upgrade_effective_head(args, target)
    flow_args = ["pr-metadata", action, "--target", str(target), "--surface", surface]
    for flag, value in (
        ("--pr", pr),
        ("--item", args.item),
        ("--issue", args.issue),
        ("--branch", branch),
        ("--head-sha", head_sha),
    ):
        if value:
            flow_args.extend([flag, str(value)])
    if output_file:
        flow_args.extend(["--output-file", output_file])
    if readback_file:
        flow_args.extend(["--readback-file", readback_file])
    if args.base_body_file:
        flow_args.extend(["--base-body-file", args.base_body_file])
    flow_args.extend(
        [
            "--change-class",
            "runtime_upgrade" if surface == "merge_ready" else "metadata_schema",
            "--suite-path",
            "not_applicable" if surface == "merge_ready" else "minimal",
            "--review-requirement",
            "current_head_review_required",
            "--release-judgment",
            "no_release",
            "--upgrade-trigger",
            "runtime_upgrade",
        ]
    )
    if surface == "closeout":
        flow_args.extend(["--upgrade-trigger", "carrier_sync_only"])
    flow_args.extend(
        [
            "--suite-na-rationale",
            "workflow-only Loom runtime version pin maintenance",
            "--suite-na-consumer-boundary",
            "CI workflow installs the pinned @mc-and-his-agents/loom runtime; carrier-only closeout remains repo metadata only",
            "--suite-na-recheck-condition",
            "workflow pin, PR metadata, head SHA, hosted checks, and carrier closeout change",
            "--suite-na-scope-proof",
            "only Loom runtime workflow pin and maintenance carrier surfaces changed",
            "--suite-na-review-requirement",
            "current_head_review_required",
        ]
    )
    return flow_args


def runtime_upgrade_parse_pr_url(raw: str) -> tuple[str | None, str | None]:
    match = re.search(r"https://github\.com/[^/\s]+/[^/\s]+/pull/(\d+)", raw)
    if match:
        return match.group(1), match.group(0)
    return None, raw.strip() or None


def runtime_upgrade_create_pr_payload(args: argparse.Namespace, target: Path, *, body_file: str) -> dict[str, Any]:
    branch = runtime_upgrade_effective_branch(args, target)
    if not branch:
        return output(
            "runtime-upgrade pr create",
            "block",
            summary="runtime-upgrade pr create requires a branch binding.",
            missing_inputs=["missing branch"],
            fallback_to=["pass --branch <branch> or run from the upgrade branch"],
        )
    title = args.title or f"chore(runtime): upgrade Loom runtime to {runtime_upgrade_version_label(args.to)}"
    command = [
        "gh",
        "pr",
        "create",
        "--base",
        args.base or "main",
        "--head",
        branch,
        "--title",
        title,
        "--body-file",
        str(target / body_file),
    ]
    completed = run_capture(command, cwd=target)
    if completed.returncode != 0:
        return output(
            "runtime-upgrade pr create",
            "block",
            summary="gh pr create failed before PR metadata readback.",
            missing_inputs=[completed.stderr.strip() or completed.stdout.strip() or "gh pr create failed"],
            fallback_to=["create the PR manually, then rerun loom runtime-upgrade pr --pr <n> --update --json"],
        )
    number, url = runtime_upgrade_parse_pr_url(completed.stdout)
    return output(
        "runtime-upgrade pr create",
        "pass",
        summary="runtime-upgrade maintenance PR created; metadata readback must still pass before hosted gate.",
        pr={"number": number, "url": url, "base": args.base or "main", "head": branch},
        host_mutations=True,
        mutates=True,
    )


def runtime_upgrade_issue_payload_from_host(target: Path, *, repo: str | None, issue: str | None) -> dict[str, Any]:
    command = "runtime-upgrade closeout issue-readback"
    if not issue:
        return output(command, "block", summary="Runtime upgrade closeout requires an issue locator.", missing_inputs=["missing issue"], fallback_to=["pass --issue <maintenance-issue>"])
    inspected = flow_payload(
        command,
        [
            "host-binding",
            "inspect",
            "--target",
            str(target),
            "--issue",
            str(issue),
            *release_closeout_repo_flow_args(repo),
        ],
        fallback_to=["loom issue inspect <issue> --json", "pass explicit --pr/--merge-commit/--target-branch/--closed-at"],
    )
    chain = inspected.get("binding_chain") if isinstance(inspected.get("binding_chain"), dict) else {}
    nodes = chain.get("nodes") if isinstance(chain.get("nodes"), dict) else {}
    issue_node = nodes.get("work_item") if isinstance(nodes.get("work_item"), dict) else {}
    issue_payload = issue_node.get("value") if isinstance(issue_node.get("value"), dict) else None
    if not isinstance(issue_payload, dict):
        return output(command, "block", summary="Issue readback payload is invalid.", missing_inputs=["host-binding issue node is missing"], fallback_to=["loom issue inspect <issue> --json", "pass explicit terminal evidence"])
    refs = issue_payload.get("closingPullRequests") or issue_payload.get("closedByPullRequestsReferences")
    pr_number = None
    if isinstance(refs, list) and refs:
        first = refs[0]
        if isinstance(first, dict) and first.get("number") is not None:
            pr_number = str(first["number"])
    missing: list[str] = []
    if str(issue_payload.get("state", "")).upper() != "CLOSED":
        missing.append("issue is not closed")
    if not issue_payload.get("closedAt"):
        missing.append("issue closedAt is missing")
    result = "pass" if not missing else "block"
    return output(
        command,
        result,
        summary="Issue readback is closed and can feed runtime-upgrade closeout." if result == "pass" else "Issue readback is not terminal.",
        issue=issue_payload,
        inferred_pr=pr_number,
        host_readback=inspected,
        missing_inputs=missing,
        fallback_to=["close the maintenance issue or pass explicit terminal evidence"] if missing else None,
    )


def runtime_upgrade_hosted_run_url(pr: dict[str, Any]) -> str | None:
    checks = pr.get("statusCheckRollup")
    if not isinstance(checks, list):
        return None
    for check in checks:
        if not isinstance(check, dict):
            continue
        name = str(check.get("name") or check.get("context") or "")
        url = check.get("detailsUrl") or check.get("targetUrl")
        if name == "loom-pr-merge-gate" and isinstance(url, str) and url:
            return url
    return None


def runtime_upgrade_closeout_next_commands(args: argparse.Namespace, target: Path, *, closeout_pr: str | None = None) -> dict[str, str]:
    branch = runtime_upgrade_effective_branch(args, target) or "<closeout-branch>"
    head_sha = runtime_upgrade_effective_head(args, target) or "<post-commit-head-sha>"
    pr = closeout_pr or args.closeout_pr or "<closeout-pr>"
    return {
        "metadata_update": f"loom pr metadata-update {pr} --target {target} --surface closeout --item {args.item or '<item>'} --branch {branch} --head-sha {head_sha} --change-class metadata_schema --release-judgment no_release --upgrade-trigger runtime_upgrade --upgrade-trigger carrier_sync_only --apply --json",
        "metadata_readback": f"loom pr metadata-readback {pr} --target {target} --surface closeout --item {args.item or '<item>'} --branch {branch} --head-sha {head_sha} --json",
        "gate": f"loom pr gate {pr} --target {target} --surface closeout --work-item {args.item or '<item>'} --head-sha {head_sha} --json",
        "merge": f"loom merge check {pr} --target {target} --work-item {args.item or '<item>'} --head-sha {head_sha} --pr-role carrier_sync_pr --carrier-sync-pr {pr} --change-class metadata_schema --json",
        "carrier_only_review": f"loom review --target {target} --item {args.item or '<item>'} --json # review only the carrier-only closeout diff; do not claim product implementation approval",
    }


def runtime_upgrade_pr_intent_prepare_payload(args: argparse.Namespace, target: Path, *, command: str, apply: bool | None = None) -> dict[str, Any] | None:
    if not args.item:
        return None
    profile = PR_INTENT_PROFILES["runtime-upgrade-only"]
    return pr_intent_prepare_payload(
        command_name=command,
        target=target,
        profile_id="runtime-upgrade-only",
        profile=profile,
        item=args.item,
        issue=args.issue,
        branch=args.branch,
        head_sha=args.head_sha,
        output_file=args.output_file,
        base_body_file=args.base_body_file or "",
        rationale=args.rationale,
        consumer_boundary=args.consumer_boundary,
        recheck_condition=args.recheck_condition,
        scope_proof=args.scope_proof,
        apply=args.apply if apply is None else apply,
    )


def runtime_upgrade_contract_payload(args: argparse.Namespace, target: Path, *, operation: str) -> dict[str, Any]:
    pins = runtime_upgrade_workflow_pins(target)
    plan = handle_delivery_payload_for_upgrade_plan(target)
    freshness = version_freshness()
    target_version = args.to or freshness.get("latest_package_version") or version_context().get("repo_version")
    plugin_payload = freshness.get("plugin_payload", {})
    plugin_guidance = plugin_payload.get("refresh_guidance") or host_plugin_refresh_boundary_action("codex")
    plugin_freshness = plugin_payload.get("freshness")
    plugin_advisory = {
        "mode": "advisory",
        "freshness": plugin_freshness,
        "action": plugin_payload.get("action"),
        "summary": (
            "Codex plugin/cache freshness is part of the runtime upgrade experience, "
            "but repository runtime-upgrade commands do not mutate workstation plugin state."
        ),
        "blocking_by_default": False,
        "blocking_when": "--require-plugin-readiness is supplied because the PR explicitly claims workstation Codex runtime/plugin readiness",
        "guidance": {
            "readback_command": "loom host doctor --host codex --scope user --json",
            "apply_commands": [
                "loom host install --host codex --scope user --apply --json",
                "loom host register --host codex --scope user --apply --json",
            ],
        },
    }
    maintenance_profile = {
        "profile": "runtime-upgrade",
        "scope": "single-repository",
        "multi_repo_batch": False,
        "suite_path": "not_applicable",
        "review_required": True,
        "pr_gate_required": True,
        "hosted_checks_required": True,
        "head_binding_required": True,
        "release_judgment": "no-release",
        "work_item_reuse_forbidden": ["INIT-0001", "product Work Item"],
    }
    return {
        "schema_version": RUNTIME_UPGRADE_SCHEMA,
        "operation": operation,
        "target": str(target),
        "to_version": target_version,
        "version_layers": {
            "loom_cli": freshness.get("cli"),
            "target_repository_workflow_pin": pins,
            "codex_plugin_cache": plugin_payload,
        },
        "workflow_pin_readback": pins,
        "codex_plugin_cache": plugin_payload,
        "codex_plugin_guidance": plugin_guidance,
        "codex_plugin_advisory": plugin_advisory,
        "mutation_boundary": {
            "repo_runtime_upgrade_prepare": "may update target repository workflow LOOM_VERSION pins only when --apply is present",
            "codex_plugin_cache_refresh": "must use loom host doctor|install|register --host codex --scope user; runtime-upgrade does not mutate workstation plugin/cache state",
        },
        "version_freshness": freshness,
        "upgrade_plan": plan,
        "maintenance_profile": maintenance_profile,
        "pr_metadata_command": runtime_upgrade_pr_metadata_command(args),
        "pr_intent_prepare_command": (
            f"loom pr-intent prepare --intent runtime-upgrade-only --target {target} --item {args.item or '<maintenance-work-item>'} "
            f"--issue {args.issue or '<issue>'} --branch {args.branch or '<branch>'} --head-sha {args.head_sha or '<head-sha>'} --apply --json"
        ),
        "required_sequence": [
            "runtime-upgrade status",
            "runtime-upgrade prepare --item <maintenance-carrier|work_item:issue> [--issue <GitHub Work Item>] --to <version> --apply",
            "pr metadata-render/update/readback with runtime_upgrade trigger",
            "hosted PR gate and semantic review for current head",
            "runtime-upgrade check --item <maintenance-carrier|work_item:issue> [--issue <GitHub Work Item>] --to <version> --head-sha <head>",
            "runtime-upgrade closeout after merge and carrier closeout-sync",
        ],
    }


def handle_runtime_upgrade(argv: list[str]) -> int:
    if not argv:
        return emit(output("runtime-upgrade", "block", schema=RUNTIME_UPGRADE_SCHEMA, summary="Runtime upgrade requires an operation.", failed_layer="runtime-upgrade-input", fail_closed_reason="missing operation", fallback_to=["loom runtime-upgrade status --target <repo> --json"]))
    operation = argv[0]
    if operation in {"-h", "--help", "help"}:
        return emit(
            output(
                "runtime-upgrade help",
                "pass",
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade lane operations: status, prepare, pr, check, closeout.",
                operations=["status", "prepare", "pr", "check", "closeout"],
                first_command="loom runtime-upgrade status --target <repo> --json",
                next_commands=[
                    "loom runtime-upgrade prepare --target <repo> --item <maintenance-carrier|work_item:issue> [--issue <GitHub Work Item>] --to <version> --apply --json",
                    "loom runtime-upgrade pr --target <repo> --item <maintenance-carrier|work_item:issue> [--issue <GitHub Work Item>] --to <version> --create --json",
                    "loom runtime-upgrade check --target <repo> --item <maintenance-carrier|work_item:issue> [--issue <GitHub Work Item>] --to <version> --pr <pr> --branch <branch> --head-sha <head-sha> --json",
                    "loom runtime-upgrade closeout --target <repo> --issue <maintenance-issue> --pr <merged-pr> --sync --create-pr --json",
                ],
                mutates=False,
            )
        )
    if operation not in {"status", "prepare", "pr", "check", "closeout"}:
        return emit(output("runtime-upgrade", "block", schema=RUNTIME_UPGRADE_SCHEMA, summary="Unsupported runtime-upgrade operation.", failed_layer="runtime-upgrade-input", fail_closed_reason=f"unsupported operation: {operation}", fallback_to=["loom runtime-upgrade status --target <repo> --json"]))

    parser = argparse.ArgumentParser(prog=f"loom runtime-upgrade {operation}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--to")
    parser.add_argument("--item")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr")
    parser.add_argument("--branch")
    parser.add_argument("--head-sha")
    parser.add_argument("--merge-commit")
    parser.add_argument("--target-branch")
    parser.add_argument("--closed-at")
    parser.add_argument("--evidence-locator")
    parser.add_argument("--repo")
    parser.add_argument("--base", default="main")
    parser.add_argument("--title")
    parser.add_argument("--closeout-pr")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--output-file")
    parser.add_argument("--base-body-file")
    parser.add_argument("--rationale")
    parser.add_argument("--consumer-boundary")
    parser.add_argument("--recheck-condition")
    parser.add_argument("--scope-proof")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--sync", action="store_true")
    parser.add_argument("--create-pr", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--require-plugin-readiness", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv[1:])
    target = resolve_target(args.target)
    command = f"runtime-upgrade {operation}"
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))

    payload = runtime_upgrade_contract_payload(args, target, operation=operation)
    pins = payload["workflow_pin_readback"]
    blocking_gaps: list[dict[str, str]] = []
    plugin_freshness = payload.get("codex_plugin_cache", {}).get("freshness")
    plugin_ready = plugin_freshness in {None, "current", "already_current"}

    if operation == "status":
        result = "pass" if pins["pin_count"] else "block"
        if not pins["pin_count"]:
            blocking_gaps.append({"id": "missing-workflow-pin", "summary": "No LOOM_VERSION workflow pin was found."})
        return emit(
            output(
                command,
                result,
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade status readback completed." if result == "pass" else "Runtime upgrade status could not find an updatable LOOM_VERSION workflow pin.",
                mutates=False,
                failed_layer=None if result == "pass" else "runtime-upgrade-workflow-pin",
                fail_closed_reason=None if result == "pass" else "missing LOOM_VERSION workflow pin",
                blocking_gaps=blocking_gaps,
                fallback_to=None if result == "pass" else ["add a workflow LOOM_VERSION pin", "loom upgrade-plan --target <repo> --json"],
                **payload,
            )
        )

    if operation in {"prepare", "pr", "check"} and not args.to:
        blocking_gaps.append({"id": "missing-target-version", "summary": "Runtime upgrade requires --to <version>."})
    if not args.item:
        blocking_gaps.append({"id": "missing-work-item", "summary": "Runtime upgrade maintenance requires a real Work Item."})
    elif args.item == "INIT-0001":
        blocking_gaps.append({"id": "reserved-work-item", "summary": "Runtime upgrade must not reuse INIT-0001."})
    elif operation in {"prepare", "pr", "check"} and not runtime_upgrade_github_work_item_locator(args):
        blocking_gaps.append(
            {
                "id": "missing-github-work-item",
                "summary": "Runtime upgrade requires --issue <GitHub Work Item> or --item work_item:<issue>; local Work Item ids alone are not host authority.",
            }
        )
    if operation in {"prepare", "pr", "check"} and not pins["pin_count"]:
        blocking_gaps.append({"id": "missing-workflow-pin", "summary": "No LOOM_VERSION workflow pin was found."})

    if operation == "prepare":
        planned_writes = [
            {"file": pin["file"], "from": pin["version"], "to": args.to}
            for pin in pins["pins"]
            if args.to and pin.get("version") != args.to
        ]
        applied_writes: list[dict[str, Any]] = []
        pr_intent_prepare = runtime_upgrade_pr_intent_prepare_payload(args, target, command=command, apply=False)
        if pr_intent_prepare and pr_intent_prepare.get("result") != "pass":
            blocking_gaps.extend({"id": "pr-intent-prepare", "summary": str(entry)} for entry in pr_intent_prepare.get("missing_inputs", []))
        if args.apply and pr_intent_prepare:
            for locator in (args.base_body_file or ".github/PULL_REQUEST_TEMPLATE.md", ".loom/companion/repo-interface.json"):
                if not (target / locator).is_file():
                    blocking_gaps.append({"id": "pr-intent-metadata-contract", "summary": f"runtime-upgrade prepare requires {locator} before writing PR metadata"})
        if args.require_plugin_readiness and not plugin_ready:
            blocking_gaps.append({"id": "codex-plugin-cache-not-ready", "summary": "Codex plugin/cache readiness was explicitly required but is stale or unreadable."})
        result = "block" if blocking_gaps else "pass"
        if result == "pass" and args.apply:
            pr_intent_prepare = runtime_upgrade_pr_intent_prepare_payload(args, target, command=command, apply=True)
            if pr_intent_prepare and pr_intent_prepare.get("result") != "pass":
                blocking_gaps.extend({"id": "pr-intent-prepare", "summary": str(entry)} for entry in pr_intent_prepare.get("missing_inputs", []))
                result = "block"
            else:
                applied_writes = runtime_upgrade_apply_workflow_pin_update(target, args.to)
                payload["workflow_pin_readback_after"] = runtime_upgrade_workflow_pins(target)
        return emit(
            output(
                command,
                result,
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade workflow pin prepared." if result == "pass" else "Runtime upgrade prepare is blocked by missing maintenance inputs.",
                mutates=args.apply,
                planned_writes=planned_writes,
                applied_writes=applied_writes,
                pr_intent_prepare=pr_intent_prepare,
                failed_layer=None if result == "pass" else "runtime-upgrade-input",
                fail_closed_reason=None if result == "pass" else "; ".join(gap["summary"] for gap in blocking_gaps),
                blocking_gaps=blocking_gaps,
                fallback_to=None if result == "pass" else ["loom runtime-upgrade status --target <repo> --json"],
                **payload,
            )
        )

    if operation == "pr":
        if not args.to:
            blocking_gaps.append({"id": "missing-target-version", "summary": "Runtime upgrade PR orchestration requires --to <version>."})
        branch = runtime_upgrade_effective_branch(args, target)
        head_sha = runtime_upgrade_effective_head(args, target)
        if not branch:
            blocking_gaps.append({"id": "missing-branch", "summary": "Runtime upgrade PR orchestration requires --branch or a checked-out branch."})
        if not head_sha:
            blocking_gaps.append({"id": "missing-head_sha", "summary": "Runtime upgrade PR orchestration requires --head-sha or a readable git HEAD."})
        output_file = args.output_file or runtime_upgrade_artifact_path(target, args.item, "runtime-upgrade-pr.md")
        readback_file = runtime_upgrade_artifact_path(target, args.item, "runtime-upgrade-pr-readback.md")
        steps: list[dict[str, Any]] = []
        rendered: dict[str, Any] | None = None
        pr_number = str(args.pr) if args.pr else None
        created: dict[str, Any] | None = None
        if not blocking_gaps:
            render_args = runtime_upgrade_pr_metadata_flow_args(
                args,
                target,
                action="render",
                surface="merge_ready",
                output_file=output_file,
            )
            rendered = flow_payload(command, render_args, fallback_to=["loom pr metadata-render --surface merge_ready --json"])
            steps.append({"name": "metadata-render", "result": rendered.get("result"), "payload": rendered})
            if rendered.get("result") != "pass":
                blocking_gaps.extend({"id": "metadata-render", "summary": str(entry)} for entry in rendered.get("missing_inputs", []))

        if not blocking_gaps and args.create:
            created = runtime_upgrade_create_pr_payload(args, target, body_file=output_file)
            steps.append({"name": "pr-create", "result": created.get("result"), "payload": created, "mutates": created.get("mutates", False)})
            if created.get("result") == "pass":
                created_pr = created.get("pr") if isinstance(created.get("pr"), dict) else {}
                if created_pr.get("number"):
                    pr_number = str(created_pr["number"])
            else:
                blocking_gaps.extend({"id": "pr-create", "summary": str(entry)} for entry in created.get("missing_inputs", []))

        if not blocking_gaps and (args.update or (args.create and pr_number)):
            if not pr_number:
                blocking_gaps.append({"id": "missing-pr", "summary": "Runtime upgrade PR update requires --pr or a PR created by --create."})
            else:
                update_args = runtime_upgrade_pr_metadata_flow_args(
                    args,
                    target,
                    action="update",
                    surface="merge_ready",
                    pr=pr_number,
                    output_file=output_file,
                    readback_file=readback_file,
                )
                update_args.append("--apply")
                updated = flow_payload(command, update_args, fallback_to=["loom pr metadata-update <pr> --surface merge_ready --apply --json"])
                steps.append({"name": "metadata-update", "result": updated.get("result"), "payload": updated, "mutates": True})
                if updated.get("result") != "pass":
                    blocking_gaps.extend({"id": "metadata-update", "summary": str(entry)} for entry in updated.get("missing_inputs", []))

        readback: dict[str, Any] | None = None
        if not blocking_gaps and pr_number:
            readback_args = runtime_upgrade_pr_metadata_flow_args(
                args,
                target,
                action="readback",
                surface="merge_ready",
                pr=pr_number,
                readback_file=readback_file,
            )
            readback = flow_payload(command, readback_args, fallback_to=["loom pr metadata-readback <pr> --surface merge_ready --json"])
            steps.append({"name": "metadata-readback", "result": readback.get("result"), "payload": readback})
            if readback.get("result") != "pass":
                blocking_gaps.extend({"id": "metadata-readback", "summary": str(entry)} for entry in readback.get("missing_inputs", []))

        result = "pass" if not blocking_gaps else "block"
        next_command = (
            f"loom runtime-upgrade check --target {target} --item {args.item or '<item>'} --to {args.to or '<version>'} --pr {pr_number or '<pr>'} --branch {branch or '<branch>'} --head-sha {head_sha or '<head-sha>'} --json"
            if result == "pass" and pr_number
            else f"loom runtime-upgrade pr --target {target} --item {args.item or '<item>'} --to {args.to or '<version>'} --branch {branch or '<branch>'} --head-sha {head_sha or '<head-sha>'} --create --json"
        )
        return emit(
            output(
                command,
                result,
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade PR metadata is rendered and read back." if result == "pass" else "Runtime upgrade PR orchestration is blocked.",
                mutates=bool(args.create or args.update),
                host_mutations=bool(args.create),
                carrier_mutations=False,
                pr={"number": pr_number, "branch": branch, "head_sha": head_sha},
                body_file=output_file,
                readback_file=readback_file if pr_number else None,
                steps=steps,
                readiness=readiness_payload(
                    ready=result == "pass" and bool(pr_number),
                    reasons=readiness_reasons_from_text([gap["summary"] for gap in blocking_gaps]),
                    next_command=next_command,
                    summary="PR metadata is ready for runtime-upgrade check." if result == "pass" and pr_number else "Create/update and read back the runtime-upgrade PR before hosted gate.",
                ),
                failed_layer=None if result == "pass" else "runtime-upgrade-pr",
                fail_closed_reason=None if result == "pass" else "; ".join(gap["summary"] for gap in blocking_gaps),
                blocking_gaps=blocking_gaps,
                fallback_to=None if result == "pass" else [next_command],
                next_action=next_command,
                **payload,
            )
        )

    if operation == "check":
        current_versions = set(pins["versions"])
        if args.to and current_versions != {args.to}:
            blocking_gaps.append({"id": "workflow-pin-drift", "summary": f"Workflow LOOM_VERSION pins do not all equal {args.to}."})
        for required, flag in ((args.pr, "--pr"), (args.branch, "--branch"), (args.head_sha, "--head-sha")):
            if not required:
                blocking_gaps.append({"id": f"missing-{flag[2:].replace('-', '_')}", "summary": f"Runtime upgrade check requires {flag} readback."})
        if args.require_plugin_readiness and not plugin_ready:
            blocking_gaps.append({"id": "codex-plugin-cache-not-ready", "summary": "Codex plugin/cache readiness was explicitly required but is stale or unreadable."})
        result = "pass" if not blocking_gaps else "block"
        return emit(
            output(
                command,
                result,
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade maintenance PR inputs are ready for normal Loom gates." if result == "pass" else "Runtime upgrade maintenance PR is not ready.",
                mutates=False,
                failed_layer=None if result == "pass" else "runtime-upgrade-readback",
                fail_closed_reason=None if result == "pass" else "; ".join(gap["summary"] for gap in blocking_gaps),
                blocking_gaps=blocking_gaps,
                fallback_to=None if result == "pass" else ["loom pr metadata-readback --surface merge_ready --json", "loom pr gate <pr> --json"],
                **payload,
            )
        )

    if operation == "closeout":
        explicit_terminal_evidence = bool(args.pr and args.merge_commit and args.target_branch and args.evidence_locator)
        if not args.issue and not explicit_terminal_evidence:
            blocking_gaps.append({"id": "missing-issue", "summary": "Runtime upgrade closeout requires --issue so Loom can read issue state and closedAt."})
        steps: list[dict[str, Any]] = []
        repo_slug = args.repo or infer_github_repo(target)
        issue_readback: dict[str, Any] | None = None
        pr_number = str(args.pr) if args.pr else None
        if not blocking_gaps and args.issue:
            issue_readback = runtime_upgrade_issue_payload_from_host(target, repo=repo_slug, issue=args.issue)
            steps.append({"name": "issue-readback", "result": issue_readback.get("result"), "payload": issue_readback})
            if issue_readback.get("result") != "pass":
                blocking_gaps.extend({"id": "issue-readback", "summary": str(entry)} for entry in issue_readback.get("missing_inputs", []))
            if not pr_number and issue_readback.get("inferred_pr"):
                pr_number = str(issue_readback["inferred_pr"])
        if not pr_number:
            blocking_gaps.append({"id": "missing-pr", "summary": "Runtime upgrade closeout requires --pr or an issue readback with a closing PR reference."})

        pr_readback: dict[str, Any] | None = None
        pr: dict[str, Any] = {}
        if not blocking_gaps and pr_number and not explicit_terminal_evidence:
            pr_readback = release_closeout_pr_readback_payload(
                target=target,
                pr_number=pr_number,
                repo=repo_slug,
                target_commit=args.merge_commit,
                pr_payload_file=args.pr_payload_file,
            )
            steps.append({"name": "pr-readback", "result": pr_readback.get("result"), "payload": pr_readback})
            if pr_readback.get("result") != "pass":
                blocking_gaps.extend({"id": "pr-readback", "summary": str(entry)} for entry in pr_readback.get("missing_inputs", []))
            else:
                pr = pr_readback.get("pr") if isinstance(pr_readback.get("pr"), dict) else {}

        issue_payload = issue_readback.get("issue") if isinstance(issue_readback, dict) and isinstance(issue_readback.get("issue"), dict) else {}
        merge_commit = pr.get("mergeCommit") if isinstance(pr.get("mergeCommit"), dict) else {}
        merge_sha = str(args.merge_commit or merge_commit.get("oid") or "not_applicable")
        target_branch = str(args.target_branch or pr.get("baseRefName") or "not_applicable")
        closed_at = str(args.closed_at or issue_payload.get("closedAt") or pr.get("mergedAt") or (now_iso() if explicit_terminal_evidence else "not_applicable"))
        hosted_run_url = runtime_upgrade_hosted_run_url(pr)
        evidence_locator = str(
            args.evidence_locator
            or ";".join(str(value) for value in (hosted_run_url, issue_payload.get("url"), pr.get("url")) if value)
            or "runtime-upgrade-host-readback"
        )
        terminal_metadata = {
            "terminal_state": "closed_out",
            "issue": str(args.issue or "not_applicable"),
            "pr": str(pr_number or "not_applicable"),
            "merge_commit": merge_sha,
            "target_branch": target_branch,
            "closed_at": closed_at,
            "evidence_locator": evidence_locator,
            "hosted_run_url": hosted_run_url,
        }
        for field_name in ("merge_commit", "target_branch", "closed_at"):
            if terminal_metadata[field_name] == "not_applicable":
                blocking_gaps.append({"id": f"missing-{field_name}", "summary": f"Runtime upgrade closeout could not infer {field_name.replace('_', ' ')} from host readback."})

        apply_closeout = args.sync or args.apply
        carrier_command = None
        if not blocking_gaps and args.item:
            carrier_args = [
                "carrier",
                "closeout-sync",
                "--target",
                str(target),
                "--item",
                args.item,
                "--terminal-state",
                "closed_out",
                "--issue",
                terminal_metadata["issue"],
                "--pr",
                terminal_metadata["pr"],
                "--merge-commit",
                terminal_metadata["merge_commit"],
                "--target-branch",
                terminal_metadata["target_branch"],
                "--closed-at",
                terminal_metadata["closed_at"],
                "--evidence-locator",
                terminal_metadata["evidence_locator"],
                "--apply" if apply_closeout else "--dry-run",
            ]
            carrier_command = "loom " + " ".join(str(part) for part in carrier_args)
            if not apply_closeout:
                steps.append(
                    {
                        "name": "carrier-closeout-sync-plan",
                        "result": "pass",
                        "payload": {"command": carrier_command, "result": "pass", "summary": "carrier closeout-sync is planned; rerun with --sync to write repo carriers."},
                        "mutates": False,
                    }
                )
            else:
                carrier = flow_payload(command, carrier_args, fallback_to=["loom carrier closeout-sync --target <repo> --item <item> --apply --json"])
                steps.append({"name": "carrier-closeout-sync", "result": carrier.get("result"), "payload": carrier, "mutates": apply_closeout})
                if carrier.get("result") != "pass":
                    blocking_gaps.extend({"id": "carrier-closeout-sync", "summary": str(entry)} for entry in carrier.get("missing_inputs", []))
            if apply_closeout and not blocking_gaps:
                stop = (
                    f"{args.item} runtime-upgrade closeout synced: PR #{terminal_metadata['pr']} merged at {terminal_metadata['merge_commit']}; "
                    "host readback consumed into terminal repo carrier state."
                )
                recovery_args = [
                    "recovery",
                    "writeback",
                    "--target",
                    str(target),
                    "--item",
                    args.item,
                    "--current-checkpoint",
                    "closed_out",
                    "--current-stop",
                    stop,
                    "--next-step",
                    "Commit/push this carrier-only closeout branch, update PR metadata, run hosted gate, then merge the carrier-only PR.",
                    "--blockers",
                    "None recorded.",
                    "--current-lane",
                    "runtime-upgrade-closeout-sync",
                ]
                recovery = flow_payload(command, recovery_args, fallback_to=["loom recovery writeback --target <repo> --item <item>"])
                steps.append({"name": "recovery-writeback", "result": recovery.get("result"), "payload": recovery, "mutates": True})
                if recovery.get("result") == "pass":
                    for surface in ("closeout", "merge_ready"):
                        refresh_args = ["carrier", "refresh", "--target", str(target), "--item", args.item, "--surface", surface, "--write"]
                        refresh = flow_payload(command, refresh_args, fallback_to=["loom carrier refresh --target <repo> --write"])
                        steps.append({"name": f"carrier-refresh-{surface}", "result": refresh.get("result"), "payload": refresh, "mutates": True})
                        if refresh.get("result") != "pass":
                            blocking_gaps.extend({"id": f"carrier-refresh-{surface}", "summary": str(entry)} for entry in refresh.get("missing_inputs", []))
                else:
                    blocking_gaps.extend({"id": "recovery-writeback", "summary": str(entry)} for entry in recovery.get("missing_inputs", []))
        elif not args.item:
            blocking_gaps.append({"id": "missing-work-item", "summary": "Runtime upgrade closeout requires --item."})

        closeout_pr_number = str(args.closeout_pr) if args.closeout_pr else None
        body_file = args.output_file or runtime_upgrade_artifact_path(target, args.item, "runtime-upgrade-closeout-pr.md")
        readback_file = runtime_upgrade_artifact_path(target, args.item, "runtime-upgrade-closeout-pr-readback.md")
        if not blocking_gaps and (args.create_pr or args.closeout_pr):
            render_args = runtime_upgrade_pr_metadata_flow_args(args, target, action="render", surface="closeout", output_file=body_file)
            rendered = flow_payload(command, render_args, fallback_to=["loom pr metadata-render --surface closeout --json"])
            steps.append({"name": "closeout-metadata-render", "result": rendered.get("result"), "payload": rendered})
            if rendered.get("result") != "pass":
                blocking_gaps.extend({"id": "closeout-metadata-render", "summary": str(entry)} for entry in rendered.get("missing_inputs", []))
            if not blocking_gaps and args.create_pr:
                created = runtime_upgrade_create_pr_payload(args, target, body_file=body_file)
                steps.append({"name": "closeout-pr-create", "result": created.get("result"), "payload": created, "mutates": created.get("mutates", False)})
                if created.get("result") == "pass":
                    created_pr = created.get("pr") if isinstance(created.get("pr"), dict) else {}
                    if created_pr.get("number"):
                        closeout_pr_number = str(created_pr["number"])
                else:
                    blocking_gaps.extend({"id": "closeout-pr-create", "summary": str(entry)} for entry in created.get("missing_inputs", []))
            if not blocking_gaps and closeout_pr_number:
                update_args = runtime_upgrade_pr_metadata_flow_args(
                    args,
                    target,
                    action="update",
                    surface="closeout",
                    pr=closeout_pr_number,
                    output_file=body_file,
                    readback_file=readback_file,
                )
                update_args.append("--apply")
                updated = flow_payload(command, update_args, fallback_to=["loom pr metadata-update <pr> --surface closeout --apply --json"])
                steps.append({"name": "closeout-metadata-update", "result": updated.get("result"), "payload": updated, "mutates": True})
                if updated.get("result") != "pass":
                    blocking_gaps.extend({"id": "closeout-metadata-update", "summary": str(entry)} for entry in updated.get("missing_inputs", []))
                else:
                    readback_args = runtime_upgrade_pr_metadata_flow_args(
                        args,
                        target,
                        action="readback",
                        surface="closeout",
                        pr=closeout_pr_number,
                        readback_file=readback_file,
                    )
                    readback = flow_payload(command, readback_args, fallback_to=["loom pr metadata-readback <pr> --surface closeout --json"])
                    steps.append({"name": "closeout-metadata-readback", "result": readback.get("result"), "payload": readback})
                    if readback.get("result") != "pass":
                        blocking_gaps.extend({"id": "closeout-metadata-readback", "summary": str(entry)} for entry in readback.get("missing_inputs", []))

        result = "pass" if not blocking_gaps else "block"
        next_commands = runtime_upgrade_closeout_next_commands(args, target, closeout_pr=closeout_pr_number)
        next_action = (
            next_commands["metadata_update"]
            if apply_closeout and result == "pass" and not closeout_pr_number
            else next_commands["gate"]
            if result == "pass" and closeout_pr_number
            else "Resolve runtime-upgrade closeout readback gaps before writing carrier metadata."
        )
        return emit(
            output(
                command,
                result,
                schema=RUNTIME_UPGRADE_SCHEMA,
                summary="Runtime upgrade closeout carrier sync is ready." if result == "pass" else "Runtime upgrade closeout stopped before terminal carrier readiness.",
                mutates=apply_closeout or bool(args.create_pr),
                host_mutations=bool(args.create_pr),
                carrier_mutations=apply_closeout,
                terminal_metadata=terminal_metadata,
                carrier_closeout_sync_command=carrier_command,
                steps=steps,
                next_commands=next_commands,
                carrier_only_review={
                    "mode": "carrier-only",
                    "summary": "Current-head review may cover only terminal carrier metadata/review carrier drift; it must not be represented as product implementation approval.",
                    "next_command": next_commands["carrier_only_review"],
                },
                readiness=readiness_payload(
                    ready=False,
                    reasons=readiness_reasons_from_text([gap["summary"] for gap in blocking_gaps]) if blocking_gaps else ["pr_metadata_stale"],
                    next_command=next_action,
                    summary="Carrier sync is written; update/read back closeout PR metadata before hosted gate." if apply_closeout and result == "pass" else "Runtime-upgrade closeout is not a hosted gate bypass.",
                ),
                failed_layer=None if result == "pass" else "runtime-upgrade-closeout",
                fail_closed_reason=None if result == "pass" else "; ".join(gap["summary"] for gap in blocking_gaps),
                blocking_gaps=blocking_gaps,
                fallback_to=None if result == "pass" else [next_action],
                next_action=next_action,
                **payload,
            )
        )

    raise AssertionError(f"unhandled runtime-upgrade operation: {operation}")


def handle_delivery(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--host", default="codex", choices=("codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    mode = "metadata-only"
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))

    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    installed_ready = installed_error is None and not validation_errors
    legacy_surfaces = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]

    if command == "install":
        planned_state = build_installed_state(target, host=args.host, mode=mode)
        state_path = target / ".loom" / "installed-state.json"
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Target repository install writes adoption metadata only and requires --apply before mutation.",
                    target=str(target),
                    host=args.host,
                    mode=mode,
                    mutates=True,
                    planned_writes=[relative_to_target(state_path, target), "AGENTS.md"],
                    host_plugin_refresh=host_plugin_refresh_boundary_action(args.host),
                    detection=detection,
                    failed_layer="install-apply",
                    fail_closed_reason="explicit --apply is required before install writes target repository installed-state metadata",
                    fallback_to=["loom install --target <repo> --apply --json", "loom repair plan --target <repo> --json"],
                )
            )
        if installed_ready and not args.force:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Valid installed-state already exists; use upgrade-plan or --force for reinstall.",
                    target=str(target),
                    installed_state_path=str(path),
                    detection=detection,
                    failed_layer="installed-state",
                    fail_closed_reason="current installed-state exists",
                    fallback_to=["loom upgrade-plan --target <repo> --json", "loom install --target <repo> --apply --force --json"],
                )
            )
        managed_writes = [ensure_agents_bootstrap(target)]
        write_json(state_path, planned_state)
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary="Target repository metadata-only adoption state and Loom bootstrap instructions were written.",
                target=str(target),
                host=args.host,
                mode=mode,
                mutates=True,
                managed_writes=[*managed_writes, relative_to_target(state_path, target)],
                installed_state_path=str(state_path),
                installed_state=planned_state,
                detection=detection,
                host_plugin_refresh=host_plugin_refresh_boundary_action(args.host),
                fallback_to=None,
            )
        )

    if command == "upgrade-plan":
        actions: list[dict[str, Any]] = []
        freshness = version_freshness()
        if installed_error is not None or validation_errors:
            actions.append(
                {
                    "id": "repair-installed-state",
                    "kind": "repair-plan",
                    "status": "required",
                    "reason": installed_error["fail_closed_reason"] if installed_error else "installed-state validation failed",
                    "command": "loom repair plan --target <repo> --json",
                }
            )
        if legacy_surfaces:
            actions.append(
                {
                    "id": "classify-legacy-surfaces",
                    "kind": "manual-migration-judgment",
                    "status": "required",
                    "surface_count": len(legacy_surfaces),
                    "command": "loom repair plan --target <repo> --json",
                }
            )
        actions.extend(
            global_cli_runtime_carrier_migration_actions(
                target,
                detection,
                installed_ready=installed_ready,
                state_path=path,
            )
        )
        migration_action = downstream_top_level_skills_migration_action(target)
        if migration_action:
            actions.append(migration_action)
        if installed_ready and not legacy_surfaces and not any(action.get("id") == "plan-global-cli-runtime-carrier-migration" for action in actions):
            actions.append(
                {
                    "id": "installed-state-current",
                    "kind": "no-op",
                    "status": "current",
                    "reason": "installed-state validates and no legacy surfaces are blocking",
                    "command": "loom verify --target <repo> --json",
                }
            )
        registration_action = workstation_registration_action(target)
        if registration_action:
            actions.append(registration_action)
        refresh_boundary_action = host_plugin_refresh_boundary_action(args.host)
        if refresh_boundary_action:
            actions.append(refresh_boundary_action)
        actions.append(version_freshness_action(freshness))
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary="Target repository upgrade plan generated without mutating installed-state; host plugin refresh uses loom host commands.",
                target=str(target),
                host=args.host,
                mutates=False,
                installed_state_path=str(path) if path else None,
                detection=detection,
                installed_state_errors=validation_errors,
                version_freshness=freshness,
                actions=actions,
                fallback_to=None if installed_ready and not legacy_surfaces else ["loom repair plan --target <repo> --json"],
            )
        )

    if command == "verify":
        doctor = doctor_payload(target)
        requirement = suite_verify_requirement(state, args.item)
        suite_check = None
        if doctor["result"] == "pass" and requirement["required"]:
            suite_check = suite_validation_check(target, requirement["item_id"])
        blocking_checks = []
        if doctor["result"] != "pass":
            blocking_checks.append({"name": "doctor", "failed_layer": "delivery-verify", "summary": "doctor reported missing, invalid, mixed, or legacy installed surfaces"})
        if suite_check and suite_check["result"] != "pass":
            blocking_checks.append(suite_check)
        result = "pass" if not blocking_checks else "block"
        failed_layer = None if result == "pass" else next((check.get("failed_layer") for check in blocking_checks if check.get("failed_layer")), "delivery-verify")
        return emit(
            output(
                command,
                result,
                schema=DELIVERY_SCHEMA,
                summary="Installed Loom delivery layers verified." if result == "pass" else "Installed Loom delivery layers or required suite validation are not ready.",
                target=str(target),
                mutates=False,
                doctor=doctor,
                suite_validation_requirement=requirement,
                suite_validation=suite_check,
                installed_state_path=str(path) if path else None,
                failed_layer=failed_layer,
                fail_closed_reason=None if result == "pass" else "; ".join(str(check.get("summary", check.get("name"))) for check in blocking_checks),
                fallback_to=None if result == "pass" else ["loom upgrade-plan --target <repo> --json", "loom repair plan --target <repo> --json", "loom suite validate --target <repo> --item <item> --json"],
            )
        )

    if command == "upgrade":
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Target repository upgrade refreshes installed-state metadata and requires --apply.",
                    target=str(target),
                    host=args.host,
                    mutates=True,
                    plan=handle_delivery_payload_for_upgrade_plan(target),
                    host_plugin_refresh=host_plugin_refresh_boundary_action(args.host),
                    failed_layer="upgrade-apply",
                    fail_closed_reason="explicit --apply is required before upgrade mutates target repository installed-state metadata",
                    fallback_to=["loom upgrade-plan --target <repo> --json", "loom verify --target <repo> --json"],
                )
            )
        if not installed_ready or legacy_surfaces:
            return emit(
                output(
                    command,
                    "block",
                    schema=DELIVERY_SCHEMA,
                    summary="Upgrade cannot apply while installed-state is invalid or legacy surfaces remain unclassified.",
                    target=str(target),
                    mutates=True,
                    detection=detection,
                    installed_state_errors=validation_errors,
                    failed_layer="upgrade-preflight",
                    fail_closed_reason="repair plan must be consumed before mutating upgrade",
                    fallback_to=["loom repair plan --target <repo> --json"],
                )
            )
        refreshed_state = dict(state)
        removed_workstation_fields = [
            field
            for field in ("target", "installed_at", "upgraded_at", "cli_freshness", "plugin_freshness", "plugin_cache_path", "host_machine_path")
            if refreshed_state.pop(field, None) is not None
        ]
        refreshed_state["upgrade_eligibility"] = "current"
        changed = refreshed_state != state
        if changed:
            write_json(path, refreshed_state)
        return emit(
            output(
                command,
                "pass",
                schema=DELIVERY_SCHEMA,
                summary=(
                    "Target repository installed-state metadata was refreshed for repository contract drift."
                    if changed
                    else "Target repository installed-state metadata already matches repository truth; workstation freshness was not written."
                ),
                target=str(target),
                host=args.host,
                mutates=changed,
                installed_state_path=str(path),
                installed_state=refreshed_state,
                removed_workstation_fields=removed_workstation_fields,
                host_plugin_refresh=host_plugin_refresh_boundary_action(args.host),
                fallback_to=None,
            )
        )

    return emit(
        output(
            command,
            "block",
            schema=DELIVERY_SCHEMA,
            summary="Rollback requires an explicit rollback artifact and remains fail-closed in this phase.",
            target=str(target),
            mutates=False,
            detection=detection,
            failed_layer="rollback-ownership",
            fail_closed_reason="rollback/delete ownership is not inferred from installed surface detection",
            fallback_to=["loom upgrade-plan --target <repo> --json", "loom repair plan --target <repo> --json"],
        )
    )


def handle_delivery_payload_for_upgrade_plan(target: Path) -> dict[str, Any]:
    detection = detect_payload(target)
    path, state, installed_error = load_installed_state(target)
    validation_errors = validate_installed_state(state) if installed_error is None else []
    installed_ready = installed_error is None and not validation_errors
    legacy_surfaces = [
        item for item in detection["surfaces"]
        if item.get("migration_status") == "legacy" or str(item.get("kind", "")).startswith("symlink-")
    ]
    actions = []
    if installed_error is not None or validation_errors:
        actions.append({"id": "repair-installed-state", "status": "required"})
    if legacy_surfaces:
        actions.append({"id": "classify-legacy-surfaces", "status": "required", "surface_count": len(legacy_surfaces)})
    actions.extend(
        global_cli_runtime_carrier_migration_actions(
            target,
            detection,
            installed_ready=installed_ready,
            state_path=path,
        )
    )
    registration_action = workstation_registration_action(target)
    if registration_action:
        actions.append(registration_action)
    refresh_boundary_action = host_plugin_refresh_boundary_action("codex")
    if refresh_boundary_action:
        actions.append(refresh_boundary_action)
    freshness = version_freshness()
    actions.append(version_freshness_action(freshness))
    return output(
        "upgrade-plan",
        "pass",
        schema=DELIVERY_SCHEMA,
        summary="Target repository upgrade plan generated without mutating installed-state; host plugin refresh uses loom host commands.",
        target=str(target),
        host="codex",
        mutates=False,
        installed_state_path=str(path) if path else None,
        detection=detection,
        installed_state_errors=validation_errors,
        version_freshness=freshness,
        actions=actions,
    )


def block_installed_state(command: str, target: Path, reason: str, *, hints: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return output(
        command,
        "block",
        summary="Installed-state cannot be trusted.",
        target=str(target),
        runtime_state="blocked",
        upgrade_eligibility="incompatible",
        failed_layer="installed-state",
        fail_closed_reason=reason,
        legacy_surface_hints=hints or legacy_surface_hints(target),
        fallback_to=["loom detect", "loom doctor", "loom repair plan"],
    )


def validate_installed_state(state: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(state, dict):
        return [{"path": "$", "reason": "installed-state must be a JSON object"}]
    if state.get("schema_version") != INSTALLED_STATE_SCHEMA:
        errors.append({"path": "schema_version", "reason": f"expected {INSTALLED_STATE_SCHEMA}"})
    for key in ("installation_id", "layers", "installation_graph"):
        if key not in state:
            errors.append({"path": key, "reason": "required field is missing"})
    layers = state.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append({"path": "layers", "reason": "must be a non-empty array"})
        return errors
    layer_ids: set[str] = set()
    layer_types: set[str] = set()
    layer_paths: set[str] = set()
    for index, layer in enumerate(layers):
        path = f"layers[{index}]"
        if not isinstance(layer, dict):
            errors.append({"path": path, "reason": "layer must be an object"})
            continue
        for key in ("id", "layer_type", "installed_path", "version_context", "runtime_state", "upgrade_eligibility"):
            if key not in layer:
                errors.append({"path": f"{path}.{key}", "reason": "required field is missing"})
        layer_id = layer.get("id")
        if isinstance(layer_id, str) and layer_id:
            if layer_id in layer_ids:
                errors.append({"path": f"{path}.id", "reason": "duplicate layer id"})
            layer_ids.add(layer_id)
        layer_type = layer.get("layer_type")
        if isinstance(layer_type, str) and layer_type:
            layer_types.add(layer_type)
            if layer_type in {"full-repo-runtime", "generated-skills", "plugin-embedded-skills", "host-adapter-plugin", "generated-single-skill"}:
                errors.append({"path": f"{path}.layer_type", "reason": "repo-local runtime, plugin, and skills layers are unsupported legacy installed-state"})
        installed_path = layer.get("installed_path")
        if isinstance(installed_path, str) and installed_path:
            normalized_installed_path = installed_path.rstrip("/")
            layer_paths.add(normalized_installed_path)
            if normalized_installed_path in {".loom/bin", "skills", "plugins/loom", "plugins/loom/skills"} or normalized_installed_path.startswith(".agents/skills"):
                errors.append({"path": f"{path}.installed_path", "reason": "repo-local runtime, plugin, and skills paths are unsupported legacy installed-state"})
        if layer.get("runtime_state") not in {"ready", "blocked", "unknown"}:
            errors.append({"path": f"{path}.runtime_state", "reason": "must be ready, blocked, or unknown"})
        if layer.get("upgrade_eligibility") not in {"current", "upgrade-available", "drift", "incompatible", "unknown"}:
            errors.append({"path": f"{path}.upgrade_eligibility", "reason": "unsupported upgrade eligibility"})
        version = layer.get("version_context")
        if not isinstance(version, dict) or not version:
            errors.append({"path": f"{path}.version_context", "reason": "must be a non-empty object"})
        elif any(value in (None, "", "unknown") for value in version.values()):
            errors.append({"path": f"{path}.version_context", "reason": "version metadata must not be missing or unknown"})
        if layer.get("runtime_state") != "ready":
            if layer.get("layer_type") == GLOBAL_CLI_PROVIDER_LAYER and layer.get("runtime_state") == "unknown":
                pass
            elif not layer.get("fail_closed_reason") or not layer.get("failed_layer"):
                errors.append({"path": path, "reason": "non-ready layers must include failed_layer and fail_closed_reason"})
    graph = state.get("installation_graph")
    if isinstance(graph, dict):
        graph_layers = graph.get("layers")
        if isinstance(graph_layers, list):
            missing = sorted(set(graph_layers) - layer_ids)
            if missing:
                errors.append({"path": "installation_graph.layers", "reason": f"unknown layer ids: {', '.join(missing)}"})
        edges = graph.get("edges", [])
        if isinstance(edges, list):
            for index, edge in enumerate(edges):
                edge_path = f"installation_graph.edges[{index}]"
                if not isinstance(edge, dict):
                    errors.append({"path": edge_path, "reason": "edge must be an object"})
                    continue
                for endpoint in ("from", "to"):
                    if edge.get(endpoint) not in layer_ids:
                        errors.append({"path": f"{edge_path}.{endpoint}", "reason": "edge endpoint must reference a known layer id"})
        else:
            errors.append({"path": "installation_graph.edges", "reason": "must be an array when present"})
    else:
        errors.append({"path": "installation_graph", "reason": "must be an object"})
    runtime_provider = state.get("runtime_provider")
    if runtime_provider != RUNTIME_PROVIDER_GLOBAL_CLI:
        errors.append({"path": "runtime_provider", "reason": "runtime provider must be global-cli"})
    inferred_runtime_provider = installed_state_runtime_provider(state)
    requires_global_cli = runtime_provider == RUNTIME_PROVIDER_GLOBAL_CLI or GLOBAL_CLI_PROVIDER_LAYER in layer_types
    global_cli_requirement = global_cli_provider_requirement(state)
    if requires_global_cli:
        if global_cli_requirement is None:
            errors.append({"path": "provider_requirements.global_cli", "reason": "global-cli runtime provider must declare provider requirements"})
        else:
            expected_scalars = {
                "required": True,
                "provider": "loom-cli",
                "authority": "workstation",
                "package": "@mc-and-his-agents/loom",
                "executable": "loom",
            }
            for key, expected in expected_scalars.items():
                if global_cli_requirement.get(key) != expected:
                    errors.append({"path": f"provider_requirements.global_cli.{key}", "reason": f"must be {expected!r}"})
            if global_cli_requirement.get("compatibility_mode_allowed") is not False:
                errors.append({"path": "provider_requirements.global_cli.compatibility_mode_allowed", "reason": "must be False"})
            version_requirement = global_cli_requirement.get("version_requirement")
            if not isinstance(version_requirement, str) or not version_requirement.strip():
                errors.append({"path": "provider_requirements.global_cli.version_requirement", "reason": "must be a non-empty string"})
            required_commands = global_cli_requirement.get("required_commands")
            if not isinstance(required_commands, list) or not required_commands:
                errors.append({"path": "provider_requirements.global_cli.required_commands", "reason": "must be a non-empty array"})
            else:
                command_set = {command for command in required_commands if isinstance(command, str)}
                missing_commands = sorted(set(GLOBAL_CLI_REQUIRED_COMMANDS) - command_set)
                if missing_commands:
                    errors.append({"path": "provider_requirements.global_cli.required_commands", "reason": f"missing required commands: {', '.join(missing_commands)}"})
    if inferred_runtime_provider == RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER and GLOBAL_CLI_PROVIDER_LAYER in layer_types and runtime_provider != RUNTIME_PROVIDER_GLOBAL_CLI:
        errors.append({"path": "runtime_provider", "reason": "global-cli provider layer requires runtime_provider global-cli"})
    repo_payload = state.get("repo_payload")
    if isinstance(repo_payload, dict):
        mode = repo_payload.get("mode")
        if mode != "metadata-only":
            errors.append({"path": "repo_payload.mode", "reason": "repo payload mode must be metadata-only"})
        adoption_mode = repo_payload.get("adoption_mode")
        if adoption_mode is not None and adoption_mode not in {"light-governance", "execution-control", "strong-governance", "attach-only"}:
            errors.append({"path": "repo_payload.adoption_mode", "reason": "unsupported repository adoption mode"})
        if mode == "metadata-only":
            if ".loom/bin" in layer_paths or "plugins/loom/skills" in layer_paths or "plugin-embedded-skills" in layer_types:
                errors.append({"path": "repo_payload.mode", "reason": "metadata-only mode must not declare repo-local runtime or embedded plugin skills payload"})
            provider = state.get("skills_provider")
            if not isinstance(provider, dict):
                errors.append({"path": "skills_provider", "reason": "metadata-only mode must declare a skills provider"})
            else:
                if provider.get("scope") != "user":
                    errors.append({"path": "skills_provider.scope", "reason": "metadata-only mode requires user scoped skills provider"})
                if provider.get("registration_authority") != "workstation":
                    errors.append({"path": "skills_provider.registration_authority", "reason": "metadata-only provider registration authority must be workstation"})
    else:
        errors.append({"path": "repo_payload", "reason": "metadata-only repo payload declaration is required"})
    return errors


def load_installed_state(target: Path) -> tuple[Path | None, Any | None, dict[str, Any] | None]:
    path = installed_state_path(target)
    if path is None:
        return None, None, block_installed_state(
            "installed-state",
            target,
            f"missing {INSTALLED_STATE_SCHEMA} metadata at one of: {', '.join(STATE_FILENAMES)}",
        )
    try:
        return path, read_json(path), None
    except (OSError, json.JSONDecodeError) as exc:
        return path, None, block_installed_state("installed-state", target, f"installed-state is unreadable: {exc}")


def handle_installed_state(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom installed-state")
    parser.add_argument("action", choices=("show", "validate", "export"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    command = f"installed-state {args.action}"
    path, state, error = load_installed_state(target)
    if error:
        error["command"] = command
        return emit(error)

    errors = validate_installed_state(state)
    if errors:
        return emit(
            output(
                command,
                "block",
                summary="Installed-state failed validation.",
                target=str(target),
                installed_state_path=str(path),
                runtime_state="blocked",
                upgrade_eligibility="incompatible",
                failed_layer="installed-state",
                fail_closed_reason="installed-state schema or version metadata is invalid",
                errors=errors,
                fallback_to=["loom repair plan", "loom installed-state export --target <repo> --json"],
            )
        )

    payload = output(
        command,
        "pass",
        summary="Installed-state is valid.",
        target=str(target),
        installed_state_path=str(path),
        runtime_state="ready",
        upgrade_eligibility=state.get("upgrade_eligibility", "current"),
        installed_state=state,
    )
    if args.action == "export":
        payload["installation_graph"] = state.get("installation_graph")
        payload["export_contract"] = "docs/adoption/loom-installed-state-v2.md"
    if args.action == "validate":
        payload.pop("installed_state")
        payload["validated_schema"] = INSTALLED_STATE_SCHEMA

    if args.json or True:
        return emit(payload)
    return 0


def workspace_payload(action: str, args: argparse.Namespace) -> dict[str, Any]:
    command = f"workspace {action}"
    target = resolve_target(args.target)
    item_args = ["--item", args.item] if getattr(args, "item", None) else []
    if action in {"locate", "create", "retire"}:
        operation = "retire" if action == "retire" else action
        payload = flow_payload(command, ["workspace", operation, "--target", str(target), *item_args], fallback_to=["admission", "loom workspace check --target <repo> --json"])
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return payload
    if action == "check":
        payload = flow_payload(command, ["purity-check", "--target", str(target), *item_args], fallback_to=["admission", "loom workspace locate --target <repo> --json"])
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return payload
    if action == "audit":
        payload = flow_payload(
            command,
            ["work-item-audit", "--target", str(target), *item_args],
            fallback_to=["loom carrier closeout-sync --target <repo> --item <item> --dry-run --json", "loom workspace check --target <repo> --json"],
        )
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return payload
    return output(command, "block", schema=WORKSPACE_SCHEMA, summary="Unsupported workspace action.", failed_layer="cli-router", fail_closed_reason=action, fallback_to=["loom help --json"])


def handle_workspace(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom workspace")
    parser.add_argument("action", choices=("create", "locate", "check", "audit", "retire"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--path")
    parser.add_argument("--branch")
    parser.add_argument("--item")
    parser.add_argument("--start-point", default="origin/main")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return emit(workspace_payload(args.action, args))


def handle_issue(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom issue")
    parser.add_argument("action", choices=("inspect", "bind", "reconcile"))
    parser.add_argument("issue", nargs="?")
    parser.add_argument("--work-item")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"issue {args.action}"
    if args.action == "inspect":
        if not args.issue:
            return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Issue inspect requires an issue number.", failed_layer="issue-input", fail_closed_reason="missing issue number", fallback_to=["loom help --json"]))
        return emit_flow(command, ["github-intake", "issue", "--target", ".", "--issue", args.issue], fallback_to=["github-intake", "manual-reconciliation"])
    if args.action == "bind":
        if not args.issue or not args.work_item:
            return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Issue bind requires issue and --work-item.", failed_layer="issue-binding", fail_closed_reason="missing issue or work item", fallback_to=["loom issue inspect <issue> --json"]))
        return emit_flow(command, ["host-binding", "inspect", "--target", ".", "--issue", args.issue], fallback_to=["loom issue inspect <issue> --json", "manual-reconciliation"])
    flow_args = ["reconciliation", "audit", "--target", "."]
    if args.issue:
        flow_args.extend(["--issue", args.issue])
    return emit_flow(command, flow_args, fallback_to=["manual-reconciliation"])


def handle_project(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom project")
    parser.add_argument("action", choices=("status", "reconcile"))
    parser.add_argument("--issue")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"project {args.action}"
    if args.issue:
        flow_args = ["github-intake", "issue", "--target", ".", "--issue", args.issue]
        return emit_flow(command, flow_args, fallback_to=["loom issue inspect <issue> --json", "manual-reconciliation"])
    return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Project status requires --issue for this CLI contract.", failed_layer="project-input", fail_closed_reason="missing --issue", fallback_to=["loom issue inspect <issue> --json"]))


def pr_command_target(explicit_target: str | None) -> str:
    if explicit_target:
        return explicit_target
    github_workspace = os.environ.get("GITHUB_WORKSPACE")
    if github_workspace:
        return github_workspace
    return "."


def handle_pr(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom pr")
    parser.add_argument("action", choices=("inspect", "metadata-render", "metadata-readback", "metadata-update", "metadata-preflight", "gate"))
    parser.add_argument("pr", nargs="?")
    parser.add_argument("--target")
    parser.add_argument("--head-sha")
    parser.add_argument("--work-item")
    parser.add_argument("--surface", choices=("pre_review", "review", "merge_ready", "closeout"), default="merge_ready")
    parser.add_argument("--item")
    parser.add_argument("--issue")
    parser.add_argument("--branch")
    parser.add_argument("--body-file")
    parser.add_argument("--output-file")
    parser.add_argument("--readback-file")
    parser.add_argument("--base-body-file")
    parser.add_argument("--compare-body-file")
    parser.add_argument("--gate-freeze-snapshot-file")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--governance-intensity")
    parser.add_argument("--change-class")
    parser.add_argument("--suite-path")
    parser.add_argument("--review-requirement")
    parser.add_argument("--release-judgment")
    parser.add_argument("--upgrade-trigger", action="append")
    parser.add_argument("--covered-issue", action="append", default=[])
    parser.add_argument("--excluded-scope", action="append", default=[])
    parser.add_argument("--suite-na-rationale")
    parser.add_argument("--suite-na-consumer-boundary")
    parser.add_argument("--suite-na-recheck-condition")
    parser.add_argument("--suite-na-scope-proof")
    parser.add_argument("--suite-na-review-requirement")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", dest="dry_run", action="store_false")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    command = f"pr {args.action}"
    target = pr_command_target(args.target)
    if not args.pr and not (
        args.action in {"metadata-render", "metadata-readback", "metadata-update"}
        or args.action == "metadata-preflight" and args.body_file
    ):
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="PR command requires a PR number.", failed_layer="pr-input", fail_closed_reason="missing PR number", fallback_to=["loom help --json"]))
    if args.action == "inspect":
        flow_args = ["host-binding", "inspect", "--target", target, "--pr", args.pr]
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        append_full_output_flag(flow_args, args)
        return emit_flow(command, flow_args, fallback_to=["loom pr gate <pr> --json", "manual-reconciliation"])
    if args.action == "metadata-render":
        flow_args = ["pr-metadata", "render", "--target", target, "--surface", args.surface]
        if args.item:
            flow_args.extend(["--item", args.item])
        if args.issue:
            flow_args.extend(["--issue", args.issue])
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        if args.branch:
            flow_args.extend(["--branch", args.branch])
        if args.output_file:
            flow_args.extend(["--output-file", args.output_file])
        if args.base_body_file:
            flow_args.extend(["--base-body-file", args.base_body_file])
        if args.governance_intensity:
            flow_args.extend(["--governance-intensity", args.governance_intensity])
        if args.change_class:
            flow_args.extend(["--change-class", args.change_class])
        if args.suite_path:
            flow_args.extend(["--suite-path", args.suite_path])
        if args.review_requirement:
            flow_args.extend(["--review-requirement", args.review_requirement])
        if args.release_judgment:
            flow_args.extend(["--release-judgment", args.release_judgment])
        for trigger in args.upgrade_trigger or []:
            flow_args.extend(["--upgrade-trigger", trigger])
        for issue in args.covered_issue or []:
            flow_args.extend(["--covered-issue", issue])
        for scope in args.excluded_scope or []:
            flow_args.extend(["--excluded-scope", scope])
        if args.suite_na_rationale:
            flow_args.extend(["--suite-na-rationale", args.suite_na_rationale])
        if args.suite_na_consumer_boundary:
            flow_args.extend(["--suite-na-consumer-boundary", args.suite_na_consumer_boundary])
        if args.suite_na_recheck_condition:
            flow_args.extend(["--suite-na-recheck-condition", args.suite_na_recheck_condition])
        if args.suite_na_scope_proof:
            flow_args.extend(["--suite-na-scope-proof", args.suite_na_scope_proof])
        if args.suite_na_review_requirement:
            flow_args.extend(["--suite-na-review-requirement", args.suite_na_review_requirement])
        append_full_output_flag(flow_args, args)
        return emit_flow(command, flow_args, fallback_to=["loom pr metadata-preflight --surface merge_ready --body-file <rendered-pr-body.md> --json"])
    if args.action == "metadata-readback":
        flow_args = ["pr-metadata", "readback", "--target", target, "--surface", args.surface]
        if args.pr:
            flow_args.extend(["--pr", args.pr])
        if args.item:
            flow_args.extend(["--item", args.item])
        if args.issue:
            flow_args.extend(["--issue", args.issue])
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        if args.branch:
            flow_args.extend(["--branch", args.branch])
        if args.body_file:
            flow_args.extend(["--body-file", args.body_file])
        if args.readback_file:
            flow_args.extend(["--readback-file", args.readback_file])
        if args.compare_body_file:
            flow_args.extend(["--compare-body-file", args.compare_body_file])
        if args.pr_payload_file:
            flow_args.extend(["--pr-payload-file", args.pr_payload_file])
        append_full_output_flag(flow_args, args)
        return emit_flow(command, flow_args, fallback_to=["loom pr metadata-preflight --surface merge_ready --body-file <rendered-pr-body.md> --json"])
    if args.action == "metadata-update":
        flow_args = ["pr-metadata", "update", "--target", target, "--surface", args.surface]
        if args.pr:
            flow_args.extend(["--pr", args.pr])
        if args.item:
            flow_args.extend(["--item", args.item])
        if args.issue:
            flow_args.extend(["--issue", args.issue])
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        if args.branch:
            flow_args.extend(["--branch", args.branch])
        if args.output_file:
            flow_args.extend(["--output-file", args.output_file])
        if args.readback_file:
            flow_args.extend(["--readback-file", args.readback_file])
        if args.base_body_file:
            flow_args.extend(["--base-body-file", args.base_body_file])
        if args.governance_intensity:
            flow_args.extend(["--governance-intensity", args.governance_intensity])
        if args.change_class:
            flow_args.extend(["--change-class", args.change_class])
        if args.suite_path:
            flow_args.extend(["--suite-path", args.suite_path])
        if args.review_requirement:
            flow_args.extend(["--review-requirement", args.review_requirement])
        if args.release_judgment:
            flow_args.extend(["--release-judgment", args.release_judgment])
        for trigger in args.upgrade_trigger or []:
            flow_args.extend(["--upgrade-trigger", trigger])
        for issue in args.covered_issue or []:
            flow_args.extend(["--covered-issue", issue])
        for scope in args.excluded_scope or []:
            flow_args.extend(["--excluded-scope", scope])
        if args.suite_na_rationale:
            flow_args.extend(["--suite-na-rationale", args.suite_na_rationale])
        if args.suite_na_consumer_boundary:
            flow_args.extend(["--suite-na-consumer-boundary", args.suite_na_consumer_boundary])
        if args.suite_na_recheck_condition:
            flow_args.extend(["--suite-na-recheck-condition", args.suite_na_recheck_condition])
        if args.suite_na_scope_proof:
            flow_args.extend(["--suite-na-scope-proof", args.suite_na_scope_proof])
        if args.suite_na_review_requirement:
            flow_args.extend(["--suite-na-review-requirement", args.suite_na_review_requirement])
        flow_args.append("--apply" if not args.dry_run else "--dry-run")
        append_full_output_flag(flow_args, args)
        return emit_flow(command, flow_args, fallback_to=["loom pr metadata-render --surface merge_ready --json", "loom pr metadata-readback --surface merge_ready --pr <number> --json"])
    if args.action == "metadata-preflight":
        flow_args = ["pr-metadata", "preflight", "--target", target, "--surface", args.surface]
        if args.pr:
            flow_args.extend(["--pr", args.pr])
        if args.item:
            flow_args.extend(["--item", args.item])
        if args.issue:
            flow_args.extend(["--issue", args.issue])
        if args.head_sha:
            flow_args.extend(["--head-sha", args.head_sha])
        if args.branch:
            flow_args.extend(["--branch", args.branch])
        if args.body_file:
            flow_args.extend(["--body-file", args.body_file])
        if args.compare_body_file:
            flow_args.extend(["--compare-body-file", args.compare_body_file])
        if args.pr_payload_file:
            flow_args.extend(["--pr-payload-file", args.pr_payload_file])
        append_full_output_flag(flow_args, args)
        return emit_flow(command, flow_args, fallback_to=["update PR body", "loom pr inspect <pr> --json"])
    flow_args = ["pr-gate", "check", "--target", target, "--pr", args.pr]
    if args.surface:
        flow_args.extend(["--surface", args.surface])
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.work_item:
        flow_args.extend(["--item", args.work_item])
    if args.body_file:
        flow_args.extend(["--body-file", args.body_file])
    if args.compare_body_file:
        flow_args.extend(["--compare-body-file", args.compare_body_file])
    if args.pr_payload_file:
        flow_args.extend(["--pr-payload-file", args.pr_payload_file])
    if args.gate_freeze_snapshot_file:
        flow_args.extend(["--gate-freeze-snapshot-file", args.gate_freeze_snapshot_file])
    append_full_output_flag(flow_args, args)
    return emit_flow(command, flow_args, fallback_to=["loom pr inspect <pr> --json", "manual-reconciliation"])


def handle_merge(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom merge")
    parser.add_argument("action", choices=("check", "run"))
    parser.add_argument("pr", metavar="pr-number", type=int)
    parser.add_argument("--target")
    parser.add_argument("--head-sha")
    parser.add_argument("--work-item")
    parser.add_argument("--merge-method", choices=("squash", "merge", "rebase"), default="merge")
    parser.add_argument("--delete-branch", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--closeout-run", action="store_true")
    parser.add_argument("--closeout-mode", choices=("host_only", "inline", "batched_carrier_pr", "full_closeout_pr"), default="host_only")
    add_legacy_carrier_compatibility_args(parser)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--target-branch")
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES)
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
    parser.add_argument("--carrier-sync-pr", type=int)
    parser.add_argument("--final-closeout-pr", type=int)
    parser.add_argument("--project")
    parser.add_argument("--phase")
    parser.add_argument("--fr")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--comment")
    parser.add_argument("--comment-file")
    parser.add_argument("--goal-completion")
    parser.add_argument("--attestation-artifact-input", type=Path)
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--gate-profile", choices=("auto", "closeout-contract", "source-self-fixture", "bootstrap-regression", "distribution-regression", "strong-profile-full-gate"))
    parser.add_argument("--issue-payload-file")
    parser.add_argument("--project-payload-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--pr-gate-result-file")
    parser.add_argument("--merge-gate-result-file")
    parser.add_argument("--governance-mode", choices=("host-enforced", "advisory/local-enforced"), default="host-enforced")
    parser.add_argument("--allow-advisory-local-enforced", action="store_true")
    parser.add_argument("--allow-high-risk-advisory", action="store_true")
    parser.add_argument("--change-class")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    command = f"merge {args.action}"
    if args.closeout_mode != "host_only":
        compatibility = legacy_carrier_compatibility(args)
        if compatibility["result"] != "pass":
            return emit(
                agent_safe_payload(
                    output(
                        command,
                        "block",
                        schema_version="loom-legacy-carrier-command/v1",
                        summary=compatibility["summary"],
                        mutates=False,
                        compatibility=compatibility,
                        missing_inputs=compatibility["missing_inputs"],
                        fallback_to="use --closeout-mode host_only",
                    )
                )
            )
    target = resolve_target(pr_command_target(args.target))
    flow_args = [
        "controlled-merge",
        "merge" if args.action == "run" else "check",
        "--target",
        str(target),
        "--pr",
        str(args.pr),
        "--merge-method",
        args.merge_method,
    ]
    if args.delete_branch:
        flow_args.append("--delete-branch")
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.work_item:
        flow_args.extend(["--item", args.work_item])
    if args.issue:
        flow_args.extend(["--issue", args.issue])
    if args.owner:
        flow_args.extend(["--owner", args.owner])
    if args.repo_name:
        flow_args.extend(["--repo", args.repo_name])
    for option, value in (
        ("--pr-payload-file", args.pr_payload_file),
        ("--status-checks-file", args.status_checks_file),
        ("--branch-protection-file", args.branch_protection_file),
        ("--ruleset-file", args.ruleset_file),
        ("--pr-gate-result-file", args.pr_gate_result_file),
        ("--merge-gate-result-file", args.merge_gate_result_file),
        ("--governance-mode", args.governance_mode),
        ("--change-class", args.change_class),
    ):
        if value:
            flow_args.extend([option, value])
    if args.allow_advisory_local_enforced:
        flow_args.append("--allow-advisory-local-enforced")
    if args.allow_high_risk_advisory:
        flow_args.append("--allow-high-risk-advisory")
    if args.action == "run" and args.apply:
        flow_args.append("--execute")
    append_full_output_flag(flow_args, args)
    if args.closeout_run:
        return handle_merge_closeout_run(command, args, flow_args)
    return emit_flow(command, flow_args, fallback_to=["loom pr gate <pr> --json", "loom merge check <pr> --json"])


def merge_closeout_namespace(args: argparse.Namespace, *, branch: str) -> argparse.Namespace:
    return argparse.Namespace(
        item=args.work_item,
        issue=args.issue,
        pr=args.pr,
        pr_role=args.pr_role,
        implementation_pr=args.implementation_pr,
        release_pr=args.release_pr,
        carrier_sync_pr=args.carrier_sync_pr,
        final_closeout_pr=args.final_closeout_pr,
        project=args.project,
        phase=args.phase,
        fr=args.fr,
        branch=branch,
        owner=args.owner,
        repo_name=args.repo_name,
        comment=args.comment,
        comment_file=args.comment_file,
        goal_completion=args.goal_completion,
        attestation_artifact_input=args.attestation_artifact_input,
        review_policy=args.review_policy,
        gate_profile=args.gate_profile,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
        status_checks_file=args.status_checks_file,
        branch_protection_file=args.branch_protection_file,
        ruleset_file=args.ruleset_file,
        skip_gate=args.skip_gate,
        apply=True,
    )


def merge_closeout_policy(args: argparse.Namespace) -> dict[str, Any]:
    mode = getattr(args, "closeout_mode", "inline")
    next_action = {
        "inline": "legacy compatibility: run the retired repo closeout backend after controlled merge",
        "host_only": "run host reconciliation and closeout readback immediately after controlled merge passes",
        "batched_carrier_pr": "queue carrier closeout after merge; do not inline carrier writes in controlled-merge",
        "full_closeout_pr": "use an explicit closeout or release PR path before merging through controlled-merge --closeout-run",
    }[mode]
    return {
        "schema_version": "loom-closeout-policy-decision/v1",
        "result": "pass",
        "policy": mode,
        "source": "merge-closeout-run",
        "creates_closeout_pr_by_default": False,
        "next_action": next_action,
    }


def merge_closeout_step(name: str, payload: dict[str, Any], *, mutates: bool, evidence_locator: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "result": payload.get("result"),
        "summary": payload.get("summary"),
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "mutates": mutates,
        "evidence_locator": evidence_locator,
        "payload": payload,
    }


def merge_closeout_target_branch(args: argparse.Namespace, merge_payload: dict[str, Any]) -> str | None:
    return args.target_branch or payload_pr_string(merge_payload, "baseRefName")


def merge_closeout_block(
    command: str,
    args: argparse.Namespace,
    *,
    summary: str,
    missing_inputs: list[str],
    steps: list[dict[str, Any]] | None = None,
    fallback_to: list[str] | str | None = None,
) -> int:
    fallback = fallback_to or ["loom merge run <pr> --apply --closeout-run --work-item <id> --issue <n> --target-branch <branch> --json"]
    mutates = any(bool(step.get("mutates")) for step in steps or [])
    closeout_policy = merge_closeout_policy(args)
    target = resolve_target(pr_command_target(args.target))
    return emit(
        agent_safe_payload(
            output(
                command,
                "block",
                schema_version="loom-merge-run/v1",
                summary=summary,
                mutates=mutates,
                apply=bool(args.apply),
                closeout_run=True,
                item={"id": args.work_item},
                issue={"number": args.issue},
                pr={"number": args.pr},
                merge_method=args.merge_method,
                closeout_policy=closeout_policy,
                closeout_mode=closeout_policy["policy"],
                creates_closeout_pr=False,
                steps=steps or [],
                missing_inputs=missing_inputs,
                fallback_to=fallback,
                next_action=fallback[0] if isinstance(fallback, list) else fallback,
            ),
            target_root=target,
            full_output=args.full_output,
        )
    )


def handle_merge_closeout_run(command: str, args: argparse.Namespace, flow_args: list[str]) -> int:
    forwarded_args, full_output = split_agent_output_args(flow_args)
    closeout_policy = merge_closeout_policy(args)
    if args.action != "run" or not args.apply:
        return merge_closeout_block(
            command,
            args,
            summary="merge --closeout-run requires an explicit mutating merge run.",
            missing_inputs=["--closeout-run requires `loom merge run <pr> --apply`"],
            fallback_to=["loom merge run <pr> --apply --closeout-run --work-item <id> --issue <n> --target-branch <branch> --json"],
        )
    if not args.work_item:
        return merge_closeout_block(
            command,
            args,
            summary="merge --closeout-run requires a Work Item binding for closeout.",
            missing_inputs=["--work-item is required for --closeout-run"],
        )
    if not args.issue:
        return merge_closeout_block(
            command,
            args,
            summary="merge --closeout-run requires an issue binding for closeout.",
            missing_inputs=["--issue is required for --closeout-run"],
        )
    if closeout_policy["policy"] not in {"inline", "host_only"}:
        mode = closeout_policy["policy"]
        return merge_closeout_block(
            command,
            args,
            summary=f"merge --closeout-run cannot inline closeout mode `{mode}`.",
            missing_inputs=[f"closeout mode `{mode}` requires an explicit post-merge carrier or closeout PR path"],
            fallback_to=[str(closeout_policy["next_action"])],
        )

    target = resolve_target(pr_command_target(args.target))
    steps: list[dict[str, Any]] = []
    if closeout_policy["policy"] == "host_only":
        premerge_attestation_args = merge_closeout_namespace(args, branch=args.target_branch or "")
        premerge_attestation = ship_host_attestation(premerge_attestation_args, target, closeout=False)
        steps.append(
            merge_closeout_step(
                "host-review-attestation",
                premerge_attestation,
                mutates=False,
                evidence_locator="GitHub host attestation readback",
            )
        )
        if premerge_attestation.get("result") != "pass":
            return merge_closeout_block(
                command,
                args,
                summary="merge run stopped before controlled merge because host review attestation did not pass.",
                missing_inputs=[str(value) for value in premerge_attestation.get("missing_inputs", [])],
                steps=steps,
                fallback_to=premerge_attestation.get("fallback_to") or "provide a valid GitHub host attestation artifact",
            )
    merge_payload = flow_payload(command, forwarded_args, fallback_to=["loom pr gate <pr> --json", "loom merge check <pr> --json"])
    steps.append(merge_closeout_step("controlled-merge-apply", merge_payload, mutates=True))
    if merge_payload.get("command") and merge_payload.get("command") != command:
        merge_payload["wrapped_command"] = merge_payload.get("command")
    merge_payload["command"] = command
    if merge_payload.get("result") != "pass":
        blocker = steps[-1]
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block",
                    schema_version="loom-merge-run/v1",
                    summary="merge run stopped because controlled merge did not pass; closeout-run was not started.",
                    mutates=True,
                    apply=True,
                    closeout_run=True,
                    item={"id": args.work_item},
                    issue={"number": args.issue},
                    pr={"number": args.pr},
                    merge_method=args.merge_method,
                    closeout_policy=closeout_policy,
                    closeout_mode=closeout_policy["policy"],
                    creates_closeout_pr=False,
                    steps=steps,
                    first_blocker=blocker,
                    missing_inputs=blocker.get("missing_inputs", []),
                    fallback_to=blocker.get("fallback_to"),
                    next_action=blocker.get("fallback_to") or "resolve controlled merge blocker before retrying closeout-run",
                ),
                target_root=target,
                full_output=full_output,
            )
        )

    closeout_branch = merge_closeout_target_branch(args, merge_payload)
    if not closeout_branch:
        return merge_closeout_block(
            command,
            args,
            summary="merge run merged successfully but could not infer the target branch for closeout-run.",
            missing_inputs=["target branch is required for closeout-run"],
            steps=steps,
            fallback_to=["rerun closeout with --target-branch <base-branch> or `loom closeout run --branch <base-branch> --apply --json`"],
        )

    closeout_args = merge_closeout_namespace(args, branch=closeout_branch)
    closeout: dict[str, Any]
    terminal_metadata: dict[str, Any] = {}
    if closeout_policy["policy"] == "host_only":
        reconciliation_args = ["reconciliation", "sync", "--target", str(target)]
        add_closeout_host_args(reconciliation_args, closeout_args, include_comment=True)
        reconciliation_args.append("--apply")
        reconciliation = flow_payload(command, reconciliation_args, fallback_to=["manual-reconciliation", "loom closeout --target <repo> --json"])
        steps.append(merge_closeout_step("host-reconciliation-sync", reconciliation, mutates=True, evidence_locator="reconciliation sync payload"))
        if reconciliation.get("result") == "pass":
            closeout = ship_host_attestation(closeout_args, target, closeout=True)
            steps.append(merge_closeout_step("host-closeout-attestation", closeout, mutates=False, evidence_locator="GitHub host attestation readback"))
        else:
            closeout = reconciliation
    else:
        closeout = run_closeout_payload(closeout_args, target)
        terminal_metadata = closeout.get("terminal_metadata") if isinstance(closeout.get("terminal_metadata"), dict) else {}
        evidence_locator = terminal_metadata.get("evidence_locator") if isinstance(terminal_metadata, dict) else None
        steps.append(merge_closeout_step("closeout-run", closeout, mutates=True, evidence_locator=evidence_locator))
    blocker = first_blocking_step(steps)
    result = "pass" if blocker is None else "block"
    summary = (
        f"merge run applied controlled merge and {closeout_policy['policy']} closeout without creating a closeout PR."
        if result == "pass"
        else "merge run applied controlled merge if it passed, then stopped at the policy-selected closeout blocker."
    )
    return emit(
        agent_safe_payload(
            output(
                command,
                result,
                schema_version="loom-merge-run/v1",
                summary=summary,
                mutates=True,
                apply=True,
                closeout_run=True,
                item={"id": args.work_item},
                issue={"number": args.issue, "state": closeout.get("issue", {}).get("state") if isinstance(closeout.get("issue"), dict) else None},
                pr={"number": args.pr, "state": closeout.get("pr", {}).get("state") if isinstance(closeout.get("pr"), dict) else None},
                merge_method=args.merge_method,
                closeout_policy=closeout_policy,
                closeout_mode=closeout_policy["policy"],
                creates_closeout_pr=False,
                target_branch=closeout_branch,
                terminal_metadata=terminal_metadata,
                evidence_locators=closeout.get("evidence_locators", []),
                steps=steps,
                first_blocker=blocker,
                missing_inputs=blocker.get("missing_inputs", []) if blocker else [],
                fallback_to=blocker.get("fallback_to") if blocker else None,
                next_action=blocker.get("fallback_to") if blocker else "merge and closeout-run completed; read back PR, issue, and target branch state.",
            ),
            target_root=target,
            full_output=full_output,
        )
    )


def ship_step(name: str, payload: dict[str, Any], *, mutates: bool = False, skipped_reason: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "result": payload.get("result", "skipped" if skipped_reason else None),
        "summary": payload.get("summary", skipped_reason),
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "mutates": mutates,
        "skipped_reason": skipped_reason,
        "payload": payload,
    }


def governance_metadata_fields(payload: dict[str, Any]) -> dict[str, Any]:
    carrier = payload.get("governance_intensity_carrier")
    envelope = carrier.get("envelope") if isinstance(carrier, dict) else None
    fields = envelope.get("fields") if isinstance(envelope, dict) else None
    return fields if isinstance(fields, dict) else {}


LEGACY_CARRIER_COMPATIBILITY_POLICY = "reinforced-carrier-compat/v1"
LEGACY_CARRIER_COMPATIBILITY_MAX_DAYS = 90


def legacy_carrier_compatibility(args: argparse.Namespace) -> dict[str, Any]:
    expiry_text = str(getattr(args, "compatibility_expires_at", "") or "").strip()
    expiry: datetime | None = None
    try:
        parsed = datetime.fromisoformat(expiry_text.replace("Z", "+00:00"))
        expiry = parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None
    except ValueError:
        expiry = None
    now = datetime.now(timezone.utc)
    valid = (
        getattr(args, "governance_intensity", None) == "reinforced"
        and getattr(args, "compatibility_policy", None) == LEGACY_CARRIER_COMPATIBILITY_POLICY
        and expiry is not None
        and now < expiry <= now + timedelta(days=LEGACY_CARRIER_COMPATIBILITY_MAX_DAYS)
    )
    return {
        "schema_version": "loom-legacy-carrier-compatibility/v1",
        "result": "pass" if valid else "block",
        "policy": getattr(args, "compatibility_policy", None),
        "governance_intensity": getattr(args, "governance_intensity", None),
        "expires_at": expiry_text or None,
        "max_days": LEGACY_CARRIER_COMPATIBILITY_MAX_DAYS,
        "summary": (
            "A reinforced, time-bounded compatibility exception explicitly enables the retired carrier backend."
            if valid
            else "The retired carrier backend is disabled outside an explicit reinforced, time-bounded compatibility exception."
        ),
        "missing_inputs": [] if valid else [
            f"set --governance-intensity reinforced --compatibility-policy {LEGACY_CARRIER_COMPATIBILITY_POLICY} "
            f"--compatibility-expires-at <RFC3339 within {LEGACY_CARRIER_COMPATIBILITY_MAX_DAYS} days>"
        ],
        "fallback_to": None if valid else "use host attestation/readback and host-only closeout",
    }


def add_legacy_carrier_compatibility_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--governance-intensity", choices=("reinforced",))
    parser.add_argument("--compatibility-policy")
    parser.add_argument("--compatibility-expires-at")


def split_legacy_carrier_compatibility_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    add_legacy_carrier_compatibility_args(parser)
    return parser.parse_known_args(argv)


def handle_review_command(argv: list[str]) -> int:
    if not argv or argv[0] != "record":
        return dispatch("review", argv)
    compatibility_args, forwarded = split_legacy_carrier_compatibility_args(argv[1:])
    compatibility = legacy_carrier_compatibility(compatibility_args)
    if compatibility["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    "review record",
                    "block",
                    schema_version="loom-legacy-carrier-command/v1",
                    summary=compatibility["summary"],
                    mutates=False,
                    compatibility=compatibility,
                    missing_inputs=compatibility["missing_inputs"],
                    fallback_to="loom attestation readback --repo <owner/repo> --pr <n> --work-item <n> --artifact-input <file> --json",
                )
            )
        )
    return dispatch("review", ["record", *forwarded])


def ship_closeout_policy(fields: dict[str, Any], *, intensity_override: str | None = None) -> dict[str, Any]:
    intensity = intensity_override if intensity_override not in {None, "auto"} else fields.get("governance_intensity")
    change_class = fields.get("change_class")
    release_judgment = fields.get("release_judgment")
    governance_mode = fields.get("governance_mode") or "host-enforced"
    governance_assurance = fields.get("governance_assurance") or ("low" if governance_mode == "advisory/local-enforced" else "strong")
    advisory_risk_label = fields.get("advisory_risk_label") if governance_mode == "advisory/local-enforced" else None
    triggers = [str(value) for value in fields.get("upgrade_triggers", []) if str(value)]
    lowered = " ".join([str(change_class or ""), *triggers]).lower()
    upgrade_reasons: list[str] = []
    if release_judgment == "release_required" or change_class == "release" or any(word in lowered for word in ("release", "version")):
        policy = "release_manifest"
        upgrade_reasons.append("release_source_change_requires_release_workflow")
    else:
        policy = "host_only"
        if intensity == "reinforced" or any(word in lowered for word in ("security", "permission", "conflict", "parent", "milestone", "multi")):
            upgrade_reasons.append("reinforced_review_without_repo_closeout_carrier")
    return {
        "schema_version": "loom-closeout-policy-decision/v1",
        "result": "pass",
        "policy": policy,
        "governance_intensity": intensity,
        "governance_mode": governance_mode,
        "governance_assurance": governance_assurance,
        "advisory_risk_label": advisory_risk_label,
        "host_enforced": governance_mode == "host-enforced",
        "change_class": change_class,
        "release_judgment": release_judgment,
        "upgrade_reasons": upgrade_reasons,
        "creates_closeout_pr_by_default": False,
        "legacy_carrier_compatibility_policy": LEGACY_CARRIER_COMPATIBILITY_POLICY,
        "next_action": "run loom ship --apply after dry-run blockers are clear" if policy == "host_only" else "publish through the release workflow, then use release readback without a closeout PR",
    }


SHIP_VALIDATION_PROFILE_CHOICES = ("auto", "host-consumer", "carrier-only", "light", "standard", "full", "release")
SHIP_VALIDATION_SOURCE_SURFACES = {
    "host-consumer": None,
    "carrier-only": None,
    "light": "contract-only",
    "standard": "source-self-fixture",
    "full": "daily-execution-cli-full",
    "release": "distribution-regression",
}


def normalize_changed_path(path: object) -> str | None:
    text = str(path or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text or None


def dedupe_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def ship_pr_changed_paths(args: argparse.Namespace, target: Path) -> tuple[list[str], list[str]]:
    if args.pr is None:
        return [], ["PR number is required for changed path readback"]
    repo_slug = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else infer_github_repo(target)
    if not repo_slug:
        return [], ["unable to infer GitHub repository for changed path readback; pass --owner and --repo"]
    completed = run_capture(
        [
            "gh",
            "api",
            "--paginate",
            f"repos/{repo_slug}/pulls/{args.pr}/files",
            "--slurp",
            "--jq",
            "map(.[].filename)",
        ],
        cwd=target,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "gh api pull request files readback failed"
        return [], [detail]
    try:
        decoded = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON from gh api pull request files readback: {exc.msg}"]
    if not isinstance(decoded, list):
        return [], ["gh api pull request files readback did not return a JSON array"]
    paths = sorted({normalized for value in decoded if (normalized := normalize_changed_path(value))})
    return paths, []


def ship_local_changed_paths(target: Path, *, target_branch: str | None, head_sha: str | None) -> tuple[list[str], list[str]]:
    candidates: list[str] = []
    if target_branch:
        candidates.extend([f"origin/{target_branch}", target_branch])
    errors: list[str] = []
    for base in candidates:
        range_spec = f"{base}...{head_sha or 'HEAD'}"
        completed = run_capture(["git", "-C", str(target), "diff", "--name-only", range_spec])
        if completed.returncode == 0:
            paths = sorted({normalized for line in completed.stdout.splitlines() if (normalized := normalize_changed_path(line))})
            return paths, []
        detail = completed.stderr.strip() or completed.stdout.strip()
        if detail:
            errors.append(detail)
    return [], errors or ["target branch is unavailable for local changed path diff"]


def ship_changed_paths_payload(args: argparse.Namespace, target: Path, *, target_branch: str | None, head_sha: str | None) -> dict[str, Any]:
    paths, errors = ship_pr_changed_paths(args, target)
    source = "github_pr_files"
    if errors:
        local_paths, local_errors = ship_local_changed_paths(target, target_branch=target_branch, head_sha=head_sha)
        if local_paths or not local_errors:
            paths = local_paths
            errors = []
            source = "local_git_diff"
        else:
            errors.extend(local_errors)
    result = "pass" if not errors else "warn"
    return {
        "schema_version": "loom-ship-changed-paths/v1",
        "result": result,
        "summary": (
            f"ship read {len(paths)} changed path(s) from {source}."
            if result == "pass"
            else "ship could not read changed paths and will choose the safe standard validation profile."
        ),
        "source": source if result == "pass" else None,
        "changed_paths": paths,
        "missing_inputs": errors,
        "fallback_to": None if result == "pass" else "rerun loom ship with readable PR files or an up-to-date target branch",
    }


def path_matches_any(path: str, prefixes: tuple[str, ...], exact: tuple[str, ...] = ()) -> bool:
    return path in exact or any(path.startswith(prefix) for prefix in prefixes)


PR_INTENT_PROFILE_SCHEMA = "loom-pr-intent-profile/v1"
PR_INTENT_PREPARE_SCHEMA = "loom-pr-intent-prepare/v1"
PR_INTENT_CHECK_SCHEMA = "loom-pr-intent-check/v1"

PR_INTENT_SHARED_CONTRACTS = (
    "docs/methodology/harness/cli-command-matrix.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/harness/task-carrier-contract.md",
    ".loom/companion/repo-interface.json",
)

PR_INTENT_DOC_PREFIXES = (
    "docs/",
    ".loom/specs/",
    ".loom/work-items/",
    ".loom/progress/",
    ".loom/status/",
    ".loom/reviews/",
    ".loom/shadow/",
)
PR_INTENT_DOC_EXACT = (
    "README.md",
    "README.zh-CN.md",
    "VISION.md",
    "AGENTS.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
)
PR_INTENT_CARRIER_PREFIXES = (
    ".loom/bootstrap/",
    ".loom/work-items/",
    ".loom/progress/",
    ".loom/status/",
    ".loom/reviews/",
    ".loom/shadow/",
    ".loom/runtime/",
)
PR_INTENT_RELEASE_PREFIXES = (
    "docs/evidence/",
    "plugins/loom/",
    "packages/",
    ".github/workflows/",
)
PR_INTENT_RELEASE_EXACT = (
    "VERSION",
    "package.json",
    "package-lock.json",
    "README.md",
    "README.zh-CN.md",
)
PR_INTENT_RELEASE_ALLOWED_PREFIXES = PR_INTENT_RELEASE_PREFIXES + PR_INTENT_CARRIER_PREFIXES
PR_INTENT_FIXTURE_PREFIXES = (
    "test/",
    "docs/evidence/fixtures/",
    "examples/new-project/",
    ".loom/specs/",
)
PR_INTENT_RUNTIME_UPGRADE_PREFIXES = (
    ".github/workflows/",
    ".loom/specs/",
    ".loom/runtime/",
    ".loom/work-items/",
    ".loom/progress/",
    ".loom/status/",
    ".loom/reviews/",
    ".loom/shadow/",
)

PR_INTENT_PROFILES: dict[str, dict[str, Any]] = {
    "docs-governance-only": {
        "aliases": ("docs", "docs-only", "governance-only", "docs-pr"),
        "summary": "Docs/governance-only PR carrier set.",
        "surface": "merge_ready",
        "governance_intensity": "light",
        "change_class": "docs_governance",
        "suite_path": "not_applicable",
        "review_requirement": "current_head_review_required",
        "release_judgment": "no_release",
        "upgrade_triggers": (),
        "allowed_prefixes": PR_INTENT_DOC_PREFIXES,
        "allowed_exact": PR_INTENT_DOC_EXACT,
        "default_rationale": "docs/governance-only PR intent does not require a formal behavior suite",
        "default_consumer_boundary": "suite validate, review, PR gate, merge-ready, and closeout may consume this only as formal suite non-applicability; Work Item truth, current-head review, CI, no-release judgment, and closeout evidence remain required",
        "default_recheck_condition": "scope expands beyond docs/governance-only carrier or contract text",
    },
    "closeout-only": {
        "aliases": ("closeout", "final-closeout-only"),
        "summary": "Terminal closeout-only PR carrier set.",
        "surface": "closeout",
        "governance_intensity": "standard",
        "change_class": "metadata_schema",
        "suite_path": "not_applicable",
        "review_requirement": "current_head_review_required",
        "release_judgment": "no_release",
        "upgrade_triggers": ("closeout_only",),
        "allowed_prefixes": PR_INTENT_CARRIER_PREFIXES,
        "allowed_exact": (),
        "default_rationale": "closeout-only PR intent only consumes already completed implementation facts",
        "default_consumer_boundary": "closeout, PR gate, and merge-ready may consume this only as formal suite non-applicability; retained review, PR metadata, host reconciliation, and terminal carrier evidence remain required",
        "default_recheck_condition": "diff touches implementation/runtime paths or non-terminal carriers",
    },
    "release-only": {
        "aliases": ("release", "release-prep-only"),
        "summary": "Release-only PR carrier set.",
        "surface": "merge_ready",
        "governance_intensity": "standard",
        "change_class": "release",
        "suite_path": "minimal",
        "review_requirement": "current_head_review_required",
        "release_judgment": "release_required",
        "upgrade_triggers": ("release_or_version_closeout",),
        "allowed_prefixes": PR_INTENT_RELEASE_ALLOWED_PREFIXES,
        "allowed_exact": PR_INTENT_RELEASE_EXACT,
        "default_rationale": None,
        "default_consumer_boundary": None,
        "default_recheck_condition": None,
    },
    "carrier-sync-only": {
        "aliases": ("carrier-sync", "carrier-only"),
        "summary": "Carrier-sync-only PR carrier set.",
        "surface": "closeout",
        "governance_intensity": "standard",
        "change_class": "metadata_schema",
        "suite_path": "not_applicable",
        "review_requirement": "current_head_review_required",
        "release_judgment": "no_release",
        "upgrade_triggers": ("carrier_sync_only",),
        "allowed_prefixes": PR_INTENT_CARRIER_PREFIXES,
        "allowed_exact": (),
        "default_rationale": "carrier-sync-only PR intent synchronizes derived Loom carriers from existing facts",
        "default_consumer_boundary": "review, PR gate, merge-ready, and closeout may consume this only as carrier synchronization non-applicability; implementation review, host readback, and closeout evidence remain required",
        "default_recheck_condition": "carrier sync introduces new implementation scope or a non-consumed fact",
    },
    "fixture-only": {
        "aliases": ("fixture", "fixtures-only"),
        "summary": "Fixture-only PR carrier set.",
        "surface": "merge_ready",
        "governance_intensity": "light",
        "change_class": "fixture",
        "suite_path": "minimal",
        "review_requirement": "current_head_review_required",
        "release_judgment": "no_release",
        "upgrade_triggers": (),
        "allowed_prefixes": PR_INTENT_FIXTURE_PREFIXES,
        "allowed_exact": (),
        "default_rationale": None,
        "default_consumer_boundary": None,
        "default_recheck_condition": None,
    },
    "runtime-upgrade-only": {
        "aliases": ("runtime-upgrade", "loom-runtime-upgrade", "workflow-runtime-upgrade"),
        "summary": "Single-repository Loom runtime workflow pin upgrade PR carrier set.",
        "surface": "merge_ready",
        "governance_intensity": "light",
        "change_class": "runtime_upgrade",
        "suite_path": "not_applicable",
        "review_requirement": "current_head_review_required",
        "release_judgment": "no_release",
        "upgrade_triggers": ("runtime_upgrade",),
        "allowed_prefixes": PR_INTENT_RUNTIME_UPGRADE_PREFIXES,
        "allowed_exact": (),
        "default_rationale": "runtime-upgrade-only PR intent updates the target repository Loom workflow pin and maintenance carriers only",
        "default_consumer_boundary": "suite validate, review, PR gate, merge-ready, and closeout may consume this only as workflow-only runtime maintenance non-applicability; PR metadata, current-head review, hosted checks, head binding, and carrier closeout remain required",
        "default_recheck_condition": "diff touches non-workflow runtime code, product behavior, release surfaces, or workstation plugin/cache state",
    },
}

PR_INTENT_ALIAS_INDEX: dict[str, str] = {
    alias: profile_id
    for profile_id, profile in PR_INTENT_PROFILES.items()
    for alias in (profile_id, *profile["aliases"])
}
PR_INTENT_PRESERVE_SUITE_PROFILES = {"closeout-only", "carrier-sync-only"}
READINESS_REASON_ORDER = (
    "head_sha_drift",
    "pr_metadata_stale",
    "review_stale",
    "shadow_stale",
    "carrier_not_terminal",
    "release_readback_mismatch",
    "carrier_set_incomplete",
)


def pr_intent_profile(raw_intent: str | None) -> tuple[str | None, dict[str, Any] | None, str | None]:
    normalized = str(raw_intent or "").strip().lower().replace("_", "-")
    profile_id = PR_INTENT_ALIAS_INDEX.get(normalized)
    if not profile_id:
        return None, None, f"unknown PR intent profile: {raw_intent or '<missing>'}"
    return profile_id, PR_INTENT_PROFILES[profile_id], None


def readiness_reasons_from_text(values: list[Any]) -> list[str]:
    text = "\n".join(str(value).lower() for value in values if value)
    reasons: list[str] = []
    if "head_sha" in text or "head sha" in text or "head-sha" in text:
        reasons.append("head_sha_drift")
    if "metadata" in text or "machine block" in text or "pr body" in text:
        reasons.append("pr_metadata_stale")
    if "review" in text:
        reasons.append("review_stale")
    if "shadow" in text:
        reasons.append("shadow_stale")
    if "carrier_not_terminal" in text or "not terminal" in text:
        reasons.append("carrier_not_terminal")
    if "release readback" in text or "release_readback" in text:
        reasons.append("release_readback_mismatch")
    if not reasons and text:
        reasons.append("carrier_set_incomplete")
    return [reason for reason in READINESS_REASON_ORDER if reason in set(reasons)]


def readiness_payload(
    *,
    ready: bool,
    reasons: list[str],
    next_command: str | None,
    summary: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "loom-shift-left-readiness/v1",
        "ready_for_hosted_gate": ready,
        "reasons": reasons,
        "next_command": None if ready else next_command,
        "summary": summary
        or (
            "Local readiness inputs are bound; hosted gate may be run for final confirmation."
            if ready
            else "Local readiness found drift or an incomplete carrier set before hosted gate."
        ),
    }


def pr_intent_effective_profile(
    *,
    target: Path,
    item: str | None,
    profile_id: str,
    profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    effective = dict(profile)
    probe: dict[str, Any] = {
        "schema_version": "loom-pr-intent-suite-path-resolution/v1",
        "profile_suite_path": profile.get("suite_path"),
        "effective_suite_path": profile.get("suite_path"),
        "source": "profile_default",
    }
    if profile_id not in PR_INTENT_PRESERVE_SUITE_PROFILES or not item:
        return effective, probe
    summary, result, payload, failed_layer, fail_reason, fallback_to = suite_validate_payload(target, item)
    existing_suite_path = str(payload.get("suite_path") or "")
    probe.update(
        {
            "suite_validate_result": result,
            "suite_path": existing_suite_path,
            "summary": summary,
            "failed_layer": failed_layer,
            "fail_closed_reason": fail_reason,
            "fallback_to": fallback_to,
        }
    )
    if result == "pass" and existing_suite_path in {"minimal", "full"}:
        effective["suite_path"] = existing_suite_path
        probe.update({"effective_suite_path": existing_suite_path, "source": "preserved_existing_suite"})
    return effective, probe


def pr_intent_current_head(target: Path, explicit_head: str | None) -> str | None:
    return explicit_head or git_head_sha_for_target(target)


def pr_intent_current_branch(target: Path, explicit_branch: str | None) -> str | None:
    return explicit_branch or git_branch_for_target(target)


def pr_intent_na_value(profile: dict[str, Any], key: str, explicit: str | None) -> str:
    return str(explicit or profile.get(f"default_{key}") or "").strip()


def pr_intent_scope_proof(profile_id: str, paths: list[str], explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    if paths:
        return f"{profile_id} changed paths: " + ", ".join(paths[:20])
    return f"{profile_id} scope proof: no changed paths reported by local diff"


def pr_intent_not_applicable_spec_content(
    *,
    item: str,
    profile_id: str,
    profile: dict[str, Any],
    rationale: str,
    consumer_boundary: str,
    recheck_condition: str,
    scope_proof: str,
) -> str:
    return (
        "# Spec\n\n"
        "- Suite path: not_applicable\n\n"
        f"- Suite-level not_applicable: rationale: {rationale}; "
        f"consumer boundary: {consumer_boundary}; "
        f"recheck condition: {recheck_condition}; "
        f"scope proof: {scope_proof}; "
        f"review requirement: {profile['review_requirement']}.\n\n"
        "## PR Intent\n\n"
        f"- Intent profile: {profile_id}\n"
        f"- Work Item: {item}\n"
        f"- Change class: {profile['change_class']}\n"
        "- Review, PR gate, merge-ready, release readback, and closeout evidence remain required by their normal gates.\n"
    )


def pr_intent_not_applicable_write(
    *,
    target: Path,
    item: str,
    profile_id: str,
    profile: dict[str, Any],
    rationale: str,
    consumer_boundary: str,
    recheck_condition: str,
    scope_proof: str,
    apply: bool,
) -> tuple[dict[str, Any], str | None]:
    item_error = suite_item_segment_error(item)
    destination = target / ".loom" / "specs" / item / "spec.md"
    locator = f".loom/specs/{item}/spec.md"
    missing_inputs: list[str] = []
    if item_error:
        missing_inputs.append(item_error)
    for component in (target / ".loom", target / ".loom" / "specs", destination.parent, destination):
        if component.is_symlink():
            try:
                missing_inputs.append(f"not_applicable path must not traverse symlink: {repo_locator(component, target)}")
            except ValueError:
                missing_inputs.append("not_applicable path must not traverse symlink")
    if destination.exists() and not destination.is_file():
        missing_inputs.append(f"not_applicable spec target is not a regular file: {locator}")
    created_locators: list[str] = []
    exists = destination.exists()
    if apply and not exists and not missing_inputs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            pr_intent_not_applicable_spec_content(
                item=item,
                profile_id=profile_id,
                profile=profile,
                rationale=rationale,
                consumer_boundary=consumer_boundary,
                recheck_condition=recheck_condition,
                scope_proof=scope_proof,
            ),
            encoding="utf-8",
        )
        created_locators.append(locator)
    payload = {
        "suite_path": "not_applicable",
        "planned_writes": [
            {
                "artifact": "spec.md",
                "locator": locator,
                "status": "exists" if exists else ("created" if created_locators else "would_create"),
                "planned_action": "preserve_existing" if exists else "create",
                "would_write": not exists,
                "wrote": bool(created_locators),
                "overwrite_policy": "preserve_existing",
                "requirement": "suite_not_applicable_decision",
            }
        ],
        "overwrite_policy": {
            "mode": "preserve_existing",
            "allows_overwrite": False,
            "existing_files": [locator] if exists else [],
        },
        "created_locators": created_locators,
        "missing_inputs": missing_inputs,
        "not_applicable": {
            "rationale": rationale,
            "consumer_boundary": consumer_boundary,
            "recheck_condition": recheck_condition,
            "scope_proof": scope_proof,
            "review_requirement": profile["review_requirement"],
        },
    }
    return payload, "invalid_not_applicable_target" if missing_inputs else None


def pr_intent_changed_paths(
    *,
    target: Path,
    explicit_paths: list[str],
    base: str | None,
    head_sha: str | None,
) -> tuple[list[str], list[str], str]:
    paths = sorted({normalized for path in explicit_paths if (normalized := normalize_changed_path(path))})
    if paths:
        return paths, [], "explicit"
    local_paths, errors = ship_local_changed_paths(target, target_branch=base, head_sha=head_sha)
    return local_paths, errors, "local_git_diff"


def pr_intent_scope_validation(profile: dict[str, Any], paths: list[str], path_errors: list[str]) -> dict[str, Any]:
    allowed_prefixes = tuple(profile.get("allowed_prefixes") or ())
    allowed_exact = tuple(profile.get("allowed_exact") or ())
    blocked_paths = [
        path
        for path in paths
        if not path_matches_any(path, prefixes=allowed_prefixes, exact=allowed_exact)
    ]
    result = "pass" if not path_errors and not blocked_paths else "block"
    return {
        "schema_version": "loom-pr-intent-scope-proof/v1",
        "result": result,
        "changed_paths": paths,
        "allowed_prefixes": list(allowed_prefixes),
        "allowed_exact": list(allowed_exact),
        "blocked_paths": blocked_paths,
        "missing_inputs": path_errors,
        "summary": (
            "Changed paths match the declared PR intent profile."
            if result == "pass"
            else "Changed paths are unreadable or outside the declared PR intent profile."
        ),
    }


def pr_intent_metadata_flow_args(
    *,
    operation: str,
    target: Path,
    profile: dict[str, Any],
    item: str,
    issue: str | None,
    branch: str | None,
    head_sha: str | None,
    body_file: str | None = None,
    output_file: str | None = None,
    base_body_file: str | None = None,
    rationale: str | None = None,
    consumer_boundary: str | None = None,
    recheck_condition: str | None = None,
    scope_proof: str | None = None,
    pr: str | None = None,
) -> list[str]:
    args = ["pr-metadata", operation, "--target", str(target), "--surface", str(profile["surface"]), "--item", item]
    if issue:
        args.extend(["--issue", issue])
    if branch:
        args.extend(["--branch", branch])
    if head_sha:
        args.extend(["--head-sha", head_sha])
    if pr:
        args.extend(["--pr", pr])
    if body_file:
        args.extend(["--body-file", body_file])
    if output_file:
        args.extend(["--output-file", output_file])
    if base_body_file:
        args.extend(["--base-body-file", base_body_file])
    if operation in {"render", "update"}:
        args.extend(["--governance-intensity", str(profile["governance_intensity"])])
        args.extend(["--change-class", str(profile["change_class"])])
        args.extend(["--suite-path", str(profile["suite_path"])])
        args.extend(["--review-requirement", str(profile["review_requirement"])])
        args.extend(["--release-judgment", str(profile["release_judgment"])])
        for trigger in profile.get("upgrade_triggers") or ():
            args.extend(["--upgrade-trigger", str(trigger)])
        if profile["suite_path"] == "not_applicable":
            args.extend(["--suite-na-rationale", rationale or ""])
            args.extend(["--suite-na-consumer-boundary", consumer_boundary or ""])
            args.extend(["--suite-na-recheck-condition", recheck_condition or ""])
            args.extend(["--suite-na-scope-proof", scope_proof or ""])
            args.extend(["--suite-na-review-requirement", str(profile["review_requirement"])])
    return args


def pr_intent_governance_fields(metadata_payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(metadata_payload, dict):
        return {}
    carrier = metadata_payload.get("governance_intensity_carrier")
    envelope = carrier.get("envelope") if isinstance(carrier, dict) else None
    fields = envelope.get("fields") if isinstance(envelope, dict) else None
    return fields if isinstance(fields, dict) else {}


def pr_intent_consistency_validation(
    *,
    target: Path,
    profile_id: str,
    profile: dict[str, Any],
    item: str,
    issue: str | None,
    branch: str | None,
    head_sha: str | None,
    metadata_payload: dict[str, Any] | None,
    suite_result: str,
) -> dict[str, Any]:
    fields = pr_intent_governance_fields(metadata_payload)
    missing: list[str] = []
    parsed_item = parse_typed_locator(item, allowed_types={"work_item"})
    repo_slug = infer_github_repo(target)
    if isinstance(issue, str) and issue.isdigit() and repo_slug:
        owner, repo = repo_slug.split("/", 1)
        expected_work_item_locator = typed_locator(owner, repo, "work_item", int(issue))
    elif parsed_item and not parsed_item["legacy"]:
        expected_work_item_locator = str(parsed_item["locator"])
    elif parsed_item and repo_slug:
        owner, repo = repo_slug.split("/", 1)
        expected_work_item_locator = typed_locator(owner, repo, "work_item", int(parsed_item["id"]))
    else:
        expected_work_item_locator = item
    expected = {
        "work_item_locator": expected_work_item_locator,
        "change_class": profile["change_class"],
        "suite_path": profile["suite_path"],
        "review_requirement": profile["review_requirement"],
        "release_judgment": profile["release_judgment"],
    }
    for key, value in expected.items():
        if fields.get(key) != value:
            missing.append(f"metadata.{key}")
    if profile["suite_path"] == "not_applicable":
        if suite_result != "not_applicable":
            missing.append("suite.not_applicable")
        suite_na = fields.get("suite_not_applicable")
        if not isinstance(suite_na, dict):
            missing.append("metadata.suite_not_applicable")
        else:
            for key in ("rationale", "consumer_boundary", "recheck_condition", "scope_proof", "review_requirement"):
                if not isinstance(suite_na.get(key), str) or not suite_na.get(key).strip():
                    missing.append(f"metadata.suite_not_applicable.{key}")
    elif suite_result not in {"pass"}:
        missing.append("suite.path_ready")
    return {
        "schema_version": "loom-pr-intent-carrier-set-consistency/v1",
        "result": "pass" if not missing else "block",
        "intent": profile_id,
        "expected": expected,
        "metadata_fields": fields,
        "suite_result": suite_result,
        "missing_inputs": missing,
        "summary": (
            "Metadata, suite path, typed Work Item binding, and profile intent agree."
            if not missing
            else "Metadata, suite path, typed Work Item binding, or profile intent drifted across carriers."
        ),
    }


def pr_intent_suite_prepare(
    *,
    target: Path,
    item: str,
    profile_id: str,
    profile: dict[str, Any],
    rationale: str,
    consumer_boundary: str,
    recheck_condition: str,
    scope_proof: str,
    apply: bool,
) -> tuple[dict[str, Any], str | None]:
    if profile["suite_path"] == "not_applicable":
        return pr_intent_not_applicable_write(
            target=target,
            item=item,
            profile_id=profile_id,
            profile=profile,
            rationale=rationale,
            consumer_boundary=consumer_boundary,
            recheck_condition=recheck_condition,
            scope_proof=scope_proof,
            apply=apply,
        )
    summary, payload, failure = suite_scaffold_payload(target, item, str(profile["suite_path"]), apply=apply)
    return {**payload, "summary": summary}, failure


def pr_intent_prepare_payload(
    *,
    command_name: str,
    target: Path,
    profile_id: str,
    profile: dict[str, Any],
    item: str | None,
    issue: str | None,
    branch: str | None,
    head_sha: str | None,
    output_file: str | None,
    base_body_file: str,
    rationale: str | None,
    consumer_boundary: str | None,
    recheck_condition: str | None,
    scope_proof: str | None,
    apply: bool,
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    if not item:
        missing_inputs.append("missing --item")
    if item and suite_item_segment_error(item):
        missing_inputs.append(str(suite_item_segment_error(item)))
    current_branch = pr_intent_current_branch(target, branch)
    current_head = pr_intent_current_head(target, head_sha)
    if not current_branch:
        missing_inputs.append("branch is unavailable; pass --branch <work/...>")
    if not current_head:
        missing_inputs.append("head_sha is unavailable; pass --head-sha <40-hex>")
    if not target.exists():
        missing_inputs.append("target path does not exist")

    effective_item = item or "<item>"
    profile, suite_path_resolution = pr_intent_effective_profile(
        target=target,
        item=item,
        profile_id=profile_id,
        profile=profile,
    )
    effective_output = output_file or f".loom/runtime/pr/{effective_item}-{profile_id}-body.md"
    paths, path_errors, path_source = pr_intent_changed_paths(target=target, explicit_paths=[], base="main", head_sha=current_head)
    effective_scope_proof = pr_intent_scope_proof(profile_id, paths, scope_proof)
    effective_rationale = pr_intent_na_value(profile, "rationale", rationale)
    effective_consumer = pr_intent_na_value(profile, "consumer_boundary", consumer_boundary)
    effective_recheck = pr_intent_na_value(profile, "recheck_condition", recheck_condition)

    suite_prepare: dict[str, Any] = {"planned_writes": [], "created_locators": [], "missing_inputs": []}
    suite_failure: str | None = None
    metadata_prepare: dict[str, Any] = {
        "operation": "render",
        "output_file": effective_output,
        "apply": apply,
        "planned_command": "loom pr metadata-render --surface "
        + str(profile["surface"])
        + " --item "
        + effective_item
        + " --output-file "
        + effective_output
        + " --json",
    }
    if not missing_inputs and item:
        suite_prepare, suite_failure = pr_intent_suite_prepare(
            target=target,
            item=item,
            profile_id=profile_id,
            profile=profile,
            rationale=effective_rationale,
            consumer_boundary=effective_consumer,
            recheck_condition=effective_recheck,
            scope_proof=effective_scope_proof,
            apply=apply,
        )
        missing_inputs.extend(str(entry) for entry in suite_prepare.get("missing_inputs", []))
        if apply:
            metadata_args = pr_intent_metadata_flow_args(
                operation="render",
                target=target,
                profile=profile,
                item=item,
                issue=issue,
                branch=current_branch,
                head_sha=current_head,
                output_file=effective_output,
                base_body_file=base_body_file,
                rationale=effective_rationale,
                consumer_boundary=effective_consumer,
                recheck_condition=effective_recheck,
                scope_proof=effective_scope_proof,
            )
            metadata_prepare = flow_payload(
                command_name,
                metadata_args,
                fallback_to=["loom pr metadata-render --surface <surface> --item <id> --json"],
            )
            if metadata_prepare.get("result") != "pass":
                missing_inputs.extend(str(entry) for entry in metadata_prepare.get("missing_inputs", []))
    metadata_preflight: dict[str, Any] | None = None
    if apply and not missing_inputs and item and metadata_prepare.get("result") == "pass":
        preflight_args = pr_intent_metadata_flow_args(
            operation="preflight",
            target=target,
            profile=profile,
            item=item,
            issue=issue,
            branch=current_branch,
            head_sha=current_head,
            body_file=effective_output,
        )
        metadata_preflight = flow_payload(
            command_name,
            preflight_args,
            fallback_to=["loom pr metadata-preflight --surface <surface> --body-file <rendered-pr-body.md> --json"],
        )
        if metadata_preflight.get("result") != "pass":
            missing_inputs.extend(str(entry) for entry in metadata_preflight.get("missing_inputs", []))
    result = "pass" if not missing_inputs and suite_failure is None else "block"
    check_command = (
        f"loom pr-intent check --intent {profile_id} --target {target} --item {effective_item} "
        f"--branch {current_branch or '<branch>'} --head-sha {current_head or '<head-sha>'} "
        f"--body-file {effective_output} --json"
    )
    readiness_reasons = readiness_reasons_from_text(missing_inputs)
    return output(
        command_name,
        result,
        schema=PR_INTENT_PREPARE_SCHEMA,
        target=str(target),
        item_id=item,
        intent=profile_id,
        mutates=apply,
        summary=(
            "PR intent prepare produced or planned the profile carrier set."
            if result == "pass"
            else "PR intent prepare found missing or invalid carrier inputs."
        ),
        profile={
            "schema_version": PR_INTENT_PROFILE_SCHEMA,
            "intent": profile_id,
            "surface": profile["surface"],
            "suite_path": profile["suite_path"],
            "change_class": profile["change_class"],
            "release_judgment": profile["release_judgment"],
        },
        path_source=path_source,
        path_read_warnings=path_errors,
        suite_path_resolution=suite_path_resolution,
        suite_prepare=suite_prepare,
        metadata_prepare=metadata_prepare,
        metadata_preflight=metadata_preflight,
        readiness=readiness_payload(
            ready=False,
            reasons=readiness_reasons or ([] if result == "pass" else ["carrier_set_incomplete"]),
            next_command=check_command if result == "pass" else f"loom pr-intent prepare --intent {profile_id} --target {target} --item <id> --apply --json",
            summary=(
                "Carrier files passed local preflight; update/read back the PR body before hosted gate."
                if result == "pass"
                else "Prepare stopped before the carrier set was ready for PR metadata readback."
            ),
        ),
        missing_inputs=dedupe_strings(missing_inputs),
        fallback_to=[f"loom {command_name} --intent {profile_id} --item <id> --apply --json"] if result == "block" else None,
        consumed_contracts=list(PR_INTENT_SHARED_CONTRACTS),
    )


def pr_intent_check_payload(
    *,
    command_name: str,
    target: Path,
    profile_id: str,
    profile: dict[str, Any],
    item: str | None,
    issue: str | None,
    branch: str | None,
    head_sha: str | None,
    body_file: str | None,
    pr: str | None,
    changed_paths: list[str],
    base: str | None,
) -> dict[str, Any]:
    blocking_gaps: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    if not item:
        missing_inputs.append("missing --item")
    if item and suite_item_segment_error(item):
        missing_inputs.append(str(suite_item_segment_error(item)))
    current_branch = pr_intent_current_branch(target, branch)
    current_head = pr_intent_current_head(target, head_sha)
    if not current_branch:
        missing_inputs.append("branch is unavailable; pass --branch <work/...>")
    if not current_head:
        missing_inputs.append("head_sha is unavailable; pass --head-sha <40-hex>")
    if not body_file and not pr:
        missing_inputs.append("metadata check requires --body-file or PR number")
    profile, suite_path_resolution = pr_intent_effective_profile(
        target=target,
        item=item,
        profile_id=profile_id,
        profile=profile,
    )

    suite_validation: dict[str, Any] = {"result": "block", "missing_inputs": ["missing --item"]}
    evidence_validation: dict[str, Any] = {"result": "not_applicable", "summary": "Suite evidence validation is not applicable for this intent profile."}
    carrier_validation: dict[str, Any] = {"result": "not_applicable", "summary": "Suite carrier validation is not applicable for this intent profile."}
    metadata_validation: dict[str, Any] | None = None

    if item and not suite_item_segment_error(item):
        suite_summary, suite_result, suite_payload, suite_failed_layer, suite_fail_reason, suite_fallback = suite_validate_payload(target, item)
        suite_validation = {
            "command": "suite validate",
            "result": suite_result,
            "summary": suite_summary,
            "failed_layer": suite_failed_layer,
            "fail_closed_reason": suite_fail_reason,
            "fallback_to": suite_fallback,
            "payload": suite_payload,
        }
        if profile["suite_path"] == "not_applicable":
            if suite_result != "not_applicable":
                missing_inputs.append("suite path is not the profile-required not_applicable decision")
        elif suite_result != "pass":
            missing_inputs.extend(str(entry) for entry in suite_payload.get("missing_inputs", []))
        else:
            evidence_summary, evidence_result, evidence_payload, evidence_failed_layer, evidence_fail_reason, evidence_fallback = suite_evidence_validate_payload(target, item)
            evidence_validation = {
                "command": "suite evidence validate",
                "result": evidence_result,
                "summary": evidence_summary,
                "failed_layer": evidence_failed_layer,
                "fail_closed_reason": evidence_fail_reason,
                "fallback_to": evidence_fallback,
                "payload": evidence_payload,
            }
            carrier_summary, carrier_result, carrier_payload, carrier_failed_layer, carrier_fail_reason, carrier_fallback = suite_carrier_validate_payload(target, item)
            carrier_validation = {
                "command": "suite carrier validate",
                "result": carrier_result,
                "summary": carrier_summary,
                "failed_layer": carrier_failed_layer,
                "fail_closed_reason": carrier_fail_reason,
                "fallback_to": carrier_fallback,
                "payload": carrier_payload,
            }
            if evidence_result != "pass":
                missing_inputs.extend(str(entry) for entry in evidence_payload.get("missing_inputs", []))
            if carrier_result != "pass":
                missing_inputs.extend(str(entry) for entry in carrier_payload.get("missing_inputs", []))

    if item and (body_file or pr):
        metadata_args = pr_intent_metadata_flow_args(
            operation="preflight",
            target=target,
            profile=profile,
            item=item,
            issue=issue,
            branch=current_branch,
            head_sha=current_head,
            body_file=body_file,
            pr=pr,
        )
        metadata_validation = flow_payload(
            command_name,
            metadata_args,
            fallback_to=["loom pr metadata-preflight --surface <surface> --body-file <rendered-pr-body.md> --json"],
        )
        if metadata_validation.get("result") != "pass":
            missing_inputs.extend(str(entry) for entry in metadata_validation.get("missing_inputs", []))

    paths, path_errors, path_source = pr_intent_changed_paths(
        target=target,
        explicit_paths=changed_paths,
        base=base,
        head_sha=current_head,
    )
    scope_validation = pr_intent_scope_validation(profile, paths, path_errors)
    if scope_validation["result"] != "pass":
        missing_inputs.extend(str(entry) for entry in scope_validation.get("missing_inputs", []))
        missing_inputs.extend(f"scope path outside intent: {path}" for path in scope_validation.get("blocked_paths", []))

    consistency_validation = pr_intent_consistency_validation(
        target=target,
        profile_id=profile_id,
        profile=profile,
        item=item or "",
        issue=issue,
        branch=current_branch,
        head_sha=current_head,
        metadata_payload=metadata_validation,
        suite_result=str(suite_validation.get("result")),
    )
    if consistency_validation["result"] != "pass":
        missing_inputs.extend(str(entry) for entry in consistency_validation.get("missing_inputs", []))

    for key, validation in (
        ("suite", suite_validation),
        ("evidence", evidence_validation),
        ("carrier", carrier_validation),
        ("metadata", metadata_validation or {}),
        ("scope", scope_validation),
        ("consistency", consistency_validation),
    ):
        if isinstance(validation, dict) and validation.get("result") == "block":
            blocking_gaps.append(
                {
                    "surface": key,
                    "summary": validation.get("summary"),
                    "missing_inputs": validation.get("missing_inputs", []),
                    "fallback_to": validation.get("fallback_to"),
                }
            )

    missing_inputs = dedupe_strings(missing_inputs)
    result = "pass" if not missing_inputs and not blocking_gaps else "block"
    ready_for_hosted_gate = result == "pass" and bool(pr)
    readiness_reasons = readiness_reasons_from_text(missing_inputs)
    if result == "pass" and not pr:
        readiness_reasons = ["pr_metadata_stale"]
    next_command = (
        f"loom pr gate {pr} --target {target} --surface {profile['surface']} --work-item {item or '<item>'} --json"
        if ready_for_hosted_gate
        else f"loom pr metadata-update <pr> --target {target} --surface {profile['surface']} --item {item or '<item>'} --branch {current_branch or '<branch>'} --apply --json"
    )
    return output(
        command_name,
        result,
        schema=PR_INTENT_CHECK_SCHEMA,
        target=str(target),
        item_id=item,
        intent=profile_id,
        mutates=False,
        summary=(
            "PR intent check passed across suite, metadata, scope, branch binding, and carrier consistency."
            if result == "pass"
            else "PR intent check found missing, stale, partial, or cross-surface drift."
        ),
        profile={
            "schema_version": PR_INTENT_PROFILE_SCHEMA,
            "intent": profile_id,
            "surface": profile["surface"],
            "suite_path": profile["suite_path"],
            "change_class": profile["change_class"],
            "release_judgment": profile["release_judgment"],
        },
        validations={
            "suite": suite_validation,
            "evidence": evidence_validation,
            "carrier": carrier_validation,
            "metadata": metadata_validation,
            "scope": scope_validation,
            "consistency": consistency_validation,
        },
        suite_path_resolution=suite_path_resolution,
        readiness=readiness_payload(
            ready=ready_for_hosted_gate,
            reasons=readiness_reasons,
            next_command=next_command,
        ),
        changed_paths={"source": path_source, "paths": paths},
        missing_inputs=missing_inputs,
        blocking_gaps=blocking_gaps,
        fallback_to=[f"loom {command_name} --intent {profile_id} --item <id> --body-file <rendered-pr-body.md> --json"] if result == "block" else None,
        consumed_contracts=list(PR_INTENT_SHARED_CONTRACTS),
    )


def handle_pr_intent(argv: list[str], *, default_intent: str | None = None, command_root: str = "pr-intent") -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command_root}")
    parser.add_argument("action", choices=("prepare", "check"))
    if default_intent is None:
        parser.add_argument("--intent", required=True)
    else:
        parser.add_argument("--intent", default=default_intent)
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--branch")
    parser.add_argument("--head-sha")
    parser.add_argument("--body-file")
    parser.add_argument("--output-file")
    parser.add_argument("--base-body-file", default=".github/PULL_REQUEST_TEMPLATE.md")
    parser.add_argument("--base", default="main")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--rationale")
    parser.add_argument("--consumer-boundary")
    parser.add_argument("--recheck-condition")
    parser.add_argument("--scope-proof")
    parser.add_argument("--apply", action="store_true")
    add_legacy_carrier_compatibility_args(parser)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    profile_id, profile, profile_error = pr_intent_profile(args.intent)
    command_name = f"{command_root} {args.action}"
    target = resolve_target(args.target)
    if profile_error or profile is None or profile_id is None:
        return emit(
            output(
                command_name,
                "block",
                schema=PR_INTENT_CHECK_SCHEMA if args.action == "check" else PR_INTENT_PREPARE_SCHEMA,
                target=str(target),
                intent=args.intent,
                mutates=False,
                summary="Unsupported PR intent profile.",
                missing_inputs=[profile_error],
                fallback_to=["loom pr-intent prepare --intent docs-governance-only --item <id> --json"],
                supported_intents=sorted(PR_INTENT_PROFILES),
            )
        )
    if profile_id in PR_INTENT_PRESERVE_SUITE_PROFILES:
        compatibility = legacy_carrier_compatibility(args)
        if compatibility["result"] != "pass":
            return emit(
                agent_safe_payload(
                    output(
                        command_name,
                        "block",
                        schema_version="loom-legacy-carrier-command/v1",
                        summary=compatibility["summary"],
                        target=str(target),
                        intent=profile_id,
                        mutates=False,
                        compatibility=compatibility,
                        missing_inputs=compatibility["missing_inputs"],
                        fallback_to="use a normal implementation/release PR and host-only closeout",
                    )
                )
            )
    if not target.exists():
        return emit(block_target(command_name, target, "target path does not exist"))
    if args.action == "prepare":
        payload = pr_intent_prepare_payload(
            command_name=command_name,
            target=target,
            profile_id=profile_id,
            profile=profile,
            item=args.item,
            issue=args.issue,
            branch=args.branch,
            head_sha=args.head_sha,
            output_file=args.output_file,
            base_body_file=args.base_body_file,
            rationale=args.rationale,
            consumer_boundary=args.consumer_boundary,
            recheck_condition=args.recheck_condition,
            scope_proof=args.scope_proof,
            apply=args.apply,
        )
    else:
        payload = pr_intent_check_payload(
            command_name=command_name,
            target=target,
            profile_id=profile_id,
            profile=profile,
            item=args.item,
            issue=args.issue,
            branch=args.branch,
            head_sha=args.head_sha,
            body_file=args.body_file,
            pr=args.pr,
            changed_paths=args.changed_path,
            base=args.base,
        )
    return emit(payload)


def ship_validation_profile_for_paths(paths: list[str], closeout_policy: dict[str, Any]) -> tuple[str, list[str]]:
    if closeout_policy.get("policy") == "release_manifest" and (
        closeout_policy.get("release_judgment") == "release_required"
        or "release_source_change_requires_release_workflow" in closeout_policy.get("upgrade_reasons", [])
    ):
        return "release", ["release_manifest_requires_release_validation"]
    if not paths:
        return "standard", ["changed_paths_unavailable_default_standard"]

    release_exact = {"VERSION", "package.json", "package-lock.json", "npm-shrinkwrap.json"}
    release_prefixes = (".github/workflows/loom-cli-release", "docs/evidence/v",)
    full_prefixes = (
        ".github/workflows/",
        ".loom/bin/",
        "bin/",
        "examples/",
        "plugins/loom/",
        "skills/shared/scripts/",
        "src/skills/shared/scripts/",
        "test/",
        "tools/",
    )
    full_exact = {"Makefile"}
    light_prefixes = ("docs/", "skills/route-matrix.md", "src/skills/route-matrix.md", "plugins/loom/skills/route-matrix.md", "packages/loom-installer/")
    light_exact = {"README.md", "README.zh-CN.md", "VISION.md", "AGENTS.md", "LICENSE"}

    if any(path_matches_any(path, release_prefixes, release_exact) for path in paths):
        return "release", ["release_or_package_surface_changed"]
    if any(path_matches_any(path, full_prefixes, full_exact) for path in paths):
        return "full", ["runtime_or_harness_surface_changed"]
    if all(path_matches_any(path, light_prefixes, light_exact) or path.endswith(".md") for path in paths):
        return "light", ["docs_or_package_tombstone_only"]
    return "standard", ["mixed_or_unclassified_paths"]


def ship_validation_profile_payload(
    args: argparse.Namespace,
    changed_paths_payload: dict[str, Any],
    closeout_policy: dict[str, Any],
) -> dict[str, Any]:
    changed_paths = [
        normalized
        for value in changed_paths_payload.get("changed_paths", [])
        if (normalized := normalize_changed_path(value))
    ]
    requested = args.validation_profile
    if requested != "auto":
        selected = requested
        reasons = ["explicit_validation_profile_override"]
    else:
        selected, reasons = ship_validation_profile_for_paths(changed_paths, closeout_policy)
        if changed_paths_payload.get("result") != "pass":
            reasons = ["changed_paths_unavailable_default_standard"]
            selected = "standard"
    source_surface = SHIP_VALIDATION_SOURCE_SURFACES[selected]
    validation_commands = (
        []
        if source_surface is None
        else [f"python3 tools/loom_check.py --profile source --source-surface {source_surface} ."]
    )
    if selected == "release":
        validation_commands.extend([
            "python3 tools/check_release_surface.py",
            "python3 tools/check_npm_package.py",
        ])
    return {
        "schema_version": "loom-ship-validation-profile/v1",
        "result": "pass",
        "summary": f"ship selected `{selected}` validation profile from changed paths.",
        "requested_profile": requested,
        "selected_profile": selected,
        "source_surface": source_surface,
        "changed_paths": changed_paths,
        "changed_paths_source": changed_paths_payload.get("source"),
        "changed_paths_readback": changed_paths_payload,
        "selection_reasons": reasons,
        "validation_commands": validation_commands,
        "fallback_to": None,
    }


def first_ship_blocker(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    for step in steps:
        if step.get("result") not in {"pass", "skipped"}:
            return step
    return None


def payload_pr_string(payload: dict[str, Any], field: str) -> str | None:
    pr = payload.get("pr")
    if isinstance(pr, dict) and pr.get(field) is not None:
        return str(pr[field])
    return None


def ship_closeout_target_branch(args: argparse.Namespace, merge_payload: dict[str, Any], *, inferred_target_branch: str | None = None) -> str | None:
    return payload_pr_string(merge_payload, "baseRefName") or args.target_branch or inferred_target_branch


def ship_apply_admission_block(
    *,
    command: str,
    target: Path,
    args: argparse.Namespace,
    steps: list[dict[str, Any]],
    closeout_policy: dict[str, Any],
    validation_profile: dict[str, Any] | None = None,
    summary: str,
    missing_inputs: list[str],
    fallback_to: list[str],
) -> int:
    payload = output(
        command,
        "block",
        schema_version="loom-ship/v1",
        summary=summary,
        mutates=False,
        dry_run=False,
        apply=True,
        target=str(target),
        item={"id": args.item},
        issue={"number": args.issue},
        pr={"number": args.pr},
        intensity=args.intensity,
        effective_intensity=closeout_policy.get("governance_intensity"),
        validation_profile=validation_profile,
        merge_method=args.merge_method,
        closeout_policy=closeout_policy,
        steps=steps,
        first_blocker=steps[-1] if steps else None,
        missing_inputs=missing_inputs,
        fallback_to=fallback_to,
        next_action=fallback_to[0] if fallback_to else "resolve ship apply admission blocker",
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def git_branch_for_target(target: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--abbrev-ref", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    branch = completed.stdout.strip()
    return branch if branch and branch != "HEAD" else None


def ship_pr_payload(args: argparse.Namespace, target: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if args.pr_payload_file:
        payload_path = Path(args.pr_payload_file)
        if not payload_path.is_absolute():
            payload_path = target / payload_path
        try:
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, [f"PR payload file is unreadable: {exc}"]
        if not isinstance(payload, dict):
            return None, ["PR payload file must contain a JSON object"]
        return payload, []
    if args.pr is None:
        return None, []
    repo_slug = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else infer_github_repo(target)
    if not repo_slug:
        return None, ["unable to infer GitHub repository for PR readback; pass --owner and --repo"]
    completed = run_capture(
        [
            "gh",
            "api",
            f"repos/{repo_slug}/pulls/{args.pr}",
            "--jq",
            (
                "{number,state,body,url,"
                "headRefName:.head.ref,"
                "headRefOid:.head.sha,"
                "baseRefName:.base.ref}"
            ),
        ],
        cwd=target,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "gh api pull request readback failed"
        return None, [detail]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON from gh api pull request readback: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, ["gh api pull request readback did not return a JSON object"]
    return payload, []


def ship_payload_string(payload: dict[str, Any] | None, field: str) -> str | None:
    if isinstance(payload, dict) and payload.get(field) is not None:
        return str(payload[field])
    return None


def ship_binding_inference_payload(args: argparse.Namespace, target: Path) -> dict[str, Any]:
    needs_pr_payload = bool(args.pr_payload_file or not args.branch or not args.head_sha or (args.apply and not args.target_branch))
    pr_payload, pr_errors = ship_pr_payload(args, target) if needs_pr_payload else (None, [])
    pr_branch = ship_payload_string(pr_payload, "headRefName")
    pr_head = ship_payload_string(pr_payload, "headRefOid")
    pr_base = ship_payload_string(pr_payload, "baseRefName")
    git_branch = git_branch_for_target(target)
    git_head = git_head_sha_for_target(target)

    effective_branch = args.branch or pr_branch or git_branch
    effective_head = args.head_sha or pr_head or git_head
    effective_target_branch = args.target_branch or pr_base
    missing_inputs: list[str] = []
    conflicts: list[str] = []
    inferences: list[dict[str, str]] = []

    if pr_errors and (not args.branch or not args.head_sha or (args.apply and not args.target_branch)):
        missing_inputs.extend(f"pr readback: {message}" for message in pr_errors)
    if not effective_branch:
        missing_inputs.append("branch")
    if not effective_head:
        missing_inputs.append("head_sha")
    if args.apply and not effective_target_branch:
        missing_inputs.append("target_branch")

    if args.branch and pr_branch and args.branch != pr_branch:
        conflicts.append(f"branch `{args.branch}` does not match PR headRefName `{pr_branch}`")
    if args.head_sha and pr_head and args.head_sha != pr_head:
        conflicts.append("head_sha does not match PR headRefOid")
    if args.target_branch and pr_base and args.target_branch != pr_base:
        conflicts.append(f"target_branch `{args.target_branch}` does not match PR baseRefName `{pr_base}`")
    missing_inputs.extend(conflicts)

    if not args.branch and effective_branch:
        source = "pr_readback" if pr_branch == effective_branch else "current_checkout"
        inferences.append({"field": "branch", "source": source, "value": effective_branch})
    if not args.head_sha and effective_head:
        source = "pr_readback" if pr_head == effective_head else "current_checkout"
        inferences.append({"field": "head_sha", "source": source, "value": effective_head})
    if not args.target_branch and effective_target_branch:
        inferences.append({"field": "target_branch", "source": "pr_readback", "value": effective_target_branch})

    result = "pass" if not missing_inputs else "block"
    return {
        "command": "ship",
        "operation": "binding-inference",
        "schema_version": "loom-ship-binding-inference/v1",
        "result": result,
        "summary": (
            "ship inferred branch, observed PR head, and target branch bindings from explicit inputs, PR readback, and checkout state."
            if result == "pass"
            else "ship could not safely infer branch, observed PR head, or target branch bindings."
        ),
        "missing_inputs": missing_inputs,
        "fallback_to": None if result == "pass" else "fix PR readback or rerun loom ship with explicit stable bindings",
        "inputs": {
            "branch": args.branch,
            "head_sha": args.head_sha,
            "target_branch": args.target_branch,
            "pr": args.pr,
            "pr_payload_file": args.pr_payload_file,
        },
        "bindings": {
            "branch": effective_branch,
            "head_sha": effective_head,
            "target_branch": effective_target_branch,
        },
        "sources": {
            "git_branch": git_branch,
            "git_head_sha": git_head,
            "pr_headRefName": pr_branch,
            "pr_headRefOid": pr_head,
            "pr_baseRefName": pr_base,
        },
        "inferences": inferences,
        "conflicts": conflicts,
    }


def ship_metadata_update_args(args: argparse.Namespace, target: Path, *, branch: str | None, head_sha: str | None) -> list[str] | None:
    if args.issue is None or not branch:
        return None
    flow_args = [
        "pr-metadata",
        "update",
        "--target",
        str(target),
        "--surface",
        "merge_ready",
        "--pr",
        str(args.pr),
        "--item",
        args.item,
        "--issue",
        str(args.issue),
        "--branch",
        branch,
        "--apply",
    ]
    if args.head_sha:
        flow_args.extend(["--head-sha", args.head_sha])
    if args.intensity != "auto":
        flow_args.extend(["--governance-intensity", args.intensity])
    return flow_args


def ship_closeout_namespace(args: argparse.Namespace, *, branch: str) -> argparse.Namespace:
    return argparse.Namespace(
        item=args.item,
        issue=args.issue,
        pr=str(args.pr),
        pr_role=args.pr_role,
        implementation_pr=args.implementation_pr,
        release_pr=args.release_pr,
        carrier_sync_pr=args.carrier_sync_pr,
        final_closeout_pr=args.final_closeout_pr,
        project=args.project,
        phase=args.phase,
        fr=args.fr,
        branch=branch,
        owner=args.owner,
        repo_name=args.repo_name,
        comment=args.comment,
        comment_file=args.comment_file,
        goal_completion=args.goal_completion,
        gate_profile=args.gate_profile,
        issue_payload_file=args.issue_payload_file,
        pr_payload_file=args.pr_payload_file,
        project_payload_file=args.project_payload_file,
        status_checks_file=args.status_checks_file,
        branch_protection_file=args.branch_protection_file,
        ruleset_file=args.ruleset_file,
        skip_gate=args.skip_gate,
    )


def ship_git_read(target: Path, args: list[str]) -> tuple[str | None, str | None]:
    completed = run_capture(["git", "-C", str(target), *args], cwd=target)
    if completed.returncode == 0:
        return completed.stdout.strip(), None
    return None, completed.stderr.strip() or completed.stdout.strip() or f"git {' '.join(args)} failed"


def ship_json_read(completed: subprocess.CompletedProcess[str], *, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        decoded = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} returned invalid JSON: {exc.msg}")
        return None
    if not isinstance(decoded, dict):
        errors.append(f"{label} returned non-object JSON")
        return None
    return decoded


def ship_missing_readback(detail: str) -> bool:
    lowered = detail.lower()
    return any(marker in lowered for marker in ("404", "not found", "no match found", "e404"))


def ship_status_surface(target: Path) -> dict[str, Any]:
    path = target / ".loom" / "status" / "current.md"
    if not path.exists():
        return {"path": ".loom/status/current.md", "state": "missing", "current_checkpoint": None, "current_stop": None}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"- (Current Checkpoint|Current Stop|Next Step|Blockers):\s*(.*)", line)
        if match:
            values[match.group(1)] = match.group(2).strip()
    checkpoint = values.get("Current Checkpoint")
    current_stop = values.get("Current Stop")
    terminal = bool(
        (checkpoint and checkpoint.lower() in {"complete", "completed", "terminal", "closed", "done"})
        or (current_stop and any(word in current_stop.lower() for word in ("complete", "terminal", "closed")))
        or values.get("Next Step", "").lower().startswith("none")
    )
    return {
        "path": ".loom/status/current.md",
        "state": "terminal" if terminal else "active",
        "current_checkpoint": checkpoint,
        "current_stop": current_stop,
        "next_step": values.get("Next Step"),
        "blockers": values.get("Blockers"),
    }


def ship_host_issue_status(target: Path, *, repo: str | None, issue: int | None, milestone: str | None) -> dict[str, Any]:
    repo_slug = repo or infer_github_repo(target)
    payload: dict[str, Any] = {"repo": repo_slug, "issue": None, "milestone": None, "errors": []}
    if not repo_slug:
        payload["errors"].append("unable to infer GitHub repository")
        return payload
    if issue is not None:
        completed = run_capture(["gh", "api", f"repos/{repo_slug}/issues/{issue}", "--jq", "{number,state,closed_at,title}"], cwd=target)
        if completed.returncode == 0:
            payload["issue"] = ship_json_read(completed, label=f"GitHub issue #{issue}", errors=payload["errors"])
        else:
            payload["errors"].append(completed.stderr.strip() or completed.stdout.strip())
    if milestone:
        completed = run_capture(["gh", "api", f"repos/{repo_slug}/milestones/{milestone}", "--jq", "{number,title,state,open_issues,closed_issues}"], cwd=target)
        if completed.returncode == 0:
            payload["milestone"] = ship_json_read(completed, label=f"GitHub milestone {milestone}", errors=payload["errors"])
        else:
            payload["errors"].append(completed.stderr.strip() or completed.stdout.strip())
    return payload


def ship_release_presence(target: Path, *, repo: str | None, version: str | None, package_name: str | None) -> dict[str, Any]:
    context = release_package_context(target, version=version, package_name=package_name)
    tag = context["tag"]
    npm_version = context["npm_version"]
    package = context["npm_package"]
    repo_slug = repo or infer_github_repo(target)
    tag_sha, _tag_error = ship_git_read(target, ["rev-list", "-n", "1", tag])
    release: dict[str, Any] = {"exists": False}
    npm_package = {"exists": False}
    errors: list[str] = []
    if repo_slug:
        completed = run_capture(["gh", "api", f"repos/{repo_slug}/releases/tags/{tag}", "--jq", "{tag_name,name,draft,prerelease,published_at,html_url}"], cwd=target)
        if completed.returncode == 0:
            decoded = ship_json_read(completed, label=f"GitHub release {tag}", errors=errors)
            if decoded is not None:
                release = {"exists": True, **decoded}
        else:
            detail = completed.stderr.strip() or completed.stdout.strip()
            if detail and not ship_missing_readback(detail):
                errors.append(detail)
    if package:
        completed = run_capture(["npm", "view", f"{package}@{npm_version}", "version", "dist-tags", "--json"], cwd=target)
        if completed.returncode == 0:
            decoded = ship_json_read(completed, label=f"npm package {package}@{npm_version}", errors=errors)
            if decoded is not None:
                npm_package = {"exists": True, "readback": decoded}
        else:
            detail = completed.stderr.strip() or completed.stdout.strip()
            if detail and not ship_missing_readback(detail):
                errors.append(detail)
    return {
        "version": context["version"],
        "tag": {"name": tag, "exists": bool(tag_sha), "commit": tag_sha},
        "github_release": release,
        "npm": {"package": package, "version": npm_version, **npm_package},
        "errors": errors,
    }


def ship_checkout_status(target: Path) -> dict[str, Any]:
    branch = git_branch_for_target(target)
    head = git_head_sha_for_target(target)
    origin_main, origin_error = ship_git_read(target, ["rev-parse", "origin/main"])
    dirty, dirty_error = ship_git_read(target, ["status", "--short"])
    stale = False
    ancestry_error = None
    if head and origin_main and head != origin_main:
        completed = run_capture(["git", "-C", str(target), "merge-base", "--is-ancestor", head, origin_main], cwd=target)
        stale = completed.returncode == 0
        if completed.returncode not in (0, 1):
            ancestry_error = completed.stderr.strip() or completed.stdout.strip() or "git merge-base --is-ancestor failed"
    return {
        "branch": branch,
        "head_sha": head,
        "origin_main": origin_main,
        "stale_against_origin_main": stale,
        "dirty": bool(dirty),
        "dirty_paths": dirty.splitlines() if dirty else [],
        "errors": [error for error in [origin_error, dirty_error, ancestry_error] if error],
    }


def ship_status_diagnostic(
    *,
    host: dict[str, Any],
    release: dict[str, Any],
    checkout: dict[str, Any],
    carrier: dict[str, Any],
    adoption_mode: str | None = None,
) -> tuple[str, list[str], list[str], str]:
    blockers: list[str] = []
    fixed: list[str] = []
    if checkout.get("stale_against_origin_main"):
        blockers.append("checkout_stale_against_origin_main")
    if checkout.get("dirty"):
        blockers.append("checkout_has_uncommitted_changes")
    issue = host.get("issue") if isinstance(host.get("issue"), dict) else None
    if issue and issue.get("state") == "closed" and carrier.get("state") == "active":
        fixed.append("legacy_repo_carrier_ignored")
    if release.get("tag", {}).get("exists") or release.get("github_release", {}).get("exists") or release.get("npm", {}).get("exists"):
        blockers.append("target_release_already_exists")
    if host.get("errors") or release.get("errors") or checkout.get("errors"):
        blockers.append("readback_errors")
    if not blockers:
        next_action = (
            "run loom workstation current --target <repo> --clear --apply --json"
            if "repair_global_current_pointer" in fixed
            else "run loom ship --dry-run or loom ship --apply after PR bindings are ready"
        )
        return "pass", blockers, fixed, next_action
    if "checkout_stale_against_origin_main" in blockers:
        fixed.append("fast-forward or recreate the issue worktree from origin/main")
    if "checkout_has_uncommitted_changes" in blockers:
        fixed.append("commit, stash, or discard local changes before shipping")
    if "repair_global_current_pointer" in fixed:
        fixed.append("run loom workstation current --target <repo> --clear --apply --json")
    if "target_release_already_exists" in blockers:
        fixed.append("read back the existing release/tag/npm package before publishing")
    return "block", blockers, fixed, fixed[0] if fixed else "resolve ship preflight blockers"


def handle_ship_status(argv: list[str], *, mode: str) -> int:
    parser = argparse.ArgumentParser(prog=f"loom ship {mode}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--fr", type=int)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--branch")
    parser.add_argument("--milestone")
    parser.add_argument("--version")
    parser.add_argument("--package")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    lifecycle_admission = host_lifecycle_admission_payload(
        target=target,
        issue=args.issue,
        fr=args.fr,
        owner=args.owner,
        repo_name=args.repo_name,
        intent="ship",
        pr=args.pr,
        branch=args.branch,
    )
    if lifecycle_admission["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    f"ship {mode}",
                    "block",
                    schema_version="loom-ship-status/v1",
                    summary="ship preflight stopped before carrier diagnostics because the host-native lifecycle admission is blocked.",
                    mutates=False,
                    target=str(target),
                    issue={"number": args.issue},
                    fr={"number": args.fr},
                    missing_inputs=lifecycle_admission.get("missing_inputs") or lifecycle_admission.get("admission", {}).get("missing_inputs", []),
                    fallback_to=[lifecycle_admission.get("primary_remediation")],
                    lifecycle_admission=lifecycle_admission,
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )
    repo_slug = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else None
    host = ship_host_issue_status(target, repo=repo_slug, issue=args.issue, milestone=args.milestone)
    release = ship_release_presence(target, repo=repo_slug, version=args.version, package_name=args.package)
    checkout = ship_checkout_status(target)
    carrier = ship_status_surface(target)
    adoption_mode = target_adoption_mode(target)
    workstation_current = read_workstation_current(target)
    result, blockers, fixed, next_action = ship_status_diagnostic(
        host=host,
        release=release,
        checkout=checkout,
        carrier=carrier,
        adoption_mode=adoption_mode,
    )
    payload = output(
        f"ship {mode}",
        result,
        schema_version="loom-ship-status/v1",
        summary="ship preflight found no blocking checkout, release, host, or carrier status drift." if result == "pass" else "ship preflight found blocking status drift before delivery.",
        mutates=False,
        target=str(target),
        item={"id": args.item},
        issue={"number": args.issue},
        fr={"number": args.fr},
        milestone={"number": args.milestone},
        adoption_mode=adoption_mode,
        diagnostic={"blocked": result == "block", "blockers": blockers, "fixed": fixed, "next_action": next_action},
        missing_inputs=blockers,
        fallback_to=fixed or None,
        host=host,
        release=release,
        checkout=checkout,
        carrier=carrier,
        workstation_current=workstation_current,
        lifecycle_admission=lifecycle_admission,
        next_action=next_action,
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def ship_host_attestation(args: argparse.Namespace, target: Path, *, closeout: bool) -> dict[str, Any]:
    repo_slug = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else infer_github_repo(target)
    pr_number = closeout_current_pr_input(args) or getattr(args, "pr", None)
    missing: list[str] = []
    if not isinstance(repo_slug, str) or repo_slug.count("/") != 1:
        missing.append("target origin GitHub owner/repo")
    if args.issue is None:
        missing.append("--issue Work Item number")
    if not isinstance(pr_number, int):
        missing.append("--pr number")
    artifact_input = getattr(args, "attestation_artifact_input", None)
    if artifact_input is None:
        missing.append("--attestation-artifact-input locator")
    if missing:
        return {
            "command": "attestation closeout" if closeout else "attestation readback",
            "result": "block",
            "summary": "Host attestation inputs are incomplete; repository review carriers are not a fallback.",
            "missing_inputs": missing,
            "fallback_to": "provide the GitHub host artifact locator and retry the same host attestation readback",
        }
    assert isinstance(repo_slug, str) and args.issue is not None and isinstance(pr_number, int) and artifact_input is not None
    try:
        artifact_id = host_attestation_artifact_id(artifact_input)
    except ValueError as exc:
        return {
            "command": "attestation closeout" if closeout else "attestation readback",
            "result": "block",
            "summary": str(exc),
            "missing_inputs": [str(exc)],
            "fallback_to": "replace the locator with JSON containing only a positive GitHub artifact_id",
        }
    owner, repo_name = repo_slug.split("/", 1)
    return host_attestation_readback(
        target,
        owner,
        repo_name,
        pr_number,
        args.issue,
        artifact_id,
        closeout=closeout,
        review_policy=getattr(args, "review_policy", "approved"),
    )


def handle_ship(argv: list[str]) -> int:
    if argv and argv[0] in {"status", "preflight"}:
        return handle_ship_status(argv[1:], mode=argv[0])
    parser = argparse.ArgumentParser(prog="loom ship")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item", required=True)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--branch")
    parser.add_argument("--target-branch")
    parser.add_argument("--head-sha")
    parser.add_argument("--intensity", choices=("auto", "light", "standard", "reinforced"), default="auto")
    parser.add_argument("--validation-profile", choices=SHIP_VALIDATION_PROFILE_CHOICES, default="auto")
    parser.add_argument("--merge-method", choices=("squash", "merge", "rebase"), default="squash")
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES, default="implementation_pr")
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
    parser.add_argument("--carrier-sync-pr", type=int)
    parser.add_argument("--final-closeout-pr", type=int)
    parser.add_argument("--project")
    parser.add_argument("--phase")
    parser.add_argument("--fr", type=int)
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--comment")
    parser.add_argument("--comment-file")
    parser.add_argument("--goal-completion")
    parser.add_argument("--attestation-artifact-input", type=Path)
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--gate-profile", choices=("auto", "closeout-contract", "source-self-fixture", "bootstrap-regression", "distribution-regression", "strong-profile-full-gate"))
    parser.add_argument("--issue-payload-file")
    parser.add_argument("--project-payload-file")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    command = "ship"
    target = resolve_target(args.target)
    lifecycle_admission = host_lifecycle_admission_payload(
        target=target,
        issue=args.issue,
        fr=args.fr,
        owner=args.owner,
        repo_name=args.repo_name,
        intent="ship",
        pr=args.pr,
        branch=args.branch,
    )
    if lifecycle_admission["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block",
                    schema_version="loom-ship/v1",
                    summary="ship stopped before repository carriers because the host-native lifecycle admission is blocked.",
                    mutates=False,
                    dry_run=not args.apply,
                    apply=args.apply,
                    target=str(target),
                    item={"id": args.item},
                    issue={"number": args.issue},
                    pr={"number": args.pr},
                    lifecycle_admission=lifecycle_admission,
                    missing_inputs=lifecycle_admission.get("missing_inputs") or lifecycle_admission.get("admission", {}).get("missing_inputs", []),
                    fallback_to=[lifecycle_admission.get("primary_remediation")],
                    next_action=lifecycle_admission.get("primary_remediation"),
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )

    common = ["--target", str(target)]
    steps: list[dict[str, Any]] = [ship_step("host-lifecycle-admission", lifecycle_admission)]
    binding_inference = ship_binding_inference_payload(args, target)
    effective_bindings = binding_inference.get("bindings") if isinstance(binding_inference.get("bindings"), dict) else {}
    effective_branch = effective_bindings.get("branch") if isinstance(effective_bindings.get("branch"), str) else None
    effective_head_sha = effective_bindings.get("head_sha") if isinstance(effective_bindings.get("head_sha"), str) else None
    effective_target_branch = effective_bindings.get("target_branch") if isinstance(effective_bindings.get("target_branch"), str) else None
    steps.append(ship_step("ship-binding-inference", binding_inference))
    if binding_inference.get("result") != "pass":
        closeout_policy = ship_closeout_policy({}, intensity_override=args.intensity)
        next_action = binding_inference.get("fallback_to") or "rerun loom ship with explicit host bindings"
        skipped_profile = "standard" if args.validation_profile == "auto" else args.validation_profile
        skipped_source_surface = SHIP_VALIDATION_SOURCE_SURFACES[skipped_profile]
        skipped_validation_commands = (
            []
            if skipped_source_surface is None
            else [f"python3 tools/loom_check.py --profile source --source-surface {skipped_source_surface} ."]
        )
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block",
                    schema_version="loom-ship/v1",
                    summary="ship stopped before delivery gates because branch, head SHA, or target branch bindings could not be inferred safely.",
                    mutates=False,
                    dry_run=not args.apply,
                    apply=args.apply,
                    target=str(target),
                    item={"id": args.item},
                    issue={"number": args.issue},
                    pr={"number": args.pr},
                    intensity=args.intensity,
                    effective_intensity=closeout_policy.get("governance_intensity"),
                    validation_profile={
                        "schema_version": "loom-ship-validation-profile/v1",
                        "result": "skipped",
                        "requested_profile": args.validation_profile,
                        "selected_profile": skipped_profile,
                        "source_surface": skipped_source_surface,
                        "selection_reasons": ["binding_inference_blocked"],
                        "changed_paths": [],
                        "validation_commands": skipped_validation_commands,
                    },
                    merge_method=args.merge_method,
                    closeout_policy=closeout_policy,
                    binding_inference=binding_inference,
                    steps=steps,
                    first_blocker=steps[-1],
                    missing_inputs=binding_inference.get("missing_inputs", []),
                    fallback_to=next_action,
                    next_action=next_action,
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )
    if args.apply:
        repair_args = ship_metadata_update_args(args, target, branch=effective_branch, head_sha=effective_head_sha)
        if repair_args is None:
            steps.append(
                ship_step(
                    "safe-metadata-repair",
                    {"result": "skipped", "summary": "safe metadata repair requires --issue plus inferred or explicit branch."},
                    skipped_reason="not enough binding inputs for safe PR metadata repair",
                )
            )
        else:
            repair = flow_payload(command, repair_args, fallback_to=["loom pr metadata-update <pr> --item <id> --issue <n> --branch <branch> --apply --json"])
            steps.append(ship_step("safe-metadata-repair", repair, mutates=True))
            if repair.get("result") != "pass":
                closeout_policy = ship_closeout_policy({}, intensity_override=args.intensity)
                return ship_apply_admission_block(
                    command=command,
                    target=target,
                    args=args,
                    steps=steps,
                    closeout_policy=closeout_policy,
                    summary="ship --apply stopped before merge because safe PR metadata repair did not pass.",
                    missing_inputs=[str(value) for value in repair.get("missing_inputs", [])],
                    fallback_to=["loom pr metadata-update <pr> --item <id> --issue <n> --branch <branch> --apply --json"],
                )

    metadata_args = ["pr-metadata", "preflight", *common, "--surface", "merge_ready", "--pr", str(args.pr), "--item", args.item]
    if args.issue is not None:
        metadata_args.extend(["--issue", str(args.issue)])
    if effective_branch:
        metadata_args.extend(["--branch", effective_branch])
    if args.head_sha:
        metadata_args.extend(["--head-sha", args.head_sha])
    if args.pr_payload_file:
        metadata_args.extend(["--pr-payload-file", args.pr_payload_file])
    metadata = flow_payload(command, metadata_args, fallback_to=["loom pr metadata-update <pr> --item <id> --apply --json"])

    pr_gate_args = ["pr-gate", "check", *common, "--pr", str(args.pr), "--item", args.item]
    if args.head_sha:
        pr_gate_args.extend(["--head-sha", args.head_sha])
    if args.pr_payload_file:
        pr_gate_args.extend(["--pr-payload-file", args.pr_payload_file])
    pr_gate = flow_payload(command, pr_gate_args, fallback_to=["loom pr gate <pr> --work-item <id> --json"])

    merge_args = ["controlled-merge", "check", *common, "--pr", str(args.pr), "--item", args.item, "--merge-method", args.merge_method]
    if args.head_sha:
        merge_args.extend(["--head-sha", args.head_sha])
    for flag, value in (
        ("--pr-payload-file", args.pr_payload_file),
        ("--status-checks-file", args.status_checks_file),
        ("--branch-protection-file", args.branch_protection_file),
        ("--ruleset-file", args.ruleset_file),
    ):
        if value:
            merge_args.extend([flag, value])
    merge_check = flow_payload(command, merge_args, fallback_to=["loom merge check <pr> --work-item <id> --json"])

    fields = governance_metadata_fields(metadata)
    closeout_policy = ship_closeout_policy(fields, intensity_override=args.intensity)
    changed_paths = ship_changed_paths_payload(args, target, target_branch=effective_target_branch, head_sha=effective_head_sha)
    validation_profile = ship_validation_profile_payload(args, changed_paths, closeout_policy)
    review_attestation = ship_host_attestation(args, target, closeout=False)
    steps.extend([
        ship_step("pr-metadata-preflight", metadata),
        ship_step("pr-gate", pr_gate),
        ship_step("controlled-merge-check", merge_check),
        ship_step("validation-profile", validation_profile),
        ship_step("host-review-attestation", review_attestation),
        ship_step("closeout-policy", closeout_policy),
    ])
    if not args.apply:
        steps.append(
            ship_step(
                "post-merge-closeout",
                {"result": "skipped", "summary": "dry-run does not mutate host or repo state."},
                skipped_reason="planned after merge/apply; no closeout PR is created by dry-run",
            )
        )
    blocker = first_ship_blocker(steps)
    result = "pass" if blocker is None else "block"
    next_action = closeout_policy["next_action"] if blocker is None else (blocker.get("fallback_to") or f"resolve `{blocker.get('name')}`")
    if args.apply and blocker is not None:
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block",
                    schema_version="loom-ship/v1",
                    summary="ship --apply stopped before merge at the first blocking delivery step.",
                    mutates=any(bool(step.get("mutates")) for step in steps),
                    dry_run=False,
                    apply=True,
                    target=str(target),
                    item={"id": args.item},
                    issue={"number": args.issue},
                    pr={"number": args.pr},
                    intensity=args.intensity,
                    effective_intensity=closeout_policy.get("governance_intensity"),
                    validation_profile=validation_profile,
                    merge_method=args.merge_method,
                    closeout_policy=closeout_policy,
                    binding_inference=binding_inference,
                    steps=steps,
                    first_blocker=blocker,
                    missing_inputs=blocker.get("missing_inputs", []),
                    fallback_to=next_action,
                    next_action=next_action,
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )
    if args.apply and args.issue is None:
        steps.append(ship_step("ship-apply-admission", {"result": "block", "summary": "ship --apply requires --issue for host closeout."}))
        return ship_apply_admission_block(
            command=command,
            target=target,
            args=args,
            steps=steps,
            closeout_policy=closeout_policy,
            validation_profile=validation_profile,
            summary="ship --apply stopped before merge because issue closeout cannot be addressed.",
            missing_inputs=["--issue is required for ship --apply"],
            fallback_to=["loom ship --item <id> --issue <n> --pr <n> --apply --json"],
        )
    if args.apply and closeout_policy.get("policy") not in {"inline", "host_only"}:
        policy = str(closeout_policy.get("policy"))
        steps.append(ship_step("ship-apply-admission", {"result": "block", "summary": f"closeout policy `{policy}` requires an explicit closeout path before ship --apply can merge."}))
        return ship_apply_admission_block(
            command=command,
            target=target,
            args=args,
            steps=steps,
            closeout_policy=closeout_policy,
            validation_profile=validation_profile,
            summary="ship --apply stopped before merge because this item requires a non-default closeout path.",
            missing_inputs=[f"closeout policy `{policy}` is not eligible for default host-only closeout"],
            fallback_to=["loom closeout queue status --item <id> --issue <n> --pr <n> --json", "use explicit full closeout PR path when policy requires it"],
        )
    closeout_branch = ship_closeout_target_branch(args, merge_check, inferred_target_branch=effective_target_branch)
    if args.apply and not closeout_branch:
        steps.append(ship_step("ship-apply-admission", {"result": "block", "summary": "ship --apply could not infer target branch for closeout readback."}))
        return ship_apply_admission_block(
            command=command,
            target=target,
            args=args,
            steps=steps,
            closeout_policy=closeout_policy,
            validation_profile=validation_profile,
            summary="ship --apply stopped before merge because target branch is unknown.",
            missing_inputs=["target branch is required for post-merge closeout"],
            fallback_to=["rerun with --target-branch <base-branch>"],
        )
    if args.apply:
        merge_apply_args = ["controlled-merge", "merge", *common, "--pr", str(args.pr), "--item", args.item, "--merge-method", args.merge_method, "--execute"]
        if args.head_sha:
            merge_apply_args.extend(["--head-sha", args.head_sha])
        for flag, value in (
            ("--pr-payload-file", args.pr_payload_file),
            ("--status-checks-file", args.status_checks_file),
            ("--branch-protection-file", args.branch_protection_file),
            ("--ruleset-file", args.ruleset_file),
        ):
            if value:
                merge_apply_args.extend([flag, value])
        merge_apply = flow_payload(command, merge_apply_args, fallback_to=["loom merge check <pr> --work-item <id> --json"])
        steps.append(ship_step("controlled-merge-apply", merge_apply, mutates=True))
        if merge_apply.get("result") != "pass":
            blocker = steps[-1]
            return emit(
                agent_safe_payload(
                    output(
                        command,
                        "block",
                        schema_version="loom-ship/v1",
                        summary="ship --apply stopped because controlled merge did not pass.",
                        mutates=True,
                        dry_run=False,
                        apply=True,
                        target=str(target),
                        item={"id": args.item},
                        issue={"number": args.issue},
                        pr={"number": args.pr},
                        intensity=args.intensity,
                        effective_intensity=closeout_policy.get("governance_intensity"),
                        validation_profile=validation_profile,
                        merge_method=args.merge_method,
                        closeout_policy=closeout_policy,
                        binding_inference=binding_inference,
                        steps=steps,
                        first_blocker=blocker,
                        missing_inputs=blocker.get("missing_inputs", []),
                        fallback_to=blocker.get("fallback_to"),
                        next_action=blocker.get("fallback_to") or "resolve controlled merge blocker",
                    ),
                    target_root=target,
                    full_output=args.full_output,
                )
            )

        closeout_branch = ship_closeout_target_branch(args, merge_apply, inferred_target_branch=effective_target_branch) or closeout_branch
        closeout_args = ship_closeout_namespace(args, branch=closeout_branch)
        reconciliation_args = ["reconciliation", "sync", "--target", str(target)]
        add_closeout_host_args(reconciliation_args, closeout_args, include_comment=True)
        reconciliation_args.append("--apply")
        reconciliation = flow_payload(command, reconciliation_args, fallback_to=["manual-reconciliation", "loom closeout --target <repo> --json"])
        steps.append(ship_step("host-reconciliation-sync", reconciliation, mutates=True))
        if reconciliation.get("result") == "pass":
            final_closeout = ship_host_attestation(args, target, closeout=True)
            steps.append(ship_step("host-closeout-attestation", final_closeout, mutates=False))
            if final_closeout.get("result") == "pass":
                current_payload = workstation_current_payload(
                    target,
                    item=args.item,
                    issue=str(args.issue) if args.issue is not None else None,
                    pr=str(args.pr),
                    branch=closeout_branch,
                    clear=True,
                )
                try:
                    current_path = write_workstation_current(target, current_payload)
                    global_current = {
                        "command": "workstation current",
                        "result": "pass",
                        "summary": "host-only closeout cleared the workstation current pointer without mutating repository carriers.",
                        "path": str(current_path),
                        "current": current_payload,
                    }
                except OSError as exc:
                    global_current = {
                        "command": "workstation current",
                        "result": "block",
                        "summary": "host-only closeout could not update the workstation current pointer.",
                        "missing_inputs": [str(exc)],
                        "fallback_to": "loom workstation current --target <repo> --clear --apply --json",
                    }
                steps.append(ship_step("global-current-closeout", global_current, mutates=global_current.get("result") == "pass"))

        blocker = first_ship_blocker(steps)
        ship_result = "pass" if blocker is None else "block"
        ship_summary = "ship --apply completed controlled merge and host closeout without creating a closeout PR." if ship_result == "pass" else "ship --apply merged only if controlled merge passed, then stopped at the first closeout blocker."
        return emit(
            agent_safe_payload(
                output(
                    command,
                    ship_result,
                    schema_version="loom-ship/v1",
                    summary=ship_summary,
                    mutates=True,
                    dry_run=False,
                    apply=True,
                    target=str(target),
                    item={"id": args.item},
                    issue={"number": args.issue},
                    pr={"number": args.pr},
                    intensity=args.intensity,
                    effective_intensity=closeout_policy.get("governance_intensity"),
                    validation_profile=validation_profile,
                    merge_method=args.merge_method,
                    closeout_policy=closeout_policy,
                    binding_inference=binding_inference,
                    closeout_mode="host_only",
                    creates_closeout_pr=False,
                    target_branch=closeout_branch,
                    steps=steps,
                    first_blocker=blocker,
                    missing_inputs=blocker.get("missing_inputs", []) if blocker else [],
                    fallback_to=(blocker.get("fallback_to") if blocker else None),
                    next_action=(blocker.get("fallback_to") if blocker else "ship --apply completed; read back PR, issue, and target branch state."),
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )

    payload = output(
        command,
        result,
        schema_version="loom-ship/v1",
        summary="ship dry-run produced the intensity-aware delivery plan." if result == "pass" else "ship dry-run stopped at the first blocking delivery step.",
        mutates=False,
        dry_run=True,
        target=str(target),
        item={"id": args.item},
        issue={"number": args.issue},
        pr={"number": args.pr},
        intensity=args.intensity,
        effective_intensity=closeout_policy.get("governance_intensity"),
        validation_profile=validation_profile,
        merge_method=args.merge_method,
        closeout_policy=closeout_policy,
        binding_inference=binding_inference,
        steps=steps,
        skipped_steps=[step for step in steps if step.get("result") == "skipped"],
        upgrade_reasons=closeout_policy.get("upgrade_reasons", []),
        first_blocker=blocker,
        missing_inputs=blocker.get("missing_inputs", []) if blocker else [],
        fallback_to=next_action if blocker else None,
        next_action=next_action,
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def handle_reconcile(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom reconcile")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--work-item")
    parser.add_argument("--head-sha")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    flow_args = ["reconciliation", "audit", "--target", "."]
    if args.issue:
        flow_args.extend(["--issue", args.issue])
    if args.pr:
        flow_args.extend(["--pr", args.pr])
    if args.work_item:
        flow_args.extend(["--item", args.work_item])
    append_full_output_flag(flow_args, args)
    return emit_flow("reconcile", flow_args, fallback_to=["manual-reconciliation"])


def handle_carrier(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom carrier")
    parser.add_argument("action", choices=("closeout-sync",))
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--output")
    parser.add_argument("--terminal-state")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--merge-commit")
    parser.add_argument("--target-branch")
    parser.add_argument("--closed-at")
    parser.add_argument("--evidence-locator")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", dest="dry_run", action="store_false")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    add_legacy_carrier_compatibility_args(parser)
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    compatibility = legacy_carrier_compatibility(args)
    if compatibility["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    f"carrier {args.action}",
                    "block",
                    schema_version="loom-legacy-carrier-command/v1",
                    summary=compatibility["summary"],
                    mutates=False,
                    target=str(target),
                    compatibility=compatibility,
                    missing_inputs=compatibility["missing_inputs"],
                    fallback_to=compatibility["fallback_to"],
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )
    flow_args = ["carrier", args.action, "--target", str(target)]
    for flag, value in (
        ("--item", args.item),
        ("--output", args.output),
        ("--terminal-state", args.terminal_state),
        ("--issue", args.issue),
        ("--pr", args.pr),
        ("--merge-commit", args.merge_commit),
        ("--target-branch", args.target_branch),
        ("--closed-at", args.closed_at),
        ("--evidence-locator", args.evidence_locator),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])
    if not args.dry_run:
        flow_args.append("--apply")
    append_full_output_flag(flow_args, args)
    command = f"carrier {args.action}"
    payload = flow_payload(command, flow_args, fallback_to=["loom closeout --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def add_closeout_host_args(flow_args: list[str], args: argparse.Namespace, *, include_comment: bool) -> None:
    for flag, value in (
        ("--item", args.item),
        ("--issue", args.issue),
        ("--pr", args.pr),
        ("--project", args.project),
        ("--phase", args.phase),
        ("--fr", args.fr),
        ("--branch", args.branch),
        ("--owner", args.owner),
        ("--repo", args.repo_name),
        ("--issue-payload-file", args.issue_payload_file),
        ("--pr-payload-file", args.pr_payload_file),
        ("--project-payload-file", args.project_payload_file),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])
    add_closeout_pr_role_args(flow_args, args)
    if include_comment:
        for flag, value in (
            ("--comment", args.comment),
            ("--comment-file", args.comment_file),
        ):
            if value is not None:
                flow_args.extend([flag, str(value)])


def add_closeout_check_args(flow_args: list[str], args: argparse.Namespace) -> None:
    add_closeout_host_args(flow_args, args, include_comment=True)
    for flag, value in (
        ("--goal-completion", args.goal_completion),
        ("--gate-profile", args.gate_profile),
        ("--status-checks-file", args.status_checks_file),
        ("--branch-protection-file", args.branch_protection_file),
        ("--ruleset-file", args.ruleset_file),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])
    if args.skip_gate:
        flow_args.append("--skip-gate")


def closeout_run_step(name: str, payload: dict[str, Any], *, mutates: bool, evidence_locator: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "result": payload.get("result"),
        "summary": payload.get("summary"),
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "mutates": mutates,
        "evidence_locator": evidence_locator,
        "payload": payload,
    }


def issue_state(payload: dict[str, Any]) -> str | None:
    issue = payload.get("issue")
    return str(issue.get("state")) if isinstance(issue, dict) and issue.get("state") is not None else None


def pr_state(payload: dict[str, Any]) -> str | None:
    pr = payload.get("pr")
    return str(pr.get("state")) if isinstance(pr, dict) and pr.get("state") is not None else None


def closeout_terminal_metadata(closeout_payload: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, str], list[str]]:
    issue = closeout_payload.get("issue") if isinstance(closeout_payload.get("issue"), dict) else {}
    pr = closeout_payload.get("pr") if isinstance(closeout_payload.get("pr"), dict) else {}
    merge_commit = pr.get("mergeCommit") if isinstance(pr, dict) else None
    merge_commit_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
    issue_number = issue.get("number") if isinstance(issue, dict) else None
    pr_number = pr.get("number") if isinstance(pr, dict) else None
    issue_url = issue.get("url") if isinstance(issue, dict) else None
    pr_url = pr.get("url") if isinstance(pr, dict) else None
    metadata = {
        "terminal_state": "closed_out",
        "issue": str(issue_number or args.issue or "not_applicable"),
        "pr": str(pr_number or args.pr or "not_applicable"),
        "merge_commit": str(merge_commit_sha or "not_applicable"),
        "target_branch": str(pr.get("baseRefName") or "not_applicable") if isinstance(pr, dict) else "not_applicable",
        "closed_at": str(issue.get("closedAt") or issue.get("closed_at") or pr.get("mergedAt") or "not_applicable") if isinstance(issue, dict) and isinstance(pr, dict) else "not_applicable",
        "evidence_locator": ";".join(str(value) for value in (issue_url, pr_url) if isinstance(value, str) and value.strip()) or "host-readback",
    }
    missing: list[str] = []
    for field_name in ("issue", "pr", "merge_commit", "target_branch", "closed_at", "evidence_locator"):
        if metadata[field_name] == "not_applicable":
            missing.append(f"{field_name.replace('_', '-')} is required for closeout run carrier sync")
    return metadata, missing


def first_blocking_step(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    for step in steps:
        if step.get("result") != "pass":
            return step
    return None


def closeout_run_failure_classifier(blocking_step: dict[str, Any] | None) -> str | None:
    if blocking_step is None:
        return None
    missing_inputs = [str(value) for value in blocking_step.get("missing_inputs") or []]
    if any("required check" in value or "status checks" in value for value in missing_inputs):
        return "host_checks_unreadable_or_incomplete"
    if any("PR is draft" in value or "pr is not merged" in value.lower() for value in missing_inputs):
        return "pr_not_merge_ready_or_unmerged"
    if any("issue is not closed" in value.lower() for value in missing_inputs):
        return "issue_not_closed"
    if any("binding" in value.lower() for value in missing_inputs):
        return "host_binding_drift"
    if any("carrier" in value.lower() or "shadow" in value.lower() for value in missing_inputs):
        return "carrier_refresh_required"
    if missing_inputs:
        return "missing_or_stale_closeout_input"
    return "closeout_step_blocked"


def closeout_run_next_action(*, apply: bool, blocking_step: dict[str, Any] | None) -> str:
    if blocking_step is None:
        return "Closeout run completed." if apply else "Review the dry-run plan, then rerun with --apply when the planned host and repo carrier mutations are acceptable."
    fallback_to = blocking_step.get("fallback_to")
    if isinstance(fallback_to, str) and fallback_to:
        return fallback_to
    if blocking_step.get("name") == "reconciliation-sync":
        return "Review reconciliation findings, then rerun closeout run after host drift is readable and safe to sync."
    if blocking_step.get("name") == "final-closeout-check":
        return "Inspect final closeout check missing_inputs; rerun closeout run only after the blocker is classified."
    return f"Resolve blocked step `{blocking_step.get('name')}` before rerunning closeout run."


def closeout_sync_step(name: str, payload: dict[str, Any], *, mutates: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "result": payload.get("result"),
        "summary": payload.get("summary"),
        "missing_inputs": payload.get("missing_inputs", []),
        "fallback_to": payload.get("fallback_to"),
        "mutates": mutates,
        "payload": payload,
    }


def closeout_sync_blocker(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    for step in steps:
        if step.get("result") == "block":
            return step
    return None


def closeout_metadata_artifact(target: Path, args: argparse.Namespace, suffix: str) -> str:
    item = args.item or "closeout"
    pr = closeout_current_pr_input(args) or args.pr or "pr"
    safe_item = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(item)).strip("-") or "closeout"
    safe_pr = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(pr)).strip("-") or "pr"
    return f".loom/runtime/pr/{safe_item}-{safe_pr}-closeout-{suffix}.md"


def add_closeout_metadata_args(flow_args: list[str], args: argparse.Namespace, target: Path, *, include_output: bool = False, include_readback: bool = False) -> None:
    for flag, value in (
        ("--pr", closeout_current_pr_input(args) or args.pr),
        ("--item", args.item),
        ("--issue", args.issue),
        ("--head-sha", getattr(args, "head_sha", None)),
        ("--branch", args.branch),
        ("--pr-payload-file", args.pr_payload_file),
    ):
        if value is not None:
            flow_args.extend([flag, str(value)])
    if include_output:
        flow_args.extend(["--output-file", closeout_metadata_artifact(target, args, "rendered")])
    if include_readback:
        flow_args.extend(["--readback-file", closeout_metadata_artifact(target, args, "readback")])


def closeout_metadata_readback_payload(args: argparse.Namespace, target: Path) -> dict[str, Any]:
    if closeout_current_pr_input(args) is None and args.pr is None:
        return {
            "command": "closeout metadata-readback",
            "result": "not_applicable",
            "summary": "PR metadata readback was skipped because no PR binding was provided.",
            "missing_inputs": [],
            "fallback_to": None,
        }
    flow_args = ["pr-metadata", "readback", "--target", str(target), "--surface", "closeout"]
    add_closeout_metadata_args(flow_args, args, target, include_readback=True)
    return flow_payload(
        "closeout sync",
        flow_args,
        fallback_to=["loom pr metadata-update <pr> --surface closeout --item <id> --head-sha <sha> --apply --json"],
    )


def closeout_metadata_update_payload(args: argparse.Namespace, target: Path, *, apply: bool) -> dict[str, Any]:
    flow_args = ["pr-metadata", "update", "--target", str(target), "--surface", "closeout"]
    add_closeout_metadata_args(flow_args, args, target, include_output=True, include_readback=True)
    flow_args.append("--apply" if apply else "--dry-run")
    return flow_payload(
        "closeout sync",
        flow_args,
        fallback_to=["loom pr metadata-render --surface closeout --item <id> --json", "loom pr metadata-readback <pr> --surface closeout --json"],
    )


def parse_git_worktree_porcelain(raw: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key:
            current[key] = value.strip()
    if current:
        entries.append(current)
    return entries


def closeout_terminal_cleanup_payload(target: Path, args: argparse.Namespace) -> dict[str, Any]:
    branch = args.branch
    checks: list[dict[str, Any]] = []
    cleanup_actions: list[str] = []
    missing_inputs: list[str] = []
    blocking = False

    worktree_result = run_capture(["git", "worktree", "list", "--porcelain"], cwd=target)
    worktrees: list[dict[str, str]] = []
    if worktree_result.returncode == 0:
        worktrees = parse_git_worktree_porcelain(worktree_result.stdout)
    else:
        missing_inputs.append(worktree_result.stderr.strip() or "git worktree list failed")
        blocking = True

    if branch:
        branch_ref = f"refs/heads/{branch}"
        matching_worktrees = [entry for entry in worktrees if entry.get("branch") == branch_ref]
        if matching_worktrees:
            for entry in matching_worktrees:
                path = entry.get("worktree")
                if path:
                    cleanup_actions.append(f"git worktree remove {path}")
            checks.append({"id": "issue_worktree", "result": "warn", "branch": branch, "worktrees": matching_worktrees})
        else:
            checks.append({"id": "issue_worktree", "result": "pass", "branch": branch, "worktrees": []})

        local_branch = run_capture(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd=target)
        if local_branch.returncode == 0:
            cleanup_actions.append(f"git branch -d {branch}")
            checks.append({"id": "local_branch", "result": "warn", "branch": branch})
        else:
            checks.append({"id": "local_branch", "result": "pass", "branch": branch})

        remote_branch = run_capture(["git", "show-ref", "--verify", f"refs/remotes/origin/{branch}"], cwd=target)
        if remote_branch.returncode == 0:
            cleanup_actions.append(f"git push origin --delete {branch}")
            checks.append({"id": "remote_branch", "result": "warn", "branch": f"origin/{branch}"})
        else:
            checks.append({"id": "remote_branch", "result": "pass", "branch": f"origin/{branch}"})
    else:
        checks.append({"id": "branch_cleanup", "result": "not_applicable", "summary": "No branch binding was provided."})

    main_worktree = next((entry.get("worktree") for entry in worktrees if entry.get("branch") == "refs/heads/main"), None)
    if main_worktree:
        dirty = run_capture(["git", "-C", main_worktree, "status", "--short"], cwd=target)
        if dirty.returncode != 0:
            missing_inputs.append(dirty.stderr.strip() or "main worktree dirty-state readback failed")
            blocking = True
            checks.append({"id": "main_worktree_dirty", "result": "block", "worktree": main_worktree})
        elif dirty.stdout.strip():
            missing_inputs.append("main worktree has uncommitted changes")
            blocking = True
            checks.append({"id": "main_worktree_dirty", "result": "block", "worktree": main_worktree, "status": dirty.stdout.strip().splitlines()})
        else:
            checks.append({"id": "main_worktree_dirty", "result": "pass", "worktree": main_worktree})
    else:
        checks.append({"id": "main_worktree_dirty", "result": "not_applicable", "summary": "No local main worktree was found in git worktree list."})

    cleanup_actions = list(dict.fromkeys(cleanup_actions))
    cleanup_needed = bool(cleanup_actions)
    result = "block" if blocking else ("warn" if cleanup_needed else "pass")
    verdict = "blocked" if blocking else ("cleanup_needed" if cleanup_needed else "clean_terminal")
    next_action = (
        "Resolve main worktree dirty state or unreadable git cleanup inputs before deleting branches."
        if blocking
        else ("; ".join(cleanup_actions) if cleanup_needed else "No terminal cleanup action required.")
    )
    return {
        "schema_version": "loom-closeout-terminal-cleanup/v1",
        "command": "closeout cleanup-check",
        "result": result,
        "verdict": verdict,
        "summary": "terminal cleanup readback found cleanup actions." if cleanup_needed else "terminal cleanup readback is clean.",
        "missing_inputs": missing_inputs,
        "fallback_to": next_action if result == "block" else None,
        "branch": branch,
        "checks": checks,
        "cleanup_actions": cleanup_actions,
        "next_action": next_action,
        "mutates": False,
    }


def closeout_sync_diagnostic(*, operation: str, apply: bool, steps: list[dict[str, Any]]) -> dict[str, Any]:
    blocker = closeout_sync_blocker(steps)
    cleanup_step = next((step for step in steps if step.get("name") == "terminal-cleanup-check"), None)
    cleanup_payload = cleanup_step.get("payload") if isinstance(cleanup_step, dict) and isinstance(cleanup_step.get("payload"), dict) else {}
    fixed = operation == "sync" and apply and blocker is None
    if blocker is not None:
        fallback = blocker.get("fallback_to")
        next_action = fallback if isinstance(fallback, str) else (fallback[0] if isinstance(fallback, list) and fallback else f"Resolve `{blocker.get('name')}` before rerunning closeout sync.")
    elif cleanup_payload.get("result") == "warn":
        next_action = str(cleanup_payload.get("next_action") or "Run terminal cleanup actions after confirming no user work remains.")
    elif operation == "sync" and not apply:
        next_action = "Review the dry-run plan, then rerun `loom closeout sync --apply` when the host reconciliation mutation is acceptable."
    else:
        next_action = "Closeout sync is terminal; proceed to the next dependent Work Item."
    return {
        "blocked": blocker is not None,
        "fixed": fixed,
        "next_action": next_action,
        "first_blocker": blocker.get("name") if blocker else None,
        "cleanup_verdict": cleanup_payload.get("verdict") if isinstance(cleanup_payload, dict) else None,
    }


def build_closeout_sync_parser(prog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--target", default=".")
    parser.add_argument("--item", required=True)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES)
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
    parser.add_argument("--carrier-sync-pr", type=int)
    parser.add_argument("--final-closeout-pr", type=int)
    parser.add_argument("--project")
    parser.add_argument("--phase")
    parser.add_argument("--fr")
    parser.add_argument("--branch")
    parser.add_argument("--head-sha")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--comment")
    parser.add_argument("--comment-file")
    parser.add_argument("--goal-completion")
    parser.add_argument("--attestation-artifact-input", type=Path)
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--gate-profile", choices=("auto", "closeout-contract", "source-self-fixture", "bootstrap-regression", "distribution-regression", "strong-profile-full-gate"), default="auto")
    parser.add_argument("--issue-payload-file")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--project-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--skip-metadata", action="store_true")
    parser.add_argument("--skip-cleanup", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    return parser


def handle_closeout_sync(operation: str, argv: list[str]) -> int:
    parser = build_closeout_sync_parser(f"loom closeout {operation}")
    args = parser.parse_args(argv)
    if closeout_current_pr_input(args) is None and args.pr is None:
        parser.error("--pr or one closeout PR role flag is required")
    target = resolve_target(args.target)
    steps: list[dict[str, Any]] = []
    if operation == "sync":
        reconciliation_args = ["reconciliation", "sync", "--target", str(target)]
        add_closeout_host_args(reconciliation_args, args, include_comment=True)
        reconciliation_args.append("--apply" if args.apply else "--dry-run")
        reconciliation = flow_payload("closeout sync", reconciliation_args, fallback_to=["manual-reconciliation"])
        steps.append(closeout_sync_step("host-reconciliation-sync", reconciliation, mutates=args.apply))

    if closeout_sync_blocker(steps) is None:
        attestation = ship_host_attestation(args, target, closeout=True)
        steps.append(closeout_sync_step("host-closeout-attestation", attestation))

    if not args.skip_cleanup:
        cleanup = closeout_terminal_cleanup_payload(target, args)
        steps.append(closeout_sync_step("terminal-cleanup-check", cleanup))

    blocker = closeout_sync_blocker(steps)
    result = "pass" if blocker is None else "block"
    diagnostic = closeout_sync_diagnostic(operation=operation, apply=args.apply, steps=steps)
    summary = (
        "closeout sync applied host reconciliation and consumed host attestation without repository carrier mutation."
        if operation == "sync" and args.apply and result == "pass"
        else "closeout sync dry-run produced a readback and repair plan."
        if operation == "sync"
        else "closeout status read back host attestation and local cleanup state."
    )
    payload = output(
        f"closeout {operation}",
        result,
        schema_version="loom-closeout-sync/v1",
        summary=summary if result == "pass" else "closeout sync/status stopped at a blocking readback step.",
        target=str(target),
        item={"id": args.item},
        issue={"number": args.issue},
        pr={"number": closeout_current_pr_input(args) or args.pr},
        apply=args.apply,
        dry_run=not args.apply,
        mutates=operation == "sync" and args.apply,
        repo_mutations=False,
        creates_closeout_pr=False,
        steps=steps,
        diagnostic=diagnostic,
        first_blocker=blocker,
        missing_inputs=blocker.get("missing_inputs", []) if blocker else [],
        fallback_to=diagnostic["next_action"] if blocker else None,
        next_action=diagnostic["next_action"],
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def closeout_run_payload(
    *,
    args: argparse.Namespace,
    target: Path,
    steps: list[dict[str, Any]],
    evidence_locators: list[str],
    closeout_payload: dict[str, Any],
    terminal_metadata: dict[str, str],
    apply: bool,
    dry_run_blocking_step: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if apply:
        blocking_step = first_blocking_step(steps)
        result = "pass" if blocking_step is None else "block"
        summary = "closeout run applied host and repo carrier closeout and final check passed." if result == "pass" else "closeout run apply stopped at a blocking step."
    else:
        blocking_step = dry_run_blocking_step
        result = "pass" if blocking_step is None else "block"
        summary = "closeout run dry-run produced a post-merge closeout step plan." if result == "pass" else "closeout run dry-run could not produce a safe step plan."

    next_action = closeout_run_next_action(apply=apply, blocking_step=blocking_step)
    pr_roles = closeout_payload.get("pr_roles") if isinstance(closeout_payload.get("pr_roles"), dict) else None
    current_pr_role = pr_roles.get("current") if isinstance(pr_roles, dict) and isinstance(pr_roles.get("current"), dict) else None
    return output(
        "closeout run",
        result,
        schema_version="loom-closeout-run/v1",
        summary=summary,
        dry_run=not apply,
        apply=apply,
        target=str(target),
        item={"id": args.item},
        issue={"number": args.issue, "state": issue_state(closeout_payload)},
        pr={"number": (current_pr_role or {}).get("number", args.pr), "state": pr_state(closeout_payload)},
        pr_roles=pr_roles,
        current_pr_role=current_pr_role,
        terminal_metadata=terminal_metadata,
        steps=steps,
        evidence_locators=evidence_locators,
        failure_classifier=closeout_run_failure_classifier(blocking_step),
        next_action=next_action,
        fallback_to=None if result == "pass" else next_action,
    )


def run_closeout_payload(args: argparse.Namespace, target: Path) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    evidence_locators: list[str] = []

    reconciliation_args = ["reconciliation", "sync", "--target", str(target)]
    add_closeout_host_args(reconciliation_args, args, include_comment=True)
    reconciliation_args.append("--apply" if args.apply else "--dry-run")
    reconciliation = flow_payload("closeout run", reconciliation_args, fallback_to=["manual-reconciliation", "loom closeout run --json"])
    steps.append(closeout_run_step("reconciliation-sync", reconciliation, mutates=args.apply, evidence_locator="reconciliation sync payload"))
    if args.apply and reconciliation.get("result") != "pass":
        terminal_metadata = {
            "terminal_state": "closed_out",
            "issue": str(args.issue),
            "pr": str(closeout_current_pr_input(args) or "not_applicable"),
            "merge_commit": "not_applicable",
            "target_branch": "not_applicable",
            "closed_at": "not_applicable",
            "evidence_locator": "host-readback",
        }
        return closeout_run_payload(
            args=args,
            target=target,
            steps=steps,
            evidence_locators=evidence_locators,
            closeout_payload={},
            terminal_metadata=terminal_metadata,
            apply=args.apply,
        )

    closeout_args = ["closeout", "check", "--target", str(target)]
    add_closeout_check_args(closeout_args, args)
    closeout_after_reconciliation = flow_payload("closeout run", closeout_args, fallback_to=["loom closeout run --json", "manual-reconciliation"])
    steps.append(closeout_run_step("closeout-check", closeout_after_reconciliation, mutates=False, evidence_locator="closeout check payload"))
    if args.apply and closeout_after_reconciliation.get("result") != "pass":
        metadata, _metadata_missing = closeout_terminal_metadata(closeout_after_reconciliation, args)
        return closeout_run_payload(
            args=args,
            target=target,
            steps=steps,
            evidence_locators=evidence_locators,
            closeout_payload=closeout_after_reconciliation,
            terminal_metadata=metadata,
            apply=args.apply,
        )

    metadata, metadata_missing = closeout_terminal_metadata(closeout_after_reconciliation, args)
    carrier_args = [
        "carrier",
        "closeout-sync",
        "--target",
        str(target),
        "--item",
        args.item,
        "--terminal-state",
        metadata["terminal_state"],
        "--issue",
        metadata["issue"],
        "--pr",
        metadata["pr"],
        "--merge-commit",
        metadata["merge_commit"],
        "--target-branch",
        metadata["target_branch"],
        "--closed-at",
        metadata["closed_at"],
        "--evidence-locator",
        metadata["evidence_locator"],
    ]
    carrier_args.append("--apply" if args.apply else "--dry-run")
    if metadata_missing:
        carrier_payload = output(
            "closeout run",
            "block",
            summary="closeout run could not infer terminal carrier metadata from host readback.",
            missing_inputs=metadata_missing,
            fallback_to=["loom closeout check --json", "manual-reconciliation"],
            terminal_metadata=metadata,
        )
    else:
        carrier_payload = flow_payload("closeout run", carrier_args, fallback_to=["loom carrier closeout-sync --json"])
    steps.append(closeout_run_step("carrier-closeout-sync", carrier_payload, mutates=args.apply, evidence_locator=metadata["evidence_locator"]))
    if metadata["evidence_locator"] != "host-readback":
        evidence_locators.append(metadata["evidence_locator"])
    if args.apply and carrier_payload.get("result") != "pass":
        return closeout_run_payload(
            args=args,
            target=target,
            steps=steps,
            evidence_locators=evidence_locators,
            closeout_payload=closeout_after_reconciliation,
            terminal_metadata=metadata,
            apply=args.apply,
        )

    if args.apply:
        stop = (
            f"{args.item} closed out by closeout run: PR #{metadata['pr']} merged at {metadata['merge_commit']}, "
            f"issue #{metadata['issue']} closed, host reconciliation consumed, terminal carrier metadata written, "
            "status/shadow refresh completed, and final closeout check passed."
        )
        recovery_args = [
            "recovery",
            "writeback",
            "--target",
            str(target),
            "--item",
            args.item,
            "--current-checkpoint",
            "closed_out",
            "--current-stop",
            stop,
            "--next-step",
            f"No further {args.item} implementation work remains.",
            "--blockers",
            "None recorded.",
            "--current-lane",
            "post-merge-closeout-run",
        ]
        recovery = flow_payload("closeout run", recovery_args, fallback_to=["loom recovery writeback --target <repo> --item <item>"])
        steps.append(closeout_run_step("recovery-writeback", recovery, mutates=True, evidence_locator=".loom/progress"))
        if recovery.get("result") != "pass":
            return closeout_run_payload(
                args=args,
                target=target,
                steps=steps,
                evidence_locators=evidence_locators,
                closeout_payload=closeout_after_reconciliation,
                terminal_metadata=metadata,
                apply=args.apply,
            )

        refresh_args = ["carrier", "refresh", "--target", str(target), "--item", args.item, "--surface", "closeout", "--write"]
        first_refresh = flow_payload("closeout run", refresh_args, fallback_to=["loom carrier refresh --target <repo> --item <item> --write"])
        steps.append(closeout_run_step("carrier-refresh", first_refresh, mutates=True, evidence_locator=".loom/shadow"))
        if first_refresh.get("result") != "pass":
            return closeout_run_payload(
                args=args,
                target=target,
                steps=steps,
                evidence_locators=evidence_locators,
                closeout_payload=closeout_after_reconciliation,
                terminal_metadata=metadata,
                apply=args.apply,
            )
        second_refresh = flow_payload("closeout run", refresh_args, fallback_to=["loom carrier refresh --target <repo> --item <item> --write"])
        steps.append(closeout_run_step("carrier-refresh-readback", second_refresh, mutates=True, evidence_locator=".loom/shadow"))
        if second_refresh.get("result") != "pass":
            return closeout_run_payload(
                args=args,
                target=target,
                steps=steps,
                evidence_locators=evidence_locators,
                closeout_payload=closeout_after_reconciliation,
                terminal_metadata=metadata,
                apply=args.apply,
            )

        final_closeout = flow_payload("closeout run", closeout_args, fallback_to=["loom closeout --target <repo> --json", "manual-reconciliation"])
        steps.append(closeout_run_step("final-closeout-check", final_closeout, mutates=False, evidence_locator="closeout check payload"))

    return closeout_run_payload(
        args=args,
        target=target,
        steps=steps,
        evidence_locators=evidence_locators,
        closeout_payload=closeout_after_reconciliation,
        terminal_metadata=metadata,
        apply=args.apply,
        dry_run_blocking_step=first_blocking_step(steps),
    )


def batch_closeout_comment_body(args: argparse.Namespace, issue: int, *, repo_slug: str | None) -> str:
    if args.comment_file:
        comment_path = Path(args.comment_file).expanduser()
        if not comment_path.is_absolute():
            comment_path = resolve_target(args.target) / comment_path
        return comment_path.read_text(encoding="utf-8")
    if args.comment:
        return args.comment

    evidence_lines = []
    if args.pr is not None:
        pr_reference = f"https://github.com/{repo_slug}/pull/{args.pr}" if repo_slug else f"#{args.pr}"
        evidence_lines.append(f"- PR: {pr_reference}")
    if args.merge_commit:
        evidence_lines.append(f"- Merge commit: {args.merge_commit}")
    if args.target_branch:
        evidence_lines.append(f"- Target branch: {args.target_branch}")
    if args.evidence_locator:
        evidence_lines.append(f"- Evidence: {args.evidence_locator}")
    evidence = "\n".join(evidence_lines) if evidence_lines else "- Evidence: host readback"
    return (
        f"Batch closeout: issue #{issue} is covered by the merged implementation batch.\n\n"
        f"{evidence}\n\n"
        "Closeout mode: host-only batch closeout; no repository closeout PR or Loom carrier mutation was created."
    )


def batch_closeout_issue_step(
    *,
    issue: int,
    comment_body: str,
    repo_slug: str | None,
    target: Path,
    apply: bool,
) -> dict[str, Any]:
    step: dict[str, Any] = {
        "issue": issue,
        "mode": "host_only",
        "planned_actions": ["comment", "close"],
        "result": "pass",
        "mutates": apply,
        "commands": [],
        "errors": [],
    }
    if not apply:
        step["status"] = "planned"
        return step
    if not repo_slug:
        step["result"] = "block"
        step["status"] = "blocked"
        step["errors"].append("unable to infer GitHub repository; pass --owner and --repo")
        return step

    comment_command = ["gh", "issue", "comment", str(issue), "--repo", repo_slug, "--body", comment_body]
    close_command = ["gh", "issue", "close", str(issue), "--repo", repo_slug, "--reason", "completed"]
    for action, command in (("comment", comment_command), ("close", close_command)):
        completed = run_capture(command, cwd=target)
        step["commands"].append({"action": action, "command": shlex.join(command), "returncode": completed.returncode})
        if completed.returncode != 0:
            step["result"] = "block"
            step["status"] = "blocked"
            step["errors"].append(completed.stderr.strip() or completed.stdout.strip() or f"gh issue {action} failed")
            break
    if step["result"] == "pass":
        step["status"] = "applied"
    return step


def handle_closeout_batch(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom closeout batch")
    parser.add_argument("--target", default=".")
    parser.add_argument("--issue", type=int, action="append", required=True, help="Repeatable covered issue number to comment and close")
    parser.add_argument("--anchor-issue", type=int)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--merge-commit")
    parser.add_argument("--target-branch", default="main")
    parser.add_argument("--evidence-locator")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--comment")
    body_group.add_argument("--comment-file")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", dest="apply", action="store_false")
    parser.set_defaults(apply=False)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)

    target = resolve_target(args.target)
    covered_issues = list(dict.fromkeys(args.issue or []))
    anchor_issue = args.anchor_issue if args.anchor_issue is not None else covered_issues[0]
    missing_inputs: list[str] = []
    if anchor_issue not in covered_issues:
        missing_inputs.append("--anchor-issue must be included in at least one --issue")
    repo_slug = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else infer_github_repo(target)
    if args.apply and not repo_slug:
        missing_inputs.append("owner/repo")

    try:
        comment_bodies = {
            issue: batch_closeout_comment_body(args, issue, repo_slug=repo_slug)
            for issue in covered_issues
        }
    except OSError as exc:
        missing_inputs.append(f"comment-file unreadable: {exc}")
        comment_bodies = {}

    if missing_inputs:
        return emit(
            output(
                "closeout batch",
                "block",
                schema_version="loom-batch-closeout/v1",
                summary="batch closeout is missing required host inputs.",
                dry_run=not args.apply,
                apply=args.apply,
                mutates=False,
                host_mutations=False,
                carrier_mutations=False,
                creates_closeout_pr=False,
                target=str(target),
                anchor_issue=anchor_issue,
                covered_issues=covered_issues,
                pr=args.pr,
                repo=repo_slug,
                missing_inputs=missing_inputs,
                fallback_to=["loom closeout batch --issue <n> --pr <merged-pr> --json"],
            )
        )

    steps = [
        batch_closeout_issue_step(
            issue=issue,
            comment_body=comment_bodies[issue],
            repo_slug=repo_slug,
            target=target,
            apply=args.apply,
        )
        for issue in covered_issues
    ]
    blocking_steps = [step for step in steps if step.get("result") == "block"]
    result = "block" if blocking_steps else "pass"
    payload = output(
        "closeout batch",
        result,
        schema_version="loom-batch-closeout/v1",
        summary=(
            "batch closeout applied host-only comments and issue closes."
            if args.apply and result == "pass"
            else "batch closeout dry-run produced a host-only issue closeout plan."
            if result == "pass"
            else "batch closeout stopped because one or more host mutations failed."
        ),
        dry_run=not args.apply,
        apply=args.apply,
        mutates=args.apply,
        host_mutations=args.apply,
        carrier_mutations=False,
        creates_closeout_pr=False,
        target=str(target),
        repo=repo_slug,
        anchor_issue=anchor_issue,
        covered_issues=covered_issues,
        pr=args.pr,
        merge_commit=args.merge_commit,
        target_branch=args.target_branch,
        evidence_locator=args.evidence_locator,
        closeout_mode="host_only_batch",
        steps=steps if args.full_output or not args.apply else [
            {
                "issue": step.get("issue"),
                "mode": step.get("mode"),
                "result": step.get("result"),
                "status": step.get("status"),
                "planned_actions": step.get("planned_actions"),
                "errors": step.get("errors"),
            }
            for step in steps
        ],
        missing_inputs=[error for step in blocking_steps for error in step.get("errors", [])],
        fallback_to=["inspect failed host mutations and rerun `loom closeout batch --apply --json`"] if blocking_steps else None,
    )
    return emit(payload)


def handle_closeout_run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom closeout run")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--pr")
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES)
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
    parser.add_argument("--carrier-sync-pr", type=int)
    parser.add_argument("--final-closeout-pr", type=int)
    parser.add_argument("--project")
    parser.add_argument("--phase")
    parser.add_argument("--fr")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--comment")
    parser.add_argument("--comment-file")
    parser.add_argument("--goal-completion")
    parser.add_argument("--gate-profile", choices=("auto", "closeout-contract", "source-self-fixture", "bootstrap-regression", "distribution-regression", "strong-profile-full-gate"))
    parser.add_argument("--issue-payload-file")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--project-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    add_legacy_carrier_compatibility_args(parser)
    args = parser.parse_args(argv)
    if closeout_current_pr_input(args) is None:
        parser.error("--pr or one closeout PR role flag is required")

    target = resolve_target(args.target)
    compatibility = legacy_carrier_compatibility(args)
    if compatibility["result"] != "pass":
        return emit(
            agent_safe_payload(
                output(
                    "closeout run",
                    "block",
                    schema_version="loom-legacy-carrier-command/v1",
                    summary=compatibility["summary"],
                    mutates=False,
                    target=str(target),
                    compatibility=compatibility,
                    missing_inputs=compatibility["missing_inputs"],
                    fallback_to="loom attestation closeout --repo <owner/repo> --pr <n> --work-item <n> --artifact-input <file> --json",
                ),
                target_root=target,
            )
        )
    return emit(run_closeout_payload(args, target))


def supported_hosts(target: Path) -> list[dict[str, Any]]:
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    codex_paths = codex_workstation_paths(home=home, codex_home=codex_home)
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    hosts = [
        {
            "id": "codex",
            "support_status": "primary",
            "detected": codex_home.exists(),
            "default_scope": "user",
            "provider": "codex-user-plugin",
            "workstation_plugin_cache_path": str(codex_paths["plugin_cache_path"]),
            "workstation_marketplace_path": str(codex_paths["marketplace_path"]),
            "workstation_config_path": str(codex_paths["config_path"]),
        },
        {
            "id": "claude",
            "support_status": "adapter",
            "detected": claude_home.exists(),
            "provider": "unsupported-for-install",
        },
        {"id": "opencode", "support_status": "adapter-contract", "detected": False, "provider": "unsupported-for-install"},
        {"id": "gemini", "support_status": "adapter-contract", "detected": False, "provider": "unsupported-for-install"},
        {"id": "cursor", "support_status": "adapter-contract", "detected": False, "provider": "unsupported-for-install"},
    ]
    return hosts


def workstation_registry_path() -> Path:
    return Path.home().expanduser().resolve() / ".loom" / "repositories.json"


def empty_workstation_registry(path: Path) -> dict[str, Any]:
    return {
        "schema_version": WORKSTATION_REPOSITORIES_SCHEMA,
        "authority": "workstation",
        "registry_path": "~/.loom/repositories.json",
        "updated_at": now_iso(),
        "repositories": [],
    }


def load_workstation_registry(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return empty_workstation_registry(path), None
    try:
        registry = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"workstation registry is unreadable: {exc}"
    if not isinstance(registry, dict):
        return None, "workstation registry must be a JSON object"
    if registry.get("schema_version") != WORKSTATION_REPOSITORIES_SCHEMA:
        return None, f"expected schema_version {WORKSTATION_REPOSITORIES_SCHEMA}"
    if registry.get("authority") != "workstation":
        return None, "workstation registry authority must be workstation"
    if not isinstance(registry.get("repositories"), list):
        return None, "workstation registry repositories must be an array"
    registry.setdefault("registry_path", "~/.loom/repositories.json")
    registry.setdefault("updated_at", now_iso())
    return registry, None


def workstation_registry_block(command: str, path: Path, reason: str) -> dict[str, Any]:
    return output(
        command,
        "block",
        schema=WORKSTATION_CONTROL_SCHEMA,
        summary="Workstation repository registry cannot be trusted.",
        registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
        registry_path=str(path),
        mutates=False,
        failed_layer="workstation-registry",
        fail_closed_reason=reason,
        fallback_to=["repair or remove ~/.loom/repositories.json", "loom workstation list --json"],
    )


def workstation_registry_classification_guidance(classification: str) -> list[str]:
    guidance = {
        "path_missing": ["loom workstation unregister --target <repo> --json", "loom workstation register --target <repo> --json"],
        "remote_hash_drift": ["confirm the repository identity", "loom workstation register --target <repo> --json"],
        "repo_id_conflict": ["manually repair ~/.loom/repositories.json", "loom workstation list --json"],
        "schema_unsupported": ["repair or remove ~/.loom/repositories.json", "loom workstation list --json"],
    }
    return guidance.get(classification, ["loom workstation list --json"])


def canonical_git_remote(target: Path) -> str:
    completed = run_readback_command(["git", "config", "--get", "remote.origin.url"], cwd=target)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def remote_hash(canonical_url: str) -> str | None:
    if not canonical_url:
        return None
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def workstation_repo_id(target: Path, remote_hash_value: str | None) -> str:
    identity = f"{target.resolve()}\0{remote_hash_value or 'missing'}"
    return "repo_" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def workstation_repo_state_dir(target: Path) -> Path:
    canonical_url = canonical_git_remote(target)
    return Path.home().expanduser().resolve() / ".loom" / "repos" / workstation_repo_id(target, remote_hash(canonical_url))


def workstation_current_path(target: Path) -> Path:
    return workstation_repo_state_dir(target) / "current.json"


def read_workstation_current(target: Path) -> dict[str, Any]:
    path = workstation_current_path(target)
    if not path.exists():
        return {
            "schema_version": WORKSTATION_CURRENT_SCHEMA,
            "authority": "workstation",
            "state": "no_active_item",
            "current_item_id": None,
            "path": "~/.loom/repos/<repo-id>/current.json",
        }
    try:
        payload = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "schema_version": WORKSTATION_CURRENT_SCHEMA,
            "authority": "workstation",
            "state": "unreadable",
            "current_item_id": None,
            "path": str(path),
            "error": str(exc),
        }
    if not isinstance(payload, dict):
        return {
            "schema_version": WORKSTATION_CURRENT_SCHEMA,
            "authority": "workstation",
            "state": "invalid",
            "current_item_id": None,
            "path": str(path),
        }
    payload.setdefault("schema_version", WORKSTATION_CURRENT_SCHEMA)
    payload.setdefault("authority", "workstation")
    payload.setdefault("path", str(path))
    return payload


def workstation_current_payload(
    target: Path,
    *,
    item: str | None,
    issue: str | None,
    pr: str | None,
    branch: str | None,
    clear: bool,
) -> dict[str, Any]:
    path = workstation_current_path(target)
    now = now_iso()
    canonical_url = canonical_git_remote(target)
    hash_value = remote_hash(canonical_url)
    repo_id = workstation_repo_id(target, hash_value)
    state = "no_active_item" if clear else "active"
    return {
        "schema_version": WORKSTATION_CURRENT_SCHEMA,
        "authority": "workstation",
        "repo_id": repo_id,
        "target": str(target.resolve()),
        "remote_hash": hash_value,
        "state": state,
        "current_item_id": None if clear else item,
        "issue": None if clear else issue,
        "pr": None if clear else pr,
        "branch": None if clear else branch,
        "updated_at": now,
        "updated_by": "loom workstation current",
        "path": str(path),
    }


def write_workstation_current(target: Path, payload: dict[str, Any]) -> Path:
    path = workstation_current_path(target)
    write_json(path, payload)
    return path


def workstation_adoption_snapshot(target: Path) -> dict[str, Any]:
    path = installed_state_path(target)
    if path is None:
        return {
            "mode": "unknown",
            "installed_state_schema": None,
            "last_seen_version": None,
        }
    try:
        state = read_json(path)
    except (OSError, json.JSONDecodeError):
        return {
            "mode": "unknown",
            "installed_state_schema": None,
            "last_seen_version": None,
        }
    if not isinstance(state, dict):
        return {
            "mode": "unknown",
            "installed_state_schema": None,
            "last_seen_version": None,
        }
    repo_payload = state.get("repo_payload") if isinstance(state.get("repo_payload"), dict) else {}
    mode = (repo_payload.get("adoption_mode") or repo_payload.get("mode")) if isinstance(repo_payload, dict) else "unknown"
    if not isinstance(mode, str):
        mode = "unknown"
    if mode not in {"light-governance", "execution-control", "strong-governance", "attach-only", "metadata-only", "repo-local-wrapper", "legacy-embedded", "unknown"}:
        mode = "unknown"
    version_data = state.get("version_context") if isinstance(state.get("version_context"), dict) else {}
    contract = state.get("contract") if isinstance(state.get("contract"), dict) else {}
    last_seen_version = (
        contract.get("minimum_loom_version")
        or version_data.get("repo_version")
        or version_data.get("loom_version")
        or version_data.get("source_package_version")
        or version_data.get("version")
    )
    return {
        "mode": mode,
        "installed_state_schema": state.get("schema_version") if isinstance(state.get("schema_version"), str) else None,
        "last_seen_version": last_seen_version if isinstance(last_seen_version, str) else None,
    }


def workstation_registry_entry(target: Path, *, source: str) -> dict[str, Any]:
    observed_at = now_iso()
    canonical_url = canonical_git_remote(target)
    hash_value = remote_hash(canonical_url)
    return {
        "id": workstation_repo_id(target, hash_value),
        "path": str(target.resolve()),
        "path_state": "present" if target.exists() else "missing",
        "remote": {
            "canonical_url": canonical_url,
            "hash": hash_value,
            "observed_at": observed_at,
        },
        "adoption": workstation_adoption_snapshot(target),
        "opt_in": {
            "enabled": True,
            "source": source,
            "updated_at": observed_at,
        },
        "last_seen_at": observed_at,
    }


def workstation_registry_classifications(registry: dict[str, Any]) -> list[dict[str, Any]]:
    classifications: list[dict[str, Any]] = []
    repositories = registry.get("repositories")
    if not isinstance(repositories, list):
        return [
            {
                "classification": "schema_unsupported",
                "entry_id": None,
                "blocking": True,
                "repair_guidance": workstation_registry_classification_guidance("schema_unsupported"),
            }
        ]
    seen_ids: dict[str, tuple[str | None, str | None]] = {}
    for entry in repositories:
        if not isinstance(entry, dict):
            classifications.append(
                {
                    "classification": "schema_unsupported",
                    "entry_id": None,
                    "blocking": True,
                    "repair_guidance": workstation_registry_classification_guidance("schema_unsupported"),
                }
            )
            continue
        entry_id = entry.get("id")
        path_value = entry.get("path")
        remote = entry.get("remote") if isinstance(entry.get("remote"), dict) else {}
        stored_remote_hash = remote.get("hash")
        identity = (path_value, stored_remote_hash)
        if isinstance(entry_id, str):
            previous = seen_ids.get(entry_id)
            if previous is not None and previous != identity:
                classifications.append(
                    {
                        "classification": "repo_id_conflict",
                        "entry_id": entry_id,
                        "blocking": True,
                        "repair_guidance": workstation_registry_classification_guidance("repo_id_conflict"),
                    }
                )
            seen_ids[entry_id] = identity
        path_missing = entry.get("path_state") != "present"
        target_path: Path | None = None
        if isinstance(path_value, str) and path_value.startswith("/"):
            target_path = Path(path_value)
            if not target_path.exists():
                path_missing = True
        else:
            classifications.append(
                {
                    "classification": "schema_unsupported",
                    "entry_id": entry_id,
                    "blocking": True,
                    "repair_guidance": workstation_registry_classification_guidance("schema_unsupported"),
                }
            )
        if path_missing:
            classifications.append(
                {
                    "classification": "path_missing",
                    "entry_id": entry_id,
                    "blocking": True,
                    "path": path_value,
                    "repair_guidance": workstation_registry_classification_guidance("path_missing"),
                }
            )
        elif target_path is not None:
            observed_remote = canonical_git_remote(target_path)
            observed_remote_hash = remote_hash(observed_remote)
            if observed_remote_hash != stored_remote_hash:
                classifications.append(
                    {
                        "classification": "remote_hash_drift",
                        "entry_id": entry_id,
                        "blocking": True,
                        "path": path_value,
                        "stored_remote_hash": stored_remote_hash,
                        "observed_remote_hash": observed_remote_hash,
                        "repair_guidance": workstation_registry_classification_guidance("remote_hash_drift"),
                    }
                )
        opt_in = entry.get("opt_in") if isinstance(entry.get("opt_in"), dict) else {}
        if opt_in.get("enabled") is False:
            classifications.append({"classification": "opted_out", "entry_id": entry_id, "blocking": False})
    return classifications


def normalized_version(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    return text[1:] if text.startswith("v") else text


def workstation_upgrade_machine_plan(target_version: str) -> dict[str, Any]:
    freshness = version_freshness()
    freshness_action = version_freshness_action(freshness)
    cli_command = f"npm install -g @mc-and-his-agents/loom@{target_version}"
    plugin_commands = [
        command
        for command in freshness_action.get("apply_commands", [])
        if isinstance(command, str) and command != "npm install -g @mc-and-his-agents/loom@latest"
    ]
    if not plugin_commands:
        plugin_commands = [
            "loom host install --host codex --scope user --apply --json",
            "loom host register --host codex --scope user --apply --json",
        ]
    return {
        "schema": "loom-workstation-machine-upgrade-plan/v1",
        "classification": "machine_only",
        "target_version": target_version,
        "mutates": False,
        "freshness": freshness,
        "steps": [
            {
                "id": "upgrade-cli",
                "kind": "npm-cli",
                "command": cli_command,
                "required": freshness.get("action") in {"upgrade_cli", "check_cli_latest"},
                "mutates_when_applied": "global npm package",
            },
            {
                "id": "refresh-codex-plugin",
                "kind": "codex-user-plugin",
                "commands": plugin_commands,
                "marketplace_upgrade": {
                    "source": "MC-and-his-Agents/Loom",
                    "summary": "If Codex installed Loom from the Loom marketplace source, refresh through Codex marketplace update; otherwise use loom host install/register.",
                    "fallback_commands": [
                        "loom host install --host codex --scope user --apply --json",
                        "loom host register --host codex --scope user --apply --json",
                    ],
                },
                "required": freshness.get("action") == "upgrade_cli" or freshness.get("plugin_payload", {}).get("action") != "already_current",
                "mutates_when_applied": "user Codex marketplace/config/plugin cache",
            },
            {
                "id": "verify-host",
                "kind": "host-doctor",
                "command": "loom host doctor --host codex --scope user --json",
                "required": True,
                "mutates_when_applied": False,
            },
        ],
    }


def workstation_upgrade_freshness_cache_plan(target_version: str, repository_count: int) -> dict[str, Any]:
    return {
        "schema": "loom-workstation-upgrade-freshness-cache/v1",
        "scope": "single_invocation",
        "status": "primed",
        "read_count": 1,
        "reused_for_repository_count": repository_count,
        "cache_key": hashlib.sha256(
            json.dumps(
                {
                    "target_version": normalized_version(target_version),
                    "source_package": "@mc-and-his-agents/loom",
                    "host": "codex",
                    "plugin_source": str(global_codex_plugin_source()),
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest(),
        "invalidates_on": [
            "target_version_change",
            "source_package_version_change",
            "codex_plugin_payload_hash_change",
            "codex_marketplace_or_runtime_cache_change",
            "host_doctor_failure",
        ],
    }


def workstation_upgrade_repo_plan(entry: dict[str, Any], *, target_version: str, blocked: dict[Any, list[dict[str, Any]]]) -> dict[str, Any]:
    entry_id = entry.get("id")
    path_value = entry.get("path")
    adoption = entry.get("adoption") if isinstance(entry.get("adoption"), dict) else {}
    opt_in = entry.get("opt_in") if isinstance(entry.get("opt_in"), dict) else {}
    blocking = blocked.get(entry_id, [])
    base = {
        "entry_id": entry_id,
        "path": path_value,
        "adoption": adoption,
        "target_version": target_version,
        "mutates": False,
    }
    if opt_in.get("enabled") is False:
        return {
            **base,
            "classification": "repo_noop",
            "reason": "repository is opted out of workstation upgrade planning",
            "commands": [],
        }
    if blocking:
        return {
            **base,
            "classification": "blocked",
            "reason": "workstation registry entry has blocking identity or path drift",
            "blocking_classifications": blocking,
            "commands": [],
        }
    if not isinstance(path_value, str) or not path_value:
        return {
            **base,
            "classification": "blocked",
            "reason": "repository path is unavailable",
            "commands": [],
        }

    mode = adoption.get("mode") if isinstance(adoption.get("mode"), str) else "unknown"
    last_seen_version = adoption.get("last_seen_version") if isinstance(adoption.get("last_seen_version"), str) else None
    if mode == "metadata-only" and normalized_version(last_seen_version) == normalized_version(target_version):
        return {
            **base,
            "classification": "repo_noop",
            "reason": "metadata-only adoption is already at the requested target version",
            "commands": ["loom doctor --target <repo> --json"],
        }
    if mode == "metadata-only":
        return {
            **base,
            "classification": "repo_auto_commit_candidate",
            "reason": "metadata-only adoption can refresh repo-local adoption metadata with low risk",
            "commands": [
                f"loom install --target {path_value} --apply --json",
                f"loom doctor --target {path_value} --json",
            ],
        }
    if mode in {"repo-local-wrapper", "legacy-embedded"}:
        return {
            **base,
            "classification": "repo_pr_required",
            "reason": f"{mode} adoption may remove or rewrite tracked repository surfaces",
            "commands": [
                f"loom upgrade-plan --target {path_value} --json",
                f"open a repository-scoped PR for {path_value}",
            ],
        }
    return {
        **base,
        "classification": "blocked",
        "reason": "repository adoption mode is unknown",
        "commands": [f"loom doctor --target {path_value} --json"],
    }


def workstation_upgrade_plan_payload(
    *,
    command: str,
    registry_path: Path,
    registry: dict[str, Any],
    target_version: str,
) -> dict[str, Any]:
    repositories = [entry for entry in registry.get("repositories", []) if isinstance(entry, dict)]
    classifications = workstation_registry_classifications(registry)
    blocking_classifications = [item for item in classifications if item.get("blocking") is True]
    blocked_by_id: dict[Any, list[dict[str, Any]]] = {}
    for item in blocking_classifications:
        blocked_by_id.setdefault(item.get("entry_id"), []).append(item)
    plans = [
        workstation_upgrade_repo_plan(entry, target_version=target_version, blocked=blocked_by_id)
        for entry in repositories
    ]
    counts: dict[str, int] = {}
    for plan in plans:
        classification = str(plan.get("classification") or "blocked")
        counts[classification] = counts.get(classification, 0) + 1
    result = "block" if any(plan.get("classification") == "blocked" for plan in plans) else "pass"
    if not plans:
        summary = "Workstation upgrade plan contains machine-level refresh steps and no registered repositories."
    elif result == "pass":
        summary = "Workstation upgrade plan classified registered repositories without mutating state."
    else:
        summary = "Workstation upgrade plan found blocked repository entries; repair registry drift before applying repository changes."
    return output(
        command,
        result,
        schema=WORKSTATION_UPGRADE_PLAN_SCHEMA,
        summary=summary,
        target_version=target_version,
        plan_only=True,
        mutates=False,
        registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
        registry_path=str(registry_path),
        logical_registry_path=registry.get("registry_path"),
        machine_plan=workstation_upgrade_machine_plan(target_version),
        freshness_cache=workstation_upgrade_freshness_cache_plan(target_version, len(plans)),
        repository_plans=plans,
        repository_count=len(repositories),
        classification_counts=counts or {"machine_only": 1},
        classifications=classifications,
        failed_layer="workstation-registry" if result == "block" else None,
        fail_closed_reason=(
            "registry contains entries that are ambiguous for mutation planning"
            if result == "block"
            else None
        ),
        fallback_to=(
            sorted(
                {
                    guidance
                    for item in blocking_classifications
                    for guidance in item.get("repair_guidance", [])
                    if isinstance(guidance, str)
                }
            )
            if result == "block"
            else None
        ),
    )


def apply_workstation_shell_command(command: str) -> dict[str, Any]:
    if os.environ.get("LOOM_TEST_WORKSTATION_APPLY") == "record":
        return {
            "command": command,
            "result": "pass",
            "simulated": True,
        }
    completed = subprocess.run(
        shlex.split(command),
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "result": "pass" if completed.returncode == 0 else "block",
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def apply_workstation_machine_plan(machine_plan: dict[str, Any]) -> dict[str, Any]:
    applied_steps: list[dict[str, Any]] = []
    source = global_codex_plugin_source()
    for step in machine_plan.get("steps", []):
        if not isinstance(step, dict):
            continue
        step_id = step.get("id")
        if step.get("required") is not True and step_id != "verify-host":
            applied_steps.append({"id": step_id, "result": "skipped", "reason": "step is not required"})
            continue
        if step_id == "upgrade-cli":
            applied_steps.append({"id": step_id, **apply_workstation_shell_command(str(step.get("command") or ""))})
        elif step_id == "refresh-codex-plugin":
            writes = register_codex_workstation(source)
            applied_steps.append({"id": step_id, "result": "pass", "writes": writes})
        elif step_id == "verify-host":
            registration = codex_workstation_registration_status(source)
            applied_steps.append(
                {
                    "id": step_id,
                    "result": registration.get("result"),
                    "workstation_registration": registration,
                }
            )
        else:
            applied_steps.append({"id": step_id, "result": "skipped", "reason": "unsupported machine plan step"})
    blocking = [step for step in applied_steps if step.get("result") == "block"]
    return {
        "schema": "loom-workstation-machine-upgrade-apply/v1",
        "result": "block" if blocking else "pass",
        "mutates": True,
        "applied_steps": applied_steps,
    }


def apply_workstation_repository_plan(plan: dict[str, Any], *, target_version: str) -> dict[str, Any]:
    classification = plan.get("classification")
    path_value = plan.get("path")
    if classification == "repo_noop":
        return {
            "schema": "loom-workstation-repository-upgrade-apply/v1",
            "result": "pass",
            "classification": classification,
            "mutates": False,
            "reason": plan.get("reason"),
        }
    if classification != "repo_auto_commit_candidate":
        return {
            "schema": "loom-workstation-repository-upgrade-apply/v1",
            "result": "block",
            "classification": classification,
            "mutates": False,
            "failed_layer": "repository-adoption",
            "fail_closed_reason": "only repo_auto_commit_candidate supports explicit single-repository apply",
            "fallback_to": ["open a repository-scoped PR", "loom upgrade-plan --target <repo> --json"],
        }
    if not isinstance(path_value, str) or not path_value:
        return {
            "schema": "loom-workstation-repository-upgrade-apply/v1",
            "result": "block",
            "classification": classification,
            "mutates": False,
            "failed_layer": "repository-adoption",
            "fail_closed_reason": "repository path is unavailable",
            "fallback_to": ["loom workstation register --target <repo> --json"],
        }
    command = [sys.executable, str(Path(__file__).resolve()), "install", "--target", path_value, "--apply", "--json"]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()}
    return {
        "schema": "loom-workstation-repository-upgrade-apply/v1",
        "result": "pass" if completed.returncode == 0 else "block",
        "classification": classification,
        "target_version": target_version,
        "mutates": completed.returncode == 0,
        "command": "loom install --target <repo> --apply --json",
        "payload": payload,
        "failed_layer": None if completed.returncode == 0 else "repository-adoption",
        "fail_closed_reason": None if completed.returncode == 0 else "repo-local metadata refresh failed",
    }


def workstation_upgrade_apply_payload(
    *,
    command: str,
    registry_path: Path,
    registry: dict[str, Any],
    target_version: str,
    target: Path | None,
) -> dict[str, Any]:
    plan = workstation_upgrade_plan_payload(
        command=command,
        registry_path=registry_path,
        registry=registry,
        target_version=target_version,
    )
    machine_apply = apply_workstation_machine_plan(plan.get("machine_plan", {}))
    repository_apply = None
    if target is not None:
        target_path = str(target.resolve())
        matches = [
            repo_plan
            for repo_plan in plan.get("repository_plans", [])
            if isinstance(repo_plan, dict) and repo_plan.get("path") == target_path
        ]
        if len(matches) != 1:
            repository_apply = {
                "schema": "loom-workstation-repository-upgrade-apply/v1",
                "result": "block",
                "mutates": False,
                "failed_layer": "workstation-registry",
                "fail_closed_reason": "explicit repository apply requires exactly one registered target match",
                "fallback_to": ["loom workstation register --target <repo> --json"],
            }
        else:
            repository_apply = apply_workstation_repository_plan(matches[0], target_version=target_version)
    blocking = [machine_apply.get("result") == "block", repository_apply is not None and repository_apply.get("result") == "block"]
    return output(
        command,
        "block" if any(blocking) else "pass",
        schema=WORKSTATION_UPGRADE_PLAN_SCHEMA,
        summary=(
            "Workstation upgrade apply completed."
            if not any(blocking)
            else "Workstation upgrade apply blocked before all requested writes completed."
        ),
        target_version=target_version,
        plan_only=False,
        mutates=True,
        registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
        registry_path=str(registry_path),
        logical_registry_path=registry.get("registry_path"),
        machine_plan=plan.get("machine_plan"),
        freshness_cache=plan.get("freshness_cache"),
        repository_plans=plan.get("repository_plans"),
        repository_count=plan.get("repository_count"),
        classification_counts=plan.get("classification_counts"),
        classifications=plan.get("classifications"),
        machine_apply=machine_apply,
        repository_apply=repository_apply,
        failed_layer=(
            "workstation-machine-refresh"
            if machine_apply.get("result") == "block"
            else "repository-adoption"
            if repository_apply is not None and repository_apply.get("result") == "block"
            else None
        ),
        fail_closed_reason=(
            "machine-level workstation refresh failed"
            if machine_apply.get("result") == "block"
            else repository_apply.get("fail_closed_reason")
            if repository_apply is not None and repository_apply.get("result") == "block"
            else None
        ),
        fallback_to=(
            repository_apply.get("fallback_to")
            if repository_apply is not None and repository_apply.get("result") == "block"
            else None
        ),
    )


LEGACY_RESIDUE_LOCATORS = (
    ".loom/bin",
    "plugins/loom",
    ".agents/skills",
    ".agents/plugins/marketplace.json",
)
REPO_LOCAL_CACHE_LOCATORS = (".loom/runtime", ".loom/tmp")
REPO_SLIMDOWN_LOCATOR_RULES = (
    (".loom/installed-state.json", "installed-state", "retain_repo_truth", "retain the minimal repository adoption truth"),
    (".loom/companion", "repo-companion", "retain_repo_truth", "retain repo-owned host adapter and interop locators"),
    (".loom/runtime", "runtime-cache", "move_to_global_cache", "move ignored or untracked runtime cache to the workstation global cache"),
    (".loom/tmp", "runtime-cache", "move_to_global_cache", "move ignored or untracked temporary output to the workstation global cache"),
    (".loom/bin", "runtime-payload", "repo_pr_required", "remove repo-local runtime payload only through a repository-scoped migration PR"),
    (".loom/bootstrap", "legacy-bootstrap-carrier", "repo_pr_required", "archive or replace legacy bootstrap carriers after installed-state is authoritative"),
    (".loom/status", "current-pointer", "repo_pr_required", "move active current pointer state to workstation current.json"),
    (".loom/work-items", "execution-carrier", "repo_pr_required", "move ordinary Work Item history to host issues or an archive"),
    (".loom/progress", "execution-carrier", "repo_pr_required", "move ordinary progress history to host comments or an archive"),
    (".loom/specs", "execution-carrier", "repo_pr_required", "move ordinary specs to host-linked archive when no longer repo truth"),
    (".loom/reviews", "execution-carrier", "repo_pr_required", "move ordinary review records to host comments or an audit archive"),
    (".loom/shadow", "shadow-evidence", "repo_pr_required", "move shadow/runtime evidence to global cache or an audit archive"),
    ("plugins/loom", "plugin-payload", "repo_pr_required", "remove repo-local Loom plugin payload after user-level plugin provider is verified"),
    (".agents/skills", "skills-payload", "repo_pr_required", "remove repo-local generated skills after user-level plugin provider is verified"),
    (".agents/plugins/marketplace.json", "plugin-marketplace-state", "repo_pr_required", "remove repo-local installed marketplace state after workstation provider is verified"),
)
INSTALLED_STATE_WORKSTATION_FIELDS = (
    "target",
    "installed_at",
    "upgraded_at",
    "cli_freshness",
    "plugin_freshness",
    "plugin_cache_path",
    "host_machine_path",
)


def git_list_files(target: Path, locator: str, *, others: bool = False, ignored: bool = False) -> list[str]:
    args = ["git", "ls-files"]
    if others:
        args.extend(["--others", "--exclude-standard"])
    if ignored:
        args.extend(["--ignored", "--others", "--exclude-standard"])
    args.extend(["--", locator])
    completed = run_readback_command(args, cwd=target)
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def git_is_ignored(target: Path, locator: str) -> bool:
    completed = run_readback_command(["git", "check-ignore", "-q", "--", locator], cwd=target)
    return completed.returncode == 0


def path_sample(entries: list[str], limit: int = 25) -> dict[str, Any]:
    return {
        "count": len(entries),
        "sample": entries[:limit],
        "truncated": len(entries) > limit,
    }


def installed_state_readback(target: Path) -> dict[str, Any]:
    path = installed_state_path(target)
    if path is None:
        return {
            "status": "missing",
            "locator": ".loom/installed-state.json",
            "valid": False,
            "blocking": True,
            "reason": "installed-state is missing",
        }
    try:
        payload = read_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "malformed",
            "locator": ".loom/installed-state.json",
            "valid": False,
            "blocking": True,
            "reason": f"installed-state is unreadable: {exc}",
        }
    if not isinstance(payload, dict) or payload.get("schema_version") != INSTALLED_STATE_SCHEMA:
        return {
            "status": "unsupported",
            "locator": ".loom/installed-state.json",
            "valid": False,
            "blocking": True,
            "reason": f"expected {INSTALLED_STATE_SCHEMA}",
        }
    repo_payload = payload.get("repo_payload") if isinstance(payload.get("repo_payload"), dict) else {}
    slimdown = installed_state_slimdown_analysis(payload)
    return {
        "status": "present",
        "locator": ".loom/installed-state.json",
        "valid": True,
        "blocking": False,
        "schema_version": payload.get("schema_version"),
        "repo_payload_mode": repo_payload.get("mode"),
        "version_context": payload.get("version_context") if isinstance(payload.get("version_context"), dict) else {},
        "slimdown": slimdown,
    }


def installed_state_slimdown_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    repo_payload = payload.get("repo_payload") if isinstance(payload.get("repo_payload"), dict) else {}
    contract = payload.get("contract") if isinstance(payload.get("contract"), dict) else {}
    companion = payload.get("repo_companion") if isinstance(payload.get("repo_companion"), dict) else {}
    workstation_fields = [field for field in INSTALLED_STATE_WORKSTATION_FIELDS if field in payload]
    missing_repo_truth: list[str] = []
    if repo_payload.get("mode") != "metadata-only":
        missing_repo_truth.append("repo_payload.mode=metadata-only")
    if not isinstance(repo_payload.get("adoption_mode"), str) or not repo_payload.get("adoption_mode"):
        missing_repo_truth.append("repo_payload.adoption_mode")
    if not isinstance(contract.get("minimum_loom_version"), str) or not contract.get("minimum_loom_version"):
        missing_repo_truth.append("contract.minimum_loom_version")
    locator_keys = ("repo_interface_locator", "repo_interop_locator", "companion_locator", "interop_locator")
    declared_locators = {
        key: value
        for key, value in companion.items()
        if key in locator_keys and isinstance(value, str) and value
    }
    update_required = bool(workstation_fields or missing_repo_truth)
    return {
        "schema_version": "loom-installed-state-slimdown/v1",
        "classification": "pr_required" if update_required else "current",
        "summary": (
            "installed-state contains workstation-local or missing minimal repo truth fields"
            if update_required
            else "installed-state already carries only repository adoption truth required by this migration check"
        ),
        "retain_fields": [
            "schema_version",
            "repo_payload.mode",
            "repo_payload.adoption_mode",
            "contract.minimum_loom_version",
            "skills_provider",
            "provider_requirements",
            "repo companion/interop locators when declared",
        ],
        "remove_workstation_fields": workstation_fields,
        "missing_repo_truth": missing_repo_truth,
        "declared_repo_locators": declared_locators,
        "mutates": False,
        "apply_action": "repo_pr_required" if update_required else "none",
    }


def migration_cache_entry(target: Path, locator: str) -> dict[str, Any]:
    path = target / locator
    tracked = git_list_files(target, locator)
    ignored_entries = git_list_files(target, locator, ignored=True)
    untracked_entries = git_list_files(target, locator, others=True)
    exists = path.exists()
    movable = exists and not tracked
    blocking = bool(tracked)
    if path.is_file() or path.is_symlink():
        file_count = 1
    elif path.is_dir():
        file_count = sum(1 for child in path.rglob("*") if child.is_file() or child.is_symlink())
    else:
        file_count = 0
    return {
        "locator": locator,
        "exists": exists,
        "tracked_entries": path_sample(tracked),
        "untracked_entries": path_sample(untracked_entries),
        "ignored_entries": path_sample(ignored_entries),
        "ignored": git_is_ignored(target, locator) or bool(ignored_entries),
        "file_count": file_count,
        "movable": movable,
        "blocking": blocking,
        "classification": "tracked_cache_blocked" if blocking else "movable_cache" if movable else "absent",
        "global_locator": f"~/.loom/repos/<repo-id>/{locator.removeprefix('.loom/')}" if exists else None,
    }


def repo_slimdown_entry(target: Path, locator: str, kind: str, disposition: str, reason: str) -> dict[str, Any]:
    path = target / locator
    tracked = git_list_files(target, locator)
    ignored_entries = git_list_files(target, locator, ignored=True)
    untracked_entries = git_list_files(target, locator, others=True)
    exists = path.exists()
    if path.is_file() or path.is_symlink():
        file_count = 1
    elif path.is_dir():
        file_count = sum(1 for child in path.rglob("*") if child.is_file() or child.is_symlink())
    else:
        file_count = 0
    if not exists:
        strategy = "no_op"
        classification = "absent"
    elif disposition == "retain_repo_truth":
        strategy = "no_op"
        classification = "retained_repo_truth"
    elif disposition == "move_to_global_cache" and not tracked:
        strategy = "auto_commit_candidate"
        classification = "global_cache_candidate"
    elif tracked:
        strategy = "pr_required"
        classification = "tracked_repo_residue"
    else:
        strategy = "auto_commit_candidate"
        classification = "untracked_repo_residue"
    return {
        "locator": locator,
        "kind": kind,
        "exists": exists,
        "file_count": file_count,
        "tracked_entries": path_sample(tracked),
        "untracked_entries": path_sample(untracked_entries),
        "ignored_entries": path_sample(ignored_entries),
        "classification": classification,
        "recommended_disposition": disposition,
        "strategy": strategy,
        "reason": reason,
        "global_locator": f"~/.loom/repos/<repo-id>/{locator.removeprefix('.loom/')}" if exists and disposition == "move_to_global_cache" else None,
        "mutated_by_apply": disposition == "move_to_global_cache" and strategy == "auto_commit_candidate",
    }


def legacy_residue_entry(target: Path, locator: str) -> dict[str, Any]:
    path = target / locator
    tracked = git_list_files(target, locator)
    ignored_entries = git_list_files(target, locator, ignored=True)
    untracked_entries = git_list_files(target, locator, others=True)
    exists = path.exists()
    if tracked:
        classification = "tracked_legacy_residue"
        strategy = "pr_required"
    elif exists:
        classification = "untracked_legacy_residue"
        strategy = "auto_commit_candidate"
    else:
        classification = "absent"
        strategy = "no_op"
    return {
        "locator": locator,
        "exists": exists,
        "tracked_entries": path_sample(tracked),
        "untracked_entries": path_sample(untracked_entries),
        "ignored_entries": path_sample(ignored_entries),
        "classification": classification,
        "ownership": "tracked_repo_payload" if tracked else "untracked_or_ignored_residue" if exists else "absent",
        "strategy": strategy,
        "blocking": False,
        "apply_action": "diagnose_only" if tracked else "leave_in_place" if exists else "none",
    }


def repo_slimdown_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(entry.get("strategy")) for entry in entries)
    retained = [
        {"locator": entry.get("locator"), "reason": entry.get("reason")}
        for entry in entries
        if entry.get("classification") == "retained_repo_truth" and entry.get("exists")
    ]
    pr_required = [
        entry.get("locator")
        for entry in entries
        if entry.get("strategy") == "pr_required"
    ]
    return {
        "schema_version": "loom-repo-slimdown-summary/v1",
        "strategy_counts": dict(sorted(counts.items())),
        "retained_repo_truth": retained,
        "pr_required_locators": pr_required,
        "target_default_loom_file_goal": "<10",
        "mutates": False,
    }


def migration_strategy(
    installed_state: dict[str, Any],
    cache_entries: list[dict[str, Any]],
    residue_entries: list[dict[str, Any]],
    slimdown_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    if installed_state.get("blocking"):
        blocking_reasons.append(str(installed_state.get("reason") or "installed-state is not valid"))
    for entry in cache_entries:
        if entry.get("blocking"):
            blocking_reasons.append(f"{entry.get('locator')} contains tracked cache entries")
    if blocking_reasons:
        return {
            "classification": "blocked",
            "display": "blocked",
            "reason": "; ".join(blocking_reasons),
            "requires_pr": False,
            "apply_allowed": False,
        }
    slimdown_pr_required = [entry for entry in slimdown_entries if entry.get("strategy") == "pr_required"]
    installed_state_slimdown = installed_state.get("slimdown") if isinstance(installed_state.get("slimdown"), dict) else {}
    if any((entry.get("tracked_entries") or {}).get("count") for entry in residue_entries) or slimdown_pr_required or installed_state_slimdown.get("classification") == "pr_required":
        return {
            "classification": "pr_required",
            "display": "PR required",
            "reason": "tracked legacy residue or installed-state slimdown requires repository-scoped review before deletion or rewrite",
            "requires_pr": True,
            "apply_allowed": False,
        }
    if (
        any(entry.get("movable") for entry in cache_entries)
        or any(entry.get("exists") for entry in residue_entries)
        or any(entry.get("strategy") == "auto_commit_candidate" for entry in slimdown_entries)
    ):
        return {
            "classification": "auto_commit_candidate",
            "display": "auto-commit candidate",
            "reason": "only untracked or ignored Loom cache/residue was detected",
            "requires_pr": False,
            "apply_allowed": True,
        }
    return {
        "classification": "no_op",
        "display": "no-op",
        "reason": "no repo-local Loom cache or legacy residue was detected",
        "requires_pr": False,
        "apply_allowed": True,
    }


def migration_plan_payload(command: str, target: Path) -> dict[str, Any]:
    if not target.exists():
        return output(
            command,
            "block",
            schema=GLOBAL_CACHE_MIGRATION_SCHEMA,
            summary="Legacy migration target does not exist.",
            target=str(target),
            plan_only=True,
            mutates=False,
            failed_layer="target",
            fail_closed_reason="target path does not exist",
            fallback_to=["loom migrate-global-cache plan --target <repo> --json"],
        )
    installed_state = installed_state_readback(target)
    cache_entries = [migration_cache_entry(target, locator) for locator in REPO_LOCAL_CACHE_LOCATORS]
    residue_entries = [legacy_residue_entry(target, locator) for locator in LEGACY_RESIDUE_LOCATORS]
    slimdown_entries = [
        repo_slimdown_entry(target, locator, kind, disposition, reason)
        for locator, kind, disposition, reason in REPO_SLIMDOWN_LOCATOR_RULES
    ]
    slimdown = repo_slimdown_summary(slimdown_entries)
    strategy = migration_strategy(installed_state, cache_entries, residue_entries, slimdown_entries)
    return output(
        command,
        "block" if strategy["classification"] == "blocked" else "pass",
        schema=GLOBAL_CACHE_MIGRATION_SCHEMA,
        summary=(
            "Legacy global cache migration plan is blocked."
            if strategy["classification"] == "blocked"
            else "Legacy global cache migration plan generated without mutating state."
        ),
        target=str(target),
        plan_only=True,
        mutates=False,
        installed_state=installed_state,
        cache_entries=cache_entries,
        legacy_residue=residue_entries,
        repo_slimdown=slimdown,
        repo_slimdown_entries=slimdown_entries,
        repo_change_strategy=strategy,
        strategy=strategy["classification"],
        strategy_display=strategy["display"],
        validation_package=None,
        failed_layer="legacy-migration" if strategy["classification"] == "blocked" else None,
        fail_closed_reason=strategy["reason"] if strategy["classification"] == "blocked" else None,
        fallback_to=(
            ["repair installed-state", "open a repository-scoped PR for tracked cache entries"]
            if strategy["classification"] == "blocked"
            else None
        ),
    )


def move_cache_file_to_global(target: Path, source: Path) -> dict[str, Any]:
    relative = source.relative_to(target).as_posix()
    destination = global_runtime_path(target, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    shutil.move(str(source), str(destination))
    return {
        "source": relative,
        "global_path": str(destination),
        "global_locator": relative,
        "sha256": sha256_path(destination) if destination.is_file() else None,
    }


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prune_empty_directories(root: Path) -> None:
    if not root.exists():
        return
    directories = [path for path in root.rglob("*") if path.is_dir()]
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass


def apply_global_cache_moves(target: Path, cache_entries: list[dict[str, Any]]) -> dict[str, Any]:
    moved: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for entry in cache_entries:
        locator = entry.get("locator")
        if not isinstance(locator, str) or not entry.get("exists"):
            skipped.append({"locator": locator, "reason": "absent"})
            continue
        if (entry.get("tracked_entries") or {}).get("count"):
            return {
                "result": "block",
                "moved": moved,
                "skipped": skipped,
                "failed_layer": "legacy-cache",
                "fail_closed_reason": f"{locator} contains tracked entries",
            }
        root = target / locator
        if root.is_file() or root.is_symlink():
            moved.append(move_cache_file_to_global(target, root))
            continue
        if not root.is_dir():
            skipped.append({"locator": locator, "reason": "not a regular file or directory"})
            continue
        files = [path for path in root.rglob("*") if path.is_file() or path.is_symlink()]
        for path in files:
            moved.append(move_cache_file_to_global(target, path))
        prune_empty_directories(root)
    return {
        "result": "pass",
        "moved": moved,
        "skipped": skipped,
        "failed_layer": None,
        "fail_closed_reason": None,
    }


def register_migrated_repository(target: Path) -> dict[str, Any]:
    path = workstation_registry_path()
    registry, error = load_workstation_registry(path)
    if error or registry is None:
        return {
            "result": "block",
            "registry_path": str(path),
            "failed_layer": "workstation-registry",
            "fail_closed_reason": error or "workstation registry is unavailable",
        }
    raw_repositories = registry.get("repositories", [])
    if not all(isinstance(entry, dict) for entry in raw_repositories):
        return {
            "result": "block",
            "registry_path": str(path),
            "failed_layer": "workstation-registry",
            "fail_closed_reason": "repository entries must be JSON objects before mutation",
        }
    blocking = [
        item for item in workstation_registry_classifications(registry) if item.get("blocking") is True
    ]
    if blocking:
        return {
            "result": "block",
            "registry_path": str(path),
            "failed_layer": "workstation-registry",
            "fail_closed_reason": "registry contains blocking identity or path drift",
            "classifications": blocking,
        }
    repositories = [entry for entry in raw_repositories if isinstance(entry, dict)]
    entry = workstation_registry_entry(target, source="loom migrate-global-cache apply")
    retained = [
        existing
        for existing in repositories
        if existing.get("id") != entry["id"] and existing.get("path") != entry["path"]
    ]
    retained.append(entry)
    registry["repositories"] = sorted(retained, key=lambda item: str(item.get("path", "")))
    registry["updated_at"] = now_iso()
    write_json(path, registry)
    return {
        "result": "pass",
        "registry_path": str(path),
        "repository": entry,
        "repository_count": len(registry["repositories"]),
        "writes": [str(path)],
    }


def run_json_command_step(step_id: str, command: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        payload: Any = json.loads(completed.stdout) if completed.stdout.strip() else None
    except json.JSONDecodeError:
        payload = None
    return {
        "id": step_id,
        "command": " ".join(shlex.quote(part) for part in command),
        "result": "pass" if completed.returncode == 0 else "block",
        "returncode": completed.returncode,
        "payload_result": payload.get("result") if isinstance(payload, dict) else None,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest() if completed.stdout else None,
        "stderr": completed.stderr.strip(),
    }


def migration_validation_package(target: Path) -> dict[str, Any]:
    loom = [sys.executable, str(Path(__file__).resolve())]
    steps = [
        run_json_command_step("installed-state-validate", [*loom, "installed-state", "validate", "--target", str(target), "--json"], cwd=REPO_ROOT),
        run_json_command_step("host-verify", [*loom, "host", "verify", "--host", "codex", "--scope", "user", "--target", str(target), "--json"], cwd=REPO_ROOT),
        run_json_command_step("skills-check", [*loom, "skills", "check", "--target", str(target), "--json"], cwd=REPO_ROOT),
        run_json_command_step("doctor", [*loom, "doctor", "--target", str(target), "--json"], cwd=REPO_ROOT),
    ]
    git_status = run_readback_command(["git", "status", "--short"], cwd=target)
    git_step = {
        "id": "git-status",
        "command": "git status --short",
        "result": "pass" if git_status.returncode == 0 else "block",
        "returncode": git_status.returncode,
        "porcelain": git_status.stdout.splitlines(),
        "stderr": git_status.stderr.strip(),
    }
    steps.append(git_step)
    blocking = [step for step in steps if step.get("result") != "pass"]
    return {
        "schema": "loom-legacy-migration-validation-package/v1",
        "result": "block" if blocking else "pass",
        "steps": steps,
        "blocking_step_ids": [str(step.get("id")) for step in blocking],
    }


def migration_apply_payload(command: str, target: Path) -> dict[str, Any]:
    plan = migration_plan_payload(command, target)
    strategy = plan.get("repo_change_strategy") if isinstance(plan.get("repo_change_strategy"), dict) else {}
    if plan.get("result") == "block":
        return {**plan, "plan_only": False, "mutates": False}
    if strategy.get("classification") == "pr_required":
        return output(
            command,
            "block",
            schema=GLOBAL_CACHE_MIGRATION_SCHEMA,
            summary="Legacy migration apply stopped before tracked repository payload changes.",
            target=str(target),
            plan_only=False,
            mutates=False,
            installed_state=plan.get("installed_state"),
            cache_entries=plan.get("cache_entries"),
            legacy_residue=plan.get("legacy_residue"),
            repo_slimdown=plan.get("repo_slimdown"),
            repo_slimdown_entries=plan.get("repo_slimdown_entries"),
            repo_change_strategy=strategy,
            strategy=strategy.get("classification"),
            strategy_display=strategy.get("display"),
            failed_layer="legacy-residue",
            fail_closed_reason=strategy.get("reason"),
            fallback_to=["open a repository-scoped PR for tracked legacy residue"],
        )
    cache_entries = [entry for entry in plan.get("cache_entries", []) if isinstance(entry, dict)]
    cache_apply = apply_global_cache_moves(target, cache_entries)
    registry_apply = register_migrated_repository(target) if cache_apply.get("result") == "pass" else None
    validation = (
        migration_validation_package(target)
        if cache_apply.get("result") == "pass" and isinstance(registry_apply, dict) and registry_apply.get("result") == "pass"
        else None
    )
    blocking = [
        cache_apply.get("result") == "block",
        isinstance(registry_apply, dict) and registry_apply.get("result") == "block",
        isinstance(validation, dict) and validation.get("result") == "block",
    ]
    return output(
        command,
        "block" if any(blocking) else "pass",
        schema=GLOBAL_CACHE_MIGRATION_SCHEMA,
        summary=(
            "Legacy global cache migration apply completed."
            if not any(blocking)
            else "Legacy global cache migration apply blocked before all validation passed."
        ),
        target=str(target),
        plan_only=False,
        mutates=bool(cache_apply.get("moved") or (isinstance(registry_apply, dict) and registry_apply.get("writes"))),
        installed_state=plan.get("installed_state"),
        cache_entries=cache_entries,
        legacy_residue=plan.get("legacy_residue"),
        repo_slimdown=plan.get("repo_slimdown"),
        repo_slimdown_entries=plan.get("repo_slimdown_entries"),
        repo_change_strategy=strategy,
        strategy=strategy.get("classification"),
        strategy_display=strategy.get("display"),
        cache_apply=cache_apply,
        registry_apply=registry_apply,
        validation_package=validation,
        failed_layer=(
            cache_apply.get("failed_layer")
            if cache_apply.get("result") == "block"
            else registry_apply.get("failed_layer")
            if isinstance(registry_apply, dict) and registry_apply.get("result") == "block"
            else "legacy-migration-validation"
            if isinstance(validation, dict) and validation.get("result") == "block"
            else None
        ),
        fail_closed_reason=(
            cache_apply.get("fail_closed_reason")
            if cache_apply.get("result") == "block"
            else registry_apply.get("fail_closed_reason")
            if isinstance(registry_apply, dict) and registry_apply.get("result") == "block"
            else "post-migration validation package failed"
            if isinstance(validation, dict) and validation.get("result") == "block"
            else None
        ),
        fallback_to=(
            ["repair validation package findings and rerun loom migrate-global-cache plan --json"]
            if any(blocking)
            else None
        ),
    )


def handle_migrate_global_cache(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom migrate-global-cache")
    parser.add_argument("action", choices=("plan", "apply"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"migrate-global-cache {args.action}"
    target = resolve_target(args.target)
    if args.action == "plan":
        return emit(migration_plan_payload(command, target))
    return emit(migration_apply_payload(command, target))


def handle_workstation(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom workstation")
    parser.add_argument("action", choices=("register", "list", "unregister", "upgrade", "current"))
    parser.add_argument("--target")
    parser.add_argument("--id")
    parser.add_argument("--item")
    parser.add_argument("--issue")
    parser.add_argument("--pr")
    parser.add_argument("--branch")
    parser.add_argument("--clear", action="store_true")
    parser.add_argument("--keep-entry", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--to", dest="target_version")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    command = f"workstation {args.action}"
    if args.action == "upgrade":
        command = "workstation upgrade"
        if args.plan == args.apply:
            parser.error("workstation upgrade requires exactly one of --plan or --apply")
        if not args.target_version:
            parser.error("workstation upgrade requires --to <version>")
    registry_path = workstation_registry_path()
    registry, error = load_workstation_registry(registry_path)
    if error or registry is None:
        return emit(workstation_registry_block(command, registry_path, error or "workstation registry is unavailable"))

    if args.action == "upgrade":
        if args.apply:
            explicit_target = resolve_target(args.target) if args.target else None
            return emit(
                workstation_upgrade_apply_payload(
                    command=command,
                    registry_path=registry_path,
                    registry=registry,
                    target_version=args.target_version,
                    target=explicit_target,
                )
            )
        return emit(
            workstation_upgrade_plan_payload(
                command=command,
                registry_path=registry_path,
                registry=registry,
                target_version=args.target_version,
            )
        )

    if args.action == "current":
        target = resolve_target(args.target or ".")
        if not target.exists():
            return emit(
                output(
                    command,
                    "block",
                    schema=WORKSTATION_CONTROL_SCHEMA,
                    summary="Target repository path does not exist.",
                    target=str(target),
                    mutates=False,
                    failed_layer="target",
                    fail_closed_reason="target path does not exist",
                    fallback_to=["loom workstation current --target <repo> --json"],
                )
            )
        current = read_workstation_current(target)
        if not args.apply:
            planned = (
                workstation_current_payload(
                    target,
                    item=args.item,
                    issue=args.issue,
                    pr=args.pr,
                    branch=args.branch,
                    clear=args.clear,
                )
                if args.clear or args.item or args.issue or args.pr or args.branch
                else None
            )
            return emit(
                output(
                    command,
                    "pass",
                    schema=WORKSTATION_CONTROL_SCHEMA,
                    summary="Workstation current pointer read without mutating repository or workstation state.",
                    target=str(target),
                    mutates=False,
                    current=current,
                    planned_current=planned,
                    apply_required=planned is not None,
                    fallback_to="loom workstation current --target <repo> --apply --json" if planned is not None else None,
                )
            )
        if not args.clear and not args.item:
            return emit(
                output(
                    command,
                    "block",
                    schema=WORKSTATION_CONTROL_SCHEMA,
                    summary="Workstation current pointer apply requires --item or --clear.",
                    target=str(target),
                    mutates=False,
                    failed_layer="workstation-current",
                    fail_closed_reason="missing current pointer item or clear intent",
                    fallback_to=["loom workstation current --target <repo> --item <WI> --apply --json", "loom workstation current --target <repo> --clear --apply --json"],
                )
            )
        payload = workstation_current_payload(
            target,
            item=args.item,
            issue=args.issue,
            pr=args.pr,
            branch=args.branch,
            clear=args.clear,
        )
        try:
            current_path = write_workstation_current(target, payload)
        except OSError as exc:
            return emit(
                output(
                    command,
                    "block",
                    schema=WORKSTATION_CONTROL_SCHEMA,
                    summary="Workstation current pointer could not be written.",
                    target=str(target),
                    mutates=True,
                    failed_layer="workstation-current",
                    fail_closed_reason=str(exc),
                    fallback_to=["repair ~/.loom permissions", "loom workstation current --target <repo> --json"],
                )
            )
        return emit(
            output(
                command,
                "pass",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary="Workstation current pointer updated without mutating the target repository.",
                target=str(target),
                mutates=True,
                writes=[str(current_path)],
                current=payload,
                fallback_to=None,
            )
        )

    if args.action == "list":
        repositories = registry.get("repositories", [])
        classifications = workstation_registry_classifications(registry)
        blocking_classifications = [item for item in classifications if item.get("blocking") is True]
        blocked_entry_ids = {item.get("entry_id") for item in blocking_classifications if item.get("entry_id") is not None}
        eligible = [
            entry.get("id")
            for entry in repositories
            if isinstance(entry, dict)
            and entry.get("path_state") == "present"
            and entry.get("id") not in blocked_entry_ids
            and isinstance(entry.get("opt_in"), dict)
            and entry["opt_in"].get("enabled") is True
        ]
        return emit(
            output(
                command,
                "block" if blocking_classifications else "pass",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary=(
                    "Workstation repository registry contains blocking entries."
                    if blocking_classifications
                    else "Workstation repository registry listed."
                ),
                registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
                registry_path=str(registry_path),
                logical_registry_path=registry.get("registry_path"),
                mutates=False,
                failed_layer="workstation-registry" if blocking_classifications else None,
                fail_closed_reason=(
                    "registry contains entries that are ambiguous for mutation planning"
                    if blocking_classifications
                    else None
                ),
                repositories=repositories,
                repository_count=len(repositories),
                eligible_for_plan=eligible,
                classifications=classifications,
                fallback_to=(
                    sorted(
                        {
                            guidance
                            for item in blocking_classifications
                            for guidance in item.get("repair_guidance", [])
                            if isinstance(guidance, str)
                        }
                    )
                    if blocking_classifications
                    else None
                ),
            )
        )

    target = resolve_target(args.target or ".")
    if args.action == "register" and not target.exists():
        return emit(
            output(
                command,
                "block",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary="Target repository path does not exist.",
                target=str(target),
                registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
                registry_path=str(registry_path),
                mutates=False,
                failed_layer="target",
                fail_closed_reason="target path does not exist",
                fallback_to=["loom workstation register --target <repo> --json"],
            )
        )

    raw_repositories = registry.get("repositories", [])
    if not all(isinstance(entry, dict) for entry in raw_repositories):
        return emit(
            output(
                command,
                "block",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary="Workstation registry contains unsupported repository entries.",
                registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
                registry_path=str(registry_path),
                mutates=False,
                failed_layer="workstation-registry",
                fail_closed_reason="repository entries must be JSON objects before mutation",
                fallback_to=["repair or remove ~/.loom/repositories.json", "loom workstation list --json"],
            )
        )
    repositories = [entry for entry in raw_repositories if isinstance(entry, dict)]
    blocking_classifications = [
        item for item in workstation_registry_classifications(registry) if item.get("blocking") is True
    ]
    if args.action == "register" and blocking_classifications:
        return emit(
            output(
                command,
                "block",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary="Workstation registry contains blocking entries; refusing to register until it is repaired.",
                registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
                registry_path=str(registry_path),
                mutates=False,
                failed_layer="workstation-registry",
                fail_closed_reason="registry contains entries that are ambiguous for mutation planning",
                classifications=blocking_classifications,
                fallback_to=sorted(
                    {
                        guidance
                        for item in blocking_classifications
                        for guidance in item.get("repair_guidance", [])
                        if isinstance(guidance, str)
                    }
                ),
            )
        )
    matched: list[dict[str, Any]]
    if args.id:
        matched = [entry for entry in repositories if entry.get("id") == args.id]
    else:
        matched = [entry for entry in repositories if entry.get("path") == str(target.resolve())]

    if args.action == "register":
        entry = workstation_registry_entry(target, source="loom workstation register")
        retained = [
            existing
            for existing in repositories
            if existing.get("id") != entry["id"] and existing.get("path") != entry["path"]
        ]
        retained.append(entry)
        registry["repositories"] = sorted(retained, key=lambda item: str(item.get("path", "")))
        registry["updated_at"] = now_iso()
        write_json(registry_path, registry)
        return emit(
            output(
                command,
                "pass",
                schema=WORKSTATION_CONTROL_SCHEMA,
                summary="Target repository registered in the workstation registry.",
                target=str(target),
                registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
                registry_path=str(registry_path),
                mutates=True,
                writes=[str(registry_path)],
                repository=entry,
                repository_count=len(registry["repositories"]),
                fallback_to=None,
            )
        )

    if args.keep_entry:
        now = now_iso()
        for entry in matched:
            entry.setdefault("opt_in", {})
            if isinstance(entry["opt_in"], dict):
                entry["opt_in"].update(
                    {
                        "enabled": False,
                        "source": "loom workstation unregister --keep-entry",
                        "updated_at": now,
                    }
                )
        removed = 0
    else:
        matched_ids = {id(entry) for entry in matched}
        registry["repositories"] = [entry for entry in repositories if id(entry) not in matched_ids]
        removed = len(matched)
    registry["updated_at"] = now_iso()
    write_json(registry_path, registry)
    return emit(
        output(
            command,
            "pass",
            schema=WORKSTATION_CONTROL_SCHEMA,
            summary="Target repository entry updated in the workstation registry.",
            target=str(target),
            registry_schema=WORKSTATION_REPOSITORIES_SCHEMA,
            registry_path=str(registry_path),
            mutates=True,
            writes=[str(registry_path)],
            removed_count=removed,
            updated_count=len(matched) if args.keep_entry else 0,
            repository_count=len(registry.get("repositories", [])),
            fallback_to=None,
        )
    )


def handle_host(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom host")
    parser.add_argument("action", choices=("list", "doctor", "install", "verify", "register", "upgrade", "remove"))
    parser.add_argument("--host", default="auto", choices=("auto", "codex", "claude", "opencode", "gemini", "cursor"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--source")
    parser.add_argument("--scope", default="user", choices=("user",))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"host {args.action}"
    target = resolve_target(args.target)
    hosts = supported_hosts(target)
    selected = [host for host in hosts if args.host == "auto" or host["id"] == args.host]
    if args.action == "list":
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Supported host adapters listed.", target=str(target), hosts=hosts, fallback_to=None))
    detected = [host for host in selected if host.get("detected")]
    if args.host == "auto" and len(detected) != 1:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Host auto-detection is ambiguous or unavailable.", target=str(target), hosts=hosts, failed_layer="host-detection", fail_closed_reason="pass --host explicitly when zero or multiple supported hosts are detected", fallback_to=["loom host list --json", "loom host doctor --host <host> --json"]))
    host = detected[0]["id"] if args.host == "auto" else args.host
    if args.action == "doctor":
        source, source_kind = resolve_codex_plugin_source(args.source) if host == "codex" else (None, None)
        registration = codex_workstation_registration_status(source) if host == "codex" else None
        install_status = codex_workstation_plugin_install_status(source) if host == "codex" else None
        payload_readback = install_status.get("plugin_payload_readback") if isinstance(install_status, dict) else None
        return emit(output(command, "pass", schema=HOST_SCHEMA, summary="Host adapter contract is readable.", target=str(target), host=host, scope=args.scope, provider="codex-user-plugin" if host == "codex" else "unsupported-for-install", hosts=hosts, source_kind=source_kind, workstation_install=install_status, workstation_registration=registration, plugin_payload_readback=payload_readback, version_freshness=version_freshness(source, payload_readback) if host == "codex" else None, verification=["docs/adoption/host-adapter-matrix.md", "tools/host_adapter_check.py"], fallback_to=None))
    if args.action == "install" and host == "codex":
        source, source_kind = resolve_codex_plugin_source(args.source)
        paths = codex_workstation_paths()
        planned_writes = [str(paths["plugin_cache_path"])]
        install_status = codex_workstation_plugin_install_status(source)
        if args.dry_run and not args.apply:
            return emit(
                output(
                    command,
                    "pass",
                    schema=HOST_SCHEMA,
                    summary="Codex user-level plugin install plan generated without mutating user state.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    source_kind=source_kind,
                    mutates=False,
                    planned_writes=planned_writes,
                    workstation_install=install_status,
                    fallback_to=["loom host install --host codex --scope user --apply --json"],
                )
            )
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=HOST_SCHEMA,
                    summary="Codex user-level plugin install is mutating and requires --apply or --dry-run.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    source_kind=source_kind,
                    mutates=True,
                    planned_writes=planned_writes,
                    workstation_install=install_status,
                    failed_layer="host-install",
                    fail_closed_reason="explicit --apply is required before writing user Codex plugin state",
                    fallback_to=["loom host install --host codex --scope user --dry-run --json"],
                )
            )
        try:
            writes = install_codex_workstation_plugin(source)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Codex user-level plugin could not be installed.", target=str(target), host=host, scope=args.scope, source=str(source), source_kind=source_kind, mutates=True, failed_layer="host-install", fail_closed_reason=str(exc), fallback_to=["loom host doctor --host codex --json"]))
        updated = codex_workstation_plugin_install_status(source)
        return emit(
            output(
                command,
                "pass" if updated["result"] == "pass" else "block",
                schema=HOST_SCHEMA,
                summary="Codex user-level plugin payload installed." if updated["result"] == "pass" else "Codex user-level plugin install writes completed but readback still failed.",
                target=str(target),
                host=host,
                scope=args.scope,
                source=str(source),
                source_kind=source_kind,
                mutates=True,
                writes=writes,
                workstation_install=updated,
                failed_layer=None if updated["result"] == "pass" else "host-install",
                fail_closed_reason=None if updated["result"] == "pass" else "user plugin cache readback failed after apply",
                fallback_to=None if updated["result"] == "pass" else ["loom host doctor --host codex --json"],
            )
        )
    if args.action == "register":
        if host != "codex":
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Workstation registration is implemented for Codex only.", target=str(target), host=host, scope=args.scope, mutates=False, failed_layer="workstation-registration", fail_closed_reason="unsupported host for workstation registration", fallback_to=["docs/adoption/host-adapter-matrix.md"]))
        source, source_kind = resolve_codex_plugin_source(args.source)
        registration = codex_workstation_registration_status(source)
        paths = codex_workstation_paths()
        planned_writes = [str(paths["plugin_cache_path"]), str(paths["marketplace_path"]), str(paths["config_path"])]
        if args.dry_run and not args.apply:
            return emit(
                output(
                    command,
                    "pass",
                    schema=HOST_SCHEMA,
                    summary="Codex workstation registration plan generated without mutating user state.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    source_kind=source_kind,
                    mutates=False,
                    planned_writes=planned_writes,
                    workstation_registration=registration,
                    reload_required=True,
                    reload_guidance=registration["reload_guidance"],
                    fallback_to=["loom host register --host codex --scope user --apply --json"],
                )
            )
        if not args.apply:
            return emit(
                output(
                    command,
                    "block",
                    schema=HOST_SCHEMA,
                    summary="Codex workstation registration is mutating and requires --apply or --dry-run.",
                    target=str(target),
                    host=host,
                    scope=args.scope,
                    source=str(source),
                    source_kind=source_kind,
                    mutates=True,
                    planned_writes=planned_writes,
                    workstation_registration=registration,
                    failed_layer="workstation-registration",
                    fail_closed_reason="explicit --apply is required before writing user Codex registration state",
                    fallback_to=["loom host register --host codex --scope user --dry-run --json"],
                )
            )
        try:
            writes = register_codex_workstation(source)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=HOST_SCHEMA, summary="Codex workstation registration could not be applied.", target=str(target), host=host, scope=args.scope, source=str(source), source_kind=source_kind, mutates=True, failed_layer="workstation-registration", fail_closed_reason=str(exc), fallback_to=["loom host doctor --host codex --json"]))
        updated = codex_workstation_registration_status(source)
        return emit(
            output(
                command,
                "pass" if updated["result"] == "pass" else "block",
                schema=HOST_SCHEMA,
                summary="Codex workstation registration applied." if updated["result"] == "pass" else "Codex workstation registration writes completed but verification still failed.",
                target=str(target),
                host=host,
                scope=args.scope,
                source=str(source),
                source_kind=source_kind,
                mutates=True,
                writes=writes,
                workstation_registration=updated,
                reload_required=True,
                reload_guidance=updated["reload_guidance"],
                failed_layer=None if updated["result"] == "pass" else "workstation-registration",
                fail_closed_reason=None if updated["result"] == "pass" else "workstation registration verification failed after apply",
                fallback_to=None if updated["result"] == "pass" else ["loom host doctor --host codex --json"],
            )
        )
    if args.action in {"upgrade", "remove"}:
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Repo-local host lifecycle commands are no longer supported by the Loom CLI.", target=str(target), host=host, scope=args.scope, mutates=False, failed_layer="host-lifecycle", fail_closed_reason="pure global install keeps host plugin state in the user workstation, not the target repository", fallback_to=["loom host install --host codex --scope user --apply --json", "loom host register --host codex --scope user --apply --json"]))
    if args.action == "install":
        return emit(output(command, "block", schema=HOST_SCHEMA, summary="Codex user-level plugin install is implemented only for --host codex.", target=str(target), host=host, scope=args.scope, mutates=False, failed_layer="host-install", fail_closed_reason="repo-local plugin, runtime, and skills payload installation is no longer supported", fallback_to=["loom host install --host codex --scope user --apply --json", "loom install --target <repo> --apply --json"]))
    ok, checks = verify_cli_managed_surfaces(target, host=host)
    registration = None
    source_kind = None
    if host == "codex":
        source, source_kind = resolve_codex_plugin_source(args.source)
        registration = codex_workstation_registration_status(source)
    provider_ok = registration is None or registration.get("result") == "pass"
    result = "pass" if ok and provider_ok else "block"
    summary = (
        "Metadata-only repository adoption and Codex user-level plugin provider verified."
        if result == "pass"
        else "Metadata-only repository adoption or Codex user-level plugin provider verification failed."
    )
    if not ok:
        failed_layer = "host-payload"
        fail_closed_reason = "one or more metadata-only target repository checks failed"
        fallback_to = ["loom install --target <repo> --apply --json", "loom repair plan --target <repo> --json"]
    elif not provider_ok:
        failed_layer = "workstation-registration"
        fail_closed_reason = "Codex user-level Loom plugin is not installed or registered for this workstation"
        fallback_to = [
            "loom host install --host codex --scope user --apply --json",
            "loom host register --host codex --scope user --apply --json",
            "loom host doctor --host codex --json",
        ]
    else:
        failed_layer = None
        fail_closed_reason = None
        fallback_to = None
    return emit(output(command, result, schema=HOST_SCHEMA, summary=summary, target=str(target), host=host, scope=args.scope, source_kind=source_kind, mutates=False, verifies="repository-adoption-metadata-and-codex-user-plugin-provider", workstation_registration=registration, checks=checks, failed_layer=failed_layer, fail_closed_reason=fail_closed_reason, fallback_to=fallback_to))


def handle_skills(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom skills")
    parser.add_argument("action", choices=("list", "generate", "check", "doctor", "package", "release-check"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    command = f"skills {args.action}"
    target = resolve_target(args.target)
    registry = read_optional_json(PLUGIN_SKILLS_ROOT / "registry.json") or {}
    entries = registry.get("entries") if isinstance(registry, dict) else []
    if args.action == "list":
        return emit(output(command, "pass", schema=SKILLS_SCHEMA, summary="Codex plugin payload skills registry listed.", registry_version=registry.get("registry_version"), root_entry=registry.get("root_entry"), skills=entries, plugin_payload_root="plugins/loom/skills", fallback_to=None))
    if args.action == "generate" and not args.apply:
        return emit(output(command, "block", schema=SKILLS_SCHEMA, summary="`loom skills generate` mutates the Loom source repository skills mirror and Codex plugin payload, and requires --apply.", target=str(target), mutates=True, failed_layer="skills-surface", fail_closed_reason="explicit --apply is required before rewriting source repository skills/plugin payload", fallback_to=["loom skills check --target <repo> --json"]))
    if args.action == "generate":
        try:
            managed_writes = generate_source_skills_payload(target)
        except RuntimeError as exc:
            return emit(output(command, "block", schema=SKILLS_SCHEMA, summary="Source skills/plugin payload generation failed.", target=str(target), mutates=True, failed_layer="skills-surface", fail_closed_reason=str(exc), fallback_to=["python3 tools/skills_surface.py check"]))
        return emit(output(command, "pass", schema=SKILLS_SCHEMA, summary="Loom source skills mirror and Codex plugin payload generated.", target=str(target), mutates=True, managed_writes=managed_writes, fallback_to=None))
    if args.action in {"check", "doctor", "release-check"}:
        checks = []
        if target.resolve() == REPO_ROOT.resolve():
            checks.append([sys.executable, str(TOOLS_ROOT / "skills_surface.py"), "check"])
        else:
            ok, managed_checks = verify_cli_managed_surfaces(target, host="codex")
            checks.append({"command": "loom skills check metadata-only adoption", "returncode": 0 if ok else 1, "stdout": json.dumps(managed_checks, ensure_ascii=False), "stderr": "" if ok else "metadata-only adoption is incomplete or contains repo-local payload residue"})
        if args.action == "release-check":
            checks.extend(
                [
                    [sys.executable, str(TOOLS_ROOT / "host_adapter_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "version_surface_check.py")],
                    [sys.executable, str(TOOLS_ROOT / "check_release_surface.py")],
                    [sys.executable, str(TOOLS_ROOT / "check_npm_package.py")],
                ]
            )
        results = []
        for check in checks:
            if isinstance(check, dict):
                results.append(check)
            else:
                completed = run_capture(check)
                results.append({"command": " ".join(check), "returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()})
        failures = [item for item in results if item["returncode"] != 0]
        result = "pass" if not failures else "block"
        release_authority = None
        if args.action == "release-check":
            release_authority = {
                "active_cli_line": "loom",
                "candidate_authority": "VERSION",
                "published_evidence": ["GitHub v* tag", "GitHub Release"],
                "legacy_installer_evidence": {
                    "package": "@mc-and-his-agents/loom-installer",
                    "final_active_baseline": "0.1.119",
                    "tag": "loom-installer-v0.1.119",
                    "active_cli_evidence": False,
                },
            }
        return emit(output(command, result, schema=SKILLS_SCHEMA, summary="Skills/plugin payload checks passed." if result == "pass" else "Skills/plugin payload checks failed.", registry_version=registry.get("registry_version"), root_entry=registry.get("root_entry"), checks=results, release_authority=release_authority, failed_layer=None if result == "pass" else "skills-surface", fail_closed_reason=None if result == "pass" else "one or more skills checks failed", fallback_to=None if result == "pass" else ["loom skills generate --apply --json"]))
    payload_root = REPO_ROOT / "plugins" / "loom" / "skills"
    missing_payload_inputs = []
    if not (REPO_ROOT / "plugins" / "loom" / ".codex-plugin" / "plugin.json").is_file():
        missing_payload_inputs.append("plugins/loom/.codex-plugin/plugin.json")
    if not (payload_root / "registry.json").is_file():
        missing_payload_inputs.append("plugins/loom/skills/registry.json")
    skill_records = []
    for entry in entries or []:
        skill_id = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(skill_id, str):
            continue
        skill_records.append(
            {
                "id": skill_id,
                "role": entry.get("role"),
                "contract_version": entry.get("contract_version"),
                "skill": f"plugins/loom/skills/{skill_id}/SKILL.md",
                "contract": f"plugins/loom/skills/{skill_id}/contract.json",
                "executable": f"plugins/loom/skills/{entry.get('executable')}",
            }
        )
    result = "pass" if not missing_payload_inputs else "block"
    return emit(
        output(
            command,
            result,
            schema=SKILLS_SCHEMA,
            summary="Codex plugin payload metadata collected without single-skill package artifacts."
            if result == "pass"
            else "Codex plugin payload is incomplete.",
            mutates=False,
            registry_version=registry.get("registry_version"),
            root_entry=registry.get("root_entry"),
            plugin_payload={
                "manifest": "plugins/loom/.codex-plugin/plugin.json",
                "skills_root": "plugins/loom/skills",
                "single_skill_packages": False,
                "skills": skill_records,
            },
            failed_layer=None if result == "pass" else "plugin-payload",
            fail_closed_reason=None if result == "pass" else "missing plugin payload inputs",
            missing_inputs=missing_payload_inputs,
            fallback_to=None if result == "pass" else ["python3 tools/skills_surface.py generate", "python3 tools/skills_surface.py check"],
        )
    )


def handle_init(argv: list[str]) -> int:
    if not argv:
        return emit(output("init", "block", schema=SCENARIO_SCHEMA, summary="Init requires an operation.", failed_layer="scenario-input", fail_closed_reason="missing init operation", fallback_to=["loom init bootstrap --target <repo> --json", "loom init verify --target <repo> --json"]))
    return emit_delegated("init", "loom_init.py", strip_json_flag(argv), failed_layer="loom-init", fallback_to=["loom init verify --target <repo> --json", "loom doctor --target <repo> --json"])


def handle_adopt(argv: list[str]) -> int:
    if not argv:
        return emit(output("adopt", "block", schema=SCENARIO_SCHEMA, summary="Adopt requires an operation.", failed_layer="adoption-input", fail_closed_reason="missing adopt operation", fallback_to=["loom adopt verify --target <repo> --item <item> --json", "loom adopt adversarial-test --target <repo> --record --json", "loom init bootstrap --target <repo> --json"]))
    operation = argv[0]
    if operation not in {"verify", "adversarial-test"}:
        return emit(output("adopt", "block", schema=SCENARIO_SCHEMA, summary="Unsupported adopt operation.", failed_layer="adoption-input", fail_closed_reason=f"unsupported adopt operation: {operation}", fallback_to=["loom adopt verify --target <repo> --item <item> --json", "loom adopt adversarial-test --target <repo> --record --json", "loom init bootstrap --target <repo> --json"]))
    return emit_flow("adopt", ["adopt", operation, *strip_json_flag(argv[1:])], fallback_to=["loom init verify --target <repo> --json", "loom profile status --target <repo> --json"])


def handle_route(argv: list[str]) -> int:
    if "--issue" in argv or any(arg.startswith("--issue=") for arg in argv):
        parser = argparse.ArgumentParser(prog="loom route")
        parser.add_argument("--target", required=True, help="Target repository root")
        parser.add_argument("--issue", type=int, required=True, help="GitHub FR or Work Item issue number")
        parser.add_argument("--task", required=True, help="Bounded Work Item proposal text")
        parser.add_argument(
            "--intent",
            choices=("planning", "branch", "build", "pr", "ship", "closeout", "completed"),
            default="planning",
            help="Lifecycle intent that requires admission",
        )
        parser.add_argument("--blocked-by", type=int, action="append", default=[], help="Native blocking issue number; may be repeated")
        parser.add_argument("--work-item", type=int, help="Existing Work Item number for a partial admission recovery")
        parser.add_argument("--apply", action="store_true", help="Apply host-native Work Item reconciliation")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--full-output", action="store_true")
        args = parser.parse_args(argv)
        flow_args = [
            "github-intake",
            "admission",
            "--target",
            args.target,
            "--issue",
            str(args.issue),
            "--task",
            args.task,
            "--intent",
            args.intent,
        ]
        for blocker in args.blocked_by:
            flow_args.extend(["--blocked-by", str(blocker)])
        if args.work_item is not None:
            flow_args.extend(["--work-item", str(args.work_item)])
        if args.apply:
            flow_args.append("--apply")
        if args.full_output:
            flow_args.append("--full-output")
        return emit_flow(
            "route",
            flow_args,
            fallback_to=["loom route --target <repo> --issue <fr> --task <work-item scope> --intent build --apply --json"],
        )
    return emit_delegated("route", "loom_init.py", ["route", *strip_json_flag(argv)], failed_layer="loom-route", fallback_to=["loom route --target <repo> --task <task> --json", "loom init verify --target <repo> --json"])


def handle_status(argv: list[str]) -> int:
    target = target_from_args(argv)
    forwarded, full_output = split_agent_output_args(argv)
    payload = delegated_payload("status", "loom_status.py", strip_json_flag(forwarded), failed_layer="loom-status", fallback_to=["loom fact-chain --target <repo> --json", "loom checkpoint admission --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != "status":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "status"
    annotate_global_cli_runtime_entrypoint(payload, command="status", target=target, argv=argv)
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def handle_fact_chain(argv: list[str]) -> int:
    target = target_from_args(argv)
    forwarded, full_output = split_agent_output_args(argv)
    payload = flow_payload("fact-chain", ["fact-chain", *strip_json_flag(forwarded)], fallback_to=["loom init verify --target <repo> --json", "loom status --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != "fact-chain":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "fact-chain"
    annotate_global_cli_runtime_entrypoint(payload, command="fact-chain", target=target, argv=argv)
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def handle_shadow_parity(argv: list[str]) -> int:
    target = target_from_args(argv)
    forwarded, full_output = split_agent_output_args(argv)
    payload = flow_payload("shadow-parity", ["shadow-parity", *strip_json_flag(forwarded)], fallback_to=["loom shadow-parity --target <repo> --surface all --blocking --json", "loom status --target <repo> --json"])
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != "shadow-parity":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "shadow-parity"
    annotate_global_cli_runtime_entrypoint(payload, command="shadow-parity", target=target, argv=argv)
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def handle_profile(argv: list[str]) -> int:
    if not argv:
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Profile requires an operation.", failed_layer="profile-input", fail_closed_reason="missing profile operation", fallback_to=["loom profile status --target <repo> --json", "loom profile upgrade-plan --target <repo> --json"]))
    operation = argv[0]
    if operation == "light-migration-plan":
        return emit_delegated(
            "profile light-migration-plan",
            "light_profile.py",
            ["plan", *strip_json_flag(argv[1:])],
            failed_layer="light-profile",
            fallback_to=["loom profile light-migration-plan --target <repo> --json"],
        )
    if operation == "light-migration-reconcile":
        return emit_delegated(
            "profile light-migration-reconcile",
            "light_profile.py",
            ["reconcile", *strip_json_flag(argv[1:])],
            failed_layer="light-profile-migration",
            fallback_to=["loom profile light-migration-reconcile --target <repo> --repository <owner/repo> --branch <branch> --work-item <issue> --gate-pr <pr> --migration-pr <pr> --context <check> --app-id <id> --json"],
        )
    if operation not in {"status", "upgrade-plan", "upgrade"}:
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Unsupported profile operation.", failed_layer="profile-input", fail_closed_reason=f"unsupported profile operation: {operation}", fallback_to=["loom profile status --target <repo> --json", "loom profile upgrade-plan --target <repo> --json", "loom profile light-migration-plan --target <repo> --json", "loom profile light-migration-reconcile --target <repo> --repository <owner/repo> --branch <branch> --work-item <issue> --gate-pr <pr> --migration-pr <pr> --context <check> --app-id <id> --json"]))
    return emit_flow(f"profile {operation}", ["governance-profile", operation, *strip_json_flag(argv[1:])], fallback_to=["loom profile status --target <repo> --json", "docs/adoption/github-profile-upgrade.md"])


def handle_governance_profile(argv: list[str]) -> int:
    if not argv:
        return emit(output("governance-profile", "block", schema=PROFILE_SCHEMA, summary="Governance profile requires an operation.", failed_layer="profile-input", fail_closed_reason="missing governance-profile operation", fallback_to=["loom governance-profile status --target <repo> --json", "loom profile status --target <repo> --json"]))
    operation = argv[0]
    if operation not in {"status", "upgrade-plan", "upgrade", "binding"}:
        return emit(output("governance-profile", "block", schema=PROFILE_SCHEMA, summary="Unsupported governance-profile operation.", failed_layer="profile-input", fail_closed_reason=f"unsupported governance-profile operation: {operation}", fallback_to=["loom governance-profile status --target <repo> --json", "loom profile status --target <repo> --json"]))
    return emit_flow(f"governance-profile {operation}", ["governance-profile", operation, *strip_json_flag(argv[1:])], fallback_to=["loom governance-profile status --target <repo> --json", "docs/adoption/github-profile-upgrade.md"])


def handle_checkpoint(argv: list[str]) -> int:
    if not argv:
        return emit(output("checkpoint", "block", schema=GATE_SCHEMA, summary="Checkpoint requires a stage.", failed_layer="checkpoint-input", fail_closed_reason="missing checkpoint stage", fallback_to=["loom checkpoint admission --target <repo> --json", "loom checkpoint build --target <repo> --json", "loom checkpoint merge --target <repo> --json"]))
    stage = argv[0]
    if stage not in {"admission", "build", "merge"}:
        return emit(output("checkpoint", "block", schema=GATE_SCHEMA, summary="Unsupported checkpoint stage.", failed_layer="checkpoint-input", fail_closed_reason=f"unsupported checkpoint stage: {stage}", fallback_to=["loom checkpoint admission --target <repo> --json", "loom checkpoint build --target <repo> --json", "loom checkpoint merge --target <repo> --json"]))
    return emit_flow(f"checkpoint {stage}", ["checkpoint", stage, *strip_json_flag(argv[1:])], fallback_to=["loom status --target <repo> --json", "loom fact-chain --target <repo> --json"])


def handle_gate(argv: list[str]) -> int:
    if not argv:
        return emit(output("gate", "block", schema=GATE_SCHEMA, summary="Gate requires a gate name.", failed_layer="gate-input", fail_closed_reason="missing gate name", fallback_to=["loom gate pre-review --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"]))
    gate = argv[0]
    rest = strip_json_flag(argv[1:])
    if gate in {"pre-review", "spec-review", "review"}:
        return emit_flow(f"gate {gate}", ["flow", gate, *rest], fallback_to=["loom status --target <repo> --json", f"loom {gate} --target <repo> --json"])
    if gate == "pr":
        return emit_flow("gate pr", ["pr-gate", "check", *rest], fallback_to=["loom pr gate <pr> --json", "loom review --target <repo> --json"])
    if gate == "merge":
        return emit_flow("gate merge", ["controlled-merge", "check", *rest], fallback_to=["loom checkpoint merge --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"])
    if gate == "freeze":
        if not rest:
            return emit(output("gate freeze", "block", schema=GATE_SCHEMA, summary="Gate freeze requires an operation.", failed_layer="gate-input", fail_closed_reason="missing gate freeze operation", fallback_to=["loom gate freeze check --target <repo> --json", "loom gate freeze write --target <repo> --json"]))
        operation = rest[0]
        if operation not in {"check", "write"}:
            return emit(output("gate freeze", "block", schema=GATE_SCHEMA, summary="Unsupported gate freeze operation.", failed_layer="gate-input", fail_closed_reason=f"unsupported gate freeze operation: {operation}", fallback_to=["loom gate freeze check --target <repo> --json", "loom gate freeze write --target <repo> --json"]))
        return emit_flow(f"gate freeze {operation}", ["gate-freeze", operation, *rest[1:]], fallback_to=["loom pr metadata-preflight --surface merge_ready --target <repo> --json", "loom shadow-parity --target <repo> --surface all --blocking --json"])
    if gate == "closeout":
        return emit_flow("gate closeout", ["closeout", "check", *rest], fallback_to=["loom merge check <pr> --json", "loom status --target <repo> --json"])
    if gate == "repair-pr":
        return emit_flow("gate repair-pr", ["gate-repair-pr", *rest], fallback_to=["loom gate pr --target <repo> --pr <number> --json", "loom merge check <pr> --json"])
    return emit(output("gate", "block", schema=GATE_SCHEMA, summary="Unsupported gate name.", failed_layer="gate-input", fail_closed_reason=f"unsupported gate name: {gate}", fallback_to=["loom gate pre-review --target <repo> --json", "loom gate pr --target <repo> --pr <number> --json"]))


def handle_closeout_queue_status(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom closeout queue status")
    parser.add_argument("--target", default=".")
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--queue-file")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        payload = block_target("closeout queue status", target, "target path does not exist")
        payload.update(
            {
                "schema_version": "loom-closeout-queue-status/v1",
                "operation": "status",
                "mode": "blocked",
                "mutates": False,
                "host_mutations": False,
                "carrier_mutations": False,
                "item_count": 0,
                "items": [],
                "next_action": "provide an existing target repository before reading closeout queue status",
                "next_command": None,
            }
        )
        return emit(payload)
    flow_args = ["closeout-queue", "status", "--target", str(target)]
    for issue in args.issue:
        flow_args.extend(["--issue", str(issue)])
    for item in args.item:
        flow_args.extend(["--item", item])
    for flag, value in (
        ("--queue-file", args.queue_file),
        ("--output", args.output),
    ):
        if value is not None:
            flow_args.extend([flag, value])
    append_full_output_flag(flow_args, args)
    payload = flow_payload(
        "closeout queue status",
        flow_args,
        fallback_to=["loom closeout --target <repo> --json", "loom reconcile --issue <issue> --pr <pr> --json"],
    )
    payload.setdefault("schema_version", SCENARIO_SCHEMA)
    if payload.get("command") and payload.get("command") != "closeout queue status":
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = "closeout queue status"
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def handle_scenario(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--output")
    parser.add_argument("--build-evidence")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES)
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
    parser.add_argument("--carrier-sync-pr", type=int)
    parser.add_argument("--final-closeout-pr", type=int)
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--project", type=int)
    parser.add_argument("--phase", type=int)
    parser.add_argument("--fr", type=int)
    parser.add_argument("--branch")
    parser.add_argument("--goal-completion")
    parser.add_argument(
        "--gate-profile",
        choices=(
            "auto",
            "closeout-contract",
            "source-self-fixture",
            "bootstrap-regression",
            "distribution-regression",
            "strong-profile-full-gate",
        ),
        default="auto",
    )
    parser.add_argument("--comment")
    parser.add_argument("--issue-payload-file")
    parser.add_argument("--project-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--branch-protection-file")
    parser.add_argument("--ruleset-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--project-drift-mode", choices=("advisory", "blocking"), default="advisory")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))

    flow_operations = {
        "story": "story",
        "build": "build",
        "pre-review": "pre-review",
        "handoff": "handoff",
        "retire": "handoff",
    }
    if command in flow_operations:
        flow_args = ["flow", flow_operations[command], "--target", str(target)]
        for flag, value in (
            ("--item", args.item),
            ("--output", args.output),
            ("--build-evidence", args.build_evidence),
            ("--owner", args.owner),
            ("--repo", args.repo_name),
            ("--issue", args.issue),
            ("--fr", args.fr),
            ("--pr", args.pr),
            ("--pr-payload-file", args.pr_payload_file),
            ("--project", args.project),
            ("--branch", args.branch),
            ("--project-drift-mode", args.project_drift_mode if command in {"pre-review"} else None),
        ):
            if value is not None:
                flow_args.extend([flag, str(value)])
        payload = flow_payload(command, flow_args, fallback_to=["loom status --target <repo> --json", "loom checkpoint build --target <repo> --json"])
        payload.setdefault("schema_version", SCENARIO_SCHEMA)
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        if command == "story":
            annotate_global_cli_runtime_entrypoint(payload, command="story", target=target, argv=argv)
        if command == "retire":
            payload["retire_contract"] = {
                "mutates": False,
                "summary": "Retire currently exposes the handoff/cleanup checklist and does not delete worktrees or host objects.",
                "fallback_to": ["loom workspace retire --target <repo> --json", "loom handoff --target <repo> --json"],
            }
        return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))

    if command in {"spec", "plan"}:
        item = args.item or "unknown-item"
        relative = f".loom/specs/{item}/{'spec.md' if command == 'spec' else 'plan.md'}"
        locator = target / relative
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block" if not locator.exists() else "pass",
                    schema=SCENARIO_SCHEMA,
                    summary=f"{command} scenario locator {'exists' if locator.exists() else 'is missing'}; authoring remains caller-owned.",
                    target=str(target),
                    item=item,
                    locator=relative,
                    mutates=False,
                    failed_layer=None if locator.exists() else f"{command}-carrier",
                    fail_closed_reason=None if locator.exists() else f"missing {relative}",
                    fallback_to=None if locator.exists() else ["loom story --target <repo> --item <item> --json", "docs/methodology/templates/spec-suite.md"],
                ),
                full_output=args.full_output,
            )
        )

    if command == "closeout":
        flow_args = ["closeout", "check", "--target", str(target)]
        for flag, value in (
            ("--item", args.item),
            ("--issue", args.issue),
            ("--pr", args.pr),
            ("--pr-role", args.pr_role),
            ("--implementation-pr", args.implementation_pr),
            ("--release-pr", args.release_pr),
            ("--carrier-sync-pr", args.carrier_sync_pr),
            ("--final-closeout-pr", args.final_closeout_pr),
            ("--project", args.project),
            ("--phase", args.phase),
            ("--fr", args.fr),
            ("--branch", args.branch),
            ("--goal-completion", args.goal_completion),
            ("--gate-profile", args.gate_profile if args.gate_profile != "auto" else None),
            ("--owner", args.owner),
            ("--repo", args.repo_name),
            ("--comment", args.comment),
            ("--issue-payload-file", args.issue_payload_file),
            ("--pr-payload-file", args.pr_payload_file),
            ("--project-payload-file", args.project_payload_file),
            ("--status-checks-file", args.status_checks_file),
            ("--branch-protection-file", args.branch_protection_file),
            ("--ruleset-file", args.ruleset_file),
        ):
            if value is not None:
                flow_args.extend([flag, str(value)])
        if args.skip_gate:
            flow_args.append("--skip-gate")
        payload = flow_payload(command, flow_args, fallback_to=["loom merge check <pr> --json", "loom reconcile --issue <issue> --pr <pr> --json"])
        payload.setdefault("schema_version", SCENARIO_SCHEMA)
        if payload.get("command") and payload.get("command") != command:
            payload["wrapped_command"] = payload.get("command")
        payload["command"] = command
        return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))

    return emit(output(command, "block", schema=SCENARIO_SCHEMA, summary="Unsupported scenario command.", failed_layer="scenario-input", fail_closed_reason=command, fallback_to=["loom help --json"]))


def dispatch(command: str, forwarded_args: list[str]) -> int:
    tool_name, prefix = COMMAND_ROUTES[command]
    tool_path = TOOLS_ROOT / tool_name
    if not tool_path.exists():
        return emit(
            output(
                command,
                "block",
                summary="Delegated compatibility wrapper is missing.",
                failed_layer="delegated-wrapper",
                fail_closed_reason=f"missing delegated tool: {tool_path}",
                fallback_to=["loom help --json"],
            ),
            stream=sys.stderr,
        )
    forwarded_args, full_output = split_agent_output_args(forwarded_args)
    target = target_root_from_explicit_arg(forwarded_args)
    payload = delegated_payload(
        command,
        tool_name,
        [*prefix, *strip_json_flag(forwarded_args)],
        failed_layer="delegated-wrapper",
        fallback_to=["loom help --json"],
    )
    payload.setdefault("schema_version", OUTPUT_SCHEMA)
    if payload.get("command") and payload.get("command") != command:
        payload["wrapped_command"] = payload.get("command")
    payload["command"] = command
    return emit(agent_safe_payload(payload, target_root=target, full_output=full_output))


def reserved_command(command: str, argv: list[str]) -> int:
    entry = COMMAND_INDEX[command]
    wants_json = "--json" in argv or True
    payload = output(
        command,
        "block",
        summary="Command is reserved by the CLI-first contract but not implemented in this Work Item.",
        command_status=entry["status"],
        domain=entry["domain"],
        failed_layer="cli-command-implementation",
        fail_closed_reason="reserved command has no executable implementation yet",
        fallback_to=["loom help --json"],
    )
    if wants_json:
        return emit(payload)
    print(f"loom: {command} is reserved but not implemented", file=sys.stderr)
    return 2


def resolve_command(argv: list[str]) -> tuple[str, list[str]] | None:
    if not argv:
        return None
    for length in (3, 2, 1):
        if len(argv) < length:
            continue
        candidate = " ".join(argv[:length])
        if candidate in COMMAND_INDEX or candidate in COMMAND_ROUTES or candidate in {"flow", "check", "suite"}:
            return candidate, argv[length:]
    return argv[0], argv[1:]


def repo_locator(path: Path, target_root: Path) -> str:
    return path.relative_to(target_root).as_posix()


def suite_item_segment_error(item: str) -> str | None:
    if not item or item in {".", ".."} or "/" in item or "\\" in item or Path(item).is_absolute():
        return "suite item must be a single repo-local path segment"
    if Path(item).name != item:
        return "suite item must be a single repo-local path segment"
    return None


def first_existing_locator(paths: list[Path], target_root: Path) -> str | None:
    for path in paths:
        if path.exists() and path.is_file() and not path.is_symlink():
            return repo_locator(path, target_root)
    return None


def suite_path_marker_values(text: str) -> tuple[list[str], list[str]]:
    lowered = text.lower()
    values: list[str] = []
    invalid_values: list[str] = []
    for line in lowered.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped.startswith("suite path:"):
            value = stripped.split(":", 1)[1].strip().replace(" ", "_").replace("-", "_")
            if value in {"full", "minimal", "not_applicable", "unknown"}:
                values.append(value)
            else:
                invalid_values.append(value)
    if "loom-full-suite-index/v1" in lowered:
        values.append("full")
    return values, invalid_values


def read_suite_path_marker_values(path: Path) -> tuple[list[str], list[str]]:
    if not path.exists() or path.is_symlink() or not path.is_file():
        return [], []
    try:
        return suite_path_marker_values(path.read_text(encoding="utf-8"))
    except OSError:
        return [], ["unreadable"]


def first_artifact_locator_or_invalid(paths: list[Path], target_root: Path) -> tuple[str | None, str | None]:
    for path in paths:
        if not path.exists():
            continue
        locator = repo_locator(path, target_root)
        if path.is_symlink() or not path.is_file():
            return None, locator
        return locator, None
    return None, None


def suite_artifact_paths(target: Path, item: str | None) -> dict[str, list[Path]]:
    if not item:
        return {}
    suite_root = target / ".loom" / "specs" / item
    return {
        "suite-index.md": [suite_root / "suite-index.md"],
        "spec.md": [suite_root / "spec.md"],
        "plan.md": [suite_root / "plan.md"],
        "research.md": [suite_root / "research.md"],
        "contracts.md": [suite_root / "contracts.md"],
        "readiness-checklist.md": [suite_root / "readiness-checklist.md"],
        "evidence-map.md": [suite_root / "evidence-map.md"],
        "consistency-analysis.md": [suite_root / "consistency-analysis.md"],
        "execution-breakdown.md": [suite_root / "execution-breakdown.md"],
        "task-carrier": [
            suite_root / "task-carrier.md",
            suite_root / "tasks.md",
            target / ".loom" / "tasks" / f"{item}.md",
            target / "tasks.md",
        ],
    }


SUITE_SCAFFOLD_TEMPLATE_LOCATORS = {
    "suite-index.md": "docs/methodology/templates/scaffold/full-suite-index.md",
    "spec.md": "docs/methodology/templates/scaffold/spec.md",
    "plan.md": "docs/methodology/templates/scaffold/plan.md",
    "research.md": "docs/methodology/templates/scaffold/research.md",
    "contracts.md": "docs/methodology/templates/scaffold/contracts.md",
    "readiness-checklist.md": "docs/methodology/templates/scaffold/readiness-checklist.md",
}

SUITE_SCAFFOLD_TEMPLATES = {
    artifact: REPO_ROOT / locator
    for artifact, locator in SUITE_SCAFFOLD_TEMPLATE_LOCATORS.items()
}

SUITE_SCAFFOLD_ARTIFACTS = {
    "minimal": ("spec.md", "plan.md"),
    "full": (
        "suite-index.md",
        "spec.md",
        "plan.md",
        "research.md",
        "contracts.md",
        "readiness-checklist.md",
    ),
}

SUITE_SCAFFOLD_REQUIRED_ARTIFACTS = {
    "minimal": ("spec.md", "plan.md"),
    "full": ("suite-index.md", "spec.md", "plan.md"),
}

SUITE_SCAFFOLD_CONDITIONAL_ARTIFACTS = {
    "minimal": (),
    "full": ("research.md", "contracts.md", "readiness-checklist.md"),
}

SUITE_REQUIRED_ARTIFACTS_BY_PATH = {
    "minimal": {"spec.md", "plan.md"},
    "full": {"suite-index.md", "spec.md", "plan.md"},
    "not_applicable": set(),
    "unknown": set(),
}

SUITE_CONDITIONAL_ARTIFACTS_BY_PATH = {
    "minimal": set(),
    "full": {"research.md", "contracts.md", "readiness-checklist.md"},
    "not_applicable": set(),
    "unknown": set(),
}

SUITE_SCAFFOLD_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/spec-suite.md",
)

SUITE_VALIDATE_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/spec-suite.md",
)

SUITE_EVIDENCE_CONTRACT_LOCATORS = (
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/templates/evidence-map.md",
)

SUITE_CARRIER_CONTRACT_LOCATORS = (
    "docs/methodology/harness/task-carrier-contract.md",
    "docs/methodology/templates/execution-breakdown.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
)

SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR = "docs/methodology/templates/scaffold/evidence-map.md"
SUITE_EVIDENCE_SCAFFOLD_TEMPLATE = REPO_ROOT / SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR

SUITE_VALIDATE_ADVISORY_ARTIFACTS = {
    "full": (
        "evidence-map.md",
        "consistency-analysis.md",
        "execution-breakdown.md",
        "task-carrier",
    ),
    "minimal": (),
    "not_applicable": (),
}

SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS = {
    "suite-index.md",
    "research.md",
    "contracts.md",
    "readiness-checklist.md",
}

SUITE_NOT_APPLICABLE_ALIASES = {
    "full-suite-artifacts": SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS,
    "full-path-artifacts": SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS,
    "suite-level": {"suite"},
    "whole-suite": {"suite"},
    "formal-suite": {"suite"},
}

SUITE_NOT_APPLICABLE_REQUIRED_FIELDS = {
    "rationale": ("rationale", "reason"),
    "consumer_boundary": ("consumer boundary", "consumer_boundary", "consumer"),
    "recheck_condition": ("recheck condition", "recheck_condition", "recheck"),
}

SUITE_MAPPING_STRATEGY_MARKERS = (
    "automated",
    "manual",
    "structural",
    "not_applicable",
    "not applicable",
    "test evidence",
    "behavior evidence",
    "validation evidence",
    "structural check",
    "manual evidence",
)

SUITE_SCENARIO_ID_PATTERN = re.compile(r"(?i)(?:^|\b)scenario\s+([A-Z][A-Z0-9_-]*\d[A-Z0-9_-]*)\b")
SUITE_ACCEPTANCE_ID_PATTERN = re.compile(r"(?i)(?:^|\b)(?:acceptance|criterion)\s+([A-Z][A-Z0-9_-]*\d[A-Z0-9_-]*)\b|\b(A\d+|AC[-_]?\d+)\s*:")

SUITE_VALIDATE_FAILURE_TAXONOMY: dict[str, dict[str, str]] = {
    "invalid_suite_item": {
        "default_result": "block",
        "failed_layer": "suite-input",
        "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
    },
    "missing_suite_path_decision": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
    },
    "missing_required_artifact": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite scaffold --target <repo> --item <item> --json",
    },
    "invalid_not_applicable_rationale": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "deferred_as_completed": {
        "default_result": "block",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_spec_plan_mapping": {
        "default_result": "block",
        "failed_layer": "spec/plan",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_optional_suite_artifact": {
        "default_result": "advisory",
        "failed_layer": "suite",
        "fallback_to": "loom suite validate --target <repo> --item <item> --json",
    },
    "missing_evidence_map": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence scaffold --target <repo> --item <item> --json",
    },
    "stale_evidence": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_fresh_verification_evidence": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "head_or_pr_drift": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_source_locator": {
        "default_result": "block",
        "failed_layer": "evidence_map",
        "fallback_to": "loom suite evidence validate --target <repo> --item <item> --json",
    },
    "missing_task_carrier_locator": {
        "default_result": "block",
        "failed_layer": "task_carrier",
        "fallback_to": "loom suite carrier validate --target <repo> --item <item> --json",
    },
    "carrier_truth_conflict": {
        "default_result": "block",
        "failed_layer": "task_carrier",
        "fallback_to": "loom suite carrier inspect --target <repo> --item <item> --json",
    },
}

SUITE_EVIDENCE_REQUIRED_TYPES = ("behavior_evidence", "test_evidence", "fresh_verification_input")
SUITE_EVIDENCE_FRESHNESS_VALUES = {"present", "stale", "missing", "conflict", "not_applicable"}
SUITE_EVIDENCE_EMPTY_MARKERS = {
    "",
    "-",
    "tbd",
    "todo",
    "unknown",
    "n/a",
    "na",
    "not set",
    "not_set",
    "not-set",
}
SUITE_CARRIER_TYPES = {
    "github_issue",
    "github_project_item",
    "checklist_item",
    "repo_tasks_md",
    "external_tracker",
    "not_applicable",
}
SUITE_CARRIER_STATUS_VALUES = {
    "pending",
    "in_progress",
    "done",
    "blocked",
    "deferred",
    "not_applicable",
}
SUITE_CARRIER_RELATIONSHIPS = {"primary", "mirror", "evidence_locator", "not_applicable"}
SUITE_CARRIER_TRUTH_SIGNALS = {
    "carrier_done",
    "project_done",
    "project_in_progress",
    "checklist_checked",
    "evidence_missing",
    "issue_open",
    "issue_closed",
    "pr_open",
    "pr_merged",
    "work_item_open",
    "work_item_terminal",
}
SUITE_CARRIER_TERMINAL_CHECKPOINTS = {"closed", "merged", "retired", "complete", "completed"}


def suite_relevant_text_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip():
            current.append(line.strip())
            continue
        if current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def suite_record_artifacts(block: str) -> set[str]:
    normalized = block.lower().replace("_", "-")
    artifacts = {
        artifact
        for artifact in SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS
        if artifact.lower() in normalized
    }
    for alias, alias_artifacts in SUITE_NOT_APPLICABLE_ALIASES.items():
        if alias in normalized or alias.replace("-", " ") in normalized:
            artifacts.update(alias_artifacts)
    return artifacts


def suite_record_required_fields(block: str) -> dict[str, bool]:
    lowered = block.lower().replace("_", " ")
    return {
        field: any(marker in lowered for marker in markers)
        for field, markers in SUITE_NOT_APPLICABLE_REQUIRED_FIELDS.items()
    }


def suite_applicability_records(paths: dict[str, list[Path]], target: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    not_applicable_records: list[dict[str, Any]] = []
    deferred_items: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for candidates in paths.values():
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            if not path.exists() or path.is_symlink() or not path.is_file():
                continue
            try:
                blocks = suite_relevant_text_blocks(path.read_text(encoding="utf-8"))
            except OSError:
                continue
            locator = repo_locator(path, target)
            for index, block in enumerate(blocks, start=1):
                lowered = block.lower()
                if "suite path:" in lowered and not any(marker in lowered for marker in ("rationale", "consumer", "recheck", "deferred")):
                    continue
                has_not_applicable = "not_applicable" in lowered or "not applicable" in lowered
                has_deferred = "deferred" in lowered
                artifacts = sorted(suite_record_artifacts(block))
                if has_not_applicable:
                    fields = suite_record_required_fields(block)
                    missing_fields = sorted(field for field, present in fields.items() if not present)
                    not_applicable_records.append(
                        {
                            "locator": locator,
                            "block": index,
                            "artifacts": artifacts,
                            "status": "valid" if artifacts and not missing_fields else "invalid",
                            "missing_fields": missing_fields,
                        }
                    )
                elif has_deferred:
                    deferred_items.append(
                        {
                            "locator": locator,
                            "block": index,
                            "artifacts": artifacts,
                            "status": "deferred",
                        }
                    )
    return not_applicable_records, deferred_items


def suite_covered_artifacts(records: list[dict[str, Any]]) -> set[str]:
    covered: set[str] = set()
    for record in records:
        if record.get("status") != "valid":
            continue
        artifacts = record.get("artifacts")
        if isinstance(artifacts, list):
            covered.update(str(artifact) for artifact in artifacts)
    return covered


def suite_unique_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip().rstrip(":").upper()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def suite_spec_plan_ids(spec_text: str) -> tuple[list[str], list[str]]:
    scenario_ids: list[str] = []
    acceptance_ids: list[str] = []
    for line in spec_text.splitlines():
        stripped = line.strip()
        scenario_match = SUITE_SCENARIO_ID_PATTERN.search(stripped)
        if scenario_match:
            scenario_ids.append(scenario_match.group(1))
        acceptance_match = SUITE_ACCEPTANCE_ID_PATTERN.search(stripped)
        if acceptance_match:
            acceptance_ids.append(next(group for group in acceptance_match.groups() if group))
    return suite_unique_ids(scenario_ids), suite_unique_ids(acceptance_ids)


def suite_plan_mapping_lines(plan_text: str, identifier: str) -> list[str]:
    token = re.escape(identifier)
    id_pattern = re.compile(rf"(?i)(?:^|[^A-Z0-9_-]){token}(?:[^A-Z0-9_-]|$)")
    lines: list[str] = []
    for line in plan_text.splitlines():
        lowered = line.lower()
        if not id_pattern.search(line):
            continue
        if "->" not in line and "mapping" not in lowered and "strategy" not in lowered:
            continue
        if not any(marker in lowered for marker in SUITE_MAPPING_STRATEGY_MARKERS):
            continue
        lines.append(line.strip())
    return lines


def suite_spec_plan_mapping(paths: dict[str, list[Path]], target: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec_locator = first_existing_locator(paths.get("spec.md", []), target)
    plan_locator = first_existing_locator(paths.get("plan.md", []), target)
    mapping = {
        "spec_locator": spec_locator,
        "plan_locator": plan_locator,
        "required_scenarios": [],
        "required_acceptance": [],
        "mapped_scenarios": [],
        "mapped_acceptance": [],
        "missing_scenarios": [],
        "missing_acceptance": [],
    }
    if spec_locator is None or plan_locator is None:
        return mapping, []

    spec_path = next((path for path in paths.get("spec.md", []) if path.exists() and path.is_file() and not path.is_symlink()), None)
    plan_path = next((path for path in paths.get("plan.md", []) if path.exists() and path.is_file() and not path.is_symlink()), None)
    if spec_path is None or plan_path is None:
        return mapping, []

    try:
        spec_text = spec_path.read_text(encoding="utf-8")
        plan_text = plan_path.read_text(encoding="utf-8")
    except OSError:
        return mapping, []

    scenario_ids, acceptance_ids = suite_spec_plan_ids(spec_text)
    mapped_scenarios: list[dict[str, Any]] = []
    missing_scenarios: list[str] = []
    for scenario_id in scenario_ids:
        lines = suite_plan_mapping_lines(plan_text, scenario_id)
        if lines:
            mapped_scenarios.append({"id": scenario_id, "plan_locator": plan_locator, "mapping": lines[0]})
        else:
            missing_scenarios.append(scenario_id)

    mapped_acceptance: list[dict[str, Any]] = []
    missing_acceptance: list[str] = []
    for acceptance_id in acceptance_ids:
        lines = suite_plan_mapping_lines(plan_text, acceptance_id)
        if lines:
            mapped_acceptance.append({"id": acceptance_id, "plan_locator": plan_locator, "mapping": lines[0]})
        else:
            missing_acceptance.append(acceptance_id)

    mapping.update(
        {
            "required_scenarios": scenario_ids,
            "required_acceptance": acceptance_ids,
            "mapped_scenarios": mapped_scenarios,
            "mapped_acceptance": mapped_acceptance,
            "missing_scenarios": missing_scenarios,
            "missing_acceptance": missing_acceptance,
        }
    )
    blocking_gaps: list[dict[str, Any]] = []
    for scenario_id in missing_scenarios:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-missing-scenario-mapping-{scenario_id.lower().replace('_', '-')}",
                classification="missing",
                failure_kind="missing_spec_plan_mapping",
                source_locator=spec_locator,
                consumer_impact=f"spec review cannot verify that scenario {scenario_id} maps to a plan validation strategy",
                remediation_direction=f"Map scenario {scenario_id} in plan.md to automated, manual, structural, or not_applicable validation.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
                surface="spec/plan",
                binding="suite-validate-spec-plan-mapping",
            )
        )
    for acceptance_id in missing_acceptance:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-missing-acceptance-mapping-{acceptance_id.lower().replace('_', '-')}",
                classification="missing",
                failure_kind="missing_spec_plan_mapping",
                source_locator=spec_locator,
                consumer_impact=f"spec review cannot verify that acceptance {acceptance_id} maps to a plan test strategy",
                remediation_direction=f"Map acceptance {acceptance_id} in plan.md to test evidence, structural check, manual evidence, or not_applicable.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
                surface="spec/plan",
                binding="suite-validate-spec-plan-mapping",
            )
        )
    return mapping, blocking_gaps


def suite_scaffold_payload(target: Path, item: str, suite_path: str, *, apply: bool) -> tuple[str, dict[str, Any], str | None]:
    item_error = suite_item_segment_error(item)
    if item_error:
        payload = {
            "suite_path": suite_path,
            "artifact_root": None,
            "suite_locator": None,
            "planned_writes": [],
            "source_templates": [],
            "consumed_locators": list(SUITE_SCAFFOLD_CONTRACT_LOCATORS),
            "overwrite_policy": {
                "mode": "preserve_existing",
                "allows_overwrite": False,
                "existing_files": [],
                "ambiguous_overwrite": "fail_closed",
            },
            "apply_required": not apply,
            "apply": apply,
            "rollback_note": "No files were created because the suite item did not resolve to a single repo-local path segment.",
            "created_locators": [],
            "missing_inputs": [item_error],
            "advisory_gaps": [],
        }
        return "Suite scaffold failed closed before resolving artifact paths.", payload, "invalid_suite_item"

    suite_root = target / ".loom" / "specs" / item
    artifacts = SUITE_SCAFFOLD_ARTIFACTS[suite_path]
    required_artifacts = SUITE_SCAFFOLD_REQUIRED_ARTIFACTS[suite_path]
    conditional_artifacts = SUITE_SCAFFOLD_CONDITIONAL_ARTIFACTS[suite_path]
    planned_writes: list[dict[str, Any]] = []
    source_templates: list[dict[str, str]] = []
    existing_files: list[str] = []
    created_locators: list[str] = []
    missing_inputs: list[str] = []
    consumed_locators = list(SUITE_SCAFFOLD_CONTRACT_LOCATORS)

    for artifact in artifacts:
        template = SUITE_SCAFFOLD_TEMPLATES[artifact]
        if not template.exists() or not template.is_file():
            missing_inputs.append(f"missing scaffold template: {template.relative_to(REPO_ROOT).as_posix()}")
        destination = suite_root / artifact
        for component in (target / ".loom", target / ".loom" / "specs", suite_root, destination):
            if component.is_symlink():
                missing_inputs.append(f"scaffold path must not traverse symlink: {repo_locator(component, target)}")
        if not destination.exists() and destination.parent.exists() and not destination.parent.is_dir():
            missing_inputs.append(f"scaffold parent is not a directory: {repo_locator(destination.parent, target)}")
        if destination.exists() and not destination.is_file():
            missing_inputs.append(f"scaffold artifact is not a regular file: {repo_locator(destination, target)}")

    for artifact in artifacts:
        destination = suite_root / artifact
        destination_locator = repo_locator(destination, target)
        template = SUITE_SCAFFOLD_TEMPLATES[artifact]
        template_locator = SUITE_SCAFFOLD_TEMPLATE_LOCATORS[artifact]
        exists = destination.exists()
        if exists:
            existing_files.append(destination_locator)
        if apply and not exists and not missing_inputs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            created_locators.append(destination_locator)
        planned_writes.append(
            {
                "artifact": artifact,
                "locator": destination_locator,
                "source_template": template_locator,
                "status": "exists" if exists else ("created" if apply and not missing_inputs else "would_create"),
                "planned_action": "preserve_existing" if exists else "create",
                "would_write": not exists,
                "wrote": apply and not exists and not missing_inputs,
                "overwrite_policy": "preserve_existing",
                "requirement": "required" if artifact in required_artifacts else "conditional",
            }
        )
        source_templates.append(
            {
                "artifact": artifact,
                "locator": template_locator,
            }
        )

    overwrite_policy = {
        "mode": "preserve_existing",
        "allows_overwrite": False,
        "existing_files": existing_files,
        "ambiguous_overwrite": "fail_closed",
    }
    payload = {
        "suite_path": suite_path,
        "artifact_root": repo_locator(suite_root, target),
        "suite_locator": repo_locator(suite_root, target),
        "planned_writes": planned_writes,
        "source_templates": source_templates,
        "required_artifacts": list(required_artifacts),
        "conditional_artifacts": list(conditional_artifacts),
        "consumed_locators": consumed_locators,
        "overwrite_policy": overwrite_policy,
        "apply_required": not apply,
        "apply": apply,
        "rollback_note": (
            "Dry-run only; no files were created. If applied later, rollback is deleting the created repo-relative locators before they are consumed as authored truth."
            if not apply
            else "Rollback is deleting the created repo-relative locators before they are consumed as authored truth; preserved existing files were not modified."
        ),
        "created_locators": created_locators,
        "missing_inputs": missing_inputs,
        "advisory_gaps": [],
    }
    if missing_inputs:
        summary = "Suite scaffold apply failed closed before writing artifacts." if apply else "Suite scaffold dry-run found unavailable scaffold inputs."
        return summary, payload, "missing_scaffold_inputs"
    if apply:
        summary = f"Suite scaffold applied {suite_path} suite artifacts with preserve-existing overwrite policy."
    else:
        summary = f"Suite scaffold dry-run planned {suite_path} suite artifacts without mutating the repository."
    return summary, payload, None


def suite_scaffold_dry_run_payload(target: Path, item: str, suite_path: str) -> tuple[str, dict[str, Any]]:
    summary, payload, _ = suite_scaffold_payload(target, item, suite_path, apply=False)
    return summary, payload


def suite_evidence_scaffold_content(target: Path, item: str, inspect_payload: dict[str, Any]) -> str:
    suite_path = str(inspect_payload.get("suite_path") or "unknown")
    suite_locator = str(inspect_payload.get("suite_locator") or f".loom/specs/{item}")
    spec_locator = str(inspect_payload.get("spec_locator") or f".loom/specs/{item}/spec.md")
    plan_locator = str(inspect_payload.get("plan_locator") or f".loom/specs/{item}/plan.md")
    path_decision_locator = str(inspect_payload.get("path_decision_locator") or "not_authored")
    task_carriers = inspect_payload.get("task_carrier_locators")
    task_carrier_locator = ", ".join(str(locator) for locator in task_carriers) if isinstance(task_carriers, list) and task_carriers else "not_applicable rationale required"
    template_text = SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "- Work Item locator:": f"- Work Item locator: .loom/work-items/{item}.md",
        "- FR / parent locator:": "- FR / parent locator:",
        "- Scope:": "- Scope: current Work Item scope; replace with authored scope before review consumption.",
        "- Suite path:": f"- Suite path: {suite_path}",
        "- Current `HEAD`:": "- Current `HEAD`: fill with current head before merge-ready consumption.",
        "- PR locator, or `not_applicable` rationale:": "- PR locator, or `not_applicable` rationale: fill when PR exists; otherwise author not_applicable rationale.",
        "- Host state locator, or `not_applicable` rationale:": "- Host state locator, or `not_applicable` rationale: fill when host state exists; otherwise author not_applicable rationale.",
        "| `spec.md` |  | required |  |  |": f"| `spec.md` | {spec_locator} | required | suite inspect | Bind to current Work Item, scope, and head before consumption. |",
        "| `plan.md` |  | required |  |  |": f"| `plan.md` | {plan_locator} | required | suite inspect | Bind to current validation strategy and head before consumption. |",
        "| suite path decision |  | candidate / optional / not_applicable |  |  |": f"| suite path decision | {path_decision_locator} | candidate / optional / not_applicable | suite inspect | Recheck when suite path changes. |",
        "| execution breakdown / task carrier |  | candidate / optional / deferred / not_applicable |  |  |": f"| execution breakdown / task carrier | {task_carrier_locator} | candidate / optional / deferred / not_applicable | suite inspect | Recheck when task carrier contract is consumed. |",
        "| review record |  | optional / required / not_applicable |  |  |": "| review record |  | optional / required / not_applicable | authored review truth | Required only after review consumption. |",
        "| merge-ready basis |  | optional / required / not_applicable |  |  |": "| merge-ready basis |  | optional / required / not_applicable | merge-ready truth | Required only for merge-ready or closeout consumption. |",
        "| host state |  | required / not_applicable |  |  |": "| host state |  | required / not_applicable | host mirror | Required when PR / issue / Project exists. |",
        "| EV-001 | behavior_evidence |  | spec scenario / acceptance locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |": f"| EV-001 | behavior_evidence |  | {spec_locator} scenario / acceptance locator | {item} / scope / head / PR | missing | review / merge-ready / closeout / status | Add behavior evidence source locator and binding before validation. |",
        "| EV-002 | test_evidence |  | plan validation / test strategy locator | Work Item / scope / head / PR | present / stale / missing / conflict / not_applicable | review / merge-ready / closeout / status |  |": f"| EV-002 | test_evidence |  | {plan_locator} validation / test strategy locator | {item} / scope / head / PR | missing | review / merge-ready / closeout / status | Add test evidence source locator and rerun validation before consumption. |",
        "| EV-003 | fresh_verification_input |  | evidence row ids | head / reviewed head / PR head / validation summary | present / stale / missing / conflict / not_applicable | merge-ready / closeout / status |  |": "| EV-003 | fresh_verification_input |  | EV-001 EV-002 | head / reviewed head / PR head / validation summary | missing | merge-ready / closeout / status | Mark present only after behavior and test evidence are present for the current object. |",
    }
    for old, new in replacements.items():
        template_text = template_text.replace(old, new)
    return template_text.rstrip() + "\n"


def suite_evidence_scaffold_payload(target: Path, item: str, *, apply: bool) -> tuple[str, dict[str, Any], str | None]:
    item_error = suite_item_segment_error(item)
    if item_error:
        payload = {
            "artifact_root": None,
            "suite_locator": None,
            "evidence_map_locator": None,
            "planned_writes": [],
            "source_templates": [],
            "consumed_locators": [*SUITE_EVIDENCE_CONTRACT_LOCATORS, SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR],
            "consumed_suite_locators": {},
            "overwrite_policy": {
                "mode": "preserve_existing",
                "allows_overwrite": False,
                "existing_files": [],
                "ambiguous_overwrite": "fail_closed",
            },
            "apply_required": not apply,
            "apply": apply,
            "rollback_note": "No files were created because the suite item did not resolve to a single repo-local path segment.",
            "created_locators": [],
            "missing_inputs": [item_error],
            "advisory_gaps": [],
            "seed_rows": [],
            "initial_freshness_policy": "scaffold never marks evidence present",
        }
        return "Suite evidence scaffold failed closed before resolving artifact paths.", payload, "invalid_suite_item"

    inspect_summary, inspect_payload = suite_inspect_payload(target, item)
    suite_root = target / ".loom" / "specs" / item
    destination = suite_root / "evidence-map.md"
    destination_locator = repo_locator(destination, target)
    missing_inputs: list[str] = []

    if not SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.exists() or not SUITE_EVIDENCE_SCAFFOLD_TEMPLATE.is_file():
        missing_inputs.append(f"missing scaffold template: {SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR}")
    for component in (target / ".loom", target / ".loom" / "specs", suite_root, destination):
        if component.is_symlink():
            missing_inputs.append(f"scaffold path must not traverse symlink: {repo_locator(component, target)}")
    if not destination.exists() and destination.parent.exists() and not destination.parent.is_dir():
        missing_inputs.append(f"scaffold parent is not a directory: {repo_locator(destination.parent, target)}")
    if destination.exists() and not destination.is_file():
        missing_inputs.append(f"scaffold artifact is not a regular file: {destination_locator}")

    exists = destination.exists()
    created_locators: list[str] = []
    if apply and not exists and not missing_inputs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(suite_evidence_scaffold_content(target, item, inspect_payload), encoding="utf-8")
        created_locators.append(destination_locator)

    existing_files = [destination_locator] if exists else []
    consumed_suite_locators = {
        "suite_path": inspect_payload.get("suite_path"),
        "suite_locator": inspect_payload.get("suite_locator"),
        "path_decision_locator": inspect_payload.get("path_decision_locator"),
        "spec_locator": inspect_payload.get("spec_locator") or f".loom/specs/{item}/spec.md",
        "plan_locator": inspect_payload.get("plan_locator") or f".loom/specs/{item}/plan.md",
        "task_carrier_locators": inspect_payload.get("task_carrier_locators", []),
    }
    payload = {
        "suite_path": inspect_payload.get("suite_path"),
        "artifact_root": repo_locator(suite_root, target),
        "suite_locator": inspect_payload.get("suite_locator") or repo_locator(suite_root, target),
        "evidence_map_locator": destination_locator,
        "planned_writes": [
            {
                "artifact": "evidence-map.md",
                "locator": destination_locator,
                "source_template": SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR,
                "status": "exists" if exists else ("created" if apply and not missing_inputs else "would_create"),
                "planned_action": "preserve_existing" if exists else "create",
                "would_write": not exists,
                "wrote": apply and not exists and not missing_inputs,
                "overwrite_policy": "preserve_existing",
                "requirement": "evidence_map",
                "initial_freshness": "missing",
            }
        ],
        "source_templates": [{"artifact": "evidence-map.md", "locator": SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR}],
        "consumed_locators": [*SUITE_EVIDENCE_CONTRACT_LOCATORS, SUITE_EVIDENCE_SCAFFOLD_TEMPLATE_LOCATOR],
        "consumed_suite_locators": consumed_suite_locators,
        "overwrite_policy": {
            "mode": "preserve_existing",
            "allows_overwrite": False,
            "existing_files": existing_files,
            "ambiguous_overwrite": "fail_closed",
        },
        "apply_required": not apply,
        "apply": apply,
        "rollback_note": (
            "Dry-run only; no files were created. If applied later, rollback is deleting the created repo-relative evidence-map locator before it is consumed as authored truth."
            if not apply
            else "Rollback is deleting the created repo-relative evidence-map locator before it is consumed as authored truth; preserved existing files were not modified."
        ),
        "created_locators": created_locators,
        "missing_inputs": missing_inputs,
        "advisory_gaps": [],
        "seed_rows": [
            {"evidence_id": "EV-001", "evidence_type": "behavior_evidence", "freshness": "missing"},
            {"evidence_id": "EV-002", "evidence_type": "test_evidence", "freshness": "missing"},
            {"evidence_id": "EV-003", "evidence_type": "fresh_verification_input", "freshness": "missing"},
        ],
        "initial_freshness_policy": "scaffold never marks evidence present",
        "inspect_summary": inspect_summary,
    }
    if missing_inputs:
        summary = "Suite evidence scaffold apply failed closed before writing artifacts." if apply else "Suite evidence scaffold dry-run found unavailable scaffold inputs."
        return summary, payload, "missing_scaffold_inputs"
    if apply:
        summary = "Suite evidence scaffold applied evidence-map artifact with preserve-existing overwrite policy."
    else:
        summary = "Suite evidence scaffold dry-run planned evidence-map artifact without mutating the repository."
    return summary, payload, None


def suite_inspect_payload(target: Path, item: str | None) -> tuple[str, dict[str, Any]]:
    paths = suite_artifact_paths(target, item)
    suite_index = paths.get("suite-index.md", [None])[0]
    spec = paths.get("spec.md", [None])[0]
    plan = paths.get("plan.md", [None])[0]

    path_decision_locator: str | None = None
    suite_path = "unknown"
    path_decisions: list[dict[str, Any]] = []
    decision_values: list[str] = []
    invalid_decision_locators: list[str] = []
    for path in (suite_index, spec, plan):
        if path is None:
            continue
        if path.exists() and (path.is_symlink() or not path.is_file()):
            if path == suite_index:
                locator = repo_locator(path, target)
                invalid_decision_locators.append(locator)
                path_decisions.append(
                    {
                        "locator": locator,
                        "value": None,
                        "status": "invalid",
                        "reason": "path decision candidate is not a regular file",
                    }
                )
            continue
        values, invalid_values = read_suite_path_marker_values(path)
        if not values and not invalid_values:
            continue
        locator = repo_locator(path, target)
        for value in values:
            path_decisions.append({"locator": locator, "value": value, "status": "present"})
            decision_values.append(value)
        for value in invalid_values:
            invalid_decision_locators.append(locator)
            path_decisions.append({"locator": locator, "value": value, "status": "invalid"})

    unique_decision_values = sorted(set(decision_values))
    if len(unique_decision_values) == 1 and not invalid_decision_locators:
        suite_path = unique_decision_values[0]
        path_decision_locator = next(
            (entry["locator"] for entry in path_decisions if entry.get("value") == suite_path),
            None,
        )

    required = SUITE_REQUIRED_ARTIFACTS_BY_PATH.get(suite_path, set())
    conditional = SUITE_CONDITIONAL_ARTIFACTS_BY_PATH.get(suite_path, set())
    advisory = set(SUITE_VALIDATE_ADVISORY_ARTIFACTS.get(suite_path, ()))

    artifact_inventory: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    locators: dict[str, Any] = {}
    if invalid_decision_locators or len(unique_decision_values) > 1:
        missing_inputs.append("suite_path_decision")
        for locator in sorted(set(invalid_decision_locators)):
            missing_inputs.append(f"invalid_suite_path_decision:{locator}")
        if len(unique_decision_values) > 1:
            for entry in path_decisions:
                if entry.get("status") == "present":
                    missing_inputs.append(f"conflicting_suite_path_decision:{entry['locator']}")
    for artifact, candidates in paths.items():
        locator, invalid_locator = first_artifact_locator_or_invalid(candidates, target)
        is_required = artifact in required
        is_conditional = artifact in conditional
        is_advisory = artifact in advisory
        requirement = (
            "required"
            if is_required
            else ("conditional" if is_conditional else ("extension" if is_advisory else "optional"))
        )
        if locator is not None:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": locator,
                    "status": "present",
                    "required": is_required,
                    "requirement": requirement,
                }
            )
        elif invalid_locator is not None:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": invalid_locator,
                    "status": "invalid",
                    "required": is_required,
                    "requirement": requirement,
                }
            )
            if is_required:
                missing_inputs.append(f"required_artifact:{invalid_locator}")
        elif is_required:
            expected = repo_locator(candidates[0], target)
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": expected,
                    "status": "missing",
                    "required": True,
                    "requirement": requirement,
                }
            )
            missing_inputs.append(f"required_artifact:{expected}")
        elif is_conditional or is_advisory:
            artifact_inventory.append(
                {
                    "artifact": artifact,
                    "locator": repo_locator(candidates[0], target),
                    "status": "absent",
                    "required": False,
                    "requirement": requirement,
                }
            )

        key = artifact.replace("-", "_").removesuffix(".md") + "_locator"
        if artifact == "task-carrier":
            locators["task_carrier_locators"] = [locator] if locator is not None else []
        else:
            locators[key] = locator

    if suite_path == "unknown" and "suite_path_decision" not in missing_inputs:
        missing_inputs.insert(0, "suite_path_decision")

    advisory_gaps = []
    if suite_path == "unknown":
        advisory_gaps.append(
            {
                "id": "suite-inspect-unknown-path",
                "classification": "missing",
                "failure_kind": "missing_suite_path_decision",
                "surface": "suite",
                "source_locator": None,
                "consumer_impact": "inspect-only",
                "remediation_direction": "Author or link a suite path decision before readiness validation.",
                "fallback_to": "loom suite inspect --target <repo> --item <item> --json",
            }
        )
    for missing in missing_inputs:
        if not missing.startswith("required_artifact:"):
            continue
        locator = missing.split(":", 1)[1]
        advisory_gaps.append(
            {
                "id": f"suite-inspect-missing-{Path(locator).name}",
                "classification": "missing",
                "failure_kind": "missing_required_artifact",
                "surface": "suite",
                "source_locator": locator,
                "consumer_impact": "inspect-only",
                "remediation_direction": "Run suite scaffold dry-run or author the missing repo-relative artifact before readiness validation.",
                "fallback_to": "loom suite scaffold --target <repo> --item <item> --json",
            }
        )

    summary_by_path = {
        "full": "Suite inspect found a full suite path decision.",
        "minimal": "Suite inspect found a minimal suite path decision.",
        "not_applicable": "Suite inspect found a not_applicable suite path decision.",
        "unknown": "Suite state is unknown; no suite path decision was derived.",
    }
    summary = summary_by_path.get(suite_path, summary_by_path["unknown"])
    if any(entry["status"] == "missing" for entry in artifact_inventory):
        summary = f"{summary} Missing expected artifact locators are reported for later validation."

    payload = {
        "suite_path": suite_path,
        "suite_locator": locators.get("suite_index_locator"),
        "path_decision_locator": path_decision_locator,
        "path_decisions": path_decisions,
        "artifact_inventory": artifact_inventory,
        "not_applicable_rationale": [],
        "deferred_items": [],
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
        **locators,
    }
    return summary, payload


def suite_validate_finding(
    *,
    gap_id: str,
    classification: str,
    failure_kind: str,
    source_locator: str | None,
    consumer_impact: str,
    remediation_direction: str,
    fallback_to: str,
    surface: str = "suite",
    binding: str = "suite-validate-core",
) -> dict[str, Any]:
    taxonomy = SUITE_VALIDATE_FAILURE_TAXONOMY.get(failure_kind, {})
    default_result = taxonomy.get("default_result", "block" if classification != "advisory" else "advisory")
    failed_layer = taxonomy.get("failed_layer", surface)
    return {
        "id": gap_id,
        "classification": classification,
        "failure_kind": failure_kind,
        "default_result": default_result,
        "failed_layer": failed_layer,
        "surface": surface,
        "source_locator": source_locator,
        "conflicting_locator": None,
        "freshness": "missing" if classification == "missing" else None,
        "binding": binding,
        "consumer_impact": consumer_impact,
        "remediation_direction": remediation_direction,
        "fallback_to": fallback_to,
    }


def suite_failure_taxonomy_for_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taxonomy_entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for finding in findings:
        failure_kind = str(finding.get("failure_kind") or "")
        if not failure_kind or failure_kind in seen:
            continue
        seen.add(failure_kind)
        taxonomy = SUITE_VALIDATE_FAILURE_TAXONOMY.get(failure_kind, {})
        taxonomy_entries.append(
            {
                "failure_kind": failure_kind,
                "classification": finding.get("classification"),
                "default_result": finding.get("default_result") or taxonomy.get("default_result"),
                "failed_layer": finding.get("failed_layer") or taxonomy.get("failed_layer"),
                "source_locator": finding.get("source_locator"),
                "consumer_impact": finding.get("consumer_impact"),
                "remediation_direction": finding.get("remediation_direction"),
                "fallback_to": finding.get("fallback_to") or taxonomy.get("fallback_to"),
                "binding": finding.get("binding"),
            }
        )
    return taxonomy_entries


def suite_evidence_path(target: Path, item: str | None) -> Path | None:
    return suite_artifact_paths(target, item).get("evidence-map.md", [None])[0]


def normalized_table_cell(value: str) -> str:
    return re.sub(r"<br\s*/?>", " ", value.strip(), flags=re.IGNORECASE).replace("`", "").strip()


def normalize_table_header(value: str) -> str:
    normalized = normalized_table_cell(value).lower().replace("-", "_").replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", normalized)


def is_empty_evidence_value(value: Any) -> bool:
    return str(value or "").strip().lower() in SUITE_EVIDENCE_EMPTY_MARKERS


def git_head_sha_for_target(target: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    head = completed.stdout.strip()
    return head if re.fullmatch(r"[0-9a-f]{40}", head) else None


def latest_validation_summary_for_item(target: Path, item: str) -> str | None:
    progress_path = target / ".loom" / "progress" / f"{item}.md"
    try:
        text = progress_path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        if line.startswith("- Latest Validation Summary:"):
            return line.split(":", 1)[1].strip()
    return None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def evidence_binding_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "")
        for field in (
            "binding",
            "freshness_rule",
            "provenance",
            "consumer_boundary",
        )
    )


def binding_sha_matches(observed: str, expected: str) -> bool:
    return expected.startswith(observed.lower()) if len(observed) < len(expected) else observed.lower() == expected


def extract_binding_shas(text: str, names: tuple[str, ...]) -> list[str]:
    name_pattern = "|".join(re.escape(name) for name in names)
    return [
        match.group(2).lower()
        for match in re.finditer(
            rf"\b({name_pattern})\b\s*[:=]\s*([0-9a-f]{{7,64}})",
            text,
            flags=re.IGNORECASE,
        )
    ]


def is_repo_local_source_locator(source_locator: str, source_kind: str) -> bool:
    if source_kind == "repo_file":
        return True
    if not source_locator or re.match(r"^[a-z][a-z0-9+.-]*:", source_locator, re.IGNORECASE):
        return False
    if source_locator.startswith((".", "/")):
        return True
    return " " not in source_locator and "/" in source_locator


def split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [normalized_table_cell(cell) for cell in stripped.strip("|").split("|")]


def is_markdown_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_evidence_map_rows(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        header_cells = split_markdown_table_row(lines[index])
        if not header_cells:
            index += 1
            continue
        if index + 1 >= len(lines):
            break
        separator_cells = split_markdown_table_row(lines[index + 1])
        if not is_markdown_separator_row(separator_cells):
            index += 1
            continue

        headers = [normalize_table_header(cell) for cell in header_cells]
        if "evidence_id" not in headers and "evidenceid" not in headers and "type" not in headers:
            index += 2
            continue

        index += 2
        while index < len(lines):
            cells = split_markdown_table_row(lines[index])
            if not cells or is_markdown_separator_row(cells):
                break
            mapped = {headers[cell_index]: cells[cell_index] for cell_index in range(min(len(headers), len(cells)))}
            evidence_id = mapped.get("evidence_id") or mapped.get("evidenceid") or mapped.get("id") or ""
            evidence_type = mapped.get("type") or mapped.get("evidence_type") or ""
            source_locator = mapped.get("source_locator") or mapped.get("source") or ""
            freshness = (mapped.get("freshness") or "").strip().lower().replace(" ", "_")
            row_locator = f"{repo_locator(path, target)}:{index + 1}"
            source_exists = None
            source_kind = mapped.get("source_kind") or mapped.get("sourcekind") or None
            if source_locator and not re.match(r"^[a-z][a-z0-9+.-]*:", source_locator, re.IGNORECASE):
                source_path = (target / source_locator).resolve()
                try:
                    source_exists = source_path.is_relative_to(target.resolve()) and source_path.exists()
                except OSError:
                    source_exists = False
            rows.append(
                {
                    "evidence_id": evidence_id,
                    "evidence_type": evidence_type.strip().lower(),
                    "source_locator": source_locator,
                    "source_kind": source_kind,
                    "consumes": mapped.get("consumes") or "",
                    "binding": mapped.get("binding") or "",
                    "freshness": freshness,
                    "freshness_rule": mapped.get("freshness_rule") or mapped.get("freshnessrule") or "",
                    "provenance": mapped.get("provenance") or "",
                    "consumer_boundary": mapped.get("consumer_boundary") or mapped.get("consumerboundary") or "",
                    "remediation_direction": mapped.get("remediation_direction") or mapped.get("remediationdirection") or "",
                    "locator": row_locator,
                    "source_exists": source_exists,
                }
            )
            index += 1
        continue
    return rows


def suite_evidence_inspect_payload(target: Path, item: str) -> tuple[str, dict[str, Any]]:
    evidence_path = suite_evidence_path(target, item)
    evidence_locator = repo_locator(evidence_path, target) if evidence_path else None
    status = "missing"
    rows: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    advisory_gaps: list[dict[str, Any]] = []

    if evidence_path is None:
        evidence_locator = f".loom/specs/{item}/evidence-map.md"
        missing_inputs.append("evidence_map_locator")
    elif evidence_path.exists() and (evidence_path.is_symlink() or not evidence_path.is_file()):
        status = "invalid"
        missing_inputs.append(f"invalid_evidence_map:{evidence_locator}")
    elif evidence_path.exists():
        status = "present"
        rows = parse_evidence_map_rows(evidence_path, target)
        if not rows:
            missing_inputs.append(f"evidence_rows:{evidence_locator}")
    else:
        missing_inputs.append("evidence_map_locator")

    if missing_inputs:
        advisory_gaps.append(
            suite_validate_finding(
                gap_id="suite-evidence-inspect-missing-evidence-map",
                classification="missing",
                failure_kind="missing_evidence_map",
                source_locator=evidence_locator,
                consumer_impact="inspect-only",
                remediation_direction="Author or scaffold evidence-map rows before evidence readiness validation.",
                fallback_to="loom suite evidence scaffold --target <repo> --item <item> --json",
                surface="evidence_map",
                binding="suite-evidence-inspect",
            )
        )

    payload = {
        "evidence_map": {
            "locator": evidence_locator,
            "status": status,
            "row_count": len(rows),
        },
        "evidence_map_locator": evidence_locator if status == "present" else None,
        "rows": rows,
        "required_evidence_types": list(SUITE_EVIDENCE_REQUIRED_TYPES),
        "freshness_values": sorted(SUITE_EVIDENCE_FRESHNESS_VALUES),
        "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
    }
    summary = "Suite evidence inspect found an evidence-map." if status == "present" else "Suite evidence inspect did not find a usable evidence-map."
    return summary, payload


def suite_evidence_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-evidence-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="evidence validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite evidence inspect --target <repo> --item <item> --json",
                surface="evidence_map",
                binding="suite-evidence-validate",
            )
        ]
        payload = {
            "evidence_map": {"locator": None, "status": "invalid", "row_count": 0},
            "rows": [],
            "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite evidence validate failed closed before resolving evidence-map.",
            "block",
            payload,
            "evidence_map",
            "invalid_suite_item",
            ["loom suite evidence inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_evidence_inspect_payload(target, item)
    rows = inspect_payload.get("rows", [])
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    evidence_locator = inspect_payload.get("evidence_map", {}).get("locator")
    current_head = git_head_sha_for_target(target)
    validation_summary = latest_validation_summary_for_item(target, item)
    validation_summary_sha256 = sha256_text(validation_summary) if validation_summary else None
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []

    def add_gap(
        *,
        gap_id: str,
        classification: str,
        failure_kind: str,
        source_locator: str | None,
        impact: str,
        remediation: str,
        fallback: str = "loom suite evidence validate --target <repo> --item <item> --json",
    ) -> None:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=gap_id,
                classification=classification,
                failure_kind=failure_kind,
                source_locator=source_locator,
                consumer_impact=impact,
                remediation_direction=remediation,
                fallback_to=fallback,
                surface="evidence_map",
                binding="suite-evidence-validate",
            )
        )

    if missing_inputs:
        add_gap(
            gap_id="suite-evidence-validate-missing-evidence-map",
            classification="missing",
            failure_kind="missing_evidence_map",
            source_locator=evidence_locator,
            impact="merge-ready evidence validation cannot consume missing or unreadable evidence-map rows",
            remediation="Author or scaffold evidence-map rows before evidence readiness validation.",
            fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
        )

    required_row_fields = (
        "evidence_id",
        "evidence_type",
        "source_locator",
        "consumes",
        "binding",
        "freshness",
        "consumer_boundary",
        "remediation_direction",
    )
    present_by_type: dict[str, list[dict[str, Any]]] = {evidence_type: [] for evidence_type in SUITE_EVIDENCE_REQUIRED_TYPES}
    present_ids_by_type: dict[str, set[str]] = {evidence_type: set() for evidence_type in SUITE_EVIDENCE_REQUIRED_TYPES}

    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_locator = str(row.get("locator") or evidence_locator or "")
            evidence_type = str(row.get("evidence_type") or "").strip().lower()
            freshness = str(row.get("freshness") or "").strip().lower()
            missing_fields = [field for field in required_row_fields if is_empty_evidence_value(row.get(field))]
            if missing_fields:
                add_gap(
                    gap_id=f"suite-evidence-validate-missing-fields-{row.get('evidence_id') or Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_evidence_map",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume evidence rows with incomplete binding, freshness, or consumer boundary fields",
                    remediation=f"Fill evidence-map fields before validation; missing: {', '.join(missing_fields)}.",
                    fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
                )
                continue
            if freshness not in SUITE_EVIDENCE_FRESHNESS_VALUES:
                add_gap(
                    gap_id=f"suite-evidence-validate-invalid-freshness-{row.get('evidence_id')}",
                    classification="missing",
                    failure_kind="missing_evidence_map",
                    source_locator=row_locator,
                    impact="merge-ready cannot classify evidence freshness from an unknown value",
                    remediation="Use one of present, stale, missing, conflict, or not_applicable for evidence freshness.",
                    fallback="loom suite evidence validate --target <repo> --item <item> --json",
                )
                continue
            binding_drift = False
            if freshness == "present":
                source_locator = str(row.get("source_locator") or "")
                source_kind = str(row.get("source_kind") or "").strip().lower()
                if row.get("source_exists") is False and is_repo_local_source_locator(source_locator, source_kind):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-missing-source-{row.get('evidence_id')}",
                        classification="missing",
                        failure_kind="missing_source_locator",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume present evidence whose repo-local source locator is missing",
                        remediation="Restore the cited source locator or update evidence-map to a current readable locator.",
                    )

                binding_text = evidence_binding_text(row)
                binding_text_lower = binding_text.lower()
                explicit_stale_markers = (
                    "previous head",
                    "old head",
                    "stale head",
                    "previous pr head",
                    "old pr head",
                    "stale pr head",
                    "old validation summary",
                    "stale validation summary",
                )
                if any(marker in binding_text_lower for marker in explicit_stale_markers):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-stale-binding-{row.get('evidence_id')}",
                        classification="stale",
                        failure_kind="stale_evidence",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume evidence with an explicitly stale HEAD, PR head, or validation summary binding",
                        remediation="Refresh the evidence binding to the current HEAD, PR head, reviewed head, and validation summary.",
                    )

                head_checks = (
                    ("head", extract_binding_shas(binding_text, ("head_sha", "current_head", "head"))),
                    ("pr_head", extract_binding_shas(binding_text, ("pr_head_sha", "pr_head"))),
                    ("reviewed_head", extract_binding_shas(binding_text, ("reviewed_head_sha", "reviewed_head"))),
                )
                for binding_name, observed_shas in head_checks:
                    if not observed_shas:
                        continue
                    if current_head is None or not any(binding_sha_matches(observed, current_head) for observed in observed_shas):
                        binding_drift = True
                        add_gap(
                            gap_id=f"suite-evidence-validate-{binding_name.replace('_', '-')}-drift-{row.get('evidence_id')}",
                            classification="stale",
                            failure_kind="head_or_pr_drift",
                            source_locator=row_locator,
                            impact=f"merge-ready cannot consume present evidence whose {binding_name} binding does not match the current execution head",
                            remediation="Rerun or re-author the evidence against the current HEAD / PR head before merge-ready.",
                        )

                validation_digests = extract_binding_shas(
                    binding_text,
                    ("validation_summary_sha256", "validation_summary_digest", "validation_summary"),
                )
                if validation_digests and (
                    validation_summary_sha256 is None
                    or not any(binding_sha_matches(observed, validation_summary_sha256) for observed in validation_digests)
                ):
                    binding_drift = True
                    add_gap(
                        gap_id=f"suite-evidence-validate-validation-summary-drift-{row.get('evidence_id')}",
                        classification="stale",
                        failure_kind="stale_evidence",
                        source_locator=row_locator,
                        impact="merge-ready cannot consume present evidence whose validation summary binding is stale",
                        remediation="Refresh validation evidence and bind it to the current Latest Validation Summary digest.",
                    )

            if binding_drift:
                continue
            if freshness in {"stale", "conflict"}:
                add_gap(
                    gap_id=f"suite-evidence-validate-stale-{row.get('evidence_id')}",
                    classification="stale",
                    failure_kind="stale_evidence",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume stale or conflicting evidence against the current execution object",
                    remediation="Refresh the cited evidence or bind it to the current HEAD, PR, review, and validation object before merge-ready.",
                )
            elif freshness == "missing":
                add_gap(
                    gap_id=f"suite-evidence-validate-missing-{row.get('evidence_id')}",
                    classification="missing",
                    failure_kind=(
                        "missing_fresh_verification_evidence"
                        if evidence_type == "fresh_verification_input"
                        else "missing_evidence_map"
                    ),
                    source_locator=row_locator,
                    impact="merge-ready cannot consume evidence rows marked missing",
                    remediation="Author the missing evidence source and update evidence-map freshness before validation.",
                    fallback=(
                        "loom suite evidence validate --target <repo> --item <item> --json"
                        if evidence_type == "fresh_verification_input"
                        else "loom suite evidence scaffold --target <repo> --item <item> --json"
                    ),
                )
            elif freshness == "present" and evidence_type in present_by_type:
                present_by_type[evidence_type].append(row)
                present_ids_by_type[evidence_type].add(str(row.get("evidence_id")))

    for evidence_type in ("behavior_evidence", "test_evidence"):
        if present_by_type[evidence_type]:
            continue
        add_gap(
            gap_id=f"suite-evidence-validate-missing-{evidence_type.replace('_', '-')}",
            classification="missing",
            failure_kind="missing_evidence_map",
            source_locator=evidence_locator,
            impact=f"merge-ready evidence validation requires a present {evidence_type} row",
            remediation=f"Author a present {evidence_type} row with source locator, binding, freshness, consumer boundary, and remediation direction.",
            fallback="loom suite evidence scaffold --target <repo> --item <item> --json",
        )

    fresh_rows = present_by_type["fresh_verification_input"]
    behavior_ids = present_ids_by_type["behavior_evidence"]
    test_ids = present_ids_by_type["test_evidence"]
    fresh_consumes_required = False
    for row in fresh_rows:
        consumes = str(row.get("consumes") or "")
        if any(evidence_id and evidence_id in consumes for evidence_id in behavior_ids) and any(
            evidence_id and evidence_id in consumes for evidence_id in test_ids
        ):
            fresh_consumes_required = True
            break
    if not fresh_rows or not fresh_consumes_required:
        add_gap(
            gap_id="suite-evidence-validate-missing-fresh-verification",
            classification="missing",
            failure_kind="missing_fresh_verification_evidence",
            source_locator=evidence_locator,
            impact="merge-ready cannot prove behavior and test evidence combine into a fresh verification input",
            remediation="Author a present fresh_verification_input row that consumes present behavior and test evidence ids for the current object.",
        )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "block" if blocking_gaps else "pass"
    failed_layer = str(blocking_gaps[0].get("failed_layer") or "evidence_map") if blocking_gaps else None
    fail_closed_reason = str(blocking_gaps[0].get("failure_kind")) if blocking_gaps else None
    fallback_to = [str(blocking_gaps[0].get("fallback_to"))] if blocking_gaps else ["loom suite evidence inspect --target <repo> --item <item> --json"]
    summary = "Suite evidence validate found blocking evidence-map gaps." if blocking_gaps else "Suite evidence validate found present behavior, test, and fresh verification evidence."

    payload = {
        **inspect_payload,
        "required_evidence_types": list(SUITE_EVIDENCE_REQUIRED_TYPES),
        "consumed_contracts": list(SUITE_EVIDENCE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "freshness_context": {
            "head_sha": current_head,
            "validation_summary_sha256": validation_summary_sha256,
            "validation_summary_status": "present" if validation_summary else "missing",
        },
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


def suite_carrier_path(target: Path, item: str | None) -> Path | None:
    return suite_artifact_paths(target, item).get("task-carrier", [None])[0]


def normalize_carrier_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9_]+", "", str(value or "").strip().lower().replace("-", "_").replace(" ", "_"))


def parse_task_carrier_rows(path: Path, target: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        header_cells = split_markdown_table_row(lines[index])
        if not header_cells or index + 1 >= len(lines):
            index += 1
            continue
        separator_cells = split_markdown_table_row(lines[index + 1])
        if not is_markdown_separator_row(separator_cells):
            index += 1
            continue

        headers = [normalize_table_header(cell) for cell in header_cells]
        if not ({"carrier_type", "carriertype"} & set(headers) or {"carrier_locator", "carrierlocator"} & set(headers)):
            index += 2
            continue

        index += 2
        while index < len(lines):
            cells = split_markdown_table_row(lines[index])
            if not cells or is_markdown_separator_row(cells):
                break
            mapped = {headers[cell_index]: cells[cell_index] for cell_index in range(min(len(headers), len(cells)))}
            carrier_locator = mapped.get("carrier_locator") or mapped.get("carrierlocator") or mapped.get("locator") or ""
            carrier_type = normalize_carrier_token(mapped.get("carrier_type") or mapped.get("carriertype") or mapped.get("type"))
            normalized_status = normalize_carrier_token(
                mapped.get("normalized_status") or mapped.get("normalizedstatus") or mapped.get("status")
            )
            relationship = normalize_carrier_token(mapped.get("relationship") or mapped.get("relation"))
            locator_exists = None
            if carrier_locator and is_repo_local_source_locator(carrier_locator, ""):
                carrier_path = (target / carrier_locator).resolve()
                try:
                    locator_exists = carrier_path.is_relative_to(target.resolve()) and carrier_path.exists()
                except OSError:
                    locator_exists = False
            rows.append(
                {
                    "carrier_type": carrier_type,
                    "carrier_locator": carrier_locator,
                    "source_value": mapped.get("source_value") or mapped.get("sourcevalue") or "",
                    "normalized_status": normalized_status,
                    "relationship": relationship,
                    "work_item_locator": mapped.get("work_item_locator") or mapped.get("workitemlocator") or "",
                    "breakdown_unit_locator": mapped.get("breakdown_unit_locator") or mapped.get("breakdownunitlocator") or "",
                    "spec_scenario_locator": mapped.get("spec_scenario_locator") or mapped.get("specscenariolocator") or "",
                    "plan_phase_locator": mapped.get("plan_phase_locator") or mapped.get("planphaselocator") or "",
                    "validation_strategy_locator": mapped.get("validation_strategy_locator") or mapped.get("validationstrategylocator") or "",
                    "provenance": mapped.get("provenance") or "",
                    "freshness_rule": mapped.get("freshness_rule") or mapped.get("freshnessrule") or "",
                    "locator": f"{repo_locator(path, target)}:{index + 1}",
                    "carrier_locator_exists": locator_exists,
                }
            )
            index += 1
        continue
    return rows


def suite_carrier_inspect_payload(target: Path, item: str) -> tuple[str, dict[str, Any]]:
    carrier_path = suite_carrier_path(target, item)
    carrier_locator = repo_locator(carrier_path, target) if carrier_path else f".loom/specs/{item}/task-carrier.md"
    status = "missing"
    rows: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    advisory_gaps: list[dict[str, Any]] = []

    if carrier_path is None:
        missing_inputs.append("task_carrier_locator")
    elif carrier_path.exists() and (carrier_path.is_symlink() or not carrier_path.is_file()):
        status = "invalid"
        missing_inputs.append(f"invalid_task_carrier:{carrier_locator}")
    elif carrier_path.exists():
        status = "present"
        rows = parse_task_carrier_rows(carrier_path, target)
        if not rows:
            missing_inputs.append(f"task_carrier_rows:{carrier_locator}")
    else:
        missing_inputs.append("task_carrier_locator")

    if missing_inputs:
        advisory_gaps.append(
            suite_validate_finding(
                gap_id="suite-carrier-inspect-missing-task-carrier",
                classification="missing",
                failure_kind="missing_task_carrier_locator",
                source_locator=carrier_locator,
                consumer_impact="inspect-only",
                remediation_direction="Author task-carrier rows before carrier readiness validation.",
                fallback_to="loom suite carrier validate --target <repo> --item <item> --json",
                surface="task_carrier",
                binding="suite-carrier-inspect",
            )
        )

    payload = {
        "task_carrier": {
            "locator": carrier_locator,
            "status": status,
            "row_count": len(rows),
        },
        "task_carrier_locator": carrier_locator if status == "present" else None,
        "rows": rows,
        "recognized_carrier_types": sorted(SUITE_CARRIER_TYPES),
        "normalized_status_values": sorted(SUITE_CARRIER_STATUS_VALUES),
        "relationship_values": sorted(SUITE_CARRIER_RELATIONSHIPS),
        "recognized_truth_signals": sorted(SUITE_CARRIER_TRUTH_SIGNALS),
        "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
        "truth_boundary": {
            "carrier_done_satisfies_work_item_done": False,
            "project_done_satisfies_work_item_done": False,
            "checklist_done_satisfies_evidence_or_gate": False,
        },
        "work_item_truth": {
            "work_item_locator": f".loom/work-items/{item}.md",
            "work_item_present": (target / ".loom" / "work-items" / f"{item}.md").is_file(),
            "recovery_locator": f".loom/progress/{item}.md",
            "recovery_present": (target / ".loom" / "progress" / f"{item}.md").is_file(),
        },
        "missing_inputs": missing_inputs,
        "advisory_gaps": advisory_gaps,
    }
    summary = "Suite carrier inspect found task-carrier rows." if status == "present" else "Suite carrier inspect did not find usable task-carrier rows."
    return summary, payload


def suite_carrier_truth_claim_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "")
        for field in (
            "carrier_locator",
            "source_value",
            "normalized_status",
            "provenance",
            "freshness_rule",
            "relationship",
        )
    ).lower()


def read_markdown_bullet_field(path: Path, field: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    prefix = f"- {field}:"
    for line in lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return ""


def suite_carrier_work_item_truth(target: Path, item: str) -> dict[str, Any]:
    recovery_path = target / ".loom" / "progress" / f"{item}.md"
    checkpoint = normalize_carrier_token(read_markdown_bullet_field(recovery_path, "Current Checkpoint"))
    return {
        "work_item_locator": f".loom/work-items/{item}.md",
        "work_item_present": (target / ".loom" / "work-items" / f"{item}.md").is_file(),
        "recovery_locator": f".loom/progress/{item}.md",
        "recovery_present": recovery_path.is_file(),
        "recovery_checkpoint": checkpoint or None,
        "recovery_terminal": checkpoint in SUITE_CARRIER_TERMINAL_CHECKPOINTS,
    }


def suite_carrier_signal_set(row: dict[str, Any]) -> set[str]:
    text = suite_carrier_truth_claim_text(row)
    carrier_type = str(row.get("carrier_type") or "")
    status = str(row.get("normalized_status") or "")
    signals: set[str] = set()
    if status == "done":
        signals.add("carrier_done")
    if carrier_type == "github_project_item" and (status == "done" or re.search(r"\b(project\s+)?done\b", text)):
        signals.add("project_done")
    if carrier_type == "github_project_item" and re.search(r"\b(project\s+)?in[_ -]?progress\b", text):
        signals.add("project_in_progress")
    if carrier_type == "checklist_item" and re.search(r"\b(checked|checklist\s+checked)\b", text):
        signals.add("checklist_checked")
    if re.search(r"\bevidence\s+(missing|absent|not[_ -]?present)\b", text):
        signals.add("evidence_missing")
    if re.search(r"\b(issue\s+)?open\b", text):
        signals.add("issue_open")
    if re.search(r"\b(issue\s+)?closed\b", text):
        signals.add("issue_closed")
    if re.search(r"\b(pr|pull request)\s+open\b", text):
        signals.add("pr_open")
    if re.search(r"\b(pr|pull request)\s+merged\b", text):
        signals.add("pr_merged")
    if re.search(r"\bwork[_ -]?item\s+(open|in[_ -]?progress)\b", text):
        signals.add("work_item_open")
    if re.search(r"\bwork[_ -]?item\s+(done|closed|complete|completed)\b", text):
        signals.add("work_item_terminal")
    return signals


def suite_carrier_truth_signal_classifications(row: dict[str, Any], truth: dict[str, Any]) -> list[dict[str, Any]]:
    signals = suite_carrier_signal_set(row)
    row_locator = str(row.get("locator") or "")
    classifications: list[dict[str, Any]] = []

    def add_conflict(conflict_id: str, observed: list[str], impact: str, remediation: str) -> None:
        classifications.append(
            {
                "id": conflict_id,
                "classification": "conflict",
                "failure_kind": "carrier_truth_conflict",
                "source_locator": row_locator,
                "carrier_type": row.get("carrier_type"),
                "carrier_locator": row.get("carrier_locator"),
                "observed_signals": observed,
                "truth_owner": "work_item+recovery",
                "work_item_truth": truth,
                "consumer_impact": impact,
                "remediation_direction": remediation,
                "blocking": True,
            }
        )

    if "project_done" in signals and "issue_open" in signals:
        add_conflict(
            "project-done-issue-open",
            ["project_done", "issue_open"],
            "merge-ready cannot consume a carrier row whose Project mirror says Done while the issue mirror says open",
            "Reconcile the host mirrors or mark one signal stale before consuming the carrier row.",
        )
    if "pr_merged" in signals and "issue_open" in signals:
        add_conflict(
            "pr-merged-issue-open",
            ["pr_merged", "issue_open"],
            "merge-ready cannot consume PR merged as Work Item completion while the issue mirror remains open",
            "Use PR merged only as merge locator evidence and close the Work Item through closeout.",
        )
    if "issue_closed" in signals and "project_in_progress" in signals:
        add_conflict(
            "issue-closed-project-in-progress",
            ["issue_closed", "project_in_progress"],
            "merge-ready cannot consume an issue-closed carrier when the Project mirror remains in progress",
            "Reconcile Project status or treat the Project value as stale mirror evidence.",
        )
    if "checklist_checked" in signals and "evidence_missing" in signals:
        add_conflict(
            "checklist-checked-evidence-missing",
            ["checklist_checked", "evidence_missing"],
            "checklist checked cannot satisfy missing evidence or gate truth",
            "Keep checklist state as tracking-only and restore evidence-map / verification evidence.",
        )
    if (
        ("project_done" in signals or "issue_closed" in signals or "pr_merged" in signals or "work_item_terminal" in signals)
        and truth.get("recovery_present")
        and not truth.get("recovery_terminal")
        and ("work_item_terminal" in signals or "work_item_open" in signals)
    ):
        add_conflict(
            "host-terminal-recovery-active",
            sorted(signals & {"project_done", "issue_closed", "pr_merged", "work_item_open", "work_item_terminal"}),
            "host terminal signals conflict with active recovery truth",
            "Return completion truth to Work Item/recovery/closeout and keep host carrier state as a mirror.",
        )

    if not classifications:
        classifications.append(
            {
                "id": "no-blocking-host-carrier-conflict",
                "classification": "not_applicable",
                "failure_kind": None,
                "source_locator": row_locator,
                "carrier_type": row.get("carrier_type"),
                "carrier_locator": row.get("carrier_locator"),
                "observed_signals": sorted(signals),
                "truth_owner": "work_item+recovery",
                "work_item_truth": truth,
                "consumer_impact": "host carrier signals remain tracking-only",
                "remediation_direction": None,
                "blocking": False,
            }
        )
    return classifications


def suite_carrier_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-carrier-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="carrier validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite carrier inspect --target <repo> --item <item> --json",
                surface="task_carrier",
                binding="suite-carrier-validate",
            )
        ]
        payload = {
            "task_carrier": {"locator": None, "status": "invalid", "row_count": 0},
            "rows": [],
            "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite carrier validate failed closed before resolving task-carrier rows.",
            "block",
            payload,
            "task_carrier",
            "invalid_suite_item",
            ["loom suite carrier inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_carrier_inspect_payload(target, item)
    rows = inspect_payload.get("rows", [])
    carrier_locator = inspect_payload.get("task_carrier", {}).get("locator")
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []
    work_item_truth = suite_carrier_work_item_truth(target, item)
    truth_signal_classifications: list[dict[str, Any]] = []

    def add_gap(
        *,
        gap_id: str,
        classification: str,
        failure_kind: str,
        source_locator: str | None,
        impact: str,
        remediation: str,
        fallback: str = "loom suite carrier validate --target <repo> --item <item> --json",
    ) -> None:
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=gap_id,
                classification=classification,
                failure_kind=failure_kind,
                source_locator=source_locator,
                consumer_impact=impact,
                remediation_direction=remediation,
                fallback_to=fallback,
                surface="task_carrier",
                binding="suite-carrier-validate",
            )
        )

    if missing_inputs:
        add_gap(
            gap_id="suite-carrier-validate-missing-task-carrier",
            classification="missing",
            failure_kind="missing_task_carrier_locator",
            source_locator=carrier_locator,
            impact="merge-ready carrier validation cannot consume missing or unreadable task-carrier rows",
            remediation="Author task-carrier rows with locator, status, relationship, Work Item backlink, provenance, and freshness rule.",
        )

    required_fields = (
        "carrier_type",
        "carrier_locator",
        "source_value",
        "normalized_status",
        "relationship",
        "work_item_locator",
        "breakdown_unit_locator",
        "spec_scenario_locator",
        "plan_phase_locator",
        "validation_strategy_locator",
        "provenance",
        "freshness_rule",
    )
    primary_by_unit: dict[str, list[dict[str, Any]]] = {}
    item_number = item.split("-", 1)[1] if item.startswith("WI-") and "-" in item else item
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_locator = str(row.get("locator") or carrier_locator or "")
            missing_fields = [field for field in required_fields if is_empty_evidence_value(row.get(field))]
            if missing_fields:
                add_gap(
                    gap_id=f"suite-carrier-validate-missing-fields-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="merge-ready cannot consume carrier rows with incomplete locator, backlink, provenance, or freshness fields",
                    remediation=f"Fill task-carrier fields before validation; missing: {', '.join(missing_fields)}.",
                )
                continue

            if str(row.get("carrier_type")) not in SUITE_CARRIER_TYPES:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-type-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot normalize an unknown carrier type",
                    remediation="Use github_issue, github_project_item, checklist_item, repo_tasks_md, external_tracker, or not_applicable.",
                )
            if str(row.get("normalized_status")) not in SUITE_CARRIER_STATUS_VALUES:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-status-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume an unknown normalized status",
                    remediation="Use pending, in_progress, done, blocked, deferred, or not_applicable.",
                )
            if str(row.get("relationship")) not in SUITE_CARRIER_RELATIONSHIPS:
                add_gap(
                    gap_id=f"suite-carrier-validate-invalid-relationship-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume an unknown carrier relationship",
                    remediation="Use primary, mirror, evidence_locator, or not_applicable.",
                )

            work_item_locator = str(row.get("work_item_locator") or "")
            if item not in work_item_locator and item_number not in work_item_locator:
                add_gap(
                    gap_id=f"suite-carrier-validate-work-item-backlink-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier rows must backlink the owning Work Item before they can be consumed",
                    remediation=f"Bind the carrier row to {item} or its issue locator.",
                )

            if row.get("carrier_locator_exists") is False:
                add_gap(
                    gap_id=f"suite-carrier-validate-missing-locator-{Path(row_locator).name}",
                    classification="missing",
                    failure_kind="missing_task_carrier_locator",
                    source_locator=row_locator,
                    impact="carrier validation cannot consume a repo-local carrier locator that is missing",
                    remediation="Restore the repo-local carrier locator or update the carrier row to a readable locator.",
                )

            if row.get("relationship") == "primary":
                primary_by_unit.setdefault(str(row.get("breakdown_unit_locator") or ""), []).append(row)

            truth_claim_text = suite_carrier_truth_claim_text(row)
            truth_replacement_markers = (
                "work_item_completed",
                "work item completed",
                "work item done",
                "closeout complete",
                "closeout completed",
                "merge-ready pass",
                "merge_ready_pass",
                "review pass",
                "review approved",
                "evidence present",
                "gate pass",
                "project done means completed",
                "checklist checked means evidence",
            )
            if any(marker in truth_claim_text for marker in truth_replacement_markers):
                add_gap(
                    gap_id=f"suite-carrier-validate-truth-conflict-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="carrier_truth_conflict",
                    source_locator=row_locator,
                    impact="carrier status cannot replace Work Item, evidence, review, merge-ready, or closeout truth",
                    remediation="Demote carrier status to tracking-only language and return completion truth to Work Item/review/merge-ready/closeout carriers.",
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

            if row.get("normalized_status") == "deferred" and re.search(r"\b(done|completed|closed)\b", truth_claim_text):
                add_gap(
                    gap_id=f"suite-carrier-validate-deferred-completed-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="deferred_as_completed",
                    source_locator=row_locator,
                    impact="deferred carrier status cannot satisfy completed truth",
                    remediation="Record an activation condition for the deferred carrier or move completion truth to the owning Work Item closeout.",
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

            row_classifications = suite_carrier_truth_signal_classifications(row, work_item_truth)
            truth_signal_classifications.extend(row_classifications)
            for classification in row_classifications:
                if not classification.get("blocking"):
                    continue
                add_gap(
                    gap_id=f"suite-carrier-validate-host-conflict-{classification['id']}-{Path(row_locator).name}",
                    classification="conflict",
                    failure_kind="carrier_truth_conflict",
                    source_locator=row_locator,
                    impact=str(classification.get("consumer_impact") or "host carrier signal conflict blocks merge-ready consumption"),
                    remediation=str(classification.get("remediation_direction") or "Reconcile host carrier mirrors before merge-ready."),
                    fallback="loom suite carrier inspect --target <repo> --item <item> --json",
                )

    for unit_locator, primary_rows in primary_by_unit.items():
        if unit_locator and len(primary_rows) > 1:
            add_gap(
                gap_id=f"suite-carrier-validate-primary-conflict-{Path(unit_locator).name}",
                classification="conflict",
                failure_kind="carrier_truth_conflict",
                source_locator=unit_locator,
                impact="a breakdown unit cannot have multiple primary carriers",
                remediation="Keep one primary carrier for the breakdown unit and mark the rest mirror or evidence_locator.",
                fallback="loom suite carrier inspect --target <repo> --item <item> --json",
            )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "block" if blocking_gaps else "pass"
    failed_layer = str(blocking_gaps[0].get("failed_layer") or "task_carrier") if blocking_gaps else None
    fail_closed_reason = str(blocking_gaps[0].get("failure_kind")) if blocking_gaps else None
    fallback_to = [str(blocking_gaps[0].get("fallback_to"))] if blocking_gaps else ["loom suite carrier inspect --target <repo> --item <item> --json"]
    summary = "Suite carrier validate found blocking task-carrier gaps." if blocking_gaps else "Suite carrier validate found carrier locators, normalized status, relationships, and Work Item backlinks."

    payload = {
        **inspect_payload,
        "required_fields": list(required_fields),
        "consumed_contracts": list(SUITE_CARRIER_CONTRACT_LOCATORS),
        "recognized_truth_signals": sorted(SUITE_CARRIER_TRUTH_SIGNALS),
        "truth_signal_classifications": truth_signal_classifications,
        "host_signal_conflicts": [entry for entry in truth_signal_classifications if entry.get("blocking")],
        "work_item_truth": {**inspect_payload.get("work_item_truth", {}), **work_item_truth},
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


def suite_validate_payload(target: Path, item: str) -> tuple[str, str, dict[str, Any], str | None, str | None, list[str]]:
    item_error = suite_item_segment_error(item)
    if item_error:
        blocking_gaps = [
            suite_validate_finding(
                gap_id="suite-validate-invalid-item",
                classification="blocking",
                failure_kind="invalid_suite_item",
                source_locator=None,
                consumer_impact="suite validation cannot bind an unsafe item segment",
                remediation_direction="Use a single repo-local Work Item id as the suite item.",
                fallback_to="loom suite inspect --target <repo> --item <item> --json",
            )
        ]
        payload = {
            "suite_path": "unknown",
            "suite_locator": None,
            "path_decision_locator": None,
            "artifact_inventory": [],
            "consumed_contracts": list(SUITE_VALIDATE_CONTRACT_LOCATORS),
            "missing_inputs": [item_error],
            "blocking_gaps": blocking_gaps,
            "advisory_gaps": [],
            "findings": blocking_gaps,
            "failure_taxonomy": suite_failure_taxonomy_for_findings(blocking_gaps),
            "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
            "remediation_directions": [blocking_gaps[0]["remediation_direction"]],
        }
        return (
            "Suite validate failed closed before resolving artifact paths.",
            "block",
            payload,
            "suite-input",
            "invalid_suite_item",
            ["loom suite inspect --target <repo> --item <item> --json"],
        )

    inspect_summary, inspect_payload = suite_inspect_payload(target, item)
    paths = suite_artifact_paths(target, item)
    suite_path = inspect_payload.get("suite_path", "unknown")
    missing_inputs = list(inspect_payload.get("missing_inputs", []))
    blocking_gaps: list[dict[str, Any]] = []
    advisory_gaps: list[dict[str, Any]] = []
    not_applicable_records, deferred_items = suite_applicability_records(paths, target)

    def add_missing_input(value: str) -> None:
        if value not in missing_inputs:
            missing_inputs.append(value)

    for missing in missing_inputs:
        if missing == "suite_path_decision":
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id="suite-validate-missing-suite-path-decision",
                    classification="missing",
                    failure_kind="missing_suite_path_decision",
                    source_locator=None,
                    consumer_impact="spec review cannot determine whether the suite is full, minimal, or not_applicable",
                    remediation_direction="Author a suite path decision before validating readiness.",
                    fallback_to="loom suite inspect --target <repo> --item <item> --json",
                )
            )
        elif missing.startswith("invalid_suite_path_decision:") or missing.startswith("conflicting_suite_path_decision:"):
            locator = missing.split(":", 1)[1]
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id=f"suite-validate-invalid-path-decision-{Path(locator).name}",
                    classification="blocking",
                    failure_kind="missing_suite_path_decision",
                    source_locator=locator,
                    consumer_impact="spec review cannot consume an invalid or conflicting suite path decision",
                    remediation_direction="Keep exactly one legal suite path decision: full, minimal, or not_applicable.",
                    fallback_to="loom suite inspect --target <repo> --item <item> --json",
                )
            )
        elif missing.startswith("required_artifact:"):
            locator = missing.split(":", 1)[1]
            blocking_gaps.append(
                suite_validate_finding(
                    gap_id=f"suite-validate-missing-{Path(locator).name}",
                    classification="missing",
                    failure_kind="missing_required_artifact",
                    source_locator=locator,
                    consumer_impact="spec review readiness cannot pass while a required suite artifact is absent",
                    remediation_direction="Run suite scaffold dry-run or author the missing repo-relative artifact.",
                    fallback_to="loom suite scaffold --target <repo> --item <item> --json",
                )
            )

    for record in not_applicable_records:
        if record.get("status") == "valid":
            continue
        locator = str(record.get("locator") or "")
        missing_fields = ", ".join(str(field) for field in record.get("missing_fields", [])) or "artifact binding"
        for field in record.get("missing_fields", []) or ["artifact_binding"]:
            add_missing_input(f"not_applicable_rationale:{locator}:block-{record.get('block')}:{field}")
        blocking_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-invalid-not-applicable-{Path(locator).name or 'record'}-{record.get('block')}",
                classification="blocking",
                failure_kind="invalid_not_applicable_rationale",
                source_locator=locator or None,
                consumer_impact="spec review cannot treat not_applicable as ready without rationale, consumer boundary, and recheck condition",
                remediation_direction=(
                    "Author not_applicable with explicit artifact binding, rationale, consumer boundary, "
                    f"and recheck condition; missing: {missing_fields}."
                ),
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    covered_not_applicable = suite_covered_artifacts(not_applicable_records)
    deferred_coverage = suite_covered_artifacts(
        [{**record, "status": "valid"} for record in deferred_items]
    )
    if suite_path == "minimal":
        missing_not_applicable = sorted(SUITE_MINIMAL_NOT_APPLICABLE_ARTIFACTS - covered_not_applicable)
        for artifact in missing_not_applicable:
            if artifact in deferred_coverage:
                matching = next(
                    (
                        record
                        for record in deferred_items
                        if artifact in [str(entry) for entry in record.get("artifacts", [])]
                    ),
                    None,
                )
                blocking_gaps.append(
                    suite_validate_finding(
                        gap_id=f"suite-validate-deferred-as-not-applicable-{artifact.replace('.', '-')}",
                        classification="blocking",
                        failure_kind="deferred_as_completed",
                        source_locator=str(matching.get("locator")) if matching else None,
                        consumer_impact="minimal suite readiness cannot consume deferred full-path artifacts as completed not_applicable rationale",
                        remediation_direction="Record not_applicable rationale, consumer boundary, and recheck condition, or keep the suite out of ready state.",
                        fallback_to="loom suite validate --target <repo> --item <item> --json",
                    )
                )
            else:
                add_missing_input(f"not_applicable_rationale:{artifact}")
                blocking_gaps.append(
                    suite_validate_finding(
                        gap_id=f"suite-validate-missing-not-applicable-{artifact.replace('.', '-')}",
                        classification="missing",
                        failure_kind="invalid_not_applicable_rationale",
                        source_locator=inspect_payload.get("path_decision_locator"),
                        consumer_impact="minimal suite readiness cannot skip full-path artifacts without authored not_applicable rationale",
                        remediation_direction=(
                            f"Author not_applicable for {artifact} with rationale, consumer boundary, "
                            "and recheck condition."
                        ),
                        fallback_to="loom suite validate --target <repo> --item <item> --json",
                    )
                )
    elif suite_path == "not_applicable" and "suite" not in covered_not_applicable:
        add_missing_input("not_applicable_rationale:suite")
        blocking_gaps.append(
            suite_validate_finding(
                gap_id="suite-validate-missing-suite-not-applicable-rationale",
                classification="missing",
                failure_kind="invalid_not_applicable_rationale",
                source_locator=inspect_payload.get("path_decision_locator"),
                consumer_impact="spec review cannot consume a not_applicable suite path without authored rationale",
                remediation_direction="Author suite-level not_applicable with rationale, consumer boundary, and recheck condition.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    spec_plan_mapping = {
        "spec_locator": inspect_payload.get("spec_locator"),
        "plan_locator": inspect_payload.get("plan_locator"),
        "required_scenarios": [],
        "required_acceptance": [],
        "mapped_scenarios": [],
        "mapped_acceptance": [],
        "missing_scenarios": [],
        "missing_acceptance": [],
    }
    if suite_path in {"full", "minimal"}:
        spec_plan_mapping, mapping_gaps = suite_spec_plan_mapping(paths, target)
        blocking_gaps.extend(mapping_gaps)

    artifact_inventory = {
        entry.get("artifact"): entry
        for entry in inspect_payload.get("artifact_inventory", [])
        if isinstance(entry, dict)
    }
    for artifact in SUITE_VALIDATE_ADVISORY_ARTIFACTS.get(str(suite_path), ()):
        if artifact_inventory.get(artifact, {}).get("status") == "present":
            continue
        locator_field = "task_carrier_locators" if artifact == "task-carrier" else artifact.replace("-", "_").removesuffix(".md") + "_locator"
        locator_value = inspect_payload.get(locator_field)
        if locator_value:
            continue
        expected_locator = f".loom/specs/{item}/{artifact if artifact != 'task-carrier' else 'task-carrier.md'}"
        advisory_gaps.append(
            suite_validate_finding(
                gap_id=f"suite-validate-advisory-missing-{artifact.replace('.', '-').replace('_', '-')}",
                classification="advisory",
                failure_kind="missing_optional_suite_artifact",
                source_locator=expected_locator,
                consumer_impact="core suite validation can continue, but later evidence/carrier checks may require this artifact",
                remediation_direction="Leave for the owning evidence, consistency, or carrier validation Work Item unless the current consumer requires it.",
                fallback_to="loom suite validate --target <repo> --item <item> --json",
            )
        )

    findings = [*blocking_gaps, *advisory_gaps]
    result = "pass"
    failed_layer: str | None = None
    fail_closed_reason: str | None = None
    fallback_to = ["loom suite inspect --target <repo> --item <item> --json"]
    if blocking_gaps:
        result = "block"
        failed_layer = str(blocking_gaps[0].get("surface") or "suite")
        fail_closed_reason = blocking_gaps[0]["failure_kind"]
        fallback_to = [blocking_gaps[0]["fallback_to"]]
        summary = "Suite validate found blocking readiness gaps."
    elif suite_path == "not_applicable":
        result = "not_applicable"
        summary = "Suite validate found a not_applicable suite path decision."
    elif advisory_gaps:
        result = "advisory"
        summary = "Suite validate found no core blocking gaps, but later suite checks still have advisory gaps."
    else:
        summary = {
            "full": "Suite validate found a full suite path with core required artifacts present.",
            "minimal": "Suite validate found a minimal suite path with core required artifacts present.",
        }.get(str(suite_path), inspect_summary)

    payload = {
        **inspect_payload,
        "not_applicable_rationale": not_applicable_records,
        "deferred_items": deferred_items,
        "spec_plan_mapping": spec_plan_mapping,
        "consumed_contracts": list(SUITE_VALIDATE_CONTRACT_LOCATORS),
        "missing_inputs": missing_inputs,
        "blocking_gaps": blocking_gaps,
        "advisory_gaps": advisory_gaps,
        "findings": findings,
        "failure_taxonomy": suite_failure_taxonomy_for_findings(findings),
        "supported_failure_kinds": sorted(SUITE_VALIDATE_FAILURE_TAXONOMY),
        "remediation_directions": [entry["remediation_direction"] for entry in findings],
    }
    return summary, result, payload, failed_layer, fail_closed_reason, fallback_to


def handle_suite(argv: list[str]) -> int:
    if not argv:
        return emit(
            output(
                "suite",
                "block",
                summary="Suite command requires an action.",
                mutates=False,
                failed_layer="suite-input",
                fail_closed_reason="missing suite action",
                fallback_to=["loom suite inspect --target <repo> --item <item> --json"],
            )
        )

    action = argv[0]
    if action not in {"inspect", "scaffold", "validate", "evidence", "carrier"}:
        return emit(
            output(
                f"suite {action}",
                "block",
                summary="Unsupported suite action.",
                mutates=False,
                failed_layer="suite-input",
                fail_closed_reason=f"unsupported suite action: {action}",
                fallback_to=["loom suite inspect --target <repo> --item <item> --json"],
            )
        )

    if action == "carrier":
        if len(argv) < 2:
            return emit(
                output(
                    "suite carrier",
                    "block",
                    summary="Suite carrier command requires inspect or validate.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing suite carrier action",
                    fallback_to=["loom suite carrier inspect --target <repo> --item <item> --json"],
                )
            )
        carrier_action = argv[1]
        if carrier_action not in {"inspect", "validate"}:
            return emit(
                output(
                    f"suite carrier {carrier_action}",
                    "block",
                    summary="Unsupported suite carrier action.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=f"unsupported suite carrier action: {carrier_action}",
                    fallback_to=["loom suite carrier inspect --target <repo> --item <item> --json"],
                )
            )
        parser = argparse.ArgumentParser(prog=f"loom suite carrier {carrier_action}")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[2:])
        command_name = f"suite carrier {carrier_action}"
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target(command_name, target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    command_name,
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=f"Suite carrier {carrier_action} requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=[f"loom {command_name} --target <repo> --item <item> --json"],
                )
            )
        if carrier_action == "inspect":
            summary, carrier_payload = suite_carrier_inspect_payload(target, args.item)
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    missing_inputs=carrier_payload.get("missing_inputs", []),
                    advisory_gaps=carrier_payload.get("advisory_gaps", []),
                    payload=carrier_payload,
                )
            )

        summary, result, carrier_payload, failed_layer, fail_closed_reason, fallback_to = suite_carrier_validate_payload(target, args.item)
        return emit(
            output(
                command_name,
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=carrier_payload.get("missing_inputs", []),
                blocking_gaps=carrier_payload.get("blocking_gaps", []),
                advisory_gaps=carrier_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=carrier_payload,
            )
        )

    if action == "evidence":
        if len(argv) < 2:
            return emit(
                output(
                    "suite evidence",
                    "block",
                    summary="Suite evidence command requires inspect, scaffold, or validate.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing suite evidence action",
                    fallback_to=["loom suite evidence inspect --target <repo> --item <item> --json"],
                )
            )
        evidence_action = argv[1]
        if evidence_action not in {"inspect", "scaffold", "validate"}:
            return emit(
                output(
                    f"suite evidence {evidence_action}",
                    "block",
                    summary="Unsupported suite evidence action.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=f"unsupported suite evidence action: {evidence_action}",
                    fallback_to=["loom suite evidence inspect --target <repo> --item <item> --json"],
                )
            )
        parser = argparse.ArgumentParser(prog=f"loom suite evidence {evidence_action}")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        if evidence_action == "scaffold":
            parser.add_argument("--apply", action="store_true")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[2:])
        command_name = f"suite evidence {evidence_action}"
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target(command_name, target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    command_name,
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=f"Suite evidence {evidence_action} requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=[f"loom {command_name} --target <repo> --item <item> --json"],
                )
            )
        if evidence_action == "scaffold":
            summary, scaffold_payload, fail_closed_reason = suite_evidence_scaffold_payload(target, args.item, apply=args.apply)
            if fail_closed_reason:
                return emit(
                    output(
                        command_name,
                        "block",
                        target=str(target),
                        item_id=args.item,
                        summary=summary,
                        mutates=False,
                        failed_layer="suite-input",
                        fail_closed_reason=fail_closed_reason,
                        missing_inputs=scaffold_payload.get("missing_inputs", []),
                        advisory_gaps=scaffold_payload.get("advisory_gaps", []),
                        fallback_to=["loom suite evidence scaffold --target <repo> --item <item> --json"],
                        payload=scaffold_payload,
                    )
                )
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=bool(scaffold_payload.get("created_locators")),
                    payload=scaffold_payload,
                )
            )
        if evidence_action == "inspect":
            summary, evidence_payload = suite_evidence_inspect_payload(target, args.item)
            return emit(
                output(
                    command_name,
                    "pass",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    missing_inputs=evidence_payload.get("missing_inputs", []),
                    advisory_gaps=evidence_payload.get("advisory_gaps", []),
                    payload=evidence_payload,
                )
            )

        summary, result, evidence_payload, failed_layer, fail_closed_reason, fallback_to = suite_evidence_validate_payload(target, args.item)
        return emit(
            output(
                command_name,
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=evidence_payload.get("missing_inputs", []),
                blocking_gaps=evidence_payload.get("blocking_gaps", []),
                advisory_gaps=evidence_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=evidence_payload,
            )
        )

    if action == "validate":
        parser = argparse.ArgumentParser(prog="loom suite validate")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[1:])
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target("suite validate", target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    "suite validate",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary="Suite validate requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    missing_inputs=["missing_work_item"],
                    blocking_gaps=[],
                    advisory_gaps=[],
                    fallback_to=["loom suite validate --target <repo> --item <item> --json"],
                )
            )
        summary, result, validate_payload, failed_layer, fail_closed_reason, fallback_to = suite_validate_payload(target, args.item)
        return emit(
            output(
                "suite validate",
                result,
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=False,
                failed_layer=failed_layer,
                fail_closed_reason=fail_closed_reason,
                missing_inputs=validate_payload.get("missing_inputs", []),
                blocking_gaps=validate_payload.get("blocking_gaps", []),
                advisory_gaps=validate_payload.get("advisory_gaps", []),
                fallback_to=fallback_to,
                payload=validate_payload,
            )
        )

    if action == "scaffold":
        parser = argparse.ArgumentParser(prog="loom suite scaffold")
        parser.add_argument("--target", default=".")
        parser.add_argument("--item")
        parser.add_argument("--suite", choices=("minimal", "full"), default="minimal")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--json", action="store_true")
        args = parser.parse_args(argv[1:])
        target = resolve_target(args.target)
        if not target.exists():
            return emit(block_target("suite scaffold", target, "target path does not exist"))
        if not args.item:
            return emit(
                output(
                    "suite scaffold",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary="Suite scaffold requires a Work Item id.",
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason="missing_work_item",
                    fallback_to=["loom suite scaffold --target <repo> --item <item> --json"],
                )
            )
        summary, scaffold_payload, fail_closed_reason = suite_scaffold_payload(target, args.item, args.suite, apply=args.apply)
        if fail_closed_reason:
            return emit(
                output(
                    "suite scaffold",
                    "block",
                    target=str(target),
                    item_id=args.item,
                    summary=summary,
                    mutates=False,
                    failed_layer="suite-input",
                    fail_closed_reason=fail_closed_reason,
                    fallback_to=["loom suite scaffold --target <repo> --item <item> --json"],
                    payload=scaffold_payload,
                )
            )
        return emit(
            output(
                "suite scaffold",
                "pass",
                target=str(target),
                item_id=args.item,
                summary=summary,
                mutates=bool(scaffold_payload.get("created_locators")),
                payload=scaffold_payload,
            )
        )

    parser = argparse.ArgumentParser(prog="loom suite inspect")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv[1:])
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("suite inspect", target, "target path does not exist"))

    summary, suite_payload = suite_inspect_payload(target, args.item)
    payload = output(
        "suite inspect",
        "pass",
        target=str(target),
        item_id=args.item,
        summary=summary,
        mutates=False,
        payload=suite_payload,
    )
    return emit(payload)


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        print_usage(sys.stderr)
        return 2
    if argv[1] in {"-v", "--version"}:
        print(version_context()["repo_version"])
        return 0

    resolved = resolve_command(argv[1:])
    if resolved is None:
        print_usage(sys.stderr)
        return 2
    command, forwarded = resolved

    if command in {"-h", "--help", "help"}:
        return handle_help(forwarded)
    if command == "version":
        return handle_version(forwarded)
    if command == "detect":
        return handle_detect(forwarded)
    if command == "doctor":
        return handle_doctor(forwarded)
    if command == "installed-state":
        return handle_installed_state(forwarded)
    if command.startswith("installed-state "):
        return handle_installed_state(command.split()[1:] + forwarded)
    if command == "repair" or command.startswith("repair "):
        repair_args = command.split()[1:] + forwarded if command.startswith("repair ") else forwarded
        return handle_repair(repair_args)
    if command == "release" or command.startswith("release "):
        release_args = command.split()[1:] + forwarded if command.startswith("release ") else forwarded
        return handle_release(release_args)
    if command in {"install", "upgrade-plan", "upgrade", "rollback", "verify"}:
        return handle_delivery(command, forwarded)
    if command == "runtime-upgrade" or command.startswith("runtime-upgrade "):
        runtime_upgrade_args = command.split()[1:] + forwarded if command.startswith("runtime-upgrade ") else forwarded
        return handle_runtime_upgrade(runtime_upgrade_args)
    if command == "migrate-global-cache" or command.startswith("migrate-global-cache "):
        migrate_args = command.split()[1:] + forwarded if command.startswith("migrate-global-cache ") else forwarded
        return handle_migrate_global_cache(migrate_args)
    if command == "workspace" or command.startswith("workspace "):
        workspace_args = command.split()[1:] + forwarded if command.startswith("workspace ") else forwarded
        return handle_workspace(workspace_args)
    if command == "issue" or command.startswith("issue "):
        issue_args = command.split()[1:] + forwarded if command.startswith("issue ") else forwarded
        return handle_issue(issue_args)
    if command == "project" or command.startswith("project "):
        project_args = command.split()[1:] + forwarded if command.startswith("project ") else forwarded
        return handle_project(project_args)
    if command == "pr-intent" or command.startswith("pr-intent "):
        intent_args = command.split()[1:] + forwarded if command.startswith("pr-intent ") else forwarded
        return handle_pr_intent(intent_args)
    if command == "docs-pr" or command.startswith("docs-pr "):
        docs_pr_args = command.split()[1:] + forwarded if command.startswith("docs-pr ") else forwarded
        return handle_pr_intent(docs_pr_args, default_intent="docs-governance-only", command_root="docs-pr")
    if command == "pr" or command.startswith("pr "):
        pr_args = command.split()[1:] + forwarded if command.startswith("pr ") else forwarded
        return handle_pr(pr_args)
    if command == "merge" or command.startswith("merge "):
        merge_args = command.split()[1:] + forwarded if command.startswith("merge ") else forwarded
        return handle_merge(merge_args)
    if command == "ship" or command.startswith("ship "):
        ship_args = command.split()[1:] + forwarded if command.startswith("ship ") else forwarded
        return handle_ship(ship_args)
    if command == "reconcile":
        return handle_reconcile(forwarded)
    if command == "carrier" or command.startswith("carrier "):
        carrier_args = command.split()[1:] + forwarded if command.startswith("carrier ") else forwarded
        return handle_carrier(carrier_args)
    if command == "host" or command.startswith("host "):
        host_args = command.split()[1:] + forwarded if command.startswith("host ") else forwarded
        return handle_host(host_args)
    if command == "workstation" or command.startswith("workstation "):
        workstation_args = command.split()[1:] + forwarded if command.startswith("workstation ") else forwarded
        return handle_workstation(workstation_args)
    if command == "skills" or command.startswith("skills "):
        skills_args = command.split()[1:] + forwarded if command.startswith("skills ") else forwarded
        return handle_skills(skills_args)
    if command == "suite" or command.startswith("suite "):
        suite_args = command.split()[1:] + forwarded if command.startswith("suite ") else forwarded
        return handle_suite(suite_args)
    if command == "acceptance" or command.startswith("acceptance "):
        acceptance_args = command.split()[1:] + forwarded if command.startswith("acceptance ") else forwarded
        return product_acceptance_main(acceptance_args)
    if command == "attestation" or command.startswith("attestation "):
        attestation_args = command.split()[1:] + forwarded if command.startswith("attestation ") else forwarded
        return host_attestation_main(attestation_args)
    if command == "init":
        return handle_init(forwarded)
    if command == "adopt" or command.startswith("adopt "):
        adopt_args = command.split()[1:] + forwarded if command.startswith("adopt ") else forwarded
        return handle_adopt(adopt_args)
    if command == "route":
        return handle_route(forwarded)
    if command == "status":
        return handle_status(forwarded)
    if command == "fact-chain":
        return handle_fact_chain(forwarded)
    if command == "shadow-parity":
        return handle_shadow_parity(forwarded)
    if command == "profile" or command.startswith("profile "):
        profile_args = command.split()[1:] + forwarded if command.startswith("profile ") else forwarded
        return handle_profile(profile_args)
    if command == "governance-profile" or command.startswith("governance-profile "):
        profile_args = command.split()[1:] + forwarded if command.startswith("governance-profile ") else forwarded
        return handle_governance_profile(profile_args)
    if command == "checkpoint" or command.startswith("checkpoint "):
        checkpoint_args = command.split()[1:] + forwarded if command.startswith("checkpoint ") else forwarded
        return handle_checkpoint(checkpoint_args)
    if command == "gate" or command.startswith("gate "):
        gate_args = command.split()[1:] + forwarded if command.startswith("gate ") else forwarded
        return handle_gate(gate_args)
    if command in {"closeout status", "closeout sync"}:
        return handle_closeout_sync(command.split()[1], forwarded)
    if command == "closeout run":
        return handle_closeout_run(forwarded)
    if command == "closeout batch":
        return handle_closeout_batch(forwarded)
    if command == "closeout queue status":
        return handle_closeout_queue_status(forwarded)
    if command in {"story", "spec", "plan", "build", "pre-review", "closeout", "handoff", "retire"}:
        return handle_scenario(command, forwarded)
    if command == "review":
        return handle_review_command(forwarded)
    if command in COMMAND_ROUTES:
        return dispatch(command, forwarded)
    if command in COMMAND_INDEX:
        return reserved_command(command, forwarded)

    payload = output(
        command,
        "block",
        summary="Unknown Loom command.",
        failed_layer="cli-command-router",
        fail_closed_reason=f"unknown command: {command}",
        fallback_to=["loom help --json"],
    )
    emit(payload, stream=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
