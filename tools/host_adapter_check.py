#!/usr/bin/env python3
"""Static checks for Loom agent harness support contracts."""

from __future__ import annotations

import sys
import json
import subprocess
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "adoption" / "host-adapter-matrix.md"
UNIFIED = ROOT / "docs" / "adoption" / "unified-install-experience.md"

HOSTS = ("Codex",)
UNSUPPORTED_HOSTS = ("Claude Code", "OpenCode", "Gemini", "Cursor")
def require_contains(path: Path, needles: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"missing {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    return [f"{path.relative_to(ROOT)} must mention `{needle}`" for needle in needles if needle not in text]


def main() -> int:
    errors: list[str] = []
    errors.extend(require_contains(MATRIX, HOSTS))
    matrix_text = MATRIX.read_text(encoding="utf-8") if MATRIX.exists() else ""
    errors.extend(f"{MATRIX.relative_to(ROOT)} must not advertise unsupported host `{host}`" for host in UNSUPPORTED_HOSTS if f"| {host} |" in matrix_text)
    errors.extend(
        require_contains(
            MATRIX,
            (
                "native/primary",
                "CLI-compatible",
                "unsupported",
                "external_result_sources",
                "legacy_repo_interop_host_adapters",
                "x-loom.host_adapter_version",
                "30 public commands",
                "fail closed",
            ),
        )
    )
    errors.extend(require_contains(UNIFIED, ("root CLI", "native", "plugins/loom/skills", "metadata-only", "loom-init")))
    for args, expected in ((["help", "--json"], "help"),):
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "loom.py"), *args],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            errors.append(f"loom {expected} did not emit JSON")
            continue
        if completed.returncode != 0 or payload.get("result") != "pass":
            errors.append(f"loom {expected} did not pass")
        if expected == "help" and (payload.get("command_count") != 30 or len(payload.get("commands", [])) != 30):
            errors.append("public implemented command surface must contain exactly 30 entries")
        if expected == "help" and (
            payload.get("protocol_type_count") != 12
            or len(payload.get("protocol_types", [])) != 12
            or payload.get("hidden_compatibility_count") != 0
        ):
            errors.append("public machine protocol must expose 12 owner types and zero hidden compatibility commands")
        if expected == "help" and any(
            command.get("protocol_type") not in payload.get("protocol_types", [])
            for command in payload.get("commands", [])
        ):
            errors.append("every public command must map to one public protocol owner type")
    retired = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "loom.py"), "host", "list", "--target", "/loom-must-not-read-target", "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        retired_payload = json.loads(retired.stdout)
    except json.JSONDecodeError:
        errors.append("retired loom host list did not emit JSON")
    else:
        primary = retired_payload.get("failure_envelope", {}).get("primary_cause", {})
        if retired.returncode == 0 or primary.get("id") != "unsupported_command_surface" or retired_payload.get("mutates") is not False:
            errors.append("retired loom host list did not fail closed before target or host access")
    if errors:
        print("agent harness support check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("agent harness support check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
