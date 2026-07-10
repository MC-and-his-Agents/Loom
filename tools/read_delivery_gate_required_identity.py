#!/usr/bin/env python3
"""Read GitHub required-check identity before a delivery gate becomes required."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "delivery_gate.py"
REPOSITORY_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


sys.dont_write_bytecode = True


def load_evaluator() -> Any:
    spec = importlib.util.spec_from_file_location("delivery_gate", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("delivery evaluator is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_repository(value: str) -> dict[str, str]:
    owner, separator, name = value.partition("/")
    if not separator or not REPOSITORY_PART.fullmatch(owner) or not REPOSITORY_PART.fullmatch(name):
        raise argparse.ArgumentTypeError("repository must be OWNER/REPOSITORY")
    return {"owner": owner, "name": name}


def github_api_json(endpoint: str, *, allow_not_found: bool = False) -> tuple[object, str | None]:
    completed = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip() or f"gh api exited {completed.returncode}"
            return {}, detail
        return {}, f"GitHub API response is not JSON: {exc}"
    if completed.returncode:
        if allow_not_found and isinstance(payload, dict) and str(payload.get("status")) == "404":
            return {}, None
        detail = completed.stderr.strip() or completed.stdout.strip() or f"gh api exited {completed.returncode}"
        return {}, detail
    return payload, None


def github_branch_protection(repository: dict[str, str], branch: str) -> tuple[object, str | None]:
    endpoint = f"repos/{repository['owner']}/{repository['name']}/branches/{quote(branch, safe='')}/protection"
    return github_api_json(endpoint, allow_not_found=True)


def github_applicable_rulesets(repository: dict[str, str], branch: str) -> tuple[object, str | None]:
    endpoint = f"repos/{repository['owner']}/{repository['name']}/rules/branches/{quote(branch, safe='')}"
    return github_api_json(endpoint)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=parse_repository, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--app-id", type=int, required=True)
    parser.add_argument("--legacy-context", action="append", default=[])
    parser.add_argument("--retained-context", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.app_id <= 0:
        parser.error("--app-id must be positive")
    if not args.branch:
        parser.error("--branch must be non-empty")
    if not args.context.strip():
        parser.error("--context must be non-empty")
    if any(not context.strip() for context in args.legacy_context):
        parser.error("--legacy-context must be non-empty")
    if any(not context.strip() for context in args.retained_context):
        parser.error("--retained-context must be non-empty")
    if args.context in args.legacy_context:
        parser.error("--legacy-context must not repeat --context")
    if set(args.legacy_context) & set(args.retained_context):
        parser.error("--legacy-context and --retained-context must not overlap")

    evaluator = load_evaluator()
    protection, branch_protection_read_error = github_branch_protection(args.repository, args.branch)
    branch_rules, branch_rules_read_error = github_applicable_rulesets(args.repository, args.branch)
    evidence = evaluator.build_required_check_identity(
        args.repository,
        args.branch,
        args.context,
        args.app_id,
        args.legacy_context,
        args.retained_context,
        protection,
        branch_rules,
        datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        branch_protection_read_error,
        branch_rules_read_error,
    )
    payload = evaluator.evaluate_required_check_identity(evidence)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if payload["result"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
