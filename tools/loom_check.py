#!/usr/bin/env python3
"""Repo-local wrapper for the Loom source/distribution loom_check runtime."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from runtime_wrapper import run_shared_script


run_shared_script("loom_check.py")
