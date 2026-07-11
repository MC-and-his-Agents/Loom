#!/usr/bin/env python3
"""Focused contract checks for the read-only product acceptance adapter."""

from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import sys
import zipfile
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
NOW = datetime(2026, 7, 11, 0, 30, tzinfo=timezone.utc)


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
    if (
        not isinstance(envelope, dict)
        or set(envelope) != {"schema_version", "primary_cause", "consequences", "suppressed_diagnostics", "secondary_causes"}
        or envelope.get("consequences") != []
        or envelope.get("suppressed_diagnostics") != []
        or envelope.get("secondary_causes") != []
    ):
        raise AssertionError("acceptance adapter must return exactly one primary cause")
    authority = result.get("authority_verdict", {}).get("verdict")
    if not isinstance(authority, dict) or authority.get("delivery_state") != "not_evaluated" or authority.get("reconciliation_state") != "not_evaluated":
        raise AssertionError("acceptance adapter must not infer delivery or reconciliation")
    if result.get("mutates") is not False or result.get("runtime_actions_executed") != []:
        raise AssertionError("acceptance adapter must remain non-mutating and non-executing")


def resolve(adapter: Any, record: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as bundle:
        bundle.writestr("acceptance.json", json.dumps(record))
    archive = output.getvalue()
    mapping = {
        "repos/MC-and-his-Agents/Loom": {"default_branch": "main"},
        "repos/MC-and-his-Agents/Loom/issues/225": {"number": 225},
        "repos/MC-and-his-Agents/Loom/actions/artifacts/7": {"id": 7, "name": adapter.ARTIFACT_NAME, "expired": False, "size_in_bytes": len(archive), "digest": "sha256:" + hashlib.sha256(archive).hexdigest(), "workflow_run": {"id": 9}, "created_at": "2026-07-11T00:01:00Z"},
        "repos/MC-and-his-Agents/Loom/actions/runs/9": {"id": 9, "status": "completed", "conclusion": "success", "head_sha": "a" * 40, "workflow_id": 11, "path": adapter.TRUSTED_WORKFLOW_PATH, "event": "workflow_dispatch", "head_branch": "main", "run_started_at": "2026-07-10T23:59:00Z", "updated_at": "2026-07-11T00:02:00Z", "repository": {"full_name": "MC-and-his-Agents/Loom"}, "triggering_actor": {"login": "maintainer", "id": 42}},
        "repos/MC-and-his-Agents/Loom/actions/workflows/11": {"id": 11, "path": adapter.TRUSTED_WORKFLOW_PATH, "state": "active"},
        "repos/MC-and-his-Agents/Loom/collaborators/maintainer/permission": {"permission": "write", "user": {"login": "maintainer", "id": 42}},
        "repos/MC-and-his-Agents/Loom/commits/" + "a" * 40: {"sha": "a" * 40},
    }
    mapping.update(overrides)

    def read_json(_root: Path, path: str):
        return (mapping[path], []) if path in mapping else (None, [f"unexpected path: {path}"])

    return adapter.resolve_acceptance(
        ROOT,
        "MC-and-his-Agents/Loom/issue/225",
        7,
        now=NOW,
        read_json=read_json,
        read_bytes=lambda _root, _path: (archive, []),
    )


def main() -> int:
    adapter = load_adapter()
    local = adapter.evaluate_acceptance(fixture("passed-live-readonly.json"), now=NOW)
    assert_result(local, outcome="block", verdict="blocked")
    if local["product_acceptance"]["trusted"] is not False:
        raise AssertionError("repo-authored acceptance JSON must not self-assert passed")
    passed = resolve(adapter, fixture("passed-live-readonly.json"))
    assert_result(passed, outcome="pass", verdict="passed")
    if passed["product_acceptance"]["trusted"] is not True or passed["product_acceptance"]["owns_lifecycle_closure"] is not False:
        raise AssertionError("resolved acceptance must be trusted without owning lifecycle closure")
    for name in ("fixture-insufficient.json", "blocked-write-boundary.json", "stale-live-readonly.json"):
        assert_result(resolve(adapter, fixture(name)), outcome="block", verdict="blocked")
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
