# Loom CLI / Installer Sunset Closeout Evidence

This file records the #1011 / #1003 closeout evidence for the move to a
single active `loom` CLI release line and the `loom-installer` sunset.

## Issue Tree Status

Checked on 2026-05-25:

| Issue | Status | Evidence |
| --- | --- | --- |
| #1004 | CLOSED / COMPLETED | Decision freeze recorded in issue comment. No repository change required. |
| #1005 | CLOSED / COMPLETED | PR #1053 merged. |
| #1006 | CLOSED / COMPLETED | PR #1056 merged. |
| #1007 | CLOSED / COMPLETED | PR #1058 merged. |
| #1008 | CLOSED / COMPLETED | PR #1059 merged. |
| #1009 | CLOSED / COMPLETED | PR #1060 merged; first CLI auto release completed. |
| #1010 | CLOSED / COMPLETED | PR #1061 merged; npm deprecate permission-block evidence recorded. |
| #1011 | OPEN at implementation time | This closeout item consumes the evidence above. |

## Implementation Chain

| Issue | PR | Head SHA | Squash Merge Commit | Merge Evidence |
| --- | --- | --- | --- | --- |
| #1005 | #1053 | `a72547468b0ea0ac6e97b638c6bb1aca84171ffb` | `3ec408d72e647eed85250eb7bdd6cdc5109b2bc4` | Installer publishing disabled. |
| #1006 | #1056 | `3ac4ab9b4a11c243e68f7cd22f0f9b1aab578dd2` | `f80c236e01c382193fe83197e7368964b19af4df` | Docs moved to the single CLI release line. |
| #1007 | #1058 | `d3766d2317ed25bfaedf37fccefdc61a8551acdd` | `b1e9465b41aa611d2ce9d08dc64e0ede07cb84af` | Release/version checks reject installer as active CLI evidence. |
| #1008 | #1059 | `d37fe95b1d56570357f6194292709533c9183453` | `f145673a3e535b345c47997a33bcf5385d7b879f` | `loom-cli-release` supports main-push publishing. |
| #1009 | #1060 | `f783e4cd180b144594c3b9a3488afdc61ecf89a9` | `a86c08fa0f14c755f6b0a0b949768b0ea1afe683` | `VERSION` bumped to `v0.13.0`; CLI release published. |
| #1010 | #1061 | `27008fcafe858eeaaa4b829d32f56a1c519d911b` | `93066b9e6705780ea0a4d053af8eefe7b323186a` | npm deprecate permission block and owner action recorded. |

All listed PRs passed their required PR checks before merge. Merge commit checks
were consumed for each implementation batch; #1010 main run `26420293852`
passed after merge.

## CLI Release Evidence

- Root `VERSION`: `v0.13.0`.
- `loom-cli-release` push run: `26418832058`, status `success`, event `push`,
  head SHA `a86c08fa0f14c755f6b0a0b949768b0ea1afe683`.
- Git tag: `v0.13.0`.
- Tag target: `a86c08fa0f14c755f6b0a0b949768b0ea1afe683`.
- GitHub Release: `Loom CLI v0.13.0`.
- Release URL: https://github.com/MC-and-his-Agents/Loom/releases/tag/v0.13.0
- Published at: `2026-05-25T20:37:43Z`.

Judgment: the first `loom` CLI automatic release for this issue tree is
complete, and its tag points at the #1009 PR squash merge commit.

## Installer Sunset Evidence

Checked on 2026-05-25:

```sh
npm view @mc-and-his-agents/loom-installer version deprecated --json
```

Observed output:

```json
"0.1.119"
```

Interpretation: npm `latest` remains `0.1.119`; no deprecation metadata was
returned by this read.

The highest installer tag remains:

```text
loom-installer-v0.1.119
```

GitHub Releases still show `loom-installer v0.1.119` as the latest installer
release, while `Loom CLI v0.13.0` is the latest overall release.

#1010 recorded the npm permission block:

```text
npm error code E401
npm error 401 Unauthorized - GET https://registry.npmjs.org/-/whoami
```

Required owner action remains:

```sh
npm deprecate @mc-and-his-agents/loom-installer@"*" "Deprecated: use the Loom CLI GitHub release line instead."
```

Judgment: `loom-installer` is no longer an active or automatic release line in
this repository, and no installer npm publish, `loom-installer-v*` tag, or
installer GitHub Release advanced during #1003.
