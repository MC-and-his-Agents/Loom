#!/usr/bin/env python3
"""Check the pure delivery evaluator and its advisory workflow contract."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tools" / "fixtures" / "delivery-gate"
WORKFLOW = ROOT / ".github" / "workflows" / "loom-delivery-gate.yml"
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "delivery_gate.py"


def load_evaluator() -> Any:
    spec = importlib.util.spec_from_file_location("delivery_gate", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("delivery evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_primary_cause(payload: dict[str, Any], expected: str) -> None:
    cause = payload.get("primary_cause")
    if not isinstance(cause, dict) or set(cause) != {"id", "domain", "code", "locator", "summary"} or cause.get("id") != expected:
        raise AssertionError(f"expected primary cause {expected}, got {cause}")
    if payload.get("product_acceptance", {}).get("verdict") != "not_evaluated":
        raise AssertionError("delivery gate must not infer product acceptance")
    if payload.get("result") != "advisory" or payload.get("enforcement") != "advisory":
        raise AssertionError("delivery gate must stay advisory")


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
    assert_primary_cause(evaluator.finalize_delivery_gate(caller["host_facts"], {"status": "passed"}), "passed")


def check_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    loom_ref_block = text.split("      loom_ref:\n", 1)[1].split("    outputs:", 1)[0] if "      loom_ref:\n" in text else ""
    required = (
        "name: loom-delivery-gate",
        "pull_request:",
        "merge_group:",
        "workflow_call:",
        "profile:",
        "validation_command:",
        "default: make delivery-gate-check",
        "loom_ref:",
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
        "const reusable = process.env.REUSABLE_MODE === \"true\";",
        "if: ${{ always() && inputs.loom_ref != '' }}",
        "if: ${{ always() && inputs.loom_ref == '' }}",
        "LOOM_SOURCE_PATH: ${{ inputs.loom_ref != '' && 'loom' || '.' }}",
        "CANDIDATE_PATH: ${{ inputs.loom_ref != '' && 'candidate' || '.' }}",
        "LOOM_SOURCE_PATH",
        "CANDIDATE_PATH",
        "$LOOM_SOURCE_PATH/src/skills/shared/scripts/delivery_gate.py",
        "bash -o pipefail -c \"$VALIDATION_COMMAND\"",
        "--validation-result-file",
        "LOOM_DELIVERY_GATE_CHANGED_PATHS_FILE",
        "LOOM_DELIVERY_GATE_HOST_FACTS_FILE",
        "LOOM_DELIVERY_GATE_DECISION_FILE",
        "CHANGED_PATHS_PATH",
        "fs.writeFileSync(process.env.CHANGED_PATHS_PATH",
        "Product acceptance: not_evaluated.",
        "continue-on-error: true",
    )
    forbidden = (
        "pull_request_target",
        "contents: write",
        "pull-requests: write",
        "issues: write",
        "id-token:",
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
    present.extend(
        line.strip()
        for line in text.splitlines()
        if line.strip() in {"paths:", "paths-ignore:"}
    )
    if text.count("name: loom-delivery-gate") != 2:
        raise AssertionError("workflow must expose one workflow name and one same-name terminal job")
    checkouts = text.split("uses: actions/checkout@v4")[1:]
    if not checkouts or any("persist-credentials: false" not in checkout for checkout in checkouts):
        raise AssertionError("every checkout must drop credentials before untrusted native validation")
    if len(checkouts) != 3:
        raise AssertionError("workflow must keep separate canonical Loom, caller candidate, and direct Loom checkout paths")
    if "required: true" not in loom_ref_block or "default:" in loom_ref_block:
        raise AssertionError("reusable callers must supply one non-default pinned Loom SHA")
    if missing or present:
        details = [*(f"missing `{item}`" for item in missing), *(f"forbidden `{item}`" for item in present)]
        raise AssertionError("delivery gate workflow contract failed: " + "; ".join(details))


def main() -> int:
    check_evaluator()
    check_workflow()
    print("delivery gate contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
