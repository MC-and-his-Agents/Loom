"""Shared entrypoint resolver for packaged Loom tool wrappers."""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def candidate_skills_roots() -> list[Path]:
    candidates: list[Path] = []
    env_root = os.environ.get("LOOM_INSTALLED_SKILLS_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend(
        [
            REPO_ROOT / "skills",
            REPO_ROOT / "src" / "skills",
            REPO_ROOT / "plugins" / "loom" / "skills",
        ]
    )
    return candidates


def resolve_skills_root(script_name: str) -> Path:
    for root in candidate_skills_roots():
        if (root / "shared" / "scripts" / script_name).is_file():
            return root
    print(
        json.dumps(
            {
                "schema_version": "loom-runtime-wrapper/v1",
                "command": script_name,
                "result": "block",
                "failed_layer": "runtime-wrapper",
                "fail_closed_reason": "shared runtime script is missing",
                "missing_input": f"shared/scripts/{script_name}",
                "searched_roots": [str(root) for root in candidate_skills_roots()],
            },
            indent=2,
        ),
        file=sys.stderr,
    )
    raise SystemExit(1)


def run_shared_script(script_name: str) -> None:
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.dont_write_bytecode = True
    skills_root = resolve_skills_root(script_name)
    os.environ["LOOM_INSTALLED_SKILLS_ROOT"] = str(skills_root)
    if skills_root.resolve() == (REPO_ROOT / "skills").resolve():
        os.environ["LOOM_SOURCE_REPO_ROOT"] = str(REPO_ROOT)
        os.environ["LOOM_RUNTIME_SCENE"] = "repo-local-demo"
    else:
        os.environ.pop("LOOM_SOURCE_REPO_ROOT", None)
        os.environ.pop("LOOM_RUNTIME_SCENE", None)
    sys.path.insert(0, str(skills_root / "shared" / "scripts"))
    runpy.run_path(skills_root / "shared" / "scripts" / script_name, run_name="__main__")
