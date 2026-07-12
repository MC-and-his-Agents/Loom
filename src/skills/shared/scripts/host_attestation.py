"""Host-readback review attestation and closeout; never reads repository carriers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from authority_contract import authority_verdict, typed_locator
from failure_envelope import envelope, primary_cause
from github_host import github_pr_attestation_readback, github_pr_closeout_readback


SCHEMA = "loom-host-attestation/v1"


def _result(*, owner: str, repo: str, work_item: int, facts: dict[str, Any] | None, errors: list[str], closeout: bool) -> dict[str, Any]:
    try:
        work_item_locator = typed_locator(owner, repo, "work_item", work_item)
    except ValueError:
        work_item_locator = "invalid:work_item"
        facts = None
        errors = ["work_item locator is invalid", *errors]
    passed = not errors and facts is not None
    cause = primary_cause(
        cause_id="host_closeout_valid" if closeout and passed else "host_attestation_valid" if passed else "host_closeout_invalid" if closeout else "host_attestation_invalid",
        failure_domain="governance_metadata" if passed or any(error.startswith(("no GitHub APPROVED", "a current-head", "GitHub Actions artifact", "GitHub Actions workflow", "GitHub PR must", "GitHub PR is not", "GitHub base branch", "typed Work Item", "GitHub issue is not typed", "GitHub Work Item is not", "single-maintainer", "exactly one explicit")) for error in errors) else "host_service",
        code="accepted" if passed else "readback_invalid",
        locator=work_item_locator,
        summary="GitHub host facts bind the merged PR, review, tree, workflow artifact, and Work Item." if closeout and passed else "GitHub host facts bind the approved review, semantic tree, and workflow artifact." if passed else errors[0] if errors else "GitHub host readback returned no facts",
        owner="github" if passed else "operator" if any(error.startswith(("no GitHub APPROVED", "a current-head", "GitHub Actions artifact", "GitHub Actions workflow", "GitHub PR must", "GitHub PR is not", "GitHub base branch", "typed Work Item", "GitHub issue is not typed", "GitHub Work Item is not", "single-maintainer", "exactly one explicit")) for error in errors) else "github",
        retryable=not passed,
        remediation_command="loom attestation closeout --repo <owner/name> --pr <number> --work-item <number> --artifact-input <file> --json" if closeout else "loom attestation readback --repo <owner/name> --pr <number> --work-item <number> --artifact-input <file> --json",
    )
    return {
        "schema_version": SCHEMA,
        "result": "pass" if passed else "block",
        "attestation": {
            "verdict": "passed" if passed else "blocked",
            "owner": "github",
            "carrier_mutations": False,
            "host_readback_only": True,
            "closeout": closeout,
        },
        "authority_verdict": authority_verdict(delivery_state="delivery_closed_out" if closeout and passed else "not_evaluated"),
        "work_item_locator": work_item_locator,
        "host_facts": facts if passed else None,
        "missing_inputs": errors,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "failure_envelope": envelope(cause),
        "mutates": False,
        "network_access": True,
    }


def _artifact_id(path: Path) -> int:
    """Accept only an Actions artifact locator from local input, never asserted facts."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read artifact input: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"artifact_id"} or not isinstance(payload.get("artifact_id"), int) or isinstance(payload["artifact_id"], bool) or payload["artifact_id"] <= 0:
        raise ValueError("artifact input must be exactly {'artifact_id': positive integer}; digest, run, PR, review, and carrier facts are host-readback only")
    return payload["artifact_id"]


def readback(root: Path, owner: str, repo: str, number: int, work_item: int, artifact_id: int, *, closeout: bool = False, review_policy: str = "approved") -> dict[str, Any]:
    reader = github_pr_closeout_readback if closeout else github_pr_attestation_readback
    if closeout:
        facts, errors = reader(root, owner, repo, number, work_item, artifact_id, review_policy=review_policy)
    else:
        facts, errors = reader(root, owner, repo, number, artifact_id, work_item=work_item, review_policy=review_policy)
    return _result(owner=owner, repo=repo, work_item=work_item, facts=facts, errors=errors, closeout=closeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loom attestation")
    parser.add_argument("action", choices=("readback", "closeout"))
    parser.add_argument("--repo", required=True, metavar="OWNER/REPO")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--work-item", type=int, required=True)
    parser.add_argument("--artifact-input", type=Path, required=True, help="JSON containing only the GitHub Actions artifact_id")
    parser.add_argument("--review-policy", choices=("approved", "single_maintainer"), default="approved")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        owner, repo = args.repo.split("/", 1)
        if not owner or not repo:
            raise ValueError("--repo must be OWNER/REPO")
        artifact_id = _artifact_id(args.artifact_input)
    except ValueError as exc:
        parser.error(str(exc))
    result = readback(Path.cwd(), owner, repo, args.pr, args.work_item, artifact_id, closeout=args.action == "closeout", review_policy=args.review_policy)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
