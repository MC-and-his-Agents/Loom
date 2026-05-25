# WI-897 Plan

1. Bind the formal worktree, branch, and fact chain to `WI-897`.
2. Record the three local sample surfaces for WebEnvoy, Syvert, and HotCP.
3. Add a versioned fixture that preserves the three sample shapes without
   depending on mutable neighboring repositories.
4. Extend `tools/check_cli_contract.py` so the fixture is mechanically checked
   with the CLI-first migration commands.
5. Add a CLI-first legacy migration playbook for operator consumption.
6. Add validation and release judgment evidence for #897 and #996 consumption.
7. Validate with CLI, version, installer, adoption, shadow parity, PR gate, and
   full repository checks before merge.
