#!/usr/bin/env python3
"""Check delivery-gate evaluator, enforcement, and required-check identity contracts."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tools" / "fixtures" / "delivery-gate"
WORKFLOW = ROOT / ".github" / "workflows" / "loom-delivery-gate.yml"
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "delivery_gate.py"
SOURCE_DIR = SOURCE.parent
IDENTITY_READER = ROOT / "tools" / "read_delivery_gate_required_identity.py"
GENERATED_COPIES = (
    ROOT / "skills" / "shared" / "scripts" / "delivery_gate.py",
    ROOT / "plugins" / "loom" / "skills" / "shared" / "scripts" / "delivery_gate.py",
)


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
        or envelope.get("secondary_causes") != []
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
    examples = (("docs.json", "light", "changed_paths", "valid"), ("runtime.json", "standard", "host_facts", "valid"))
    for name, profile, source, host_status in examples:
        payload = evaluator.evaluate_host_facts(json.loads((FIXTURES / name).read_text(encoding="utf-8")))
        assert_primary_cause(payload, "passed")
        if payload["delivery"]["profile"] != profile or payload["delivery"]["profile_source"] != source:
            raise AssertionError(f"{name} selected an unexpected profile")
        if payload["host_facts"]["status"] != host_status:
            raise AssertionError(f"{name} unexpectedly rejected valid host facts")
        if not payload["native_validation"]["command"]:
            raise AssertionError(f"{name} must select a usable default validation command")

    valid = json.loads((FIXTURES / "docs.json").read_text(encoding="utf-8"))
    reusable = evaluator.evaluate_host_facts({**valid, "profile": "reinforced", "validation_command": "python -m pytest -q"})
    assert_primary_cause(reusable, "passed")
    if reusable["delivery"]["profile"] != "reinforced" or reusable["native_validation"]["command"] != "python -m pytest -q":
        raise AssertionError("reusable callers must retain their declared profile and validation command")
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
        or caller.get("host_facts", {}).get("event") != "pull_request"
    ):
        raise AssertionError("caller fixture must prove a pull_request caller selects pinned Loom and candidate paths")
    assert_primary_cause(evaluator.finalize_delivery_gate(caller["host_facts"], {"status": "passed"}, "enforce"), "passed", "enforce", "passed")


def materialize_light_candidate(root: Path, forbidden: bool) -> Path:
    candidate = root / ("forbidden" if forbidden else "clean")
    candidate.mkdir()
    subprocess.run(["git", "init"], cwd=candidate, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "loom@example.invalid"], cwd=candidate, check=True)
    subprocess.run(["git", "config", "user.name", "Loom Fixture"], cwd=candidate, check=True)
    state = candidate / ".loom" / "installed-state.json"
    state.parent.mkdir(parents=True)
    state.write_text(
        json.dumps(
            {
                "schema_version": "loom-installed-state/v2",
                "repo_payload": {"mode": "metadata-only", "adoption_mode": "light-governance"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
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
        forbidden = materialize_light_candidate(root, True)
        clean = materialize_light_candidate(root, False)
        blocked = evaluator.finalize_delivery_gate(facts, {"status": "passed"}, "enforce", forbidden)
        assert_primary_cause(blocked, "light_profile_forbidden_carrier", "enforce", "blocked")
        if blocked.get("light_invariant", {}).get("status") != "blocked":
            raise AssertionError("explicit light delivery profile must consume the forbidden candidate tree")
        passed = evaluator.finalize_delivery_gate(facts, {"status": "passed"}, "enforce", clean)
        assert_primary_cause(passed, "passed", "enforce", "passed")
        for profile in ("standard", "reinforced"):
            bypassed = evaluator.finalize_delivery_gate({**facts, "profile": profile}, {"status": "passed"}, "enforce", forbidden)
            assert_primary_cause(bypassed, "passed", "enforce", "passed")
            if bypassed.get("light_invariant", {}).get("status") != "not_evaluated":
                raise AssertionError(f"{profile} delivery profile must not consume the light invariant")

        host_facts = root / "host-facts.json"
        validation = root / "validation.json"
        host_facts.write_text(json.dumps(facts) + "\n", encoding="utf-8")
        validation.write_text('{"status":"passed"}\n', encoding="utf-8")
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
            raise AssertionError(f"host-level light-profile negative integration drifted: {payload}")


def check_generated_copies() -> None:
    source = SOURCE.read_bytes()
    drifted = [str(path.relative_to(ROOT)) for path in GENERATED_COPIES if not path.is_file() or path.read_bytes() != source]
    if drifted:
        raise AssertionError("delivery-gate generated copy drift: " + ", ".join(drifted))


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
    if ready["result"] != "ready" or ready["primary_cause"]["id"] != "passed":
        raise AssertionError("matching GitHub required check and app identity must be ready")

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
            15368,
            [],
            [],
            {},
            json.loads((FIXTURES / "required-check-identity-ruleset-expected.json").read_text(encoding="utf-8")),
            observed_at,
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
    if retained["result"] != "ready" or retained["primary_cause"]["id"] != "passed":
        raise AssertionError("explicitly retained native checks must remain allowed")

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
        "--repository",
        "--branch",
        "--context",
        "--app-id",
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
    loom_ref_block = text.split("      loom_ref:\n", 1)[1].split("    outputs:", 1)[0] if "      loom_ref:\n" in text else ""
    enforcement_block = text.split("      enforcement:\n", 1)[1].split("    outputs:", 1)[0] if "      enforcement:\n" in text else ""
    required = (
        "name: loom-delivery-gate",
        "pull_request:",
        "merge_group:",
        "workflow_call:",
        "profile:",
        "validation_command:",
        "default: make delivery-gate-check",
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
        "path: loom",
        "repository: ${{ github.repository }}",
        "path: candidate",
        "REUSABLE_MODE: ${{ inputs.loom_ref != '' }}",
        "WORKFLOW_CALL_ENFORCEMENT",
        "const reusable = process.env.REUSABLE_MODE === \"true\";",
        "if: ${{ always() && inputs.loom_ref != '' }}",
        "if: ${{ always() && inputs.loom_ref == '' }}",
        "LOOM_SOURCE_PATH: ${{ inputs.loom_ref != '' && 'loom' || '.' }}",
        "CANDIDATE_PATH: ${{ inputs.loom_ref != '' && 'candidate' || '.' }}",
        "DELIVERY_GATE_ENFORCEMENT: ${{ inputs.loom_ref != '' && inputs.enforcement || 'enforce' }}",
        "LOOM_SOURCE_PATH",
        "CANDIDATE_PATH",
        "$LOOM_SOURCE_PATH/src/skills/shared/scripts/delivery_gate.py",
        "bash -o pipefail -c \"$VALIDATION_COMMAND\"",
        "--validation-result-file",
        "--candidate-path \"$CANDIDATE_PATH\"",
        "--enforcement \"$DELIVERY_GATE_ENFORCEMENT\"",
        "LOOM_DELIVERY_GATE_CHANGED_PATHS_FILE",
        "LOOM_DELIVERY_GATE_HOST_FACTS_FILE",
        "LOOM_DELIVERY_GATE_DECISION_FILE",
        "CHANGED_PATHS_PATH",
        "fs.writeFileSync(process.env.CHANGED_PATHS_PATH",
        "Product acceptance: not_evaluated.",
        "failure_envelope:",
        "core.setOutput(\"failure_envelope\", JSON.stringify(failureEnvelope))",
        "remediation=${failureEnvelope.primary_cause?.remediation_command || \"unavailable\"}",
        "Publish terminal delivery result",
        'payload?.result || (enforcement === "advisory" ? "advisory" : "blocked")',
        "core.setFailed(`loom-delivery-gate blocked: ${cause}`)",
        "continue-on-error: true",
    )
    forbidden = (
        "pull_request_target",
        "contents: write",
        "pull-requests: write",
        "issues: write",
        "id-token:",
        "secrets: inherit",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "github.event_name",
        'event === "workflow_call"',
        'const cause = "product_acceptance:not_evaluated"',
        "loom_flow.py",
        "current.md",
        ".loom/",
    )
    missing = [needle for needle in required if needle not in text]
    present = [needle for needle in forbidden if needle in text]
    present.extend(line.strip() for line in text.splitlines() if line.strip() in {"paths:", "paths-ignore:"})
    if text.count("name: loom-delivery-gate") != 2:
        raise AssertionError("workflow must expose one workflow name and one same-name terminal job")
    checkouts = text.split("uses: actions/checkout@v4")[1:]
    if not checkouts or any("persist-credentials: false" not in checkout for checkout in checkouts):
        raise AssertionError("every checkout must drop credentials before untrusted native validation")
    if len(checkouts) != 3:
        raise AssertionError("workflow must keep separate canonical Loom, caller candidate, and direct Loom checkout paths")
    if "required: true" not in loom_ref_block or "default:" in loom_ref_block:
        raise AssertionError("reusable callers must supply one non-default pinned Loom SHA")
    if "required: true" not in enforcement_block or "default:" in enforcement_block:
        raise AssertionError("reusable callers must explicitly choose advisory or enforce")
    terminal = text.split("      - name: Publish terminal delivery result\n", 1)[-1].split("        uses: actions/github-script@v7", 1)[0]
    if "continue-on-error" in terminal:
        raise AssertionError("terminal delivery result must fail an enforced non-passing check")
    if missing or present:
        details = [*(f"missing `{item}`" for item in missing), *(f"forbidden `{item}`" for item in present)]
        raise AssertionError("delivery gate workflow contract failed: " + "; ".join(details))


def main() -> int:
    check_evaluator()
    check_light_profile_host_integration()
    check_generated_copies()
    check_required_check_identity()
    check_identity_reader_boundary()
    check_workflow()
    print("delivery gate contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
