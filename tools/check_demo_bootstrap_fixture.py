#!/usr/bin/env python3
"""Check the demo bootstrap fixture without rewriting the stable fixture."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_IGNORES = {
    ".loom/runtime",
    ".loom/tmp",
    ".loom/cache",
    "__pycache__",
}


def relative_to_root(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def ignored(path: Path, root: Path, ignored_relatives: set[str]) -> bool:
    relative = relative_to_root(path, root)
    parts = set(path.relative_to(root).parts)
    if bool(parts & ignored_relatives):
        return True
    return any(relative == ignored or relative.startswith(f"{ignored}/") for ignored in ignored_relatives)


def compare_trees(expected: Path, actual: Path, ignored_relatives: set[str]) -> list[str]:
    differences: list[str] = []

    expected_paths = {
        relative_to_root(path, expected)
        for path in expected.rglob("*")
        if not ignored(path, expected, ignored_relatives)
    }
    actual_paths = {
        relative_to_root(path, actual)
        for path in actual.rglob("*")
        if not ignored(path, actual, ignored_relatives)
    }

    for relative in sorted(expected_paths - actual_paths):
        differences.append(f"missing generated path: {relative}")
    for relative in sorted(actual_paths - expected_paths):
        differences.append(f"unexpected generated path: {relative}")

    for relative in sorted(expected_paths & actual_paths):
        expected_path = expected / relative
        actual_path = actual / relative
        if expected_path.is_dir() or actual_path.is_dir():
            if expected_path.is_dir() != actual_path.is_dir():
                differences.append(f"path type differs: {relative}")
            continue
        if expected_path.is_symlink() or actual_path.is_symlink():
            if expected_path.is_symlink() != actual_path.is_symlink() or os.readlink(expected_path) != os.readlink(actual_path):
                differences.append(f"symlink target differs: {relative}")
            continue
        if comparable_bytes(expected_path, relative) != comparable_bytes(actual_path, relative):
            differences.append(f"file content differs: {relative}")

    return differences


def comparable_bytes(path: Path, relative: str) -> bytes:
    if relative == ".loom/bootstrap/init-result.json":
        return canonical_init_result(path)
    return path.read_bytes()


def canonical_init_result(path: Path) -> bytes:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        governance_surface = payload.get("governance_surface")
        if isinstance(governance_surface, dict):
            # Host/CI visibility is intentionally outside the demo fixture drift
            # contract; compare stable bootstrap content without live host proof.
            governance_surface["github_control_plane"] = {"comparison": "ignored-host-dynamic"}
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    fixture = (repo_root / args.fixture).resolve()
    if not fixture.exists():
        print(f"demo bootstrap fixture is missing: {fixture}", file=sys.stderr)
        return 2

    ignored_relatives = set(DEFAULT_IGNORES)
    ignored_relatives.update(args.ignore)

    with tempfile.TemporaryDirectory(prefix=".loom-demo-bootstrap-check-", dir=repo_root) as tmp:
        generated = Path(tmp) / fixture.name
        shutil.copytree(fixture, generated, symlinks=True)
        command = [
            sys.executable,
            "tools/loom_init.py",
            "bootstrap",
            "--target",
            str(generated),
            "--scenario",
            "new",
            "--intent",
            "execution-control",
            "--intake",
            str(generated / ".loom/bootstrap/intake.snapshot.json"),
            "--write",
            "--force",
            "--install-pr-template",
            "--portable-output",
        ]
        result = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout,
            check=False,
        )
        if result.returncode != 0:
            print("demo bootstrap fixture check failed while rebuilding isolated fixture", file=sys.stderr)
            print(result.stdout, end="")
            print(result.stderr, end="", file=sys.stderr)
            return result.returncode

        differences = compare_trees(fixture, generated, ignored_relatives)
        if differences:
            print("demo bootstrap fixture drift detected:", file=sys.stderr)
            for difference in differences[: args.max_differences]:
                print(f"- {difference}", file=sys.stderr)
            if len(differences) > args.max_differences:
                print(f"- ... {len(differences) - args.max_differences} more differences", file=sys.stderr)
            print("run `make loom-demo-new-project-sync` to refresh the stable fixture intentionally.", file=sys.stderr)
            return 1

    print(f"demo bootstrap fixture: OK ({fixture.relative_to(repo_root)})")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Loom source repository root.")
    parser.add_argument("--fixture", default="examples/new-project", help="Stable demo fixture path.")
    parser.add_argument("--ignore", action="append", default=[], help="Additional repo-relative fixture paths to ignore.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Isolated bootstrap timeout in seconds.")
    parser.add_argument("--max-differences", type=int, default=40, help="Maximum drift entries to print.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
