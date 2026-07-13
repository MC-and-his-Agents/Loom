#!/usr/bin/env python3
"""Write one host-bound Loom product acceptance record for Actions upload."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--evidence-class", choices=("contract_test", "process_runtime", "live_readonly"), required=True)
    parser.add_argument("--provider-profile", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--verifier-login", required=True)
    parser.add_argument("--verifier-id", required=True, type=int)
    parser.add_argument("--release-readback", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if len(args.head_sha) != 40 or any(character not in "0123456789abcdef" for character in args.head_sha.lower()):
        parser.error("--head-sha must be a 40-character hexadecimal commit")
    if args.evidence_class == "live_readonly":
        if args.release_readback is None:
            parser.error("live_readonly evidence requires --release-readback")
        try:
            release_readback = json.loads(args.release_readback.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"cannot read release readback: {exc}")
        classification = release_readback.get("classification") if isinstance(release_readback, dict) else None
        if (
            release_readback.get("result") != "pass"
            or not isinstance(classification, dict)
            or classification.get("verdict") != "published"
            or classification.get("gaps") != []
        ):
            parser.error("live_readonly release evidence must be a passed, gap-free published readback")
    elif args.release_readback is not None:
        parser.error("--release-readback is only valid for live_readonly evidence")

    observed_actions = ["read"]
    if args.evidence_class == "process_runtime":
        observed_actions.insert(0, "launch")

    record = {
        "schema_version": "loom-product-acceptance/v1",
        "story_locator": args.story,
        "scenario_id": args.scenario,
        "verdict": "passed",
        "minimum_evidence_class": args.evidence_class,
        "evidence": [
            {
                "evidence_class": args.evidence_class,
                "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "freshness_window_seconds": 604800,
                "run_id": args.run_id,
                "artifact_refs": ["github-actions:self"],
                "provider_profile": {
                    "provider": "github-actions",
                    "profile": args.provider_profile,
                    "redacted": True,
                },
                "component_versions": {args.repository: args.head_sha.lower()},
                "operation_boundary": {
                    "allowed_actions": observed_actions,
                    "prohibited_actions": [
                        "login",
                        "captcha_or_risk_bypass",
                        "submit",
                        "publish",
                        "send",
                        "external_visible_write",
                    ],
                    "observed_actions": observed_actions,
                },
            }
        ],
        "verifier": {"login": args.verifier_login, "id": args.verifier_id},
    }
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
