# WI-862 Plan

## Steps

1. Add Story Business Confirmation to story-intake governance and evidence mapping.
2. Update spec / plan / Work Item / review / gate references so confirmed or not-applicable story semantics are the only delivery-consumable states.
3. Update story scaffold templates with out-of-scope and confirmation fields.
4. Update `loom-story` source contracts, routing signals, runtime flow payload, and checker fixtures.
5. Regenerate the checked-in `skills/` install surface.
6. Refresh `examples/new-project` runtime carriers from the updated install surface.
7. Validate generated surface, compile cleanliness, routing, story flow payload, demo bootstrap, version surface, host adapter, and `loom_check`.
8. Run spec review, implementation review, merge-ready validation, PR checks, controlled merge, and closeout.

## Validation

- `python3 tools/skills_surface.py check`
- `python3 tools/py_compile_clean.py tools/loom_flow.py tools/loom_init.py tools/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_init.py skills/shared/scripts/loom_check.py skills/shared/scripts/loom_story_carriers.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_init.py src/skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_story_carriers.py`
- `python3 tools/loom_init.py route --target examples/new-project --task '请确认 story 业务语义或根据修订意见回到 story shaping'`
- `python3 tools/loom_flow.py flow story --target examples/new-project`
- `python3 tools/loom_init.py bootstrap --target examples/new-project --scenario new --intent execution-control --write --force --verify --install-pr-template --portable-output`
- `python3 tools/version_surface_check.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py`
- PR checks
