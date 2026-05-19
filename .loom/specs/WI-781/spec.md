# WI-781 Spec

## Problem

Adoption can create stable `.loom` carriers while a target repository has a blanket `.loom` gitignore rule. File-existence checks can pass, but Git cannot see the carriers, leaving work items, progress, review, status, specs, and bootstrap evidence uncommittable.

## Required Behavior

- Bootstrap must detect blanket `.loom` ignore patterns that hide stable Loom carriers, including `.loom`, `.loom/`, `.loom/*`, `.loom/**`, `/.loom`, `/.loom/`, `/.loom/*`, and `/.loom/**`.
- Write mode must fail closed by default when a blanket `.loom` ignore exists.
- `--repair-gitignore` must remove blanket `.loom` ignore patterns and preserve only scratch ignores for `.loom/runtime/`, `.loom/tmp/`, and `.loom/cache/`.
- `verify` must fail if a repository later reintroduces a blanket `.loom` ignore.
- Stable Loom carriers must remain Git-visible after repair.
- Runtime, tmp, and cache scratch paths must remain ignored.
- Generated skills surfaces and example bootstrap outputs must be refreshed from source truth.

## Non-goals

- Do not change attach-only host truth ownership; #784 owns that boundary.
- Do not add the broader stable-carrier verification contract; #782 owns that.
- Do not promote downstream repo-specific guardian, project, review, or release rules into Loom core.
