# Installing Loom for Codex

Enable Loom skills in Codex via native skill discovery. Clone the repository and symlink each generated public Loom skill package.

## Prerequisites

- Git
- Python `>=3.10`, recommended `3.11+`

## Installation

1. Clone Loom:

   ```bash
   git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
   ```

2. Create skill symlinks:

   ```bash
   mkdir -p ~/.agents/skills
   for skill in ~/.codex/loom/skills/loom-*; do
     ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
   done
   ```

3. Restart Codex.

Codex should start from `loom-init` after discovery reloads. The npm installer is not the Codex default path; it remains available for adapter-specific and single-skill helper flows.

## Verify

```bash
ls -la ~/.agents/skills/loom-init
ls ~/.agents/skills/loom-init/SKILL.md
ls ~/.agents/skills/loom-init/loom-package.json
```

## Update

```bash
cd ~/.codex/loom && git pull
```

The skills update through the symlink.

Run this from a Loom checkout when validating the generated install surface:

```bash
make skills-check
```

## Uninstall

```bash
rm ~/.agents/skills/loom-*
```

Optionally delete the clone:

```bash
rm -rf ~/.codex/loom
```
