#!/usr/bin/env python3
"""Repo-local aggregate CLI for Loom wrapper tools."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_ROOT = REPO_ROOT / "tools"

COMMAND_ROUTES: dict[str, tuple[str, tuple[str, ...]]] = {
    "init": ("loom_init.py", ()),
    "route": ("loom_init.py", ("route",)),
    "flow": ("loom_flow.py", ()),
    "review": ("loom_flow.py", ("review",)),
    "check": ("loom_check.py", ()),
}


def print_usage(stream) -> None:
    stream.write(
        "usage: loom <command> [args ...]\n\n"
        "Repo-local aggregate entry for existing Loom wrapper tools.\n\n"
        "commands:\n"
        "  init    pass through to tools/loom_init.py\n"
        "  route   shortcut for tools/loom_init.py route\n"
        "  flow    pass through to tools/loom_flow.py\n"
        "  review  shortcut for tools/loom_flow.py review\n"
        "  check   pass through to tools/loom_check.py\n\n"
        "examples:\n"
        "  python3 tools/loom.py init bootstrap --target examples/new-project --write\n"
        "  python3 tools/loom.py route --target examples/new-project --task \"请接手当前事项并恢复上下文后继续推进\"\n"
        "  python3 tools/loom.py flow review --target examples/new-project --item INIT-0001\n"
        "  python3 tools/loom.py review read --target examples/new-project --item INIT-0001\n"
        "  python3 tools/loom.py check\n"
    )


def dispatch(command: str, forwarded_args: list[str]) -> int:
    tool_name, prefix = COMMAND_ROUTES[command]
    tool_path = TOOLS_ROOT / tool_name
    if not tool_path.exists():
        print(f"loom: missing delegated tool: {tool_path}", file=sys.stderr)
        return 2
    completed = subprocess.run(
        [sys.executable, str(tool_path), *prefix, *forwarded_args],
        check=False,
    )
    return completed.returncode


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        print_usage(sys.stderr)
        return 2

    command = argv[1]
    if command in {"-h", "--help", "help"}:
        print_usage(sys.stdout)
        return 0

    if command not in COMMAND_ROUTES:
        print(f"loom: unknown command `{command}`", file=sys.stderr)
        print_usage(sys.stderr)
        return 2

    return dispatch(command, argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
