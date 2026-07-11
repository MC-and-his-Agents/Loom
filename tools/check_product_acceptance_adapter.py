#!/usr/bin/env python3
"""Focused contract checks for the read-only product acceptance adapter."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "skills" / "shared" / "scripts" / "product_acceptance.py"
SOURCE_DIR = SOURCE.parent
FIXTURES = ROOT / "tools" / "fixtures" / "product-acceptance"
GENERATED_COPIES = (
    ROOT / "skills" / "shared" / "scripts" / "product_acceptance.py",
    ROOT / "plugins" / "loom" / "skills" / "shared" / "scripts" / "product_acceptance.py",
    ROOT / ".loom" / "bin" / "product_acceptance.py",
)
NOW = datetime(2026, 7, 11, tzinfo=timezone.utc)


def load_adapter() -> Any:
    sys.path.insert(0, str(SOURCE_DIR))
    spec = importlib.util.spec_from_file_location("product_acceptance", SOURCE)
    if spec is None or spec.loader is None:
        raise AssertionError("product acceptance adapter is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def assert_result(result: dict[str, Any], *, outcome: str, verdict: str) -> None:
    if result.get("result") != outcome or result.get("product_acceptance", {}).get("verdict") != verdict:
        raise AssertionError(f"expected {outcome}/{verdict}, got {result}")
    envelope = result.get("failure_envelope")
    if not isinstance(envelope, dict) or set(envelope) != {"schema_version", "primary_cause", "consequences"} or envelope.get("consequences") != []:
        raise AssertionError("acceptance adapter must return exactly one primary cause")
    authority = result.get("authority_verdict", {}).get("verdict")
    if not isinstance(authority, dict) or authority.get("delivery_state") != "not_evaluated" or authority.get("reconciliation_state") != "not_evaluated":
        raise AssertionError("acceptance adapter must not infer delivery or reconciliation")
    if result.get("mutates") is not False or result.get("network_access") is not False or result.get("runtime_actions_executed") != []:
        raise AssertionError("acceptance adapter must remain read-only and non-executing")


def main() -> int:
    adapter = load_adapter()
    assert_result(adapter.evaluate_acceptance(fixture("passed-live-readonly.json"), now=NOW), outcome="pass", verdict="passed")
    for name in ("fixture-insufficient.json", "blocked-write-boundary.json", "stale-live-readonly.json"):
        assert_result(adapter.evaluate_acceptance(fixture(name), now=NOW), outcome="block", verdict="blocked")
    waived = fixture("waived.json")
    assert_result(adapter.evaluate_acceptance(waived, now=NOW), outcome="pass", verdict="waived")
    if "delivery_gate" in SOURCE.read_text(encoding="utf-8"):
        raise AssertionError("product acceptance adapter must not depend on delivery gate")
    source = SOURCE.read_bytes()
    drifted = [str(path.relative_to(ROOT)) for path in GENERATED_COPIES if not path.is_file() or path.read_bytes() != source]
    if drifted:
        raise AssertionError("product acceptance generated copy drift: " + ", ".join(drifted))
    print("product acceptance adapter checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
