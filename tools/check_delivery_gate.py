#!/usr/bin/env python3
"""Check delivery-gate evaluator, enforcement, and required-check identity contracts."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from build_distribution import build


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tools" / "fixtures" / "delivery-gate"
WORKFLOW = ROOT / ".github" / "workflows" / "loom-delivery-gate.yml"
CHECK_WORKFLOW = ROOT / ".github" / "workflows" / "loom-check.yml"
WORKFLOW_MATRIX = FIXTURES / "workflow-event-matrix.json"
REUSABLE_AUTHORITY_CASES = FIXTURES / "reusable-authority-cases.json"
HOST_AUTHORITY_FAILURE_CASES = FIXTURES / "host-authority-failure-cases.json"
WORKFLOW_SPOOF_CASES = FIXTURES / "workflow-spoof-cases.json"
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "delivery_gate.py"
SOURCE_DIR = SOURCE.parent
IDENTITY_READER = ROOT / "tools" / "read_delivery_gate_required_identity.py"
COMPOSITE_CHECKER = ROOT / "tools" / "check_composite_actions.py"
TRUSTED_RUNNER = ROOT / "tools" / "run_trusted_candidate_validation.py"
def load_evaluator() -> Any:
    if str(SOURCE_DIR) not in sys.path:
        sys.path.insert(0, str(SOURCE_DIR))
    spec = importlib.util.spec_from_file_location("delivery_gate", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("delivery evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_primary_cause(
    payload: dict[str, Any],
    expected: str,
    enforcement: str = "advisory",
    result: str = "advisory",
) -> None:
    cause = payload.get("primary_cause")
    expected_fields = {
        "id",
        "failure_domain",
        "code",
        "locator",
        "summary",
        "owner",
        "retryable",
        "cause_class",
        "transient",
        "details",
        "consequence_of",
        "remediation_command",
    }
    if not isinstance(cause, dict) or set(cause) != expected_fields or cause.get("id") != expected:
        raise AssertionError(f"expected primary cause {expected}, got {cause}")
    envelope = payload.get("failure_envelope")
    if (
        not isinstance(envelope, dict)
        or envelope.get("schema_version") != "loom-failure-envelope/v1"
        or envelope.get("primary_cause") != cause
        or not isinstance(envelope.get("consequences"), list)
        or not isinstance(envelope.get("suppressed_diagnostics"), list)
        or envelope.get("secondary_causes") != [*envelope["consequences"], *envelope["suppressed_diagnostics"]]
    ):
        raise AssertionError(f"delivery gate did not expose one actionable failure envelope: {envelope}")
    if payload.get("product_acceptance", {}).get("verdict") != "not_evaluated":
        raise AssertionError("delivery gate must not infer product acceptance")
    if payload.get("result") != result or payload.get("enforcement") != enforcement:
        raise AssertionError(
            f"delivery gate expected {enforcement}/{result}, got {payload.get('enforcement')}/{payload.get('result')}"
        )


def check_evaluator() -> None:
    evaluator = load_evaluator()
    examples = (
        ("docs.json", "light", "changed_paths", "valid", ["skills-doc-reference-sync-check"]),
        (
            "runtime.json",
            "standard",
            "host_facts",
            "valid",
            ["py-compile", "skills-check", "delivery-gate-check"],
        ),
    )
    for name, profile, source, host_status, targets in examples:
        payload = evaluator.evaluate_host_facts(json.loads((FIXTURES / name).read_text(encoding="utf-8")))
        assert_primary_cause(payload, "passed")
        if payload["delivery"]["profile"] != profile or payload["delivery"]["profile_source"] != source:
            raise AssertionError(f"{name} selected an unexpected profile")
        if payload["host_facts"]["status"] != host_status:
            raise AssertionError(f"{name} unexpectedly rejected valid host facts")
        native = payload["native_validation"]
        if native["targets"] != targets or native["command"] != f"make -- {' '.join(targets)}":
            raise AssertionError(f"{name} did not select its changed-path native validation: {native}")
        if native["selection_source"] != "changed_paths_profile" or native["command"] == "make delivery-gate-check":
            raise AssertionError(f"{name} must select candidate validation, not only evaluator self-tests")

    valid = json.loads((FIXTURES / "docs.json").read_text(encoding="utf-8"))
    reusable = evaluator.evaluate_host_facts({**valid, "profile": "reinforced", "validation_command": "py-compile skills-check"})
    assert_primary_cause(reusable, "passed")
    if (
        reusable["delivery"]["profile"] != "reinforced"
        or reusable["native_validation"]["command"] != "make -- py-compile skills-check"
        or reusable["native_validation"]["targets"] != ["py-compile", "skills-check"]
        or reusable["native_validation"]["selection_source"] != "host_facts"
    ):
        raise AssertionError("reusable callers must retain their declared profile and validation command")
    for unsafe in (
        "${{ github.sha }}",
        "py-compile ${{ github.sha }}",
        "py-compile\nskills-check",
        "py-compile;curl",
        "py-compile|curl",
        "py-compile && curl",
        "py-compile > result",
        "py-compile $(curl)",
        "curl",
    ):
        rejected = evaluator.evaluate_host_facts({**valid, "validation_command": unsafe})
        assert_primary_cause(rejected, "validation_command_missing")
        if rejected["native_validation"]["targets"] or not rejected["native_validation"]["command_errors"]:
            raise AssertionError(f"unsafe validation input was not rejected: {unsafe!r}")
    reinforced = evaluator.evaluate_host_facts({**valid, "profile": "reinforced"})
    if reinforced["native_validation"]["targets"] != [
        "py-compile",
        "skills-doc-reference-sync-check",
        "skills-check",
        "cli-contract-check",
    ]:
        raise AssertionError("reinforced profile must add its native contract surfaces")
    release = evaluator.evaluate_host_facts({**valid, "changed_paths": ["VERSION", "package.json"]})
    if release["native_validation"]["targets"] != ["py-compile", "release-surface-check", "npm-package-check"]:
        raise AssertionError("release paths must select release and package validation")
    light_profile = evaluator.evaluate_host_facts({**valid, "changed_paths": ["tools/check_light_profile.py"]})
    if light_profile["native_validation"]["targets"] != ["py-compile", "light-profile-check"]:
        raise AssertionError("light-profile paths must select their semantic contract check")
    priority_cases = (
        (
            {**valid, "host_read_error": "GitHub unavailable", "profile": "unsupported", "changed_paths": ["../carrier"], "validation_command": ""},
            {"status": "failed"},
            "host_facts_unreadable",
        ),
        ({**valid, "profile": "unsupported", "changed_paths": ["../carrier"], "validation_command": ""}, {"status": "failed"}, "profile_unsupported"),
        ({**valid, "changed_paths": ["../carrier"], "validation_command": ""}, {"status": "failed"}, "invalid_change_set"),
        ({**valid, "validation_command": ""}, {"status": "passed"}, "validation_command_missing"),
        (valid, {"status": "command_missing"}, "validation_command_missing"),
        (valid, {"status": "failed"}, "native_validation_failed"),
        (valid, {"status": "passed"}, "passed"),
    )
    for facts, validation, expected in priority_cases:
        assert_primary_cause(evaluator.finalize_delivery_gate(facts, validation), expected)
    combined = evaluator.finalize_delivery_gate(priority_cases[0][0], {"status": "failed"})
    if combined["native_validation"]["status"] != "failed":
        raise AssertionError("higher-priority host failure must not erase the native validation result")
    suppressed = combined["failure_envelope"]["suppressed_diagnostics"]
    if len(suppressed) != 1 or suppressed[0].get("id") != "native_validation_failed" or suppressed[0].get("consequence_of") != []:
        raise AssertionError("independent validation failures must be suppressed diagnostics, not invented consequences")
    if combined["failure_envelope"]["consequences"] != [] or combined["failure_envelope"]["secondary_causes"] != suppressed:
        raise AssertionError("v1 secondary_causes must remain a deprecated compatibility alias")

    domain_cases = (
        ("permission_error", "permission_denied", "permission"),
        ("git_history_error", "git_history_unreadable", "git_history"),
        ("environment_error", "environment_unavailable", "environment"),
    )
    for field, expected_id, expected_domain in domain_cases:
        classified = evaluator.evaluate_host_facts({**valid, field: "fixture failure"})
        assert_primary_cause(classified, expected_id)
        if classified["primary_cause"]["failure_domain"] != expected_domain:
            raise AssertionError(f"{field} did not classify as {expected_domain}")

    assert_primary_cause(
        evaluator.finalize_delivery_gate(valid, {"status": "failed"}, "enforce"),
        "native_validation_failed",
        "enforce",
        "blocked",
    )
    assert_primary_cause(evaluator.finalize_delivery_gate(valid, {"status": "passed"}, "enforce"), "passed", "enforce", "passed")
    assert_primary_cause(
        evaluator.finalize_delivery_gate(valid, {"status": "passed"}, "unsupported"),
        "enforcement_unsupported",
        "invalid",
        "blocked",
    )

    caller = json.loads((FIXTURES / "caller.json").read_text(encoding="utf-8"))
    caller_ref = caller.get("loom_ref")
    expected = caller.get("expected")
    if (
        not isinstance(caller_ref, str)
        or len(caller_ref) != 40
        or any(character not in "0123456789abcdef" for character in caller_ref)
        or not isinstance(expected, dict)
        or expected != {"reusable_mode": True, "loom_source_path": "loom", "candidate_path": "candidate"}
        or caller.get("host_facts", {}).get("event") != "pull_request_target"
    ):
        raise AssertionError("caller fixture must prove a pull_request_target caller selects pinned Loom and candidate paths")
    assert_primary_cause(evaluator.finalize_delivery_gate(caller["host_facts"], {"status": "passed"}, "enforce"), "passed", "enforce", "passed")


def check_native_surface_inventory() -> None:
    evaluator = load_evaluator()
    workflows = {
        str(path.relative_to(ROOT)) for path in (ROOT / ".github" / "workflows").glob("*.yml")
    }
    checker_tools = {
        str(path.relative_to(ROOT)) for path in (ROOT / "tools").glob("check_*.py")
    }
    mapped = set(evaluator.EXACT_NATIVE_SURFACES)
    missing_inventory = sorted((workflows | checker_tools) - mapped)
    if missing_inventory:
        raise AssertionError("native contract inventory is missing: " + ", ".join(missing_inventory))

    make_targets = {
        line.split(":", 1)[0]
        for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith(("\t", ".")) and ":" in line
    }
    declared_targets = {
        target for targets in evaluator.EXACT_NATIVE_SURFACES.values() for target in targets
    }
    missing_make_targets = sorted(declared_targets - make_targets)
    if missing_make_targets:
        raise AssertionError("native contract inventory references missing Make targets: " + ", ".join(missing_make_targets))

    required_surfaces = {
        "product-acceptance-adapter-check",
        "fr-phase-close-guard-check",
        "host-attestation-check",
        "light-profile-check",
        "authority-contract-check",
        "fr-wi-admission-check",
        "pr-metadata-check",
        "failure-envelope-check",
        "npm-package-check",
        "release-surface-check",
        "workflow-contract-check",
        "composite-action-contract-check",
    }
    available = set(evaluator.ALLOWED_MAKE_TARGETS)
    if not required_surfaces <= available:
        raise AssertionError("native target allowlist is incomplete: " + ", ".join(sorted(required_surfaces - available)))

    for path in sorted(workflows | checker_tools):
        selected = set(evaluator._automatic_validation_targets([path], "standard"))
        expected = set(evaluator.EXACT_NATIVE_SURFACES[path])
        if not expected <= selected or selected <= {"py-compile"}:
            raise AssertionError(f"{path} lacks semantic native validation: {selected} expected {expected}")
    fail_safe = {
        ".github/workflows/future-control.yml": "workflow-contract-check",
        ".github/actions/native/action.yml": "composite-action-contract-check",
        "tools/check_future_control.py": "cli-contract-check",
        "src/skills/shared/scripts/future_control.py": "cli-contract-check",
        "test/product_acceptance_test.py": "check",
    }
    for path, expected in fail_safe.items():
        selected = evaluator._automatic_validation_targets([path], "standard")
        if expected not in selected:
            raise AssertionError(f"unknown control-plane path {path} did not fail safe: {selected}")


def materialize_candidate(
    root: Path,
    adoption_mode: str | None,
    forbidden: bool,
    *,
    companion: bool = False,
    host_truth_locators: object = None,
) -> Path:
    authority = "companion" if companion else "installed-state"
    candidate = root / f"{authority}-{adoption_mode or 'legacy'}-{'forbidden' if forbidden else 'clean'}"
    candidate.mkdir()
    subprocess.run(["git", "init"], cwd=candidate, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=candidate, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=candidate, check=True)
    if companion:
        state = candidate / ".loom" / "companion" / "repo-interface.json"
        payload = {"schema_version": "loom-repo-interface/v2"}
        if host_truth_locators is not None:
            payload["host_truth_locators"] = host_truth_locators
    else:
        if adoption_mode is None:
            raise AssertionError("installed-state fixture requires adoption_mode")
        state = candidate / ".loom" / "installed-state.json"
        payload = {
            "schema_version": "loom-installed-state/v2",
            "repo_payload": {"mode": "metadata-only", "adoption_mode": adoption_mode},
        }
    state.parent.mkdir(parents=True)
    state.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    if forbidden:
        carrier = candidate / ".loom" / "status" / "current.md"
        carrier.parent.mkdir(parents=True)
        carrier.write_text("forbidden\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=candidate, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=candidate, check=True, capture_output=True)
    return candidate


def check_light_profile_host_integration() -> None:
    evaluator = load_evaluator()
    facts = {**json.loads((FIXTURES / "docs.json").read_text(encoding="utf-8")), "profile": "light"}
    missing_candidate = evaluator.finalize_delivery_gate(facts, {"status": "passed"}, "enforce")
    assert_primary_cause(missing_candidate, "light_profile_tree_unreadable", "enforce", "blocked")
    with tempfile.TemporaryDirectory(prefix="loom-delivery-light-") as raw_tmp:
        root = Path(raw_tmp)
        direct_facts = json.loads((FIXTURES / "direct-light.json").read_text(encoding="utf-8"))
        if "profile" in direct_facts or direct_facts.get("event") != "pull_request_target":
            raise AssertionError("direct-event fixture must not inject a caller profile")
        forbidden = materialize_candidate(root, "light-governance", True)
        clean = materialize_candidate(root, "light-governance", False)
        blocked = evaluator.finalize_delivery_gate(direct_facts, {"status": "passed"}, "enforce", forbidden)
        assert_primary_cause(blocked, "light_profile_forbidden_carrier", "enforce", "blocked")
        if blocked["primary_cause"]["failure_domain"] != "carrier":
            raise AssertionError("forbidden light carriers must classify in the carrier failure domain")
        delivery = blocked.get("delivery", {})
        if blocked.get("light_invariant", {}).get("status") != "blocked" or delivery.get("profile") != "light" or delivery.get("profile_source") != "candidate_state":
            raise AssertionError("direct light event must derive profile authority and consume the candidate tree")
        if delivery.get("candidate_profile", {}).get("authority") != ".loom/installed-state.json":
            raise AssertionError("light adoption must come from explicit installed-state authority")
        passed = evaluator.finalize_delivery_gate(direct_facts, {"status": "passed"}, "enforce", clean)
        assert_primary_cause(passed, "passed", "enforce", "passed")
        for profile in ("standard", "reinforced"):
            elevated = evaluator.finalize_delivery_gate({**direct_facts, "profile": profile}, {"status": "passed"}, "enforce", forbidden)
            assert_primary_cause(elevated, "light_profile_forbidden_carrier", "enforce", "blocked")

        mismatch_facts = json.loads((FIXTURES / "profile-mismatch.json").read_text(encoding="utf-8"))
        for adoption_mode in ("execution-control", "strong-governance"):
            candidate = materialize_candidate(root, adoption_mode, True)
            mismatch = evaluator.finalize_delivery_gate(mismatch_facts, {"status": "passed"}, "enforce", candidate)
            assert_primary_cause(mismatch, "profile_state_mismatch", "enforce", "blocked")

        for fixture_id, host_truth in ((None, ["issue:1"]), ("execution-control", {"work_item": "github:issue"})):
            execution_companion = materialize_candidate(root, fixture_id, True, companion=True, host_truth_locators=host_truth)
            execution_result = evaluator.finalize_delivery_gate(direct_facts, {"status": "passed"}, "enforce", execution_companion)
            assert_primary_cause(execution_result, "passed", "enforce", "passed")
            if execution_result.get("light_invariant", {}).get("status") != "not_evaluated" or execution_result.get("delivery", {}).get("candidate_profile", {}).get("adoption_mode") != "execution-control":
                raise AssertionError("execution-control host truth locators must not imply light adoption")

        deleted_state = materialize_candidate(root, "attach-only", False)
        (deleted_state / ".loom" / "installed-state.json").unlink()
        deleted_facts = {**direct_facts, "changed_paths": [".loom/installed-state.json"]}
        deleted = evaluator.finalize_delivery_gate(deleted_facts, {"status": "passed"}, "enforce", deleted_state)
        assert_primary_cause(deleted, "candidate_profile_unreadable", "enforce", "blocked")

        host_facts = root / "host-facts.json"
        validation = root / "validation.json"
        host_facts.write_text(json.dumps(direct_facts) + "\n", encoding="utf-8")
        validation.write_text('{"status":"passed"}\n', encoding="utf-8")
        malicious = forbidden / "src" / "skills" / "shared" / "scripts" / "delivery_gate.py"
        malicious.parent.mkdir(parents=True)
        malicious.write_text(
            "import json\nprint(json.dumps({'result': 'passed', 'primary_cause': {'id': 'passed'}}))\n",
            encoding="utf-8",
        )
        attacker = subprocess.run([sys.executable, str(malicious)], check=False, text=True, capture_output=True)
        if json.loads(attacker.stdout).get("result") != "passed":
            raise AssertionError("malicious candidate evaluator fixture must attempt to self-pass")
        completed = subprocess.run(
            [
                sys.executable,
                str(SOURCE),
                "--host-facts-file",
                str(host_facts),
                "--validation-result-file",
                str(validation),
                "--candidate-path",
                str(forbidden),
                "--enforcement",
                "enforce",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        payload = json.loads(completed.stdout)
        if completed.returncode != 0 or payload.get("result") != "blocked" or payload.get("primary_cause", {}).get("id") != "light_profile_forbidden_carrier":
            raise AssertionError(f"trusted evaluator consumed the malicious candidate evaluator: {payload}")


def check_generated_copies() -> None:
    source = SOURCE.read_bytes()
    with tempfile.TemporaryDirectory(prefix="loom-delivery-gate-distribution-") as tmp:
        output = Path(tmp) / "distribution"
        build(output)
        copies = (
            output / "skills" / "shared" / "scripts" / "delivery_gate.py",
            output / "plugins" / "loom" / "skills" / "shared" / "scripts" / "delivery_gate.py",
        )
        if any(path.read_bytes() != source for path in copies):
            raise AssertionError("delivery-gate generated artifact drift")


def check_required_check_identity() -> None:
    evaluator = load_evaluator()
    repository = {"owner": "WebEnvoy", "name": "Lode"}
    observed_at = "2026-07-10T00:00:00Z"
    context = "loom-delivery-gate / loom-delivery-gate"
    no_rulesets: list[object] = []
    valid = evaluator.build_required_check_identity(
        repository,
        "main",
        context,
        15368,
        [],
        [],
        json.loads((FIXTURES / "required-check-identity-valid.json").read_text(encoding="utf-8")),
        no_rulesets,
        observed_at,
    )
    ready = evaluator.evaluate_required_check_identity(valid)
    if ready["result"] != "blocked" or ready["primary_cause"]["id"] != "host_enforcement_unavailable":
        raise AssertionError("same-app required context must remain limited because a candidate can spoof its name")

    distinct_protection = json.loads((FIXTURES / "required-check-identity-valid.json").read_text(encoding="utf-8"))
    distinct_protection["required_status_checks"]["checks"][0]["app_id"] = 424242
    distinct = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            424242,
            [],
            [],
            distinct_protection,
            no_rulesets,
            observed_at,
            trust_mode="distinct_app_check",
        )
    )
    if distinct["result"] != "ready" or distinct["identity"]["trust_verdict"] != "strong":
        raise AssertionError("a required check bound to a distinct GitHub App must be strong")

    for name, app_ids in (("conflicting", [424242, 999]), ("duplicate", [424242, 424242])):
        ambiguous_protection = json.loads(json.dumps(distinct_protection))
        ambiguous_protection["required_status_checks"]["checks"] = [
            {"context": context, "app_id": app_id} for app_id in app_ids
        ]
        ambiguous = evaluator.evaluate_required_check_identity(
            evaluator.build_required_check_identity(
                repository,
                "main",
                context,
                424242,
                [],
                [],
                ambiguous_protection,
                no_rulesets,
                observed_at,
                trust_mode="distinct_app_check",
            )
        )
        if ambiguous["result"] != "blocked" or ambiguous["primary_cause"]["id"] != "required_check_identity_invalid":
            raise AssertionError(f"{name} distinct-app bindings must fail closed: {ambiguous}")

    required_workflow = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            [],
            {},
            [
                {
                    "type": "workflows",
                    "ruleset_id": 99,
                    "parameters": {"workflows": [{"path": ".github/workflows/loom-delivery-gate.yml", "ref": "refs/heads/main", "repository_id": 1211191257}]},
                }
            ],
            observed_at,
            trust_mode="required_workflow",
            workflow_readback={"id": 123, "path": ".github/workflows/loom-delivery-gate.yml", "state": "active", "enforcement_verified": True},
        )
    )
    if required_workflow["result"] != "blocked" or required_workflow["primary_cause"]["id"] != "host_enforcement_unavailable":
        raise AssertionError("required workflow proof remains limited until #2063 binds the full host identity")

    unknown = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            [],
            json.loads((FIXTURES / "required-check-identity-unknown.json").read_text(encoding="utf-8")),
            no_rulesets,
            observed_at,
        )
    )
    if unknown["result"] != "blocked" or unknown["primary_cause"]["id"] != "required_check_identity_unknown":
        raise AssertionError("missing required-check identity must block readiness")

    invalid = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            [],
            json.loads((FIXTURES / "required-check-identity-invalid.json").read_text(encoding="utf-8")),
            no_rulesets,
            observed_at,
        )
    )
    if invalid["result"] != "blocked" or invalid["primary_cause"]["id"] != "required_check_identity_invalid":
        raise AssertionError("wrong required-check app identity must block readiness")

    unreadable = evaluator.evaluate_required_check_identity({"schema_version": "wrong"})
    if unreadable["result"] != "blocked" or unreadable["primary_cause"]["id"] != "required_check_identity_unreadable":
        raise AssertionError("malformed identity evidence must block readiness")

    blank_context = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(repository, "main", "", 15368, [], [], {}, no_rulesets, observed_at)
    )
    if blank_context["result"] != "blocked" or blank_context["primary_cause"]["id"] != "required_check_identity_unreadable":
        raise AssertionError("empty expected check context must block readiness")

    expected_ruleset = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            424242,
            [],
            [],
            {},
            json.loads((FIXTURES / "required-check-identity-ruleset-expected.json").read_text(encoding="utf-8")),
            observed_at,
            trust_mode="distinct_app_check",
        )
    )
    if expected_ruleset["result"] != "blocked" or expected_ruleset["primary_cause"]["id"] != "required_check_identity_unknown":
        raise AssertionError("ruleset-only context without app identity must block readiness")

    legacy = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            ["loom-pr-merge-gate"],
            [],
            json.loads((FIXTURES / "required-check-identity-valid.json").read_text(encoding="utf-8")),
            json.loads((FIXTURES / "required-check-identity-ruleset-legacy.json").read_text(encoding="utf-8")),
            observed_at,
        )
    )
    if legacy["result"] != "blocked" or legacy["primary_cause"]["id"] != "legacy_required_checks_present":
        raise AssertionError("legacy required check in an applicable ruleset must block readiness")

    branch_legacy = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            ["loom-pr-merge-gate"],
            [],
            json.loads((FIXTURES / "required-check-identity-branch-legacy.json").read_text(encoding="utf-8")),
            no_rulesets,
            observed_at,
        )
    )
    if branch_legacy["result"] != "blocked" or branch_legacy["primary_cause"]["id"] != "legacy_required_checks_present":
        raise AssertionError("legacy required check in branch protection must block readiness")

    retained = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            ["py-compile"],
            json.loads((FIXTURES / "required-check-identity-branch-retained.json").read_text(encoding="utf-8")),
            no_rulesets,
            observed_at,
        )
    )
    if retained["result"] != "blocked" or retained["primary_cause"]["id"] != "host_enforcement_unavailable":
        raise AssertionError("retained checks do not upgrade a spoofable same-app delivery context")

    unexpected_branch = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            [],
            json.loads((FIXTURES / "required-check-identity-branch-legacy.json").read_text(encoding="utf-8")),
            no_rulesets,
            observed_at,
        )
    )
    if unexpected_branch["result"] != "blocked" or unexpected_branch["primary_cause"]["id"] != "unexpected_required_checks_present":
        raise AssertionError("undeclared branch-protection checks must block readiness")

    unexpected_ruleset = evaluator.evaluate_required_check_identity(
        evaluator.build_required_check_identity(
            repository,
            "main",
            context,
            15368,
            [],
            [],
            json.loads((FIXTURES / "required-check-identity-valid.json").read_text(encoding="utf-8")),
            json.loads((FIXTURES / "required-check-identity-ruleset-legacy.json").read_text(encoding="utf-8")),
            observed_at,
        )
    )
    if unexpected_ruleset["result"] != "blocked" or unexpected_ruleset["primary_cause"]["id"] != "unexpected_required_checks_present":
        raise AssertionError("undeclared ruleset checks must block readiness")


def check_identity_reader_boundary() -> None:
    text = IDENTITY_READER.read_text(encoding="utf-8")
    required = (
        'subprocess.run(["gh", "api", endpoint]',
        "capture_output=True",
        "check=False",
        "branches/{quote(branch, safe='')}/protection",
        "rules/branches/{quote(branch, safe='')}",
        "actions/workflows?per_page=100",
        "--repository",
        "--branch",
        "--context",
        "--app-id",
        "--trust-mode",
        "--workflow-path",
        "--legacy-context",
        "--retained-context",
        "REPOSITORY_PART",
        "sys.dont_write_bytecode = True",
        "return 0 if payload[\"result\"] == \"ready\" else 1",
    )
    forbidden = ("shell=True", "GITHUB_TOKEN", "GH_TOKEN", "--method POST", "--method PATCH", "--method PUT", "--method DELETE")
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    if missing or present:
        details = [*(f"missing `{item}`" for item in missing), *(f"forbidden `{item}`" for item in present)]
        raise AssertionError("required-check identity reader boundary failed: " + "; ".join(details))


def check_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    host_facts_block = text.split("      host_facts:\n", 1)[1].split("      profile:\n", 1)[0] if "      host_facts:\n" in text else ""
    profile_block = text.split("      profile:\n", 1)[1].split("      validation_command:\n", 1)[0] if "      profile:\n" in text else ""
    validation_command_block = text.split("      validation_command:\n", 1)[1].split("      loom_ref:\n", 1)[0] if "      validation_command:\n" in text else ""
    loom_ref_block = text.split("      loom_ref:\n", 1)[1].split("    outputs:", 1)[0] if "      loom_ref:\n" in text else ""
    enforcement_block = text.split("      enforcement:\n", 1)[1].split("    outputs:", 1)[0] if "      enforcement:\n" in text else ""
    required = (
        "name: loom-delivery-gate",
        "pull_request_target:",
        "merge_group:",
        "workflow_call:",
        "profile:",
        "validation_command:",
        "loom_ref:",
        "enforcement:",
        'description: "Required delivery-gate mode: advisory records the result; enforce fails a non-passing terminal check."',
        "required: true",
        "^[0-9a-f]{40}$",
        "loom-delivery-gate:",
        "name: loom-delivery-gate",
        "contents: read",
        "pull-requests: read",
        "persist-credentials: false",
        "actions/github-script@v7",
        "repo: context.repo.repo",
        "pull_number: context.payload.number",
        "repository: MC-and-his-Agents/Loom",
        "ref: ${{ inputs.loom_ref }}",
        "github.rest.pulls.get",
        "pull.head?.repo?.full_name",
        'core.setOutput("base_repository"',
        'core.setOutput("head_repository"',
        "repository: ${{ steps.host-facts.outputs.base_repository }}",
        "repository: ${{ steps.host-facts.outputs.head_repository }}",
        "repository: ${{ needs.plan.outputs.base_repository }}",
        "repository: ${{ needs.plan.outputs.head_repository }}",
        "ref: ${{ steps.host-facts.outputs.base_sha }}",
        "ref: ${{ steps.host-facts.outputs.head_sha }}",
        "ref: ${{ needs.plan.outputs.base_sha }}",
        "ref: ${{ needs.plan.outputs.head_sha }}",
        "path: loom",
        "path: candidate",
        "REUSABLE_MODE: ${{ inputs.loom_ref != '' }}",
        "WORKFLOW_CALL_ENFORCEMENT",
        "const reusable = process.env.REUSABLE_MODE === \"true\";",
        "LOOM_SOURCE_PATH: loom",
        "CANDIDATE_PATH: candidate",
        "DELIVERY_GATE_ENFORCEMENT: ${{ inputs.loom_ref != '' && inputs.enforcement || 'enforce' }}",
        "LOOM_SOURCE_PATH",
        "CANDIDATE_PATH",
        "$LOOM_SOURCE_PATH/src/skills/shared/scripts/delivery_gate.py",
        'python3 "$RUNNER_ROOT/tools/run_trusted_candidate_validation.py"',
        '["native_validation"]["targets"]',
        "host_facts_base64",
        "base_sha: ${{ steps.host-facts.outputs.base_sha }}",
        "head_sha: ${{ steps.host-facts.outputs.head_sha }}",
        "authority_ready: ${{ steps.host-facts.outputs.authority_ready }}",
        "needs: plan",
        "needs: [plan, native-validation]",
        "actions/upload-artifact@v4",
        "github.rest.actions.getWorkflowRun",
        "github.rest.actions.getWorkflow",
        'workflow.path !== ".github/workflows/loom-delivery-gate.yml"',
        '"source":"untrusted_raw_artifact_not_consumed"',
        "name: untrusted-loom-native-validation-${{ github.run_id }}",
        "files.length >= 3000",
        "comparisonFiles.length >= 300",
        "delivery_gate_sha256",
        "delivery gate result changed after trusted finalization",
        "--validation-result-file",
        "--candidate-path \"$CANDIDATE_PATH\"",
        "--enforcement \"$DELIVERY_GATE_ENFORCEMENT\"",
        "CHANGED_PATHS_PATH",
        "fs.writeFileSync(process.env.CHANGED_PATHS_PATH",
        "Product acceptance: not_evaluated.",
        "facts.permission_error = message",
        "facts.git_history_error = message",
        'id: "host_authority_unavailable"',
        'failure_domain: "host_service"',
        "failure_envelope:",
        'core.setOutput("assurance", "limited")',
        "host_enforcement=host_enforcement_unavailable",
        "core.setOutput(\"failure_envelope\", JSON.stringify(failureEnvelope))",
        "remediation=${failureEnvelope.primary_cause?.remediation_command || \"unavailable\"}",
        "Publish terminal delivery result",
        'const result = authenticated ? "limited" : "blocked"',
        'core.setOutput("compatibility_check_success", authenticated ? "true" : "false")',
        'core.setOutput("trust_verdict", authenticated ? "limited" : "blocked")',
        "core.setFailed(`loom-delivery-gate blocked: ${cause}`)",
        "continue-on-error: true",
        "group: loom-delivery-gate-${{ github.event.pull_request.number || github.event.merge_group.head_ref || github.run_id }}",
        "cancel-in-progress: true",
    )
    forbidden = (
        "contents: write",
        "pull-requests: write",
        "issues: write",
        "id-token:",
        "secrets: inherit",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "bash -o pipefail -c",
        "          VALIDATION_COMMAND:",
        "LOOM_DELIVERY_GATE_HOST_FACTS_FILE",
        "LOOM_DELIVERY_GATE_DECISION_FILE",
        "github.event_name",
        'event === "workflow_call"',
        'const cause = "product_acceptance:not_evaluated"',
        "loom_flow.py",
        "current.md",
        ".loom/",
        "Object.assign(facts, supplied)",
        "|| github.sha",
    )
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    present.extend(line.strip() for line in text.splitlines() if line.strip() in {"paths:", "paths-ignore:"})
    if text.count("name: loom-delivery-gate") != 2:
        raise AssertionError("workflow must expose one workflow name and one same-name terminal job")
    checkouts = text.split("uses: actions/checkout@v4")[1:]
    if not checkouts or any("persist-credentials: false" not in checkout for checkout in checkouts):
        raise AssertionError("every checkout must drop credentials before untrusted native validation")
    if len(checkouts) != 10:
        raise AssertionError("plan, isolated native validation, caller base harness, and finalizer need separate checkouts")
    checkout_steps = text.split("      - name: ")[1:]
    unguarded = [
        step.splitlines()[0]
        for step in checkout_steps
        if "uses: actions/checkout@v4" in step
        and "authority_ready == 'true'" not in step.split("uses: actions/checkout@v4", 1)[0]
    ]
    if unguarded:
        raise AssertionError("authority-unready checkout steps remain: " + ", ".join(unguarded))
    plan_job = text.split("  plan:\n", 1)[1].split("  native-validation:\n", 1)[0]
    native_job = text.split("  native-validation:\n", 1)[1].split("  loom-delivery-gate:\n", 1)[0]
    final_job = text.split("  loom-delivery-gate:\n", 1)[1]
    if "ref: ${{ steps.host-facts.outputs.base_sha }}" not in plan_job or "ref: ${{ steps.host-facts.outputs.head_sha }}" not in plan_job:
        raise AssertionError("planning checkouts must consume only GitHub host-readback SHAs")
    for name, block in (("native-validation", native_job), ("finalizer", final_job)):
        if "ref: ${{ needs.plan.outputs.base_sha }}" not in block or "ref: ${{ needs.plan.outputs.head_sha }}" not in block:
            raise AssertionError(f"{name} must consume the planned authoritative base/head SHAs")
    if (
        "needs: plan" not in native_job
        or "RUNNER_ROOT: ${{ github.workspace }}/loom" not in native_job
        or "path: harness" not in native_job
        or "ref: ${{ needs.plan.outputs.base_sha }}" not in native_job
        or "SYMLINK_POLICY: ${{ inputs.loom_ref != '' && 'protected' || 'reject' }}" not in native_job
    ):
        raise AssertionError("candidate validation must run in a dependent job through the trusted harness")
    if (
        "needs: [plan, native-validation]" not in final_job
        or '"status":"command_missing","source":"untrusted_raw_artifact_not_consumed"' not in final_job
        or "actions/download-artifact@v4" in final_job
        or "listWorkflowRunArtifacts" in final_job
        or "listJobsForWorkflowRun" in final_job
    ):
        raise AssertionError("trusted finalizer must bind but never consume the untrusted native artifact verdict")
    for step_name in ("Evaluate delivery facts", "Finalize advisory delivery result"):
        block = text.split(f"      - name: {step_name}\n", 1)[1].split("      - name: ", 1)[0]
        if "authority_ready == 'true'" not in block:
            raise AssertionError(f"{step_name} must not execute without complete host authority")
    exposed = [name for name in ("HOST_FACTS_PATH", "LOOM_SOURCE_PATH", "DELIVERY_GATE_PLAN_PATH") if name in native_job]
    if exposed:
        raise AssertionError("candidate validation received trusted evaluator paths: " + ", ".join(exposed))
    for name, block in (("host_facts", host_facts_block), ("profile", profile_block)):
        if "required: true" not in block or "default:" in block:
            raise AssertionError(f"reusable callers must supply non-default {name}")
    if "required: true" not in loom_ref_block or "default:" in loom_ref_block:
        raise AssertionError("reusable callers must supply one non-default pinned Loom SHA")
    if "required: true" not in validation_command_block or "default:" in validation_command_block:
        raise AssertionError("reusable callers must supply their repository-native validation command")
    if "required: true" not in enforcement_block or "default:" in enforcement_block:
        raise AssertionError("reusable callers must explicitly choose advisory or enforce")
    terminal = text.split("      - name: Publish terminal delivery result\n", 1)[-1].split("        uses: actions/github-script@v7", 1)[0]
    if "continue-on-error" in terminal:
        raise AssertionError("terminal delivery result must fail an enforced non-passing check")
    if missing or present:
        details = [*(f"missing `{item}`" for item in missing), *(f"forbidden `{item}`" for item in present)]
        raise AssertionError("delivery gate workflow contract failed: " + "; ".join(details))
    for index, script_tail in enumerate(text.split("          script: |\n")[1:], start=1):
        script_lines: list[str] = []
        for line in script_tail.splitlines():
            if line and not line.startswith("            "):
                break
            script_lines.append(line[12:] if line else "")
        compiled = subprocess.run(
            [
                "node",
                "-e",
                "const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor; new AsyncFunction('github','context','core',process.argv[1]);",
                "\n".join(script_lines),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if compiled.returncode != 0:
            raise AssertionError(f"GitHub script {index} is not valid async JavaScript: {compiled.stderr}")


def check_composite_action_contract() -> None:
    valid = subprocess.run(
        [sys.executable, str(COMPOSITE_CHECKER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if valid.returncode != 0:
        raise AssertionError(f"repository composite action contract failed: {valid.stderr}")
    nested = FIXTURES.parent / "composite-action" / "nested-valid"
    nested_result = subprocess.run(
        [sys.executable, str(COMPOSITE_CHECKER), "--root", str(nested)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if nested_result.returncode != 0 or "1 manifests" not in nested_result.stdout:
        raise AssertionError(f"nested composite action was not discovered: {nested_result.stderr}")
    for name in (
        "invalid-yaml",
        "invalid-schema",
        "missing-name",
        "missing-description",
        "dangerous-uses",
        "dangerous-local-uses",
        "invalid-step-key",
    ):
        fixture = FIXTURES.parent / "composite-action" / name
        completed = subprocess.run(
            [sys.executable, str(COMPOSITE_CHECKER), "--root", str(fixture)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            raise AssertionError(f"invalid composite action fixture passed: {name}")
    with tempfile.TemporaryDirectory(prefix="loom-action-symlink-") as temporary:
        fixture = Path(temporary)
        action = fixture / ".github" / "actions" / "native"
        action.mkdir(parents=True)
        target = fixture / "manifest.yml"
        target.write_text(
            "name: Linked\ndescription: Invalid linked manifest\nruns:\n  using: composite\n  steps:\n    - shell: bash\n      run: echo invalid\n",
            encoding="utf-8",
        )
        (action / "action.yml").symlink_to(target)
        linked = subprocess.run(
            [sys.executable, str(COMPOSITE_CHECKER), "--root", str(fixture)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if linked.returncode == 0 or "must not contain symlinks" not in linked.stderr:
            raise AssertionError("composite action manifest symlink did not fail closed")
    with tempfile.TemporaryDirectory(prefix="loom-action-root-symlink-") as temporary:
        fixture = Path(temporary)
        external = fixture / "external-actions"
        external.mkdir()
        github = fixture / ".github"
        github.mkdir()
        (github / "actions").symlink_to(external, target_is_directory=True)
        linked_root = subprocess.run(
            [sys.executable, str(COMPOSITE_CHECKER), "--root", str(fixture)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if linked_root.returncode == 0 or "ancestor must not be a symlink" not in linked_root.stderr:
            raise AssertionError("composite actions root symlink did not fail closed")


def check_trusted_candidate_harness() -> None:
    with tempfile.TemporaryDirectory(prefix="loom-trusted-harness-") as temporary:
        root = Path(temporary)
        trusted = root / "trusted"
        candidate = root / "candidate"
        for tree in (trusted, candidate):
            (tree / "tools" / "fixtures").mkdir(parents=True)
            (tree / "src" / "skills" / "shared" / "scripts").mkdir(parents=True)
            (tree / ".github" / "workflows").mkdir(parents=True)
            (tree / "test").mkdir()
            shutil.copy2(
                ROOT / "src" / "skills" / "shared" / "scripts" / "native_validation.py",
                tree / "src" / "skills" / "shared" / "scripts" / "native_validation.py",
            )
            for name in ("delivery_gate.py", "failure_envelope.py", "light_profile.py"):
                (tree / "src" / "skills" / "shared" / "scripts" / name).write_text("# protected fixture\n", encoding="utf-8")
            (tree / ".github" / "workflows" / "loom-delivery-gate.yml").write_text("name: fixture\n", encoding="utf-8")
            (tree / "test" / "npm-package-smoke.test.mjs").write_text("// protected fixture\n", encoding="utf-8")
            for name in ("host_adapter_check.py", "py_compile_clean.py", "read_delivery_gate_required_identity.py", "skills_surface.py", "version_surface_check.py"):
                (tree / "tools" / name).write_text("# protected fixture\n", encoding="utf-8")
            (tree / "Makefile").write_text(
                "delivery-gate-check:\n\tpython3 tools/check_probe.py\n",
                encoding="utf-8",
            )
            (tree / "tools" / "check_probe.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(TRUSTED_RUNNER),
                "--trusted-root",
                str(trusted),
                "--candidate-root",
                str(candidate),
                "--targets-json",
                '["delivery-gate-check"]',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0 or "Error 7" not in completed.stderr:
            raise AssertionError(
                "trusted baseline harness did not control candidate validation: "
                f"returncode={completed.returncode} stdout={completed.stdout} stderr={completed.stderr}"
            )
        drift_cases = {
            "makefile": ("Makefile", "delivery-gate-check:\n\t@true\n"),
            "checker": ("tools/check_probe.py", "raise SystemExit(0)\n"),
            "os-exit": ("src/skills/shared/scripts/delivery_gate.py", "import os\nos._exit(0)\n"),
            "top-level-side-effect": ("src/skills/shared/scripts/light_profile.py", "raise SystemExit(0)\n"),
        }
        for name, (relative, content) in drift_cases.items():
            drifted = root / f"candidate-drift-{name}"
            shutil.copytree(candidate, drifted)
            (drifted / relative).write_text(content, encoding="utf-8")
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(TRUSTED_RUNNER),
                    "--trusted-root",
                    str(trusted),
                    "--candidate-root",
                    str(drifted),
                    "--targets-json",
                    '["delivery-gate-check"]',
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if rejected.returncode != 2 or "protected validation harness drift" not in rejected.stderr:
                raise AssertionError(f"candidate {name} drift did not fail closed: {rejected.stderr}")

        env_trusted = root / "trusted-env"
        env_candidate = root / "candidate-env"
        shutil.copytree(trusted, env_trusted)
        shutil.copytree(trusted, env_candidate)
        env_probe = (
            "import os\n"
            "for prefix in ('ACTIONS_', 'GITHUB_', 'RUNNER_'):\n"
            "    assert not any(key.startswith(prefix) for key in os.environ), prefix\n"
        )
        for tree in (env_trusted, env_candidate):
            (tree / "tools" / "check_probe.py").write_text(env_probe, encoding="utf-8")
        safe_env = os.environ.copy()
        safe_env.update({"ACTIONS_RUNTIME_TOKEN": "secret", "GITHUB_TOKEN": "secret", "RUNNER_TRACKING_ID": "secret"})
        stripped = subprocess.run(
            [
                sys.executable,
                str(TRUSTED_RUNNER),
                "--trusted-root",
                str(env_trusted),
                "--candidate-root",
                str(env_candidate),
                "--targets-json",
                '["delivery-gate-check"]',
            ],
            env=safe_env,
            check=False,
            capture_output=True,
            text=True,
        )
        if stripped.returncode != 0:
            raise AssertionError(f"candidate validation inherited Actions credentials: {stripped.stderr}")
        for relative in ("Makefile", "src", "tools", "tools/fixtures"):
            unsafe = root / f"candidate-{relative.replace('/', '-')}"
            shutil.copytree(candidate, unsafe)
            path = unsafe / relative
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(root / "outside", target_is_directory=relative != "Makefile")
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(TRUSTED_RUNNER),
                    "--trusted-root",
                    str(trusted),
                    "--candidate-root",
                    str(unsafe),
                    "--targets-json",
                    '["delivery-gate-check"]',
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if rejected.returncode != 2 or "candidate tree contains symlinks" not in rejected.stderr:
                raise AssertionError(f"candidate symlink did not fail closed: {relative}: {rejected.stderr}")

        reusable = root / "candidate-reusable"
        shutil.copytree(candidate, reusable)
        asset = reusable / "assets"
        asset.mkdir()
        (asset / "versioned").mkdir()
        (asset / "current").symlink_to("versioned", target_is_directory=True)
        reusable_result = subprocess.run(
            [
                sys.executable,
                str(TRUSTED_RUNNER),
                "--trusted-root",
                str(trusted),
                "--candidate-root",
                str(reusable),
                "--targets-json",
                '["delivery-gate-check"]',
                "--symlink-policy",
                "protected",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if reusable_result.returncode == 0 or "Error 7" not in reusable_result.stderr:
            raise AssertionError("reusable caller legal non-harness symlink was incorrectly rejected")

        unsafe_targets = {
            "absolute": str(root / "outside"),
            "outside": "../../outside",
            "harness": os.path.relpath(trusted, asset),
            "broken": "missing-target",
        }
        for name, target in unsafe_targets.items():
            unsafe_candidate = root / f"candidate-reusable-{name}"
            shutil.copytree(candidate, unsafe_candidate)
            unsafe_asset = unsafe_candidate / "assets"
            unsafe_asset.mkdir()
            (unsafe_asset / "current").symlink_to(target, target_is_directory=True)
            unsafe_link_result = subprocess.run(
                [
                    sys.executable,
                    str(TRUSTED_RUNNER),
                    "--trusted-root",
                    str(trusted),
                    "--candidate-root",
                    str(unsafe_candidate),
                    "--targets-json",
                    '["delivery-gate-check"]',
                    "--symlink-policy",
                    "protected",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if unsafe_link_result.returncode != 2 or "candidate tree contains symlinks" not in unsafe_link_result.stderr:
                raise AssertionError(f"reusable caller unsafe {name} symlink did not fail closed")

        reusable_unsafe = root / "candidate-reusable-unsafe"
        shutil.copytree(candidate, reusable_unsafe)
        shutil.rmtree(reusable_unsafe / "tools")
        (reusable_unsafe / "tools").symlink_to(root / "outside", target_is_directory=True)
        unsafe_result = subprocess.run(
            [
                sys.executable,
                str(TRUSTED_RUNNER),
                "--trusted-root",
                str(trusted),
                "--candidate-root",
                str(reusable_unsafe),
                "--targets-json",
                '["delivery-gate-check"]',
                "--symlink-policy",
                "protected",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if unsafe_result.returncode != 2 or "candidate tree contains symlinks" not in unsafe_result.stderr:
            raise AssertionError("reusable caller protected harness symlink did not fail closed")

        spec = importlib.util.spec_from_file_location("trusted_runner_contract", TRUSTED_RUNNER)
        if spec is None or spec.loader is None:
            raise AssertionError("trusted candidate runner is not importable")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        source = trusted / "Makefile"
        output_root = root / "validation-root"
        output_root.mkdir()
        try:
            runner.replace_path(source, output_root / ".." / "escaped", output_root)
        except ValueError:
            pass
        else:
            raise AssertionError("trusted overlay accepted a path traversal destination")

    indexed_symlinks = subprocess.run(
        ["git", "ls-files", "-s"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    if any(line.startswith("120000 ") for line in indexed_symlinks):
        raise AssertionError("Loom direct candidate still tracks symlinks")
    if (ROOT / ".agents" / "skills").exists():
        raise AssertionError("legacy .agents/skills compatibility links must remain absent")


def check_reusable_host_authority_cases() -> None:
    fixture = json.loads(REUSABLE_AUTHORITY_CASES.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "loom-delivery-gate-reusable-authority-cases/v1":
        raise AssertionError("reusable authority fixture schema drifted")
    observed = fixture["observed"]
    for case in fixture["cases"]:
        supplied = case["supplied"]
        conflict = False
        declared_repository = supplied.get("repository")
        if declared_repository and declared_repository != observed["repository"]:
            conflict = True
        declared_change = supplied.get("change")
        if isinstance(declared_change, dict):
            conflict = conflict or any(
                key in declared_change and declared_change[key] != observed["change"].get(key)
                for key in ("base_sha", "head_sha", "base_repository", "head_repository", "number")
            )
        if supplied.get("event") and supplied["event"] != observed["event"]:
            conflict = True
        if "changed_paths" in supplied and supplied["changed_paths"] != observed["changed_paths"]:
            conflict = True
        verdict = "conflict" if conflict else "consistent"
        if verdict != case["expected"]:
            raise AssertionError(f"reusable authority case drifted: {case['name']}: {verdict}")


def check_host_authority_failure_cases() -> None:
    fixture = json.loads(HOST_AUTHORITY_FAILURE_CASES.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "loom-delivery-gate-host-authority-failure-cases/v1":
        raise AssertionError("host authority failure fixture schema drifted")
    for case in fixture["cases"]:
        cap = 3000 if case["event"] == "pull_request_target" else 300
        authority_ready = (
            case["api_status"] == 200
            and case["authority_fields_complete"]
            and case["changed_path_count"] < cap
        )
        checkout_count = 10 if authority_ready else 0
        result = "passed_to_evaluator" if authority_ready else "blocked"
        if result != case["expected"] or (not authority_ready and checkout_count != 0):
            raise AssertionError(f"host authority failure case drifted: {case['name']}")


def check_workflow_spoof_cases() -> None:
    fixture = json.loads(WORKFLOW_SPOOF_CASES.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "loom-delivery-gate-workflow-spoof-cases/v1":
        raise AssertionError("workflow spoof fixture schema drifted")
    for case in fixture["cases"]:
        if case["coordinator_source"] != "base":
            verdict = "blocked"
        elif case["trust_mode"] == "distinct_app_check":
            verdict = "strong"
        else:
            verdict = "limited"
        if verdict != case["expected"]:
            raise AssertionError(f"workflow spoof case drifted: {case['name']}: {verdict}")


def check_workflow_event_matrix() -> None:
    matrix = json.loads(WORKFLOW_MATRIX.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "loom-delivery-gate-workflow-matrix/v1",
        "loom-check": {
            "pull_request": ["py-compile"],
            "merge_group": ["py-compile"],
            "push_main": ["py-compile", "demo-bootstrap", "repo-local-cli", "root-self-governance", "loom-check"],
        },
        "loom-delivery-gate": {
            "pull_request_target": "enforce",
            "merge_group": "enforce",
            "trusted_evaluator": "base_sha_or_pinned_loom_ref",
            "candidate": "isolated_head_tree",
        },
    }
    if matrix != expected:
        raise AssertionError(f"workflow event matrix fixture drifted: {matrix}")

    text = CHECK_WORKFLOW.read_text(encoding="utf-8")
    required = (
        "  push:\n    branches:\n      - main\n",
        "  pull_request:\n",
        "  merge_group:\n",
        "group: loom-check-${{ github.event.pull_request.number || github.event.merge_group.head_ref || github.ref }}",
        "cancel-in-progress: true",
    )
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise AssertionError("loom-check event contract missing: " + ", ".join(missing))
    job_names = ["demo-bootstrap", "repo-local-cli", "root-self-governance", "loom-check"]
    for name in job_names:
        start = text.index(f"  {name}:\n")
        following = [text.find(f"  {other}:\n", start + 1) for other in ["py-compile", *job_names]]
        stops = [position for position in following if position > start]
        block = text[start : min(stops) if stops else len(text)]
        if "if: ${{ github.event_name == 'push' }}" not in block:
            raise AssertionError(f"{name} must remain a main-push aggregate job")
    py_start = text.index("  py-compile:\n")
    py_end = min(text.index(f"  {name}:\n") for name in job_names)
    if "github.event_name == 'push'" in text[py_start:py_end]:
        raise AssertionError("py-compile must remain available to pull_request and merge_group required checks")

    delivery = WORKFLOW.read_text(encoding="utf-8")
    if "\n  push:\n" in delivery or "DELIVERY_GATE_ENFORCEMENT: ${{ inputs.loom_ref != '' && inputs.enforcement || 'enforce' }}" not in delivery:
        raise AssertionError("delivery gate must enforce direct PR/merge-group events without a duplicate push run")
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        workflow_text = workflow.read_text(encoding="utf-8")
        if "\n  push:\n" in workflow_text and "\n    branches:\n      - main\n" not in workflow_text:
            raise AssertionError(f"{workflow.name} must not run feature-branch push validation")


def main() -> int:
    check_evaluator()
    check_native_surface_inventory()
    check_light_profile_host_integration()
    check_generated_copies()
    check_required_check_identity()
    check_identity_reader_boundary()
    check_workflow()
    check_composite_action_contract()
    check_trusted_candidate_harness()
    check_reusable_host_authority_cases()
    check_host_authority_failure_cases()
    check_workflow_spoof_cases()
    check_workflow_event_matrix()
    print("delivery gate contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
