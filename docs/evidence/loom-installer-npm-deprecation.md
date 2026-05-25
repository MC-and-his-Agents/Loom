# loom-installer npm Deprecation Evidence

This file records #1010 evidence for the deprecated
`@mc-and-his-agents/loom-installer` package.

## Current Registry State

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

## Permission Check

Checked on 2026-05-25:

```sh
npm whoami
```

Observed result:

```text
npm error code E401
npm error 401 Unauthorized - GET https://registry.npmjs.org/-/whoami
```

Judgment: this environment does not have npm registry identity sufficient to
run `npm deprecate`.

## Required Owner Action

An npm owner for `@mc-and-his-agents/loom-installer` must run:

```sh
npm deprecate @mc-and-his-agents/loom-installer@"*" "Deprecated: use the Loom CLI GitHub release line instead."
```

Then re-read:

```sh
npm view @mc-and-his-agents/loom-installer version deprecated --json
```

## Installer Non-Advancement

The last active installer baseline remains:

- npm package: `@mc-and-his-agents/loom-installer` `0.1.119`
- GitHub tag/release: `loom-installer-v0.1.119`

#1010 does not publish npm, bump the installer package version, create a new
`loom-installer-v*` tag, or create an installer GitHub Release.
