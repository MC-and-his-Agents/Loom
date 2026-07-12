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
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--verifier-login", required=True)
    parser.add_argument("--verifier-id", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if len(args.head_sha) != 40 or any(character not in "0123456789abcdef" for character in args.head_sha.lower()):
        parser.error("--head-sha must be a 40-character hexadecimal commit")

    record = {
        "schema_version": "loom-product-acceptance/v1",
        "story_locator": args.story,
        "scenario_id": args.scenario,
        "verdict": "passed",
        "minimum_evidence_class": "contract_test",
        "evidence": [
            {
                "evidence_class": "contract_test",
                "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "freshness_window_seconds": 604800,
                "run_id": args.run_id,
                "artifact_refs": ["github-actions:self"],
                "provider_profile": {
                    "provider": "github-actions",
                    "profile": "loom-v0.30-stage-a",
                    "redacted": True,
                },
                "component_versions": {args.repository: args.head_sha.lower()},
                "operation_boundary": {
                    "allowed_actions": ["read"],
                    "prohibited_actions": [
                        "login",
                        "captcha_or_risk_bypass",
                        "submit",
                        "publish",
                        "send",
                        "external_visible_write",
                    ],
                    "observed_actions": ["read"],
                },
            }
        ],
        "verifier": {"login": args.verifier_login, "id": args.verifier_id},
    }
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
