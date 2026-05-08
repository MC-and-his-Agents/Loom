# WI-566 Plan

## Steps

1. Add the dynamic tool handshake contract and status surface docs.
2. Extend governance surface to derive `tool_availability` from companion declarations.
3. Extend flow/status output to expose applicable tool availability and required-tool blocking semantics.
4. Add unsupported, unavailable, and failed tool fixtures to `loom_check`.
5. Regenerate skills surfaces and demo bootstrap artifacts.
6. Run targeted smoke commands and `make check`.
7. Record spec/implementation review evidence, open the #566 PR, merge, verify main, and close #567-#570 through the batch PR.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/governance_surface.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_status.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_flow.py flow review --target . --item WI-566`
- `python3 tools/loom_flow.py flow merge-ready --target . --item WI-566`
- `python3 tools/loom_status.py --target . --item WI-566`
- `python3 tools/loom_check.py`
- `make check`
