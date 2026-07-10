#!/usr/bin/env python3
"""Resolve installed-skills runtime paths without assuming a repo-local layout."""

from __future__ import annotations

import os
import hashlib
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

GLOBAL_RUNTIME_PREFIXES = (".loom/runtime", ".loom/tmp")


def caller_path(caller_file: str) -> Path:
    return Path(caller_file).resolve()


def installed_skills_root(caller_file: str) -> Path | None:
    env_root = os.environ.get("LOOM_INSTALLED_SKILLS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    path = caller_path(caller_file)
    if path.parent.name == "scripts" and path.parent.parent.name == "shared":
        return path.parents[2]
    if path.parent.name == "scripts" and path.parents[2].name == "skills":
        return path.parents[2]
    if path.parent.name == "bin" and path.parent.parent.name == ".loom":
        repo_root = path.parents[2]
        skills_root = repo_root / "skills"
        if (skills_root / "shared").is_dir():
            return skills_root
    if path.parent.name == "tools":
        repo_root = path.parents[1]
        skills_root = repo_root / "skills"
        if (skills_root / "shared").is_dir():
            return skills_root
    return None


def source_repo_root() -> Path | None:
    env_root = os.environ.get("LOOM_SOURCE_REPO_ROOT")
    if not env_root:
        return None
    return Path(env_root).expanduser().resolve()


def repo_local_root(caller_file: str) -> Path | None:
    hinted = source_repo_root()
    if hinted is not None:
        return hinted

    path = caller_path(caller_file)
    if path.parent.name == "bin" and path.parent.parent.name == ".loom":
        return path.parents[2]
    return None


def workstation_root() -> Path:
    env_root = os.environ.get("LOOM_WORKSTATION_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.home().expanduser().resolve() / ".loom"


def canonical_git_remote(target_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=target_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def remote_hash(canonical_url: str) -> str | None:
    if not canonical_url:
        return None
    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def workstation_repo_id(target_root: Path) -> str:
    hash_value = remote_hash(canonical_git_remote(target_root))
    identity = f"{target_root.resolve()}\0{hash_value or 'missing'}"
    return "repo_" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def global_repo_cache_root(target_root: Path) -> Path:
    return workstation_root() / "repos" / workstation_repo_id(target_root)


def _normalized_repo_locator(locator: str | Path) -> str:
    return str(locator).strip().replace("\\", "/").rstrip("/")


def is_global_runtime_locator(locator: str | Path) -> bool:
    normalized = _normalized_repo_locator(locator)
    return normalized in GLOBAL_RUNTIME_PREFIXES or any(
        normalized.startswith(f"{prefix}/") for prefix in GLOBAL_RUNTIME_PREFIXES
    )


def global_runtime_path(target_root: Path, locator: str | Path) -> Path:
    normalized = _normalized_repo_locator(locator)
    if normalized == ".loom/runtime":
        return global_repo_cache_root(target_root) / "runtime"
    if normalized.startswith(".loom/runtime/"):
        return global_repo_cache_root(target_root) / "runtime" / normalized.removeprefix(".loom/runtime/")
    if normalized == ".loom/tmp":
        return global_repo_cache_root(target_root) / "tmp"
    if normalized.startswith(".loom/tmp/"):
        return global_repo_cache_root(target_root) / "tmp" / normalized.removeprefix(".loom/tmp/")
    raise ValueError(f"not a Loom runtime locator: {locator}")


def global_runtime_locator_for_path(target_root: Path, path: Path) -> str | None:
    resolved = path.resolve()
    cache_root = global_repo_cache_root(target_root).resolve()
    for directory, prefix in (("runtime", ".loom/runtime"), ("tmp", ".loom/tmp")):
        root = cache_root / directory
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        relative_text = relative.as_posix()
        return prefix if not relative_text else f"{prefix}/{relative_text}"
    return None


def bootstrap_runtime_root(caller_file: str) -> Path | None:
    path = caller_path(caller_file)
    if path.parent.name == "bin" and path.parent.parent.name == ".loom":
        return path.parent
    return None


def bootstrap_manifest_path(caller_file: str) -> Path | None:
    runtime_root = bootstrap_runtime_root(caller_file)
    if runtime_root is None:
        return None
    return runtime_root.parent / "bootstrap" / "manifest.json"


def shared_root(caller_file: str) -> Path:
    skills_root = installed_skills_root(caller_file)
    if skills_root is None:
        raise RuntimeError("installed skills root is not available for this runtime")
    shared = skills_root / "shared"
    if not shared.exists():
        raise RuntimeError(f"shared runtime root is missing: {shared}")
    return shared


def shared_script(caller_file: str, script_name: str) -> Path:
    script_path = shared_root(caller_file) / "scripts" / script_name
    if not script_path.exists():
        raise RuntimeError(f"shared runtime script is missing: {script_path}")
    return script_path


def shared_asset(caller_file: str, relative_path: str) -> Path:
    asset_path = shared_root(caller_file) / "assets" / relative_path
    if not asset_path.exists():
        raise RuntimeError(f"shared runtime asset is missing: {asset_path}")
    return asset_path


def shared_reference(caller_file: str, relative_path: str) -> Path:
    reference_path = shared_root(caller_file) / "references" / relative_path
    if not reference_path.exists():
        raise RuntimeError(f"shared reference is missing: {reference_path}")
    return reference_path


def registry_path(caller_file: str) -> Path:
    skills_root = installed_skills_root(caller_file)
    if skills_root is not None:
        return skills_root / "registry.json"

    path = caller_path(caller_file)
    if path.parent.name == "bin" and path.parent.parent.name == ".loom":
        return path.parent.parent / "skills" / "registry.json"

    raise RuntimeError("registry path is unavailable outside installed-skills or .loom/bin runtime")


def install_layout_path(caller_file: str) -> Path:
    skills_root = installed_skills_root(caller_file)
    if skills_root is None:
        raise RuntimeError("install layout path is unavailable outside installed-skills runtime")
    return skills_root / "install-layout.json"


def installed_skill_script(caller_file: str, skill_id: str) -> Path:
    skills_root = installed_skills_root(caller_file)
    if skills_root is None:
        raise RuntimeError("installed skills root is not available for skill entry lookup")
    script_path = skills_root / skill_id / "scripts" / f"{skill_id}.py"
    if not script_path.exists():
        raise RuntimeError(f"installed skill entry script is missing: {script_path}")
    return script_path
