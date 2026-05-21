#!/usr/bin/env python3
"""Compile Python files without writing bytecode into the repository tree."""

from __future__ import annotations

import argparse
import glob
import hashlib
import py_compile
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def has_glob_magic(pattern: str) -> bool:
    return any(character in pattern for character in "*?[")


def expand_inputs(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        matches = [Path(match) for match in glob.glob(pattern)] if has_glob_magic(pattern) else [Path(pattern)]
        if not matches:
            raise FileNotFoundError(f"`{pattern}` did not match any files")
        for match in matches:
            path = match if match.is_absolute() else REPO_ROOT / match
            if not path.exists():
                raise FileNotFoundError(f"`{match}` does not exist")
            if not path.is_file():
                raise ValueError(f"`{match}` is not a file")
            if path.suffix != ".py":
                raise ValueError(f"`{match}` is not a Python file")
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                paths.append(resolved)
    return paths


def cache_path_for(source: Path, cache_root: Path) -> Path:
    digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:16]
    return cache_root / f"{source.stem}-{digest}.pyc"


def compile_files(paths: list[Path]) -> None:
    with tempfile.TemporaryDirectory(prefix="loom-pycompile-") as tmp:
        cache_root = Path(tmp)
        for source in paths:
            py_compile.compile(
                str(source),
                cfile=str(cache_path_for(source, cache_root)),
                doraise=True,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Python files or shell-style glob patterns to compile")
    args = parser.parse_args()
    try:
        paths = expand_inputs(args.paths)
        compile_files(paths)
    except (FileNotFoundError, ValueError, py_compile.PyCompileError) as exc:
        print(f"py_compile_clean: {exc}", file=sys.stderr)
        return 1
    print(f"py_compile_clean: OK ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
