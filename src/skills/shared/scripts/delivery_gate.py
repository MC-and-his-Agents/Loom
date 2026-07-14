#!/usr/bin/env python3
"""Evaluate delivery facts without reading Loom repository carriers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from failure_envelope import envelope, primary_cause
from light_profile import LIGHT_PROFILES, STATE_FILENAMES, installed_state, plan_payload as evaluate_light_profile, read_json
from native_validation import ALLOWED_MAKE_TARGETS, parse_make_targets


SCHEMA = "loom-delivery-gate/v1"
HOST_FACTS_SCHEMA = "loom-delivery-gate-host-facts/v1"
REQUIRED_CHECK_IDENTITY_SCHEMA = "loom-delivery-gate-required-check-identity/v3"
REQUIRED_CHECK_IDENTITY_READINESS_SCHEMA = "loom-delivery-gate-required-check-readiness/v3"
SUPPORTED_EVENTS = {"pull_request_target", "merge_group"}
PROFILES = {"light", "standard", "reinforced"}
PROFILE_ORDER = {"light": 0, "standard": 1, "reinforced": 2}
ADOPTION_PROFILES = {
    "attach-only": "light",
    "light-governance": "light",
    "execution-control": "standard",
    "strong-governance": "reinforced",
}
ENFORCEMENTS = {"advisory", "enforce"}
LIGHT_PATH_PREFIXES = ("docs/",)
LIGHT_PATHS = {"README.md", "README.zh-CN.md"}
EXACT_NATIVE_SURFACES = {
    ".github/workflows/host-attestation-evidence.yml": ("host-attestation-check", "workflow-contract-check"),
    ".github/workflows/loom-check.yml": ("workflow-contract-check",),
    ".github/workflows/loom-cli-release.yml": ("release-surface-check", "workflow-contract-check"),
    ".github/workflows/loom-delivery-gate.yml": ("delivery-gate-check", "workflow-contract-check"),
    ".github/workflows/loom-delivery-gate-attestor.yml": ("distinct-app-gate-workflow-check", "workflow-contract-check"),
    ".github/workflows/loom-fr-phase-close-guard.yml": ("fr-phase-close-guard-check", "workflow-contract-check"),
    ".github/workflows/loom-product-acceptance.yml": ("product-acceptance-adapter-check", "workflow-contract-check"),
    ".github/workflows/pr-merge-gate.yml": ("pr-binding-workflow-check", "workflow-contract-check"),
    "tools/check_authority_contract.py": ("authority-contract-check", "fr-wi-admission-check"),
    "tools/check_cli_contract.py": ("cli-contract-check",),
    "tools/check_composite_actions.py": ("composite-action-contract-check",),
    "tools/check_delivery_gate.py": ("delivery-gate-check",),
    "tools/check_distinct_app_gate_workflow.py": ("distinct-app-gate-workflow-check",),
    "tools/check_demo_bootstrap_fixture.py": ("loom-demo-new-project-check",),
    "tools/check_fr_phase_close_guard.py": ("fr-phase-close-guard-check",),
    "tools/check_fr_phase_close_guard_workflow.py": ("fr-phase-close-guard-check",),
    "tools/check_host_attestation.py": ("host-attestation-check",),
    "tools/check_light_profile.py": ("light-profile-check",),
    "tools/check_loom_check_runtime_regressions.py": ("loom-check-runtime-regression",),
    "tools/check_npm_package.py": ("npm-package-check",),
    "tools/check_pr_binding_workflow.py": ("pr-binding-workflow-check",),
    "tools/check_product_acceptance_adapter.py": ("product-acceptance-adapter-check",),
    "tools/check_release_admission.py": ("release-surface-check",),
    "tools/check_release_surface.py": ("release-surface-check",),
    "tools/release_admission.py": ("release-surface-check",),
    "tools/host_adapter_check.py": ("host-adapter-check",),
    "tools/read_delivery_gate_required_identity.py": ("delivery-gate-check",),
    "tools/run_trusted_candidate_validation.py": ("delivery-gate-check",),
    "tools/skills_surface.py": ("skills-check",),
    "tools/stamp_plugin_payload_metadata.py": ("npm-package-check",),
    "tools/version_surface_check.py": ("release-surface-check",),
    "tools/write_product_acceptance.py": ("product-acceptance-adapter-check",),
}
SCRIPT_NATIVE_SURFACES = {
    "authority_contract.py": ("authority-contract-check",),
    "github_admission.py": ("authority-contract-check", "fr-wi-admission-check"),
    "github_closure_guard.py": ("fr-phase-close-guard-check",),
    "host_attestation.py": ("host-attestation-check",),
    "light_profile.py": ("light-profile-check",),
    "product_acceptance.py": ("product-acceptance-adapter-check",),
    "failure_envelope.py": ("failure-envelope-check",),
    "native_validation.py": ("delivery-gate-check", "light-profile-check"),
    "delivery_gate.py": ("delivery-gate-check",),
}
CAUSES = {
    "host_facts_unreadable": {
        "failure_domain": "host_service",
        "code": "unreadable",
        "locator": "host_facts:unreadable",
        "summary": "GitHub host facts are unreadable or incomplete.",
        "owner": "github",
        "retryable": True,
        "transient": True,
        "remediation_command": "rerun loom-delivery-gate after GitHub host fact readback succeeds",
    },
    "profile_unsupported": {
        "failure_domain": "governance_metadata",
        "code": "unsupported",
        "locator": "delivery_profile:unsupported",
        "summary": "The requested delivery profile is unsupported.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "set host_facts.profile to light, standard, or reinforced",
    },
    "candidate_profile_unreadable": {
        "failure_domain": "carrier",
        "code": "unreadable",
        "locator": "candidate_tree:repository_profile",
        "summary": "The candidate repository profile metadata is unreadable or unsupported.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "restore valid installed-state or companion repository profile metadata",
    },
    "profile_state_mismatch": {
        "failure_domain": "governance_metadata",
        "code": "mismatch",
        "locator": "delivery_profile:candidate_state_mismatch",
        "summary": "The requested delivery profile would downgrade the candidate repository profile.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "remove the profile override or select a profile at least as strong as candidate state",
    },
    "invalid_change_set": {
        "failure_domain": "governance_metadata",
        "code": "invalid",
        "locator": "change_set:invalid",
        "summary": "Changed paths are not a normalized repository-relative change set.",
        "owner": "github",
        "retryable": True,
        "remediation_command": "rerun loom-delivery-gate with normalized GitHub changed paths",
    },
    "validation_command_missing": {
        "failure_domain": "toolchain",
        "code": "command_missing",
        "locator": "native_validation:command_missing",
        "summary": "The selected native validation command is unavailable.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "declare an installed native validation command for this delivery profile",
    },
    "native_validation_failed": {
        "failure_domain": "toolchain",
        "code": "failed",
        "locator": "native_validation:failed",
        "summary": "The selected native validation command failed.",
        "owner": "repository",
        "retryable": True,
        "remediation_command": "fix the reported native validation failure, then rerun loom-delivery-gate",
    },
    "light_profile_forbidden_carrier": {
        "failure_domain": "carrier",
        "code": "forbidden_carrier",
        "locator": "candidate_tree:forbidden_carrier",
        "summary": "The candidate tree contains carriers forbidden by the declared light profile.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "remove forbidden light-profile carriers from the candidate tree",
    },
    "light_profile_state_unreadable": {
        "failure_domain": "carrier",
        "code": "unreadable",
        "locator": "candidate_tree:installed_state",
        "summary": "The candidate tree does not expose readable light-profile installed state.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "restore valid metadata-only light-profile installed state",
    },
    "light_profile_tree_unreadable": {
        "failure_domain": "environment",
        "code": "unreadable",
        "locator": "candidate_tree:unreadable",
        "summary": "The declared light-profile candidate tree could not be evaluated.",
        "owner": "github",
        "retryable": True,
        "transient": True,
        "remediation_command": "rerun loom-delivery-gate after the candidate checkout is readable",
    },
    "git_history_unreadable": {
        "failure_domain": "git_history",
        "code": "unreadable",
        "locator": "git_history:unreadable",
        "summary": "The Git history required to resolve the candidate change is unavailable.",
        "owner": "github",
        "retryable": True,
        "transient": True,
        "remediation_command": "rerun loom-delivery-gate with readable base and head history",
    },
    "environment_unavailable": {
        "failure_domain": "environment",
        "code": "unavailable",
        "locator": "environment:unavailable",
        "summary": "The delivery-gate execution environment is unavailable.",
        "owner": "ci",
        "retryable": True,
        "transient": True,
        "remediation_command": "rerun loom-delivery-gate after the execution environment is available",
    },
    "permission_denied": {
        "failure_domain": "permission",
        "code": "denied",
        "locator": "github:permission",
        "summary": "GitHub denied a host read required by the delivery gate.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "grant the workflow the documented read permissions, then rerun loom-delivery-gate",
    },
    "enforcement_unsupported": {
        "failure_domain": "governance_metadata",
        "code": "enforcement_unsupported",
        "locator": "delivery_gate:enforcement_unsupported",
        "summary": "The requested delivery-gate enforcement mode is unsupported.",
        "owner": "repository",
        "retryable": False,
        "remediation_command": "set delivery-gate enforcement to advisory or enforce",
    },
    "passed": {
        "failure_domain": "governance_metadata",
        "code": "passed",
        "locator": "delivery:passed",
        "summary": "Host facts and selected native validation passed.",
        "owner": "loom",
        "retryable": False,
        "remediation_command": "none",
    },
}

IDENTITY_CAUSES = {
    "required_check_identity_unreadable": {
        "failure_domain": "host_service",
        "code": "unreadable",
        "locator": "required_check_identity:unreadable",
        "summary": "The required-check host readback is malformed or incomplete.",
        "owner": "github",
        "retryable": True,
        "remediation_command": "rerun required-check identity readback after GitHub branch controls are readable",
    },
    "required_check_identity_unknown": {
        "failure_domain": "governance_metadata",
        "code": "unknown",
        "locator": "required_check_identity:unknown",
        "summary": "GitHub does not show the expected delivery check as required with an app identity.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "configure the expected delivery check and GitHub App identity in branch protection",
    },
    "required_check_identity_invalid": {
        "failure_domain": "governance_metadata",
        "code": "invalid",
        "locator": "required_check_identity:invalid",
        "summary": "GitHub requires the expected delivery-check context from a different app identity.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "replace the required check with loom-delivery-gate from the expected GitHub App",
    },
    "legacy_required_checks_present": {
        "failure_domain": "governance_metadata",
        "code": "legacy_required_checks_present",
        "locator": "required_check_identity:legacy_required_checks_present",
        "summary": "Configured legacy required checks remain enforced by GitHub branch controls.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "remove the listed legacy required checks from GitHub branch controls",
    },
    "unexpected_required_checks_present": {
        "failure_domain": "governance_metadata",
        "code": "unexpected_required_checks_present",
        "locator": "required_check_identity:unexpected_required_checks_present",
        "summary": "Undeclared required checks remain enforced by GitHub branch controls.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "declare or remove the unexpected required checks in GitHub branch controls",
    },
    "host_enforcement_unavailable": {
        "failure_domain": "host_service",
        "code": "host_enforcement_unavailable",
        "locator": "required_check_identity:host_enforcement_unavailable",
        "summary": "GitHub host enforcement cannot distinguish the trusted delivery gate from a spoofed same-app context.",
        "owner": "operator",
        "retryable": False,
        "remediation_command": "configure a required workflow/path or a distinct GitHub App check identity",
    },
    "passed": {
        "failure_domain": "governance_metadata",
        "code": "passed",
        "locator": "required_check_identity:passed",
        "summary": "GitHub requires the expected delivery-check context from the expected app identity.",
        "owner": "loom",
        "retryable": False,
        "remediation_command": "none",
    },
    "passed_limited": {
        "failure_domain": "governance_metadata",
        "code": "passed_limited",
        "locator": "required_check_identity:passed_limited",
        "summary": "GitHub requires the expected base-owned delivery check with limited same-app identity assurance.",
        "owner": "loom",
        "retryable": False,
        "remediation_command": "none",
    },
}


def _paths(value: object) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], ["changed_paths must be a list"]
    paths: list[str] = []
    errors: list[str] = []
    for raw_path in value:
        if not isinstance(raw_path, str) or not raw_path or raw_path.startswith("/") or ".." in raw_path.split("/"):
            errors.append("changed_paths must contain normalized repository-relative paths")
            continue
        paths.append(raw_path)
    return paths, list(dict.fromkeys(errors))


def _candidate_profile(candidate_path: Path | None, paths: list[str]) -> tuple[str | None, dict[str, Any], list[str]]:
    profile = {"status": "not_declared", "profile": None, "adoption_mode": None, "authority": None}
    if candidate_path is None:
        return None, profile, []
    if candidate_path.is_symlink() or not candidate_path.is_dir():
        profile["status"] = "unreadable"
        return None, profile, ["candidate tree is unavailable"]
    existing_state = next((locator for locator in STATE_FILENAMES if (candidate_path / locator).exists() or (candidate_path / locator).is_symlink()), None)
    if existing_state is not None:
        locator, state, state_error = installed_state(candidate_path)
        repo_payload = state.get("repo_payload") if isinstance(state, dict) else None
        adoption_mode = repo_payload.get("adoption_mode") if isinstance(repo_payload, dict) else None
        if state_error or adoption_mode not in ADOPTION_PROFILES:
            profile.update({"status": "unreadable", "adoption_mode": adoption_mode, "authority": locator})
            return None, profile, [state_error or "installed-state adoption_mode is unsupported"]
        if adoption_mode in LIGHT_PROFILES and repo_payload.get("mode") != "metadata-only":
            profile.update({"status": "unreadable", "adoption_mode": adoption_mode, "authority": locator})
            return None, profile, [f"{adoption_mode} installed-state must use metadata-only repository payload"]
        resolved = ADOPTION_PROFILES[adoption_mode]
        profile.update({"status": "valid", "profile": resolved, "adoption_mode": adoption_mode, "authority": locator})
        return resolved, profile, []
    if any(path in STATE_FILENAMES for path in paths):
        profile["status"] = "unreadable"
        return None, profile, ["candidate change set removed installed-state profile authority"]
    companion_locator = ".loom/companion/repo-interface.json"
    companion_path = candidate_path / companion_locator
    if companion_path.exists() or companion_path.is_symlink():
        if companion_path.is_symlink() or not companion_path.is_file():
            profile.update({"status": "unreadable", "authority": companion_locator})
            return None, profile, ["repo companion profile authority must be a regular file"]
        companion = read_json(companion_path)
        if companion is None or companion.get("schema_version") != "loom-repo-interface/v2":
            profile.update({"status": "unreadable", "authority": companion_locator})
            return None, profile, ["repo companion profile authority is unreadable"]
        adoption_mode = "execution-control"
        resolved = ADOPTION_PROFILES[adoption_mode]
        profile.update({"status": "valid", "profile": resolved, "adoption_mode": adoption_mode, "authority": companion_locator})
        return resolved, profile, []
    return None, profile, []


def _profile(facts: dict[str, Any], paths: list[str], candidate_profile: str | None) -> tuple[str, str]:
    requested = facts.get("profile")
    if isinstance(requested, str) and requested in PROFILES:
        return requested, "host_facts"
    if candidate_profile is not None:
        return candidate_profile, "candidate_state"
    if paths and all(path in LIGHT_PATHS or path.startswith(LIGHT_PATH_PREFIXES) for path in paths):
        return "light", "changed_paths"
    return "standard", "default"


def _automatic_validation_targets(paths: list[str], profile: str) -> list[str]:
    targets: set[str] = set()
    docs_only = bool(paths) and all(
        path in LIGHT_PATHS or path.startswith(LIGHT_PATH_PREFIXES) for path in paths
    )
    if docs_only:
        targets.add("skills-doc-reference-sync-check")
    if not docs_only or any(path.endswith(".py") for path in paths):
        targets.add("py-compile")
    for path in paths:
        matched = False
        if path in EXACT_NATIVE_SURFACES:
            targets.update(EXACT_NATIVE_SURFACES[path])
            matched = True
        script_targets = SCRIPT_NATIVE_SURFACES.get(Path(path).name)
        if script_targets and path.startswith(("src/skills/shared/scripts/", "skills/shared/scripts/", "plugins/loom/skills/shared/scripts/")):
            targets.update(script_targets)
            matched = True
        if path.startswith(("src/skills/", "skills/", "plugins/loom/skills/")):
            targets.add("skills-check")
            matched = True
        if path.startswith(("src/skills/shared/scripts/", "skills/shared/scripts/", "plugins/loom/skills/shared/scripts/")) and not script_targets:
            targets.add("cli-contract-check")
        if path.startswith("tools/fixtures/product-acceptance/"):
            targets.add("product-acceptance-adapter-check")
            matched = True
        elif path.startswith("tools/fixtures/light-profile/"):
            targets.add("light-profile-check")
            matched = True
        elif path.startswith("tools/fixtures/delivery-gate/"):
            targets.add("delivery-gate-check")
            matched = True
        if path.startswith("test/"):
            targets.add("check")
            matched = True
        if path.startswith(".github/actions/"):
            targets.add("composite-action-contract-check")
            matched = True
        if path in {"VERSION", "package.json", "package-lock.json"} or path.startswith("bin/"):
            targets.update(("release-surface-check", "npm-package-check"))
            matched = True
        if path.startswith("examples/"):
            targets.add("loom-demo-new-project-check")
            matched = True
        if path.endswith(".md"):
            targets.add("skills-doc-reference-sync-check")
            matched = True
        if path.startswith((".agents/", "plugins/")):
            targets.add("skills-check")
            matched = True
        if path.startswith(".loom/"):
            targets.add("cli-contract-check")
            matched = True
        if not matched and path.startswith(".github/workflows/"):
            targets.add("workflow-contract-check")
        elif not matched and path.startswith("tools/"):
            targets.add("cli-contract-check")
        elif not matched and path.startswith(("src/skills/", "skills/", "plugins/loom/skills/")):
            targets.update(("skills-check", "cli-contract-check"))
        elif path == "Makefile":
            targets.update(("delivery-gate-check", "workflow-contract-check"))
    if profile == "reinforced":
        targets.update(("py-compile", "skills-check", "cli-contract-check"))
    if not targets:
        targets.add("py-compile")
    return [target for target in ALLOWED_MAKE_TARGETS if target in targets]


def _validation_command(
    facts: dict[str, Any], paths: list[str], profile: str
) -> tuple[str, list[str], list[str], str]:
    if "validation_command" in facts:
        targets, errors = parse_make_targets(facts.get("validation_command"))
        return (f"make -- {' '.join(targets)}" if targets else ""), targets, errors, "host_facts"
    targets = _automatic_validation_targets(paths, profile)
    return f"make -- {' '.join(targets)}", targets, [], "changed_paths_profile"


def _enforcement(value: object) -> tuple[str, list[str]]:
    if value in ENFORCEMENTS:
        return str(value), []
    return "invalid", ["enforcement must be advisory or enforce"]


def _cause(cause_id: str) -> dict[str, Any]:
    return primary_cause(cause_id=cause_id, **CAUSES[cause_id])


def _identity_cause(cause_id: str) -> dict[str, Any]:
    return primary_cause(cause_id=cause_id, **IDENTITY_CAUSES[cause_id])


def _result(enforcement: str, cause_id: str) -> str:
    if enforcement == "advisory":
        return "advisory"
    return "passed" if enforcement == "enforce" and cause_id == "passed" else "blocked"


def _light_invariant(
    candidate_profile: str | None,
    profile: str,
    profile_source: str,
    candidate_path: Path | None,
) -> tuple[dict[str, Any], str]:
    if candidate_profile != "light" and not (candidate_profile is None and profile == "light" and profile_source == "host_facts"):
        return {"status": "not_evaluated", "applicable": False, "source": "delivery_profile"}, "passed"
    if candidate_path is None:
        return {"status": "blocked", "applicable": True, "source": "candidate_tree", "violations": []}, "light_profile_tree_unreadable"
    try:
        evaluated = evaluate_light_profile(candidate_path)
    except (OSError, ValueError):
        return {"status": "blocked", "applicable": True, "source": "candidate_tree", "violations": []}, "light_profile_tree_unreadable"
    cause_id = evaluated.get("primary_cause", {}).get("id")
    if evaluated.get("result") == "pass" and evaluated.get("applicable") is False:
        return {"status": "blocked", "applicable": False, "source": "candidate_tree", "violations": []}, "profile_state_mismatch"
    if evaluated.get("result") == "pass":
        return {"status": "passed", "applicable": bool(evaluated.get("applicable")), "source": "candidate_tree", "violations": []}, "passed"
    if cause_id not in {"light_profile_forbidden_carrier", "light_profile_state_unreadable", "light_profile_tree_unreadable"}:
        cause_id = "light_profile_tree_unreadable"
    violations = evaluated.get("violations")
    return {
        "status": "blocked",
        "applicable": True,
        "source": "candidate_tree",
        "violations": violations if isinstance(violations, list) else [],
    }, cause_id


def evaluate_host_facts(
    host_facts: object,
    enforcement: object = "advisory",
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate host facts before the selected native validation runs."""

    host_errors: list[str] = []
    facts = host_facts if isinstance(host_facts, dict) else {}
    if not isinstance(host_facts, dict):
        host_errors.append("host facts must be a JSON object")
    if facts.get("schema_version") != HOST_FACTS_SCHEMA:
        host_errors.append(f"schema_version must be `{HOST_FACTS_SCHEMA}`")
    if any(isinstance(facts.get(key), str) and facts[key] for key in ("host_read_error", "read_error")):
        host_errors.append("host facts could not be read from GitHub")
    typed_host_errors = {
        "permission_error": "permission_denied",
        "git_history_error": "git_history_unreadable",
        "environment_error": "environment_unavailable",
    }
    typed_host_cause = next(
        (cause_id for field, cause_id in typed_host_errors.items() if isinstance(facts.get(field), str) and facts[field]),
        None,
    )
    event = facts.get("event")
    if event not in SUPPORTED_EVENTS:
        host_errors.append("event must be pull_request_target or merge_group")
    repository = facts.get("repository")
    if not isinstance(repository, dict) or not all(isinstance(repository.get(key), str) and repository[key] for key in ("owner", "name")):
        host_errors.append("repository.owner and repository.name are required")
        repository = {}
    paths, path_errors = _paths(facts.get("changed_paths"))
    candidate_profile, candidate_profile_evidence, candidate_profile_errors = _candidate_profile(candidate_path, paths)
    profile_errors = ["profile must be light, standard, or reinforced when supplied"] if "profile" in facts and facts.get("profile") not in PROFILES else []
    requested_profile = facts.get("profile")
    if isinstance(requested_profile, str) and requested_profile in PROFILES and candidate_profile in PROFILES and PROFILE_ORDER[requested_profile] < PROFILE_ORDER[candidate_profile]:
        profile_errors.append("requested profile cannot downgrade candidate repository state")
    profile, profile_source = _profile(facts, paths, candidate_profile)
    validation_command, validation_targets, validation_command_errors, validation_source = _validation_command(
        facts, paths, profile
    )
    enforcement_mode, enforcement_errors = _enforcement(enforcement)
    light_invariant = {"status": "not_evaluated", "applicable": False, "source": "delivery_profile"}
    if typed_host_cause is not None:
        cause_id = typed_host_cause
    elif host_errors:
        cause_id = "host_facts_unreadable"
    elif enforcement_errors:
        cause_id = "enforcement_unsupported"
    elif profile_errors:
        cause_id = "profile_state_mismatch" if "requested profile cannot downgrade candidate repository state" in profile_errors else "profile_unsupported"
    elif path_errors:
        cause_id = "invalid_change_set"
    elif candidate_profile_errors:
        cause_id = "candidate_profile_unreadable"
    elif validation_command_errors:
        cause_id = "validation_command_missing"
    else:
        light_invariant, cause_id = _light_invariant(candidate_profile, profile, profile_source, candidate_path)

    primary = _cause(cause_id)
    typed_host_detail = next(
        (facts[field] for field in typed_host_errors if isinstance(facts.get(field), str) and facts[field]),
        None,
    )
    primary["details"] = {
        key: value
        for key, value in {
            "host_error": typed_host_detail,
            "host_errors": list(dict.fromkeys(host_errors)),
            "profile_errors": profile_errors,
            "change_set_errors": path_errors,
            "candidate_profile_errors": candidate_profile_errors,
            "validation_command_errors": validation_command_errors,
            "enforcement_errors": enforcement_errors,
        }.items()
        if value
    }
    return {
        "schema_version": SCHEMA,
        "result": _result(enforcement_mode, cause_id),
        "enforcement": enforcement_mode,
        "summary": "Delivery facts were evaluated without inferring product acceptance.",
        "primary_cause": primary,
        "failure_envelope": envelope(primary),
        "product_acceptance": {"verdict": "not_evaluated"},
        "host_facts": {
            "status": "valid" if not host_errors else "unreadable",
            "event": event if isinstance(event, str) else "unknown",
            "repository": repository,
            "input_errors": list(dict.fromkeys(host_errors)),
        },
        "delivery": {
            "profile": profile,
            "profile_source": profile_source,
            "changed_paths": paths,
            "profile_errors": profile_errors,
            "change_set_errors": path_errors,
            "candidate_profile": candidate_profile_evidence,
            "candidate_profile_errors": candidate_profile_errors,
        },
        "native_validation": {
            "command": validation_command,
            "targets": validation_targets,
            "selection_source": validation_source,
            "command_errors": validation_command_errors,
            "status": "pending",
            "security_boundary": "untrusted_execution_read_token_only",
        },
        "light_invariant": light_invariant,
        "enforcement_errors": enforcement_errors,
    }


def finalize_delivery_gate(
    host_facts: object,
    validation_result: object,
    enforcement: object = "advisory",
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    """Apply the fixed delivery-cause priority after native validation."""

    payload = evaluate_host_facts(host_facts, enforcement, candidate_path)
    result = validation_result if isinstance(validation_result, dict) else {}
    status = result.get("status")
    payload["native_validation"]["status"] = status if isinstance(status, str) else "command_missing"
    if payload["primary_cause"]["id"] == "passed":
        if status == "command_missing":
            cause_id = "validation_command_missing"
        elif status == "failed":
            cause_id = "native_validation_failed"
        elif status == "passed":
            cause_id = "passed"
        else:
            cause_id = "validation_command_missing"
        payload["primary_cause"] = _cause(cause_id)
    additional: list[dict[str, Any]] = []
    if payload["primary_cause"]["id"] != "passed" and status in {"command_missing", "failed"}:
        additional.append(_cause("validation_command_missing" if status == "command_missing" else "native_validation_failed"))
    payload["failure_envelope"] = envelope(payload["primary_cause"], suppressed_diagnostics=additional)
    payload["result"] = _result(payload["enforcement"], payload["primary_cause"]["id"])
    return payload


def build_required_check_identity(
    repository: dict[str, str],
    branch: str,
    expected_context: str,
    expected_app_id: int,
    legacy_contexts: object,
    retained_contexts: object,
    branch_protection: object,
    branch_rules: object,
    observed_at: str,
    branch_protection_read_error: str | None = None,
    branch_rules_read_error: str | None = None,
    trust_mode: str = "pull_request_target_same_app",
    expected_workflow_path: str = ".github/workflows/loom-delivery-gate.yml",
    workflow_readback: object = None,
    workflow_read_error: str | None = None,
    github_actions_app_id: int = 15368,
) -> dict[str, Any]:
    """Normalize effective required checks from GitHub branch protection and applicable rulesets."""

    errors: list[str] = []
    branch_protection_checks: list[dict[str, Any]] = []
    if branch_protection == {}:
        pass
    elif not isinstance(branch_protection, dict):
        errors.append("branch protection readback must be an object when present")
    else:
        status_checks = branch_protection.get("required_status_checks")
        checks = status_checks.get("checks") if isinstance(status_checks, dict) else None
        if not isinstance(checks, list):
            errors.append("branch protection required_status_checks.checks must be a list")
        else:
            for check in checks:
                if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"]:
                    errors.append("branch protection required checks must contain non-empty contexts")
                    continue
                if not isinstance(check.get("app_id"), int) or check["app_id"] <= 0:
                    errors.append("branch protection required checks must contain positive app_id values")
                    continue
                branch_protection_checks.append({"context": check["context"], "app_id": check["app_id"], "plane": "branch_protection"})

    ruleset_checks: list[dict[str, Any]] = []
    required_workflows: list[dict[str, Any]] = []
    if not isinstance(branch_rules, list):
        errors.append("applicable branch rules readback must be a list")
    else:
        for rule in branch_rules:
            if isinstance(rule, dict) and rule.get("type") in {"workflows", "required_workflows"}:
                parameters = rule.get("parameters")
                workflows = parameters.get("workflows") if isinstance(parameters, dict) else None
                if not isinstance(workflows, list):
                    errors.append("applicable required-workflow rules must expose workflows as a list")
                else:
                    for workflow in workflows:
                        if isinstance(workflow, dict) and isinstance(workflow.get("path"), str):
                            required_workflows.append(
                                {
                                    "path": workflow["path"],
                                    "ref": workflow.get("ref"),
                                    "repository_id": workflow.get("repository_id"),
                                    "ruleset_id": rule.get("ruleset_id"),
                                }
                            )
                continue
            if not isinstance(rule, dict) or rule.get("type") != "required_status_checks":
                continue
            parameters = rule.get("parameters")
            checks = parameters.get("required_status_checks") if isinstance(parameters, dict) else None
            if not isinstance(checks, list):
                errors.append("applicable required-status-checks rules must expose required_status_checks as a list")
                continue
            for check in checks:
                if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"]:
                    errors.append("applicable ruleset required checks must contain non-empty contexts")
                    continue
                ruleset_checks.append(
                    {
                        "context": check["context"],
                        "app_id": None,
                        "plane": "ruleset",
                        "ruleset_id": rule.get("ruleset_id"),
                    }
                )
    return {
        "schema_version": REQUIRED_CHECK_IDENTITY_SCHEMA,
        "source": "github_branch_controls",
        "repository": repository,
        "branch": branch,
        "observed_at": observed_at,
        "required_check": {"context": expected_context, "app_id": expected_app_id},
        "trust_mode": trust_mode,
        "github_actions_app_id": github_actions_app_id,
        "expected_workflow_path": expected_workflow_path,
        "workflow_readback": workflow_readback,
        "required_workflows": required_workflows,
        "legacy_contexts": legacy_contexts,
        "retained_contexts": retained_contexts,
        "branch_protection_checks": branch_protection_checks,
        "ruleset_checks": ruleset_checks,
        "normalization_errors": errors,
        "host_read_errors": {
            "branch_protection": branch_protection_read_error,
            "applicable_rulesets": branch_rules_read_error,
            "workflow": workflow_read_error,
        },
    }


def evaluate_required_check_identity(evidence: object) -> dict[str, Any]:
    """Fail closed unless all GitHub branch-control planes require the expected check and no legacy check remains."""

    value = evidence if isinstance(evidence, dict) else {}
    errors: list[str] = []
    if value.get("schema_version") != REQUIRED_CHECK_IDENTITY_SCHEMA:
        errors.append(f"schema_version must be `{REQUIRED_CHECK_IDENTITY_SCHEMA}`")
    if value.get("source") != "github_branch_controls":
        errors.append("source must be github_branch_controls")
    repository = value.get("repository")
    if not isinstance(repository, dict) or not all(isinstance(repository.get(key), str) and repository[key] for key in ("owner", "name")):
        errors.append("repository.owner and repository.name are required")
        repository = {}
    if not isinstance(value.get("branch"), str) or not value["branch"]:
        errors.append("branch is required")
    if not isinstance(value.get("observed_at"), str) or not value["observed_at"]:
        errors.append("observed_at is required")
    required_check = value.get("required_check")
    if (
        not isinstance(required_check, dict)
        or not isinstance(required_check.get("context"), str)
        or not required_check["context"].strip()
        or not isinstance(required_check.get("app_id"), int)
        or required_check["app_id"] <= 0
    ):
        errors.append("required_check must name a non-empty context and a positive expected app_id")
        required_check = {"context": None, "app_id": None}
    trust_mode = value.get("trust_mode")
    if trust_mode not in {"required_workflow", "distinct_app_check", "pull_request_target_same_app"}:
        errors.append("trust_mode must be required_workflow, distinct_app_check, or pull_request_target_same_app")
    github_actions_app_id = value.get("github_actions_app_id")
    if not isinstance(github_actions_app_id, int) or github_actions_app_id <= 0:
        errors.append("github_actions_app_id must be a positive integer")
        github_actions_app_id = 15368
    expected_workflow_path = value.get("expected_workflow_path")
    if not isinstance(expected_workflow_path, str) or not expected_workflow_path.startswith(".github/workflows/"):
        errors.append("expected_workflow_path must identify a repository workflow")
        expected_workflow_path = None
    workflow_readback = value.get("workflow_readback")
    if workflow_readback is not None and not isinstance(workflow_readback, dict):
        errors.append("workflow_readback must be an object when present")
        workflow_readback = None
    required_workflows = value.get("required_workflows")
    if not isinstance(required_workflows, list):
        errors.append("required_workflows must be a list")
        required_workflows = []
    legacy_contexts = value.get("legacy_contexts")
    retained_contexts = value.get("retained_contexts")
    if not isinstance(legacy_contexts, list) or any(not isinstance(context, str) or not context.strip() for context in legacy_contexts):
        errors.append("legacy_contexts must be a list of non-empty contexts")
        legacy_contexts = []
    if not isinstance(retained_contexts, list) or any(not isinstance(context, str) or not context.strip() for context in retained_contexts):
        errors.append("retained_contexts must be a list of non-empty contexts")
        retained_contexts = []
    if isinstance(required_check["context"], str) and required_check["context"] in legacy_contexts:
        errors.append("legacy_contexts must not contain the expected check context")
    if set(legacy_contexts) & set(retained_contexts):
        errors.append("legacy_contexts and retained_contexts must not overlap")
    branch_protection_checks = value.get("branch_protection_checks")
    ruleset_checks = value.get("ruleset_checks")
    if not isinstance(branch_protection_checks, list) or not isinstance(ruleset_checks, list):
        errors.append("branch_protection_checks and ruleset_checks must be lists")
        branch_protection_checks = []
        ruleset_checks = []
    checks = [*branch_protection_checks, *ruleset_checks]
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("context"), str) or not check["context"] or check.get("plane") not in {"branch_protection", "ruleset"}:
            errors.append("effective required checks must carry a non-empty context and known plane")
            break
    normalization_errors = value.get("normalization_errors")
    if not isinstance(normalization_errors, list) or any(not isinstance(error, str) for error in normalization_errors):
        errors.append("normalization_errors must be a list of strings")
    else:
        errors.extend(normalization_errors)
    host_read_errors = value.get("host_read_errors")
    if not isinstance(host_read_errors, dict) or any(
        key not in host_read_errors or host_read_errors[key] is not None and not isinstance(host_read_errors[key], str)
        for key in ("branch_protection", "applicable_rulesets", "workflow")
    ):
        errors.append("host_read_errors must describe branch protection and applicable rulesets")
        host_read_errors = {}

    expected_context = required_check["context"]
    branch_context_checks = [
        item
        for item in branch_protection_checks
        if isinstance(item, dict) and item.get("context") == expected_context
    ]
    matching_app_ids = [item.get("app_id") for item in checks if isinstance(item, dict) and item.get("context") == expected_context]
    matching_known_app_ids = [app_id for app_id in matching_app_ids if isinstance(app_id, int) and app_id > 0]
    matching_app_identity_unavailable = any(app_id is None for app_id in matching_app_ids)
    legacy_required_checks = [
        item
        for item in checks
        if isinstance(item, dict) and item.get("context") in legacy_contexts
    ]
    allowed_contexts = {expected_context, *retained_contexts}
    unexpected_required_checks = [
        item
        for item in checks
        if isinstance(item, dict) and item.get("context") not in allowed_contexts
    ]
    if errors:
        cause_id = "required_check_identity_unreadable"
    elif any(host_read_errors.values()):
        cause_id = "required_check_identity_unknown"
    elif legacy_required_checks:
        cause_id = "legacy_required_checks_present"
    elif unexpected_required_checks:
        cause_id = "unexpected_required_checks_present"
    elif trust_mode == "required_workflow":
        cause_id = "host_enforcement_unavailable"
    elif trust_mode == "distinct_app_check":
        if (
            len(branch_context_checks) == 1
            and branch_context_checks[0].get("app_id") == required_check["app_id"]
            and required_check["app_id"] != github_actions_app_id
        ):
            cause_id = "passed"
        elif matching_app_identity_unavailable and not branch_context_checks:
            cause_id = "required_check_identity_unknown"
        else:
            cause_id = "required_check_identity_invalid"
    elif (
        len(branch_context_checks) == 1
        and len(matching_app_ids) == 1
        and branch_context_checks[0].get("app_id") == required_check["app_id"] == github_actions_app_id
    ):
        cause_id = "passed_limited"
    elif not matching_app_ids:
        cause_id = "required_check_identity_unknown"
    elif matching_app_identity_unavailable:
        cause_id = "required_check_identity_unknown"
    else:
        cause_id = "required_check_identity_invalid"

    primary = _identity_cause(cause_id)
    return {
        "schema_version": REQUIRED_CHECK_IDENTITY_READINESS_SCHEMA,
        "result": "ready" if cause_id in {"passed", "passed_limited"} else "blocked",
        "primary_cause": primary,
        "failure_envelope": envelope(primary),
        "identity": {
            "source": value.get("source"),
            "repository": repository,
            "branch": value.get("branch"),
            "observed_at": value.get("observed_at"),
            "required_check": required_check,
            "observed_app_ids": matching_known_app_ids,
            "effective_required_checks": checks,
            "legacy_required_checks": legacy_required_checks,
            "retained_contexts": sorted(allowed_contexts),
            "unexpected_required_checks": unexpected_required_checks,
            "trust_mode": trust_mode,
            "trust_verdict": "strong" if cause_id == "passed" else ("limited" if cause_id == "passed_limited" else "blocked"),
            "expected_workflow_path": expected_workflow_path,
            "required_workflows": required_workflows,
            "workflow_readback": workflow_readback,
        },
        "input_errors": errors,
    }


def _read_host_facts(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"read_error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-facts-file", type=Path, required=True)
    parser.add_argument("--validation-result-file", type=Path)
    parser.add_argument("--candidate-path", type=Path)
    parser.add_argument("--enforcement", default="advisory")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    host_facts = _read_host_facts(args.host_facts_file)
    payload = (
        finalize_delivery_gate(host_facts, _read_host_facts(args.validation_result_file), args.enforcement, args.candidate_path)
        if args.validation_result_file
        else evaluate_host_facts(host_facts, args.enforcement, args.candidate_path)
    )
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
