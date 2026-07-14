#!/usr/bin/env python3
"""CLI-first Loom control-plane entry for the frozen public product surface.

The 30 public commands are implemented here. Removed compatibility commands
fail before target, host, or mutation access with one structured failure.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
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
from failure_envelope import enforce_public_remediation, public_cli_failure_envelope
import github_host as github_host_module
import delivery_control as delivery_control_module
import governance_surface as governance_surface_module
import host_profile as host_profile_module
from github_admission import github_fr_wi_admission_payload
from github_host import github_lifecycle_subject_readback
from host_attestation import _artifact_id as host_attestation_artifact_id
from host_attestation import main as host_attestation_main
from host_attestation import readback as host_attestation_readback
from product_acceptance import main as product_acceptance_main
from loom_init import host_derived_manifest


class _GitHubAdmissionHost:
    """Narrow function facade consumed by the host-native admission module."""

    detect_github_repo = staticmethod(governance_surface_module.detect_github_repo)
    build_governance_surface = staticmethod(governance_surface_module.build_governance_surface)
    github_intake_taxonomy_mapping = staticmethod(host_profile_module.github_intake_taxonomy_mapping)
    github_intake_object_type = staticmethod(host_profile_module.github_intake_object_type)
    normalize_taxonomy_match_text = staticmethod(host_profile_module.normalize_taxonomy_match_text)
    normalized_issue_labels = staticmethod(host_profile_module.normalized_issue_labels)
    issue_tree_payload = staticmethod(host_profile_module.issue_tree_payload)
    github_issue_payload = staticmethod(github_host_module.github_issue_payload)
    gh_graphql_json = staticmethod(github_host_module.gh_graphql_json)
    gh_rest_write_json = staticmethod(github_host_module.gh_rest_write_json)
    normalize_rest_issue = staticmethod(github_host_module.normalize_rest_issue)


GITHUB_ADMISSION_HOST = _GitHubAdmissionHost()

LOOM_BOOTSTRAP_START = "<!-- LOOM_BOOTSTRAP_START -->"
LOOM_BOOTSTRAP_END = "<!-- LOOM_BOOTSTRAP_END -->"
LOOM_BOOTSTRAP_BLOCK = f"""{LOOM_BOOTSTRAP_START}
## Loom Execution

本仓库使用 Loom 编排 Work Item、build、review、merge-ready 与 host closeout。Loom
消费 GitHub 与工作现场事实，不用 repo current、progress、review、shadow 或 closeout
carrier 替代宿主真相。

开始改文件前：

1. 用 `loom route --target . --issue <issue> --json` 判断规划或执行入口。
2. 实现必须显式绑定 Work Item 与 issue-scoped branch；PR 创建前可直接运行
   `loom build --target . --issue <work-item> --branch <branch> --json`。
3. 一次只推进一个有界目标；不要创建空提交、空 PR 或治理载体来满足 admission。
4. PR 存在后再运行 `loom pre-review`、`loom review`、`loom merge-ready` 或 `loom ship`；
   这些入口从 GitHub readback 取得 branch、head、review、checks 与 merge 状态。
5. 验证证据记录命令、结果、时间或 head/run id；变更代码或 PR review 输入后重新确认
   current-head attestation 与 gate freshness。
6. merge 不等于产品完成；用 `loom attestation closeout` 消费宿主 closeout，用
   `loom release readback` 消费发布事实，不创建 closeout/current-retire PR。

环境或 provider 问题由 `loom doctor --target . --json` 分类；退役命令返回
`unsupported_command_surface`，不得通过 compatibility flag 恢复。
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
SCENARIO_SCHEMA = "loom-scenario-control/v1"
PROFILE_SCHEMA = "loom-profile/v1"
DELIVERY_SCHEMA = "loom-delivery-control/v1"
RELEASE_READBACK_SCHEMA = "loom-release-readback/v1"
CLOSEOUT_PR_ROLES = (
    "implementation_pr",
    "release_pr",
)

RUNTIME_PROVIDER_GLOBAL_CLI = "global-cli"
RUNTIME_PROVIDER_REPO_LOCAL_WRAPPER = "repo-local-wrapper"
GLOBAL_CLI_PROVIDER_LAYER = "global-cli-runtime-provider"
GLOBAL_CLI_REQUIRED_COMMANDS = [
    "installed-state validate",
    "detect",
    "doctor",
    "verify",
    "status",
    "story",
]
REMOVED_PROVIDER_COMMAND_REPLACEMENTS = {
    "fact-chain": "status",
    "shadow-parity": "verify",
    "workstation current": "status",
}


COMMANDS: list[dict[str, Any]] = [{'command': 'version',
  'domain': 'core',
  'status': 'implemented',
  'json': True,
  'summary': 'Show Loom CLI and distribution version context.'},
 {'command': 'help',
  'domain': 'core',
  'status': 'implemented',
  'json': True,
  'summary': 'Show task-oriented guidance plus the frozen CLI command matrix.'},
 {'command': 'acceptance resolve',
  'domain': 'acceptance',
  'status': 'implemented',
  'json': True,
  'summary': 'Resolve a trusted product acceptance verdict from authenticated GitHub host facts.'},
 {'command': 'attestation readback',
  'domain': 'host-attestation',
  'status': 'implemented',
  'json': True,
  'summary': 'Read an approved PR review, semantic tree, and workflow artifact from GitHub only.'},
 {'command': 'attestation closeout',
  'domain': 'host-attestation',
  'status': 'implemented',
  'json': True,
  'summary': 'Read a host-native Work Item closeout without creating repository carriers.'},
 {'command': 'installed-state validate',
  'domain': 'installation',
  'status': 'implemented',
  'json': True,
  'summary': 'Validate installed-state schema, layers, graph, runtime-provider declarations, and fail-closed '
             'metadata.'},
 {'command': 'detect',
  'domain': 'diagnostics',
  'status': 'implemented',
  'json': True,
  'summary': 'Detect installed Loom surfaces, legacy layouts, symlinks, and mixed installations.'},
 {'command': 'doctor',
  'domain': 'diagnostics',
  'status': 'implemented',
  'json': True,
  'summary': 'Diagnose metadata-only adoption, global CLI provider, user-level plugin provider, and unsupported legacy '
             'residue.'},
 {'command': 'repair plan',
  'domain': 'repair',
  'status': 'implemented',
  'json': True,
  'summary': 'Emit a non-mutating repair plan for metadata-only adoption, legacy layouts, or provider drift.'},
 {'command': 'install',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Install metadata-only repository adoption; does not write runtime, plugin, or skills payload into the '
             'repository.'},
 {'command': 'upgrade', 'domain': 'delivery', 'status': 'implemented', 'json': True},
 {'command': 'verify',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Verify the same readiness boundary as doctor for metadata-only adoption and global providers.'},
 {'command': 'route', 'domain': 'scenario', 'status': 'implemented', 'json': True},
 {'command': 'status', 'domain': 'harness', 'status': 'implemented', 'json': True},
 {'command': 'profile status', 'domain': 'profile', 'status': 'implemented', 'json': True},
 {'command': 'profile light-migration-reconcile',
  'domain': 'profile',
  'status': 'implemented',
  'json': True,
  'summary': 'Reconcile light-profile GitHub required checks and verify the migrated main tree through host readback.'},
 {'command': 'story', 'domain': 'scenario', 'status': 'implemented', 'json': True},
 {'command': 'build', 'domain': 'scenario', 'status': 'implemented', 'json': True},
 {'command': 'pre-review', 'domain': 'scenario', 'status': 'implemented', 'json': True},
 {'command': 'review', 'domain': 'scenario', 'status': 'implemented', 'json': True,
  'summary': 'Authenticate current-head semantic review through GitHub host attestation.'},
 {'command': 'merge-ready', 'domain': 'scenario', 'status': 'implemented', 'json': True,
  'summary': 'Check current-head attestation, hosted delivery gate, required checks, and mergeability.'},
 {'command': 'closeout',
  'domain': 'scenario',
  'status': 'implemented',
  'json': True,
  'summary': 'Read host-native closeout readiness without repository execution carriers.'},
 {'command': 'release readback',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Read target package surface, tag, GitHub Release, npm, workflow, and host release state into a '
             'publish/missing/drifted/blocked verdict without publishing.'},
 {'command': 'workspace create', 'domain': 'host-control', 'status': 'implemented', 'json': True},
 {'command': 'workspace check', 'domain': 'host-control', 'status': 'implemented', 'json': True},
 {'command': 'workspace retire',
  'domain': 'host-control',
  'status': 'implemented',
  'json': True,
  'summary': 'Emit local-only worksite retirement evidence; does not close host objects or write versioned terminal '
             'carriers.'},
 {'command': 'pr gate',
  'domain': 'host-control',
  'status': 'implemented',
  'json': True,
  'summary': 'Read the hosted delivery-gate result for an explicit PR head and typed Work Item.'},
 {'command': 'merge check',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Read-only controlled merge preflight; consumes PR gate, required checks, triggered checks, host '
             'enforcement, and mergeability.'},
 {'command': 'merge run',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Execute host merge only with `--apply` after `merge check` passes for the same PR head and Work Item.'},
 {'command': 'ship',
  'domain': 'delivery',
  'status': 'implemented',
  'json': True,
  'summary': 'Dry-run the host-native delivery path across attestation, hosted gate readback, controlled merge, '
             'changed-path validation, and closeout policy.'}]

PUBLIC_COMMAND_NAMES = {
    "version", "help", "acceptance resolve", "attestation readback", "attestation closeout",
    "installed-state validate", "detect", "doctor", "repair plan", "install", "upgrade", "verify",
    "route", "status", "profile status", "profile light-migration-reconcile", "story", "build",
    "pre-review", "review", "merge-ready", "closeout", "pr gate", "merge check", "merge run", "ship",
    "release readback", "workspace create", "workspace check", "workspace retire",
}
PUBLIC_PROTOCOL_TYPES = (
    "manifest",
    "locator",
    "observation",
    "delivery_verdict",
    "product_acceptance",
    "reconciliation_verdict",
    "review_attestation",
    "host_attestation",
    "failure_envelope",
    "migration_plan",
    "release_judgment",
    "readback",
)
LEGACY_COMMAND_INVENTORY = (
    "acceptance validate",
    "upgrade-plan",
    "runtime-upgrade status", "runtime-upgrade prepare", "runtime-upgrade check", "runtime-upgrade pr", "runtime-upgrade closeout",
    "migrate-global-cache plan", "migrate-global-cache apply", "rollback", "release resume", "release closeout-sync", "ship status", "ship preflight",
    "checkpoint admission", "checkpoint build", "checkpoint merge", "gate pre-review", "gate spec-review", "gate review", "gate pr", "gate merge",
    "gate freeze check", "gate freeze write", "gate closeout", "gate repair-pr",
    "carrier closeout-sync", "fact-chain", "shadow-parity",
    "host list", "host doctor", "host install", "host verify", "host register", "host upgrade", "host remove",
    "closeout run", "closeout batch", "workspace locate", "workspace audit", "issue inspect", "issue bind", "issue reconcile",
    "project status", "project reconcile", "pr inspect", "pr metadata-render", "pr metadata-readback", "pr metadata-update", "pr metadata-preflight",
    "pr-intent prepare", "pr-intent check", "docs-pr prepare", "docs-pr check", "reconcile",
    "installed-state show", "installed-state export",
    "profile upgrade-plan", "profile upgrade", "profile light-migration-plan", "governance-profile status", "governance-profile upgrade-plan",
    "governance-profile upgrade", "governance-profile binding", "repair apply",
    "init", "adopt", "adopt adversarial-test", "spec", "plan", "spec-review", "closeout status", "closeout sync", "closeout queue status",
    "resume", "handoff", "retire",
    "skills list", "skills generate", "skills check", "skills doctor", "skills package", "skills release-check",
    "suite inspect", "suite scaffold", "suite validate", "suite evidence inspect", "suite evidence scaffold", "suite evidence validate",
    "suite carrier inspect", "suite carrier validate",
    "workstation register", "workstation list", "workstation unregister", "workstation upgrade", "workstation current",
)

PUBLIC_COMMAND_PROTOCOL_TYPES = {
    "version": "manifest",
    "help": "manifest",
    "acceptance resolve": "product_acceptance",
    "attestation readback": "host_attestation",
    "attestation closeout": "host_attestation",
    "installed-state validate": "manifest",
    "detect": "observation",
    "doctor": "observation",
    "repair plan": "migration_plan",
    "install": "migration_plan",
    "upgrade": "migration_plan",
    "verify": "readback",
    "route": "locator",
    "status": "observation",
    "profile status": "observation",
    "profile light-migration-reconcile": "reconciliation_verdict",
    "story": "locator",
    "build": "delivery_verdict",
    "pre-review": "delivery_verdict",
    "review": "review_attestation",
    "merge-ready": "delivery_verdict",
    "closeout": "reconciliation_verdict",
    "pr gate": "delivery_verdict",
    "merge check": "delivery_verdict",
    "merge run": "delivery_verdict",
    "ship": "delivery_verdict",
    "release readback": "release_judgment",
    "workspace create": "locator",
    "workspace check": "readback",
    "workspace retire": "reconciliation_verdict",
}
HARNESS_SUPPORT_SCHEMA = "loom-agent-harness-support/v1"


def harness_support_contract() -> dict[str, Any]:
    native_requirements = [
        "installation",
        "discovery",
        "execution",
        "session_binding",
        "tool_mapping",
        "verification",
        "live_e2e",
    ]
    return {
        "schema_version": HARNESS_SUPPORT_SCHEMA,
        "levels": ["native/primary", "CLI-compatible", "unsupported"],
        "native_primary": {
            "harness": "codex",
            "level": "native/primary",
            "requirements": native_requirements,
            "verified": True,
        },
        "cli_compatible": {
            "level": "CLI-compatible",
            "condition": "the harness can invoke the root loom CLI and consume its JSON output",
            "does_not_imply": ["plugin integration", "session binding", "tool mapping", "native E2E"],
        },
        "unsupported_native_harnesses": ["claude", "cursor", "gemini", "opencode"],
        "native_admission": {
            "minimum_requirements": native_requirements,
            "rule": "all requirements need an implemented consumer and real E2E evidence before a harness may be native",
        },
    }

HELP_TASK_ROUTES: list[dict[str, Any]] = [
    {
        "task": "resume",
        "summary": "Take over the current Work Item from GitHub and worktree facts.",
        "first_command": "loom status --target <repo> --issue <work-item> --json",
        "next_step": "Continue with build, review, merge-ready, or closeout based on the derived route.",
    },
    {
        "task": "prepare-pr",
        "summary": "Prepare or verify a known PR intent carrier set before review/gate.",
        "first_command": "loom build --target <repo> --item <WI> --json",
        "next_step": "Continue to pre-review only after build returns a passing delivery verdict.",
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
        "first_command": "loom upgrade --target <repo> --json",
        "next_step": "Apply the reported migration plan through the repository's normal maintenance PR.",
    },
    {
        "task": "host-plugin-doctor",
        "summary": "Diagnose local Codex plugin/cache freshness.",
        "first_command": "loom doctor --target <repo> --json",
        "next_step": "Use the reported remediation only when refreshing the user workstation surface is intended.",
    },
    {
        "task": "workstation-registry",
        "summary": "List or update the machine-local Loom repository registry.",
        "first_command": "loom workspace check --target <repo> --json",
        "next_step": "Use workspace create or retire to manage the explicit repository worktree binding.",
    },
]

HELP_COMMAND_TIERS: dict[str, list[str]] = {
    "common_path": [
        "route",
        "build",
        "pre-review",
        "review",
        "merge-ready",
        "pr gate",
        "merge check",
        "merge run",
        "attestation readback",
        "attestation closeout",
        "closeout",
    ],
    "maintenance_path": [
        "detect",
        "doctor",
        "repair plan",
        "install",
        "upgrade",
        "verify",
        "release readback",
        "workspace create",
        "workspace check",
        "workspace retire",
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

COMMAND_ROUTES: dict[str, tuple[str, tuple[str, ...]]] = {}

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
    readback_command = "loom doctor --target <repo> --json"
    reload_note = "Start a new Codex session, or restart Codex Desktop if the plugin list was already loaded."

    provider_actions: list[dict[str, Any]] = []
    next_steps: list[str] = [readback_command]
    reload_required = False
    status = "required"
    summary = "Codex plugin payload refresh is required."

    if action == "install_cli":
        provider_actions = [
            {
                "provider": "npm",
                "operation": "upgrade_global_cli",
                "command": "npm install -g @mc-and-his-agents/loom@latest",
            },
            {
                "provider": "codex",
                "operation": "refresh_marketplace_plugin",
                "instruction": "Refresh the Loom marketplace source and plugin cache in Codex, then reload the Codex session.",
            },
        ]
        summary = "Upgrade the root Loom CLI, then refresh the Codex-owned marketplace plugin payload."
    elif action == "install_plugin":
        provider_actions = [
            {
                "provider": "codex",
                "operation": "refresh_marketplace_plugin",
                "instruction": "Refresh the Loom marketplace source and plugin cache in Codex, then reload the Codex session.",
            }
        ]
        summary = "Refresh the Codex-owned marketplace plugin payload."
    elif action == "reload_host":
        reload_required = True
        provider_actions = [
            {
                "provider": "codex",
                "operation": "reload_runtime_cache",
                "instruction": reload_note,
            }
        ]
        summary = "The Codex-owned runtime cache is stale; reload Codex, then read back host doctor."
    elif action == "already_current" or freshness == "already_current":
        status = "current"
        summary = "Codex plugin payload is already current."
    else:
        provider_actions = [
            {
                "provider": "codex",
                "operation": "inspect_plugin_state",
                "instruction": "Inspect the Codex marketplace source and runtime plugin cache before retrying Loom doctor.",
            }
        ]

    return {
        "schema": "loom-plugin-payload-refresh-guidance/v1",
        "status": status,
        "freshness": freshness,
        "action": action,
        "summary": summary,
        "apply_commands": [],
        "provider_actions": provider_actions,
        "readback_command": readback_command,
        "reload_required": reload_required,
        "reload_note": reload_note if reload_required else None,
        "next_steps": next_steps,
        "authority_boundary": {
            "provider": "codex-user-plugin",
            "managed_by": "Codex marketplace and runtime cache",
            "target_install_upgrade_scope": "repository installed-state only",
            "legacy_host_commands": "removed",
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
            "command": "loom doctor --target <repo> --json",
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
        command = "loom doctor --target <repo> --json"
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
    command = payload.get("command")
    if command in PUBLIC_COMMAND_NAMES:
        payload["protocol_type"] = PUBLIC_COMMAND_PROTOCOL_TYPES[command]
    failure_envelope = enforce_public_remediation(
        public_cli_failure_envelope(payload),
        command=str(command or "loom"),
        public_commands=PUBLIC_COMMAND_NAMES,
    )
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


def emit_imported_main(command: str, handler: Any, argv: list[str]) -> int:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        status = handler(argv)
    if not stream.getvalue():
        return int(status)
    try:
        payload = json.loads(stream.getvalue())
    except json.JSONDecodeError:
        payload = output(
            command,
            "block",
            summary="Imported command did not emit JSON.",
            failed_layer="cli-command-router",
            fail_closed_reason=f"invalid JSON from {command}",
        )
    payload["command"] = command
    return emit(payload)


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
    for role in ("release_pr", "implementation_pr"):
        if role in role_numbers:
            return role_numbers[role]
    return getattr(args, "pr", None)


def closeout_current_pr_binding(args: argparse.Namespace) -> tuple[int | None, str | None]:
    current = closeout_current_pr_input(args)
    explicit = getattr(args, "pr", None)
    if isinstance(explicit, int) and isinstance(current, int) and explicit != current:
        return None, f"--pr #{explicit} conflicts with the selected {getattr(args, 'pr_role', None) or 'PR role'} #{current}"
    return current, None


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
    item: str | None = None,
    issue: int | None,
    fr: int | None = None,
    owner: str | None,
    repo_name: str | None,
    intent: str,
    pr: int | None = None,
    branch: str | None = None,
    pr_role: str | None = None,
) -> dict[str, Any]:
    """Use the shared host admission evaluator before a lifecycle entrypoint."""

    parsed_item = parse_typed_locator(item, allowed_types={"work_item"}, allow_legacy=False) if item else None
    legacy_item_match = re.fullmatch(r"WI-(\d+)", item or "")
    legacy_item_issue = int(legacy_item_match.group(1)) if legacy_item_match is not None else None
    legacy_item_compatibility = legacy_item_issue is not None and issue == legacy_item_issue
    if item and parsed_item is None and not legacy_item_compatibility:
        return {
            "result": "block",
            "lifecycle_state": "missing_subject",
            "primary_remediation": "provide --issue <work-item> or --item <owner/repo/work_item/id>",
            "carrier_mutations": False,
            "missing_inputs": ["canonical Work Item locator"],
        }
    target_repo_slug = infer_github_repo(target)
    target_owner, target_repo = target_repo_slug.split("/", 1) if target_repo_slug and "/" in target_repo_slug else (None, None)
    if not target_owner or not target_repo:
        return {
            "result": "block",
            "lifecycle_state": "missing_subject",
            "primary_remediation": "restore a readable target origin GitHub owner/repo binding before entering execution",
            "carrier_mutations": False,
            "missing_inputs": ["target origin GitHub owner/repo"],
        }
    identities = [
        ("item owner", parsed_item.get("owner") if parsed_item else None, target_owner),
        ("item repo", parsed_item.get("repo") if parsed_item else None, target_repo),
        ("explicit owner", owner, target_owner),
        ("explicit repo", repo_name, target_repo),
    ]
    conflicts = [label for label, supplied, expected in identities if supplied is not None and supplied.casefold() != expected.casefold()]
    if conflicts:
        return {
            "result": "block",
            "lifecycle_state": "subject_conflict",
            "primary_remediation": "make --item, --owner/--repo, and the target origin identify the same repository",
            "carrier_mutations": False,
            "missing_inputs": [f"consistent {label}" for label in conflicts],
        }
    if parsed_item is not None:
        item_issue = int(parsed_item["id"])
        if issue is not None and issue != item_issue:
            return {
                "result": "block",
                "lifecycle_state": "subject_conflict",
                "primary_remediation": "make --issue and --item identify the same Work Item",
                "carrier_mutations": False,
                "missing_inputs": ["consistent Work Item subject"],
            }
        issue = item_issue

    effective_owner = owner or target_owner
    effective_repo = repo_name or target_repo
    closing_policy = {"closing_issue_policy": "forbidden"} if pr_role == "release_pr" else {}
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
        **closing_policy,
    )
    issue = subject_readback.get("issue_number") if isinstance(subject_readback.get("issue_number"), int) else None
    if subject_readback.get("result") != "pass" or issue is None:
        release_closing_error = pr_role == "release_pr" and any(
            "must not natively close issues" in str(error)
            for error in subject_readback.get("errors", [])
        )
        return {
            "result": "block",
            "lifecycle_state": "closing_policy_violation" if release_closing_error else "missing_subject",
            "primary_remediation": (
                "remove native closing references from the release PR and close the Work Item only after release readback"
                if release_closing_error
                else "provide --issue <work-item-or-fr> or bind the branch to one PR with exactly one native closing Work Item"
            ),
            "carrier_mutations": False,
            "subject_readback": subject_readback,
            "missing_inputs": list(subject_readback.get("errors") or ["host lifecycle subject"]),
        }
    payload = github_fr_wi_admission_payload(
        host=GITHUB_ADMISSION_HOST,
        target_root=target,
        owner=effective_owner,
        repo_name=effective_repo,
        issue_number=issue,
        intent=intent,
        task=None,
        blocked_by=[],
        work_item_number=None,
        apply=False,
        lifecycle_only=True,
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
            "protocol_type": PUBLIC_COMMAND_PROTOCOL_TYPES[entry["command"]],
            "output_policy": command_output_policy(entry["command"]),
        }
        for entry in COMMANDS
        if entry["command"] in PUBLIC_COMMAND_NAMES
    ]


def internal_command_matrix() -> list[dict[str, Any]]:
    return [
        {
            "command": entry["command"],
            "domain": entry["domain"],
            "status": entry["status"],
            "json": entry.get("json", True),
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
    matrix = {entry["command"]: entry for entry in internal_command_matrix()}
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
        "CLI-first Loom control-plane entry.\n"
        "Use `loom help --json` for the complete 30-command public surface.\n"
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
    parser.add_argument("--internal-capabilities", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.internal_capabilities:
        capabilities = [
            handle_gate_freeze_operation(operation, [], probe=True)["capability"]
            for operation in ("check", "write")
        ]
        return emit(
            output(
                "help",
                "pass",
                summary="Internal compatibility capabilities resolved without target access.",
                visibility="internal",
                capabilities=capabilities,
                mutates=False,
            )
        )
    payload = output(
        "help",
        "pass",
        summary="Task-oriented guidance plus the frozen CLI command matrix.",
        command_count=len(PUBLIC_COMMAND_NAMES),
        hidden_compatibility_count=len(COMMANDS) - len(PUBLIC_COMMAND_NAMES),
        protocol_type_count=len(PUBLIC_PROTOCOL_TYPES),
        protocol_types=list(PUBLIC_PROTOCOL_TYPES),
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
        if entry["command"] not in PUBLIC_COMMAND_NAMES:
            continue
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
    declared_commands = required_commands if isinstance(required_commands, list) else GLOBAL_CLI_REQUIRED_COMMANDS
    normalized_commands = [
        REMOVED_PROVIDER_COMMAND_REPLACEMENTS.get(command, command) if isinstance(command, str) else command
        for command in declared_commands
    ]
    missing_commands = [
        declared
        for declared, normalized in zip(declared_commands, normalized_commands, strict=True)
        if not isinstance(normalized, str) or normalized not in command_names
    ]
    migrated_requirements = [
        {"declared": declared, "replacement": normalized}
        for declared, normalized in zip(declared_commands, normalized_commands, strict=True)
        if declared != normalized
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
        "required_commands": declared_commands,
        "normalized_required_commands": normalized_commands,
        "migrated_requirements": migrated_requirements,
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
        harness_support=harness_support_contract(),
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
                "fallback_to": None if codex_registration["result"] == "pass" else ["loom doctor --target <repo> --json"],
                "provider_action": None if codex_registration["result"] == "pass" else {
                    "provider": "codex",
                    "operation": "refresh_marketplace_plugin",
                    "instruction": "Refresh or enable the Loom plugin through the Codex marketplace, then reload Codex.",
                },
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
        harness_support=harness_support_contract(),
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
    result = "pass" if detection["surface_count"] or actions else "block"
    return output(
        "repair plan",
        result,
        schema=REPAIR_PLAN_SCHEMA,
        summary="Repair plan generated without reading or mutating repository execution carriers." if result == "pass" else "No installed surface exists to repair.",
        target=str(target),
        mutates=False,
        detection=detection,
        repo_execution_carriers_consumed=False,
        carrier_mutations=False,
        actions=actions,
        failed_layer=None if result == "pass" else "installed-surface",
        fail_closed_reason=None if result == "pass" else "target has no detectable Loom surface",
        fallback_to=None if result == "pass" else ["loom install"],
    )


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
    if args.action == "plan":
        return emit(repair_plan_payload(target))
    plan = repair_plan_payload_with_carrier(
        target,
        item=args.item,
        issue=args.issue,
        output_relative=args.output,
    )
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
        command = "loom doctor --target <repo> --json"
    elif not marketplace_payload["metadata_complete"]:
        freshness = "marketplace_source_metadata_missing"
        action = "install_plugin"
        command = "loom doctor --target <repo> --json"
    elif (
        marketplace_payload.get("plugin_payload_version") != source_payload.get("plugin_payload_version")
        or marketplace_payload.get("plugin_payload_hash") != source_payload.get("plugin_payload_hash")
    ):
        freshness = "marketplace_source_stale"
        action = "install_plugin"
        command = "loom doctor --target <repo> --json"
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
            "marketplace_source": "Codex-owned local marketplace source; Loom only reads its payload metadata",
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
            "repo_payload_verify_command": "loom verify --target <repo> --json",
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
            "remediation_command": "loom doctor --target <repo> --json",
            "provider_action": {
                "provider": "codex",
                "operation": "refresh_marketplace_plugin",
                "instruction": "Refresh or enable the Loom plugin through the Codex marketplace, then reload Codex.",
            },
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
        "status": "provider-action-required",
        "reason": (
            "target install/upgrade manages repository installed-state and adoption metadata only; "
            "it does not refresh the Codex workstation plugin cache"
        ),
        "remediation_command": "loom doctor --target <repo> --json",
        "provider_action": {
            "provider": "codex",
            "operation": "refresh_marketplace_plugin",
            "instruction": "Refresh the Loom plugin through the Codex marketplace and reload the Codex runtime cache.",
        },
        "apply_commands": [],
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


def handle_delivery(command: str, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog=f"loom {command}")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--host", default="codex", choices=("codex",))
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
            summary="Target repository install plan is ready; --apply is required before mutation.",
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
                    summary="Valid installed-state already exists; use `loom upgrade` or --force for reinstall.",
                    target=str(target),
                    installed_state_path=str(path),
                    detection=detection,
                    failed_layer="installed-state",
                    fail_closed_reason="current installed-state exists",
                    fallback_to=["loom upgrade --target <repo> --json", "loom install --target <repo> --apply --force --json"],
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
                harness_support=harness_support_contract(),
                suite_validation_requirement=requirement,
                suite_validation=suite_check,
                installed_state_path=str(path) if path else None,
                failed_layer=failed_layer,
                fail_closed_reason=None if result == "pass" else "; ".join(str(check.get("summary", check.get("name"))) for check in blocking_checks),
                fallback_to=None if result == "pass" else ["loom upgrade --target <repo> --json", "loom repair plan --target <repo> --json", "loom build --target <repo> --item <item> --json"],
            )
        )

    if command == "upgrade":
        if not args.apply:
            return emit(
                output(
                    command,
                    "pass",
                    schema=DELIVERY_SCHEMA,
                    summary="Target repository upgrade plan generated without mutation; rerun with --apply after resolving required actions.",
                    target=str(target),
                    host=args.host,
                    mutates=True,
                    plan=handle_delivery_payload_for_upgrade_plan(target),
                    host_plugin_refresh=host_plugin_refresh_boundary_action(args.host),
                    failed_layer=None,
                    fail_closed_reason=None,
                    fallback_to=["loom upgrade --target <repo> --apply --json", "loom verify --target <repo> --json"],
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
            fallback_to=["loom upgrade --target <repo> --json", "loom repair plan --target <repo> --json"],
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
        "upgrade",
        "pass",
        schema=DELIVERY_SCHEMA,
        summary="Target repository upgrade plan generated without mutating installed-state; Codex plugin refresh remains a provider action.",
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
        payload["harness_support"] = harness_support_contract()

    if args.json or True:
        return emit(payload)
    return 0


def workspace_payload(action: str, args: argparse.Namespace) -> dict[str, Any]:
    command = f"workspace {action}"
    target = resolve_target(args.target)
    item = parse_typed_locator(getattr(args, "item", None), allowed_types={"work_item"}, allow_legacy=False)

    def git_value(path: Path, *git_args: str) -> tuple[str | None, str | None]:
        completed = subprocess.run(
            ["git", "-C", str(path), *git_args],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            return None, (completed.stderr or completed.stdout).strip() or "git readback failed"
        return completed.stdout.strip(), None

    def workspace_readback(path: Path) -> tuple[dict[str, Any], list[str]]:
        errors: list[str] = []
        top_level, top_error = git_value(path, "rev-parse", "--show-toplevel")
        head, head_error = git_value(path, "rev-parse", "HEAD^{commit}")
        branch, branch_error = git_value(path, "branch", "--show-current")
        status, status_error = git_value(path, "status", "--porcelain=v1")
        for label, error in (("top-level", top_error), ("head", head_error), ("branch", branch_error), ("status", status_error)):
            if error:
                errors.append(f"git {label} readback: {error}")
        if top_level:
            try:
                if Path(top_level).resolve() != path.resolve():
                    errors.append("workspace path must be the exact Git checkout top-level")
            except OSError as exc:
                errors.append(f"workspace path cannot be resolved: {exc}")
        if head and re.fullmatch(r"[0-9a-f]{40}", head) is None:
            errors.append("workspace HEAD is not a full Git commit SHA")
        expected_branch = getattr(args, "branch", None)
        if expected_branch and branch != expected_branch:
            errors.append(f"checked-out branch `{branch or 'detached'}` does not match `{expected_branch}`")
        if item is not None and branch and re.search(rf"(?:^|[/_-]){item['id']}(?:$|[/_-])", branch) is None:
            errors.append("formal branch is not issue-scoped to the Work Item")
        return {
            "path": str(path),
            "top_level": top_level,
            "branch": branch,
            "head_sha": head,
            "dirty": bool(status),
            "dirty_paths": status.splitlines() if status else [],
            "work_item": item["locator"] if item else None,
        }, errors

    if action == "create":
        path_value = getattr(args, "path", None)
        branch = getattr(args, "branch", None)
        missing = []
        if item is None:
            missing.append("--item must be one canonical owner/repo/work_item/id locator")
        if not path_value:
            missing.append("--path is required")
        if not branch:
            missing.append("--branch is required")
        if item is not None and branch and re.search(rf"(?:^|[/_-]){item['id']}(?:$|[/_-])", branch) is None:
            missing.append("--branch must be issue-scoped to the Work Item")
        workspace_path = None
        if path_value:
            candidate = Path(path_value).expanduser()
            workspace_path = candidate.resolve() if candidate.is_absolute() else (target.parent / candidate).resolve()
            if workspace_path.exists():
                missing.append("workspace path already exists")
        if missing:
            return output(
                command,
                "block",
                schema=WORKSPACE_SCHEMA,
                summary="Workspace creation requires an explicit typed Work Item, issue-scoped branch, and unused path.",
                missing_inputs=missing,
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
                remediation_command="loom workspace create --target <repo> --path <path> --branch <issue-scoped-branch> --item <owner/repo/work_item/id> --apply --json",
            )
        if not getattr(args, "apply", False):
            return output(
                command,
                "pass",
                schema=WORKSPACE_SCHEMA,
                summary="Host-native worktree creation plan is valid; no repository carrier was read or written.",
                plan={"target": str(target), "path": str(workspace_path), "branch": branch, "item": item["locator"], "start_point": args.start_point},
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
            )
        completed = subprocess.run(
            ["git", "-C", str(target), "worktree", "add", "-b", str(branch), str(workspace_path), str(args.start_point)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            return output(
                command,
                "block",
                schema=WORKSPACE_SCHEMA,
                summary="Git could not create the formal worktree.",
                failed_layer="git-worktree",
                fail_closed_reason=(completed.stderr or completed.stdout).strip(),
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
                remediation_command="loom workspace create --target <repo> --path <path> --branch <issue-scoped-branch> --item <owner/repo/work_item/id> --apply --json",
            )
        readback, errors = workspace_readback(workspace_path)
        return output(
            command,
            "pass" if not errors else "block",
            schema=WORKSPACE_SCHEMA,
            summary="Formal Git worktree was created and read back." if not errors else "Worktree creation completed but host readback is inconsistent.",
            workspace=readback,
            missing_inputs=errors,
            repo_execution_carriers_consumed=False,
            carrier_mutations=False,
            mutates=True,
        )

    if action == "check":
        path_value = getattr(args, "path", None)
        workspace_path = Path(path_value).expanduser().resolve() if path_value else target
        if not workspace_path.exists():
            return output(
                command,
                "block",
                schema=WORKSPACE_SCHEMA,
                summary="Workspace path does not exist.",
                failed_layer="workspace-path",
                fail_closed_reason=str(workspace_path),
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
                remediation_command="loom workspace check --target <repo> --path <path> --json",
            )
        readback, errors = workspace_readback(workspace_path)
        return output(
            command,
            "pass" if not errors else "block",
            schema=WORKSPACE_SCHEMA,
            summary="Workspace is bound from live Git and worktree facts without a repository current pointer." if not errors else "Workspace Git/worktree binding is inconsistent.",
            workspace=readback,
            missing_inputs=errors,
            repo_execution_carriers_consumed=False,
            carrier_mutations=False,
            mutates=False,
            remediation_command="loom workspace check --target <repo> --path <path> --json",
        )

    if action == "retire":
        path_value = getattr(args, "path", None)
        workspace_path = Path(path_value).expanduser().resolve() if path_value else target
        readback, errors = workspace_readback(workspace_path) if workspace_path.exists() else ({"path": str(workspace_path)}, ["workspace path does not exist"])
        if readback.get("dirty"):
            errors.append("workspace has uncommitted changes")
        worktrees, list_error = git_value(target, "worktree", "list", "--porcelain")
        registered_paths = {
            line.removeprefix("worktree ")
            for line in (worktrees or "").splitlines()
            if line.startswith("worktree ")
        }
        if list_error:
            errors.append(f"git worktree list readback: {list_error}")
        elif str(workspace_path) not in registered_paths:
            errors.append("workspace is not a registered Git worktree")
        primary_path = next(iter(registered_paths), None)
        if primary_path and Path(primary_path).resolve() == workspace_path:
            errors.append("primary repository worktree cannot be retired")
        if errors:
            return output(
                command,
                "block",
                schema=WORKSPACE_SCHEMA,
                summary="Workspace retirement is not safe.",
                workspace=readback,
                missing_inputs=errors,
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
                remediation_command="loom workspace check --target <repo> --path <path> --json",
            )
        if not getattr(args, "apply", False):
            return output(
                command,
                "pass",
                schema=WORKSPACE_SCHEMA,
                summary="Local worktree retirement plan is safe; --apply was not requested.",
                workspace=readback,
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
            )
        completed = subprocess.run(
            ["git", "-C", str(target), "worktree", "remove", str(workspace_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        return output(
            command,
            "pass" if completed.returncode == 0 else "block",
            schema=WORKSPACE_SCHEMA,
            summary="Local worktree retired without changing host or repository truth." if completed.returncode == 0 else "Git could not retire the local worktree.",
            workspace=readback,
            failed_layer=None if completed.returncode == 0 else "git-worktree",
            fail_closed_reason=None if completed.returncode == 0 else (completed.stderr or completed.stdout).strip(),
            repo_execution_carriers_consumed=False,
            carrier_mutations=False,
            mutates=completed.returncode == 0,
        )
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


def pr_command_target(explicit_target: str | None) -> str:
    if explicit_target:
        return explicit_target
    github_workspace = os.environ.get("GITHUB_WORKSPACE")
    if github_workspace:
        return github_workspace
    return "."


def handle_public_pr_gate(argv: list[str]) -> int:
    """Read the base-owned hosted delivery gate without repository review carriers."""

    parser = argparse.ArgumentParser(prog="loom pr gate")
    parser.add_argument("pr", type=int)
    parser.add_argument("--target", default=".")
    parser.add_argument("--head-sha")
    parser.add_argument("--work-item", required=True)
    parser.add_argument("--branch")
    parser.add_argument("--pr-payload-file")
    parser.add_argument("--status-checks-file")
    parser.add_argument("--attestation-artifact-input", type=Path, required=True)
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES, default="implementation_pr")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if (args.pr_payload_file or args.status_checks_file) and os.environ.get("LOOM_ALLOW_TEST_FIXTURES") != "1":
        return emit(output("pr gate", "block", schema=HOST_OBJECT_SCHEMA, summary="Public PR gate requires fresh authenticated GitHub readback; local host-fact fixtures are test-only.", missing_inputs=["remove --pr-payload-file/--status-checks-file"], primary_error_code="github_host_readback_failure", failure_domain="host_service", failure_owner="github", remediation_command="rerun against the live GitHub PR", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    parsed_item = parse_typed_locator(args.work_item, allowed_types={"work_item"}, allow_legacy=False)
    if parsed_item is None:
        return emit(output("pr gate", "block", schema=HOST_OBJECT_SCHEMA, summary="PR gate requires a canonical typed Work Item.", missing_inputs=["owner/repo/work_item/id"], repo_execution_carriers_consumed=False, carrier_mutations=False))
    issue = int(parsed_item["id"])
    lifecycle = host_lifecycle_admission_payload(
        target=target,
        item=args.work_item,
        issue=issue,
        owner=str(parsed_item["owner"]),
        repo_name=str(parsed_item["repo"]),
        intent="pre-review",
        pr=args.pr,
        branch=args.branch,
        pr_role=args.pr_role,
    )
    if lifecycle.get("result") != "pass":
        return emit(output("pr gate", "block", schema=HOST_OBJECT_SCHEMA, summary="PR gate host binding is invalid.", lifecycle_admission=lifecycle, missing_inputs=lifecycle.get("missing_inputs", []), fallback_to=lifecycle.get("primary_remediation"), repo_execution_carriers_consumed=False, carrier_mutations=False))
    repo_slug = infer_github_repo(target)
    owner, repo_name = repo_slug.split("/", 1) if repo_slug and "/" in repo_slug else (None, None)
    pr_payload: dict[str, Any] | None = None
    errors: list[str] = []
    if args.pr_payload_file:
        path = Path(args.pr_payload_file)
        path = path if path.is_absolute() else target / path
        try:
            raw_pr = read_json(path)
            pr_payload = raw_pr if isinstance(raw_pr, dict) else None
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"PR fixture: {exc}")
    elif owner and repo_name:
        pr_payload, errors = github_host_module.github_pr_payload(target, owner, repo_name, args.pr)
    else:
        errors.append("target origin GitHub owner/repo")
    status_payload: Any = None
    if args.status_checks_file:
        path = Path(args.status_checks_file)
        path = path if path.is_absolute() else target / path
        try:
            status_payload = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"status checks fixture: {exc}")
    elif repo_slug:
        completed = run_capture(["gh", "pr", "view", str(args.pr), "--repo", repo_slug, "--json", "statusCheckRollup"])
        if completed.returncode == 0:
            try:
                status_payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"status checks readback: {exc}")
        else:
            errors.append((completed.stderr or completed.stdout or "status checks readback failed").strip())
    rows = status_payload.get("statusCheckRollup", []) if isinstance(status_payload, dict) else status_payload
    rows = rows if isinstance(rows, list) else []
    matches = [
        row for row in rows
        if isinstance(row, dict) and str(row.get("name") or row.get("context") or "") == "loom-delivery-gate"
    ]
    passing = [
        row for row in matches
        if str(row.get("status") or "").upper() == "COMPLETED"
        and str(row.get("conclusion") or row.get("state") or "").upper() in {"SUCCESS", "EXPECTED", "PASS"}
    ]
    if not isinstance(pr_payload, dict):
        errors.append("current PR readback")
    else:
        if int(pr_payload.get("number") or 0) != args.pr:
            errors.append("PR readback number mismatch")
        if str(pr_payload.get("state") or "").upper() != "OPEN":
            errors.append("PR must be open")
        current_head = pr_payload.get("headRefOid")
        if args.head_sha and current_head != args.head_sha:
            errors.append("hosted gate PR head does not match --head-sha")
    if len(matches) != 1:
        errors.append(f"expected one current loom-delivery-gate check; found {len(matches)}")
    elif len(passing) != 1:
        errors.append("loom-delivery-gate is not completed successfully")
    attestation_args = argparse.Namespace(
        owner=owner,
        repo_name=repo_name,
        issue=issue,
        pr=args.pr,
        implementation_pr=None,
        release_pr=None,
        pr_role="implementation_pr",
        attestation_artifact_input=args.attestation_artifact_input,
        review_policy=args.review_policy,
    )
    review_attestation = ship_host_attestation(attestation_args, target, closeout=False)
    if review_attestation.get("result") != "pass":
        errors.extend(str(value) for value in review_attestation.get("missing_inputs", []) or ["current-head review attestation"])
    attested_host_facts = review_attestation.get("host_facts") if isinstance(review_attestation.get("host_facts"), dict) else {}
    attested_pr = attested_host_facts.get("pr") if isinstance(attested_host_facts.get("pr"), dict) else {}
    if isinstance(pr_payload, dict):
        if attested_pr.get("number") != pr_payload.get("number"):
            errors.append("review attestation PR number does not match live PR")
        if attested_pr.get("head_sha") != pr_payload.get("headRefOid"):
            errors.append("review attestation head does not match live PR head")
    result = "pass" if not errors else "block"
    payload = output(
        "pr gate",
        result,
        schema="loom-delivery-gate-readback/v1",
        summary=("The base-owned hosted delivery gate passed for the current PR head." if result == "pass" else "The hosted delivery gate is missing, stale, or non-passing."),
        lifecycle_admission=lifecycle,
        work_item={"locator": args.work_item, "issue": issue},
        pr={
            "number": pr_payload.get("number") if isinstance(pr_payload, dict) else args.pr,
            "head_sha": pr_payload.get("headRefOid") if isinstance(pr_payload, dict) else None,
            "state": pr_payload.get("state") if isinstance(pr_payload, dict) else None,
        },
        hosted_check=passing[0] if passing else (matches[0] if matches else None),
        review_attestation=review_attestation,
        assurance="limited",
        missing_inputs=list(dict.fromkeys(errors)),
        fallback_to=None if result == "pass" else "rerun the base-owned loom-delivery-gate for the current PR head",
        repo_execution_carriers_consumed=False,
        carrier_mutations=False,
        mutates=False,
    )
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


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
    parser.add_argument("--closeout-mode", choices=("host_only",), default="host_only")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--target-branch")
    parser.add_argument("--pr-role", choices=CLOSEOUT_PR_ROLES)
    parser.add_argument("--implementation-pr", type=int)
    parser.add_argument("--release-pr", type=int)
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
    target = resolve_target(pr_command_target(args.target))
    parsed_item = parse_typed_locator(args.work_item, allowed_types={"work_item"}, allow_legacy=False) if args.work_item else None
    if parsed_item is None:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Merge requires a canonical typed Work Item.", missing_inputs=["--work-item <owner>/<repo>/work_item/<issue>"], repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    item_issue = int(parsed_item["id"])
    if args.issue is not None and args.issue != item_issue:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Merge Work Item and issue bindings conflict.", missing_inputs=["consistent --work-item and --issue"], repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    args.issue = item_issue
    effective_pr, pr_conflict = closeout_current_pr_binding(args)
    if pr_conflict:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Merge PR role binding is inconsistent.", missing_inputs=[pr_conflict], primary_error_code="subject_conflict", failure_domain="governance_metadata", failure_owner="operator", remediation_command="make --pr and the selected role-specific PR identify the same pull request", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    lifecycle = host_lifecycle_admission_payload(
        target=target,
        item=args.work_item,
        issue=args.issue,
        owner=str(parsed_item["owner"]),
        repo_name=str(parsed_item["repo"]),
        intent="ship",
        pr=effective_pr,
        pr_role=args.pr_role,
    )
    if lifecycle.get("result") != "pass":
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Merge host binding is invalid.", lifecycle_admission=lifecycle, missing_inputs=lifecycle.get("missing_inputs", []), fallback_to=lifecycle.get("primary_remediation"), repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    unsafe_fixture_inputs = [
        name
        for name, value in (
            ("--pr-payload-file", args.pr_payload_file),
            ("--status-checks-file", args.status_checks_file),
            ("--branch-protection-file", args.branch_protection_file),
            ("--ruleset-file", args.ruleset_file),
        )
        if value
    ]
    if args.action == "run" and args.apply and unsafe_fixture_inputs:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="A mutating merge must use fresh authenticated GitHub readback, not local host-fact fixtures.", missing_inputs=[f"remove {name}" for name in unsafe_fixture_inputs], primary_error_code="github_host_readback_failure", failure_domain="host_service", failure_owner="github", remediation_command="rerun without local PR/check/protection/ruleset fixture inputs", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    if not args.pr_gate_result_file:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="Merge requires the retained base-owned loom-delivery-gate readback for the current PR head.", missing_inputs=["--pr-gate-result-file"], remediation_command="run loom pr gate against the live PR and retain its JSON result", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    if args.merge_gate_result_file:
        return emit(output(command, "block", schema=HOST_OBJECT_SCHEMA, summary="The legacy retained merge-gate input is not part of the public merge path.", missing_inputs=["remove --merge-gate-result-file"], primary_error_code="unsupported_command_surface", failure_domain="toolchain", failure_owner="loom", remediation_command="use the host-native loom-delivery-gate readback only", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
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
        flow_args.extend(["--issue", str(args.issue)])
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
    if args.closeout_run:
        return handle_merge_closeout_run(command, args, flow_args)
    review_attestation = ship_host_attestation(args, target, closeout=False)
    if review_attestation.get("result") != "pass":
        return emit(agent_safe_payload(output(command, "block", schema="loom-host-native-merge/v1", summary="Merge requires a live current-head GitHub review attestation; asserted gate JSON is not review authority.", review_attestation=review_attestation, missing_inputs=review_attestation.get("missing_inputs", []), fallback_to=review_attestation.get("fallback_to"), repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False), target_root=target, full_output=args.full_output))
    controlled = flow_payload(command, flow_args, fallback_to=["refresh the live loom-delivery-gate readback for the current PR head"])
    result = "pass" if controlled.get("result") == "pass" else "block"
    return emit(agent_safe_payload(output(command, result, schema="loom-host-native-merge/v1", summary=("Live review attestation and controlled merge preconditions passed." if result == "pass" else "Controlled merge is blocked after live review attestation."), review_attestation=review_attestation, controlled_merge=controlled, missing_inputs=controlled.get("missing_inputs", []), fallback_to=controlled.get("fallback_to"), repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=bool(controlled.get("merge", {}).get("executed")) if isinstance(controlled.get("merge"), dict) else False), target_root=target, full_output=args.full_output))


def merge_closeout_namespace(args: argparse.Namespace, *, branch: str) -> argparse.Namespace:
    return argparse.Namespace(
        item=args.work_item,
        issue=args.issue,
        pr=args.pr,
        pr_role=args.pr_role,
        implementation_pr=args.implementation_pr,
        release_pr=args.release_pr,
        carrier_sync_pr=None,
        final_closeout_pr=None,
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
    return {
        "schema_version": "loom-closeout-policy-decision/v1",
        "result": "pass",
        "policy": "host_only",
        "source": "merge-closeout-run",
        "creates_closeout_pr_by_default": False,
        "next_action": "run host reconciliation and closeout readback immediately after controlled merge passes",
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
    target = resolve_target(pr_command_target(args.target))
    steps: list[dict[str, Any]] = []
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
                terminal_metadata={},
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


def ship_closeout_policy(fields: dict[str, Any], *, intensity_override: str | None = None) -> dict[str, Any]:
    intensity = intensity_override if intensity_override not in {None, "auto"} else fields.get("governance_intensity")
    change_class = fields.get("change_class")
    release_judgment = fields.get("release_judgment")
    governance_mode = fields.get("governance_mode") or "host-enforced"
    governance_assurance = "low" if governance_mode == "advisory/local-enforced" else "limited"
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
        "next_action": "run loom ship --apply after dry-run blockers are clear" if policy == "host_only" else "publish through the release workflow, then use release readback without a closeout PR",
    }


SHIP_VALIDATION_PROFILE_CHOICES = ("auto", "host-consumer", "carrier-only", "light", "standard", "full", "release")
SHIP_VALIDATION_SOURCE_SURFACES = {
    "host-consumer": None,
    "carrier-only": None,
    "light": "contract-only",
    "standard": "source-self-fixture",
    "full": "source-self-fixture",
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


def github_default_branch_for_target(target: Path) -> tuple[str | None, str | None]:
    repo_slug = infer_github_repo(target)
    if not repo_slug:
        return None, "target origin GitHub owner/repo"
    completed = run_capture(["gh", "repo", "view", repo_slug, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"], cwd=target)
    if completed.returncode != 0:
        return None, (completed.stderr or completed.stdout or "GitHub default branch readback failed").strip()
    branch = completed.stdout.strip()
    return (branch, None) if branch else (None, "GitHub default branch readback was empty")


def public_pr_stage_binding(
    *,
    target: Path,
    lifecycle_admission: dict[str, Any],
    expected_branch: str | None,
) -> dict[str, Any]:
    """Bind a public PR stage to live GitHub and the checked-out worktree only."""

    subject = lifecycle_admission.get("subject_readback")
    subject = subject if isinstance(subject, dict) else {}
    pr_number = subject.get("pr_number")
    repo_slug = infer_github_repo(target)
    missing: list[str] = []
    if not isinstance(repo_slug, str) or repo_slug.count("/") != 1:
        missing.append("target origin GitHub owner/repo")
    if not isinstance(pr_number, int):
        missing.append("current GitHub PR")
    if missing:
        return {
            "result": "block",
            "summary": "The PR stage requires an authenticated GitHub PR binding.",
            "missing_inputs": missing,
            "primary_error_code": "github_host_readback_failure",
            "failure_domain": "host_service",
            "failure_owner": "github",
            "remediation_command": "create or bind the real implementation PR, then retry the same command",
        }
    assert isinstance(repo_slug, str) and isinstance(pr_number, int)
    owner, repo_name = repo_slug.split("/", 1)
    pr_payload, errors = github_host_module.github_pr_payload(target, owner, repo_name, pr_number)
    if errors or pr_payload is None:
        return {
            "result": "block",
            "summary": "The current GitHub PR could not be read back.",
            "missing_inputs": list(errors or ["GitHub PR readback"]),
            "primary_error_code": "github_host_readback_failure",
            "failure_domain": "host_service",
            "failure_owner": "github",
            "remediation_command": f"gh pr view {pr_number} --repo {repo_slug}",
        }
    worktree_branch = git_branch_for_target(target)
    worktree_head = git_head_sha_for_target(target)
    branch = expected_branch or worktree_branch
    if pr_payload.get("state") != "OPEN":
        missing.append(f"open PR; GitHub reports {pr_payload.get('state') or 'UNKNOWN'}")
    if pr_payload.get("isDraft") is True:
        missing.append("PR must be ready for review")
    if branch and pr_payload.get("headRefName") != branch:
        missing.append("PR head branch must match the formal worktree branch")
    if worktree_branch and branch and worktree_branch != branch:
        missing.append("checked-out worktree branch must match the requested branch")
    if worktree_head and pr_payload.get("headRefOid") and worktree_head != pr_payload.get("headRefOid"):
        missing.append("checked-out HEAD must match the current GitHub PR head")
    return {
        "result": "pass" if not missing else "block",
        "summary": (
            "GitHub PR, current head, branch, Work Item, and worktree are consistently bound."
            if not missing
            else "The GitHub PR and formal worktree binding is inconsistent."
        ),
        "missing_inputs": missing,
        "repository": repo_slug,
        "pr": pr_payload,
        "issue_number": subject.get("issue_number"),
        "branch": branch,
        "worktree_head": worktree_head,
        "primary_error_code": None if not missing else "github_host_readback_failure",
        "failure_domain": None if not missing else "host_service",
        "failure_owner": None if not missing else "github",
        "remediation_command": None if not missing else "push the formal worktree head or correct the PR/branch binding, then retry",
        "repo_execution_carriers_consumed": False,
        "carrier_mutations": False,
        "mutates": False,
    }


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
        carrier_sync_pr=None,
        final_closeout_pr=None,
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


def ship_host_attestation(args: argparse.Namespace, target: Path, *, closeout: bool) -> dict[str, Any]:
    detected_repo = infer_github_repo(target)
    requested_repo = f"{args.owner}/{args.repo_name}" if args.owner and args.repo_name else None
    repo_slug = detected_repo
    pr_number, pr_conflict = closeout_current_pr_binding(args)
    if pr_conflict:
        return {
            "command": "attestation closeout" if closeout else "attestation readback",
            "result": "block",
            "summary": "Host attestation PR role binding is inconsistent.",
            "missing_inputs": [pr_conflict],
            "fallback_to": "make --pr and the selected role-specific PR identify the same pull request",
        }
    missing: list[str] = []
    if not isinstance(detected_repo, str) or detected_repo.count("/") != 1:
        missing.append("target origin GitHub owner/repo")
    elif requested_repo is not None and requested_repo != detected_repo:
        missing.append("explicit GitHub owner/repo must match the target origin")
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
    parser.add_argument("--pr-gate-result-file")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    command = "ship"
    target = resolve_target(args.target)
    parsed_item = parse_typed_locator(args.item, allowed_types={"work_item"}, allow_legacy=False)
    if parsed_item is None:
        return emit(output(command, "block", schema="loom-ship/v1", summary="Ship requires a canonical typed Work Item.", missing_inputs=["--item <owner>/<repo>/work_item/<issue>"], repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    item_issue = int(parsed_item["id"])
    if args.issue is not None and args.issue != item_issue:
        return emit(output(command, "block", schema="loom-ship/v1", summary="Ship Work Item and issue bindings conflict.", missing_inputs=["consistent --item and --issue"], repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    args.issue = item_issue
    effective_pr, pr_conflict = closeout_current_pr_binding(args)
    if pr_conflict:
        return emit(output(command, "block", schema="loom-ship/v1", summary="Ship PR role binding is inconsistent.", missing_inputs=[pr_conflict], primary_error_code="subject_conflict", failure_domain="governance_metadata", failure_owner="operator", remediation_command="make --pr and the selected role-specific PR identify the same pull request", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    if args.apply and any((args.pr_payload_file, args.status_checks_file, args.branch_protection_file, args.ruleset_file)):
        return emit(output(command, "block", schema="loom-ship/v1", summary="Mutating ship requires fresh authenticated GitHub readback, not local host-fact fixtures.", missing_inputs=["remove local PR/check/protection/ruleset fixture inputs"], primary_error_code="github_host_readback_failure", failure_domain="host_service", failure_owner="github", remediation_command="rerun ship --apply against live GitHub host facts", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
    lifecycle_admission = host_lifecycle_admission_payload(
        target=target,
        item=args.item,
        issue=args.issue,
        fr=args.fr,
        owner=args.owner,
        repo_name=args.repo_name,
        intent="ship",
        pr=effective_pr,
        branch=args.branch,
        pr_role=args.pr_role,
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
    closeout_policy = ship_closeout_policy({}, intensity_override=args.intensity)
    changed_paths = ship_changed_paths_payload(args, target, target_branch=effective_target_branch, head_sha=effective_head_sha)
    validation_profile = ship_validation_profile_payload(args, changed_paths, closeout_policy)
    review_attestation = ship_host_attestation(args, target, closeout=False)
    if not args.pr_gate_result_file:
        merge_check = {"result": "block", "summary": "Ship requires the retained host-native delivery gate result.", "missing_inputs": ["--pr-gate-result-file"], "fallback_to": "loom pr gate <pr> --work-item <locator> --attestation-artifact-input <locator> --json"}
    else:
        merge_check = delivery_control_module.controlled_merge_payload(
            target_root=target,
            output_relative=".loom/runtime/controlled-merge.json",
            expected_item=args.item,
            owner=str(parsed_item["owner"]),
            repo_name=str(parsed_item["repo"]),
            issue_number=args.issue,
            pr_number=args.pr,
            head_sha=effective_head_sha or args.head_sha,
            merge_method=args.merge_method,
            delete_branch=False,
            execute=False,
            pr_payload_file=args.pr_payload_file,
            status_checks_file=args.status_checks_file,
            branch_protection_file=args.branch_protection_file,
            ruleset_file=args.ruleset_file,
            pr_gate_result_file=args.pr_gate_result_file,
            merge_gate_result_file=None,
        )
    steps.extend([
        ship_step("host-review-attestation", review_attestation),
        ship_step("controlled-merge-check", merge_check),
        ship_step("validation-profile", validation_profile),
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
            fallback_to=["use an explicit release Work Item and host attestation when policy requires it"],
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
        merge_apply = delivery_control_module.controlled_merge_payload(
            target_root=target,
            output_relative=".loom/runtime/controlled-merge.json",
            expected_item=args.item,
            owner=str(parsed_item["owner"]),
            repo_name=str(parsed_item["repo"]),
            issue_number=args.issue,
            pr_number=args.pr,
            head_sha=effective_head_sha or args.head_sha,
            merge_method=args.merge_method,
            delete_branch=False,
            execute=True,
            pr_payload_file=None,
            status_checks_file=None,
            branch_protection_file=None,
            ruleset_file=None,
            pr_gate_result_file=args.pr_gate_result_file,
            merge_gate_result_file=None,
        )
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
        final_closeout = ship_host_attestation(args, target, closeout=True)
        steps.append(ship_step("host-closeout-attestation", final_closeout, mutates=False))

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


def first_blocking_step(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    for step in steps:
        if step.get("result") != "pass":
            return step
    return None


def supported_hosts(target: Path) -> list[dict[str, Any]]:
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    codex_paths = codex_workstation_paths(home=home, codex_home=codex_home)
    return [
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
    ]


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
    cli_command = f"npm install -g @mc-and-his-agents/loom@{target_version}"
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
                "commands": [],
                "marketplace_upgrade": {
                    "source": "MC-and-his-Agents/Loom",
                    "summary": "Refresh the Loom plugin through the Codex marketplace, then reload the Codex runtime cache.",
                    "provider_action": {
                        "provider": "codex",
                        "operation": "refresh_marketplace_plugin",
                    },
                    "fallback_commands": [],
                },
                "required": freshness.get("action") == "upgrade_cli" or freshness.get("plugin_payload", {}).get("action") != "already_current",
                "mutates_when_applied": "user Codex marketplace/config/plugin cache",
            },
            {
                "id": "verify-host",
                "kind": "host-doctor",
                "command": "loom doctor --target <repo> --json",
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
    return {
        "status": "present",
        "locator": ".loom/installed-state.json",
        "valid": True,
        "blocking": False,
        "schema_version": payload.get("schema_version"),
        "repo_payload_mode": repo_payload.get("mode"),
        "version_context": payload.get("version_context") if isinstance(payload.get("version_context"), dict) else {},
    }


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
    parser.add_argument("--host", default="auto", choices=("auto", "codex"))
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


def handle_route(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom route")
    parser.add_argument("--target", required=True, help="Target repository root")
    parser.add_argument("--item", help="Canonical owner/repo/work_item/id locator")
    parser.add_argument("--issue", type=int, help="GitHub FR or Work Item issue number")
    parser.add_argument("--task", help="Bounded Work Item proposal text")
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
    target = resolve_target(args.target)
    parsed_item = parse_typed_locator(args.item, allowed_types={"work_item"}, allow_legacy=False) if args.item else None
    if args.item and parsed_item is None:
        return emit(output("route", "block", schema=SCENARIO_SCHEMA, summary="Route requires a canonical host Work Item subject.", missing_inputs=["canonical Work Item locator"], fallback_to="provide --issue <issue> or --item <owner/repo/work_item/id>"))
    if parsed_item is not None:
        target_repo_slug = infer_github_repo(target)
        target_owner, target_repo = target_repo_slug.split("/", 1) if target_repo_slug and "/" in target_repo_slug else (None, None)
        if not target_owner or not target_repo:
            return emit(output("route", "block", schema=SCENARIO_SCHEMA, summary="Route requires a readable target origin GitHub repository.", missing_inputs=["target origin GitHub owner/repo"], fallback_to="restore the target origin before routing a typed Work Item"))
        if parsed_item["owner"].casefold() != target_owner.casefold() or parsed_item["repo"].casefold() != target_repo.casefold():
            return emit(output("route", "block", schema=SCENARIO_SCHEMA, summary="Route typed Work Item does not belong to the target repository.", missing_inputs=["typed Work Item matching target origin"], fallback_to="make --item and --target identify the same repository"))
    issue = args.issue or (int(parsed_item["id"]) if parsed_item else None)
    if issue is None:
        if args.task and args.intent == "planning" and not args.apply and not args.blocked_by and args.work_item is None:
            return emit(
                output(
                    "route",
                    "pass",
                    schema=SCENARIO_SCHEMA,
                    summary="The task remains an unbound read-only planning input; execution is not admitted.",
                    target=str(target),
                    admission_state="planning_unbound",
                    task=args.task,
                    selected_skill="loom-adopt",
                    mutates=False,
                    host_mutations=False,
                    carrier_mutations=False,
                    execution_admitted=False,
                    next_action="select or provide one GitHub FR/Work Item subject before entering execution",
                    fallback_to="loom route --target <repo> --issue <issue> --json",
                )
            )
        return emit(output("route", "block", schema=SCENARIO_SCHEMA, summary="Route requires one host subject.", missing_inputs=["host subject"], fallback_to="loom route --target <repo> --issue <issue> --json"))
    if args.issue is not None and parsed_item is not None and args.issue != parsed_item["id"]:
        return emit(output("route", "block", schema=SCENARIO_SCHEMA, summary="Route host subjects conflict.", missing_inputs=["consistent Work Item subject"], fallback_to="make --issue and --item identify the same Work Item"))
    repo_slug = infer_github_repo(target)
    owner, repo_name = repo_slug.split("/", 1) if repo_slug and "/" in repo_slug else (None, None)
    payload = github_fr_wi_admission_payload(
        host=GITHUB_ADMISSION_HOST,
        target_root=target,
        owner=str(parsed_item["owner"]) if parsed_item is not None else owner,
        repo_name=str(parsed_item["repo"]) if parsed_item is not None else repo_name,
        issue_number=int(issue),
        intent=args.intent,
        task=args.task,
        blocked_by=args.blocked_by,
        work_item_number=args.work_item,
        apply=args.apply,
        lifecycle_only=False,
    )
    payload["command"] = "route"
    payload["repo_execution_carriers_consumed"] = False
    payload["carrier_mutations"] = False
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def handle_status(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="loom status")
    parser.add_argument("--target", default=".")
    parser.add_argument("--item")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--branch")
    parser.add_argument("--owner")
    parser.add_argument("--repo", dest="repo_name")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target("status", target, "target path does not exist"))
    repo_slug = infer_github_repo(target)
    owner, repo_name = repo_slug.split("/", 1) if repo_slug and "/" in repo_slug else (None, None)
    owner, repo_name = args.owner or owner, args.repo_name or repo_name
    branch = args.branch or git_branch_for_target(target)
    head = git_head_sha_for_target(target)
    subject: dict[str, Any] | None = None
    if owner and repo_name and any(value is not None for value in (args.item, args.issue, args.pr)):
        parsed_item = parse_typed_locator(args.item, allowed_types={"work_item"}, allow_legacy=False) if args.item else None
        if args.item and parsed_item is None:
            return emit(output("status", "block", schema=SCENARIO_SCHEMA, summary="Status requires a canonical typed Work Item locator.", missing_inputs=["canonical Work Item locator"], repo_execution_carriers_consumed=False, carrier_mutations=False))
        subject = github_lifecycle_subject_readback(
            target,
            owner,
            repo_name,
            issue_number=args.issue or (int(parsed_item["id"]) if parsed_item else None),
            pr_number=args.pr,
            branch_name=branch,
            intent="build" if args.pr is None else "pre-review",
            target_owner=repo_slug.split("/", 1)[0] if repo_slug and "/" in repo_slug else None,
            target_repo=repo_slug.split("/", 1)[1] if repo_slug and "/" in repo_slug else None,
        )
    result = "pass" if subject is None or subject.get("result") == "pass" else "block"
    payload = output(
        "status",
        result,
        schema=SCENARIO_SCHEMA,
        summary=("Status is derived from the formal worktree and live GitHub subject; repository execution carriers were not read." if result == "pass" else "Live GitHub subject readback is inconsistent."),
        target=str(target),
        repository=repo_slug,
        branch=branch,
        head_sha=head,
        subject_readback=subject,
        missing_inputs=[] if subject is None else subject.get("errors", []),
        fallback_to=None if result == "pass" else "correct the explicit Work Item/PR/branch binding and retry",
        repo_execution_carriers_consumed=False,
        carrier_mutations=False,
        mutates=False,
    )
    annotate_global_cli_runtime_entrypoint(payload, command="status", target=target, argv=argv)
    return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))


def handle_profile(argv: list[str]) -> int:
    if not argv:
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Profile requires an operation.", failed_layer="profile-input", fail_closed_reason="missing profile operation", fallback_to=["loom profile status --target <repo> --json"]))
    operation = argv[0]
    if operation == "light-migration-reconcile":
        return emit_delegated(
            "profile light-migration-reconcile",
            "light_profile.py",
            ["reconcile", *strip_json_flag(argv[1:])],
            failed_layer="light-profile-migration",
            fallback_to=["loom profile light-migration-reconcile --target <repo> --repository <owner/repo> --branch <branch> --work-item <issue> --gate-pr <pr> --migration-pr <pr> --context <check> --app-id <id> --json"],
        )
    if operation != "status":
        return emit(output("profile", "block", schema=PROFILE_SCHEMA, summary="Unsupported profile operation.", failed_layer="profile-input", fail_closed_reason=f"unsupported profile operation: {operation}", fallback_to=["loom profile status --target <repo> --json", "loom profile light-migration-reconcile --target <repo> --repository <owner/repo> --branch <branch> --work-item <issue> --gate-pr <pr> --migration-pr <pr> --context <check> --app-id <id> --json"]))
    return emit_flow(f"profile {operation}", ["governance-profile", operation, *strip_json_flag(argv[1:])], fallback_to=["loom profile status --target <repo> --json", "docs/adoption/github-profile-upgrade.md"])


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
    parser.add_argument("--pr-gate-result-file")
    parser.add_argument("--merge-gate-result-file")
    parser.add_argument("--attestation-artifact-input", type=Path)
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--project-drift-mode", choices=("advisory", "blocking"), default="advisory")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full-output", action="store_true")
    args = parser.parse_args(argv)
    target = resolve_target(args.target)
    if not target.exists():
        return emit(block_target(command, target, "target path does not exist"))
    derived_manifest, manifest_errors = host_derived_manifest(target)
    if manifest_errors:
        return emit(
            agent_safe_payload(
                output(
                    command,
                    "block",
                    schema_version=SCENARIO_SCHEMA,
                    summary="Light-profile manifest is invalid; legacy execution carriers are not a fallback.",
                    target=str(target),
                    missing_inputs=manifest_errors,
                    fallback_to="loom adopt verify --target <repo> --json",
                    carrier_mutations=False,
                    repo_execution_carriers_consumed=False,
                ),
                target_root=target,
                full_output=args.full_output,
            )
        )

    if command == "story":
        payload = flow_payload(
            command,
            ["flow", "story", "--target", str(target), *(["--item", args.item] if args.item else [])],
            fallback_to=["loom route --target <repo> --issue <issue> --json"],
        )
        payload.setdefault("schema_version", SCENARIO_SCHEMA)
        payload["command"] = command
        annotate_global_cli_runtime_entrypoint(payload, command="story", target=target, argv=argv)
        return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))

    if command in {"build", "pre-review", "review", "merge-ready"}:
        legacy_item_match = re.fullmatch(r"WI-(\d+)", args.item or "")
        if legacy_item_match is not None:
            return emit(
                output(
                    command,
                    "block",
                    schema=SCENARIO_SCHEMA,
                    summary="Legacy Work Item locators are removed from the public lifecycle.",
                    missing_inputs=["canonical typed Work Item locator"],
                    primary_error_code="unsupported_command_surface",
                    failure_domain="toolchain",
                    failure_owner="loom",
                    remediation_command="use <owner>/<repo>/work_item/<issue> together with --issue <issue>",
                    carrier_mutations=False,
                    repo_execution_carriers_consumed=False,
                )
            )
        stage_intent = "build" if command == "build" else "pre-review"
        effective_branch = args.branch or git_branch_for_target(target)
        effective_pr, pr_conflict = closeout_current_pr_binding(args)
        if pr_conflict:
            return emit(
                output(
                    command,
                    "block",
                    schema=SCENARIO_SCHEMA,
                    summary="Lifecycle PR role binding is inconsistent.",
                    missing_inputs=[pr_conflict],
                    primary_error_code="subject_conflict",
                    failure_domain="governance_metadata",
                    failure_owner="operator",
                    remediation_command="make --pr and the selected role-specific PR identify the same pull request",
                    repo_execution_carriers_consumed=False,
                    carrier_mutations=False,
                    mutates=False,
                )
            )
        lifecycle_admission = host_lifecycle_admission_payload(
            target=target,
            item=args.item,
            issue=args.issue,
            fr=args.fr,
            owner=args.owner,
            repo_name=args.repo_name,
            intent=stage_intent,
            pr=effective_pr,
            branch=effective_branch,
            pr_role=args.pr_role,
        )
        if lifecycle_admission["result"] != "pass":
            return emit(
                output(
                    command,
                    "block",
                    schema=SCENARIO_SCHEMA,
                    summary="Host lifecycle admission blocked without reading repository execution carriers.",
                    lifecycle_admission=lifecycle_admission,
                    missing_inputs=lifecycle_admission.get("missing_inputs", []),
                    fallback_to=lifecycle_admission.get("primary_remediation"),
                    repo_execution_carriers_consumed=False,
                    carrier_mutations=False,
                )
            )
        subject = lifecycle_admission.get("subject_readback") if isinstance(lifecycle_admission.get("subject_readback"), dict) else {}
        if command == "build":
            local_branch = git_branch_for_target(target)
            branch_errors = []
            default_branch, default_branch_error = github_default_branch_for_target(target)
            if not effective_branch:
                branch_errors.append("formal issue-scoped branch")
            elif local_branch != effective_branch:
                branch_errors.append("checked-out worktree branch must match --branch")
            if default_branch_error:
                branch_errors.append(f"GitHub default branch readback: {default_branch_error}")
            elif effective_branch == default_branch:
                branch_errors.append("build must not run on the repository default branch")
            item_issue = subject.get("issue_number") or args.issue
            if effective_branch and isinstance(item_issue, int) and re.search(rf"(?:^|[/_-]){item_issue}(?:$|[/_-])", effective_branch) is None:
                branch_errors.append("formal branch must be issue-scoped to the Work Item")
            result = "pass" if not branch_errors else "block"
            return emit(
                output(
                    command,
                    result,
                    schema=SCENARIO_SCHEMA,
                    summary=(
                        "Build is admitted from the explicit GitHub Work Item and worktree branch; no PR or repository execution carrier is required."
                        if result == "pass"
                        else "Build requires the formal issue-scoped worktree branch, but never an empty PR."
                    ),
                    target=str(target),
                    item={"id": args.item, "issue": subject.get("issue_number") or args.issue},
                    branch=effective_branch,
                    pre_pr=subject.get("pr_number") is None,
                    lifecycle_admission=lifecycle_admission,
                    missing_inputs=branch_errors,
                    repo_execution_carriers_consumed=False,
                    carrier_mutations=False,
                    mutates=False,
                    next_action="implement the bounded Work Item, then run loom pre-review after a real diff and PR exist" if result == "pass" else "switch to the formal issue-scoped branch and retry",
                    fallback_to=None if result == "pass" else "git switch <issue-scoped-branch>",
                )
            )
        binding = public_pr_stage_binding(
            target=target,
            lifecycle_admission=lifecycle_admission,
            expected_branch=effective_branch,
        )
        if binding["result"] != "pass" or command == "pre-review":
            payload = output(
                command,
                binding["result"],
                schema=SCENARIO_SCHEMA,
                summary=binding["summary"],
                lifecycle_admission=lifecycle_admission,
                host_binding=binding,
                missing_inputs=binding.get("missing_inputs", []),
                fallback_to=binding.get("remediation_command"),
                next_action=("perform semantic review and publish a current-head host attestation" if binding["result"] == "pass" else binding.get("remediation_command")),
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
            )
            return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))
        attestation = ship_host_attestation(args, target, closeout=False)
        if attestation.get("result") != "pass" or command == "review":
            result = "pass" if attestation.get("result") == "pass" else "block"
            payload = output(
                command,
                result,
                schema=SCENARIO_SCHEMA,
                summary=(
                    "Current-head semantic review is authenticated by GitHub host attestation."
                    if result == "pass"
                    else "Semantic review is not authenticated for the current GitHub PR head."
                ),
                lifecycle_admission=lifecycle_admission,
                host_binding=binding,
                review_attestation=attestation,
                missing_inputs=attestation.get("missing_inputs", []),
                fallback_to=attestation.get("fallback_to"),
                next_action="run loom merge-ready with the same current-head attestation and hosted PR-gate result" if result == "pass" else attestation.get("fallback_to"),
                repo_execution_carriers_consumed=False,
                carrier_mutations=False,
                mutates=False,
            )
            return emit(agent_safe_payload(payload, target_root=target, full_output=args.full_output))
        if not args.pr_gate_result_file:
            return emit(
                output(
                    command,
                    "block",
                    schema=SCENARIO_SCHEMA,
                    summary="Merge readiness requires the hosted PR-gate result for this exact PR head.",
                    lifecycle_admission=lifecycle_admission,
                    host_binding=binding,
                    review_attestation=attestation,
                    missing_inputs=["--pr-gate-result-file"],
                    fallback_to="download or save the hosted loom-delivery-gate result, then retry",
                    repo_execution_carriers_consumed=False,
                    carrier_mutations=False,
                    mutates=False,
                )
            )
        repo_slug = str(binding["repository"])
        owner, repo_name = repo_slug.split("/", 1)
        work_item = args.item or typed_locator(owner, repo_name, "work_item", int(subject["issue_number"]))
        effective_issue = int(subject["issue_number"])
        if any((args.pr_payload_file, args.status_checks_file, args.branch_protection_file, args.ruleset_file)) and os.environ.get("LOOM_ALLOW_TEST_FIXTURES") != "1":
            return emit(output(command, "block", schema=SCENARIO_SCHEMA, summary="Public merge readiness requires live GitHub host facts; local host-fact fixtures are test-only.", missing_inputs=["remove local PR/check/protection/ruleset fixture inputs"], primary_error_code="github_host_readback_failure", failure_domain="host_service", failure_owner="github", remediation_command="rerun against the live GitHub PR", repo_execution_carriers_consumed=False, carrier_mutations=False, mutates=False))
        pr_number = int(binding.get("pr", {}).get("number"))
        merge_args = [
            "controlled-merge", "check", "--target", str(target), "--pr", str(pr_number),
            "--item", work_item, "--issue", str(effective_issue),
            "--head-sha", str(binding.get("pr", {}).get("headRefOid")),
            "--owner", owner, "--repo", repo_name,
            "--pr-gate-result-file", args.pr_gate_result_file,
        ]
        for flag, value in (
            ("--pr-payload-file", args.pr_payload_file),
            ("--status-checks-file", args.status_checks_file),
            ("--branch-protection-file", args.branch_protection_file),
            ("--ruleset-file", args.ruleset_file),
            ("--merge-gate-result-file", args.merge_gate_result_file),
        ):
            if value:
                merge_args.extend([flag, str(value)])
        merge_check = flow_payload(command, merge_args, fallback_to=["refresh the hosted gate result for the current PR head"])
        result = "pass" if merge_check.get("result") == "pass" else "block"
        payload = output(
            command,
            result,
            schema=SCENARIO_SCHEMA,
            summary=("The current PR head is merge-ready from host attestation, retained hosted gate, required checks, and mergeability." if result == "pass" else "The current PR head is not merge-ready."),
            lifecycle_admission=lifecycle_admission,
            host_binding=binding,
            review_attestation=attestation,
            merge_check=merge_check,
            missing_inputs=merge_check.get("missing_inputs", []),
            fallback_to=merge_check.get("fallback_to"),
            repo_execution_carriers_consumed=False,
            carrier_mutations=False,
            mutates=False,
        )
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
        attestation = ship_host_attestation(args, target, closeout=True)
        attestation["command"] = "closeout"
        attestation["profile"] = derived_manifest.get("profile") if isinstance(derived_manifest, dict) else None
        attestation["repo_execution_carriers_consumed"] = False
        attestation["carrier_mutations"] = False
        return emit(agent_safe_payload(attestation, target_root=target, full_output=args.full_output))

    return emit(output(command, "block", schema=SCENARIO_SCHEMA, summary="Unsupported scenario command.", failed_layer="scenario-input", fail_closed_reason=command, fallback_to=["loom help --json"]))


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


def resolve_removed_legacy_command(argv: list[str]) -> str | None:
    """Recognize a retired command without parsing target, host, or mutation flags."""

    for length in (3, 2, 1):
        if len(argv) >= length:
            candidate = " ".join(argv[:length])
            if candidate in LEGACY_COMMAND_INVENTORY:
                return candidate
    return None


def reject_unsupported_command_surface(command: str) -> int:
    return emit(
        output(
            command,
            "block",
            summary="This command is not part of the Loom v0.31 public surface.",
            failed_layer="cli-command-router",
            fail_closed_reason="unsupported legacy command surface",
            fallback_to=["loom help --json"],
            failure_domain="toolchain",
            primary_error_code="unsupported_command_surface",
            cause_class="unsupported_command_surface",
            failure_owner="loom",
            retryable=False,
            remediation_command="loom help --json",
            mutates=False,
            host_mutations=False,
            carrier_mutations=False,
        )
    )


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

    removed_legacy_command = resolve_removed_legacy_command(argv[1:])
    if removed_legacy_command is not None:
        return reject_unsupported_command_surface(removed_legacy_command)

    resolved = resolve_command(argv[1:])
    if resolved is None:
        print_usage(sys.stderr)
        return 2
    command, forwarded = resolved

    if command not in PUBLIC_COMMAND_NAMES and command not in {"-h", "--help"}:
        return reject_unsupported_command_surface(command)

    if command in {"-h", "--help", "help"}:
        return handle_help(forwarded)
    if command == "version":
        return handle_version(forwarded)
    if command == "detect":
        return handle_detect(forwarded)
    if command == "doctor":
        return handle_doctor(forwarded)
    if command == "installed-state validate":
        return handle_installed_state(command.split()[1:] + forwarded)
    if command == "repair plan":
        return handle_repair(["plan", *forwarded])
    if command == "release readback":
        return handle_release(["readback", *forwarded])
    if command in {"install", "upgrade", "verify"}:
        return handle_delivery(command, forwarded)
    if command.startswith("workspace "):
        return handle_workspace([command.split()[1], *forwarded])
    if command == "pr gate":
        return handle_public_pr_gate(forwarded)
    if command.startswith("merge "):
        return handle_merge([command.split()[1], *forwarded])
    if command == "ship":
        return handle_ship(forwarded)
    if command == "acceptance resolve":
        return emit_imported_main(command, product_acceptance_main, ["resolve", *forwarded])
    if command.startswith("attestation "):
        return emit_imported_main(command, host_attestation_main, [command.split()[1], *forwarded])
    if command == "route":
        return handle_route(forwarded)
    if command == "status":
        return handle_status(forwarded)
    if command.startswith("profile "):
        return handle_profile([command.split()[1], *forwarded])
    if command in {"story", "build", "pre-review", "review", "merge-ready", "closeout"}:
        return handle_scenario(command, forwarded)
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
