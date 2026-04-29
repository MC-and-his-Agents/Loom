import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');

const requiredNeedles = [
  {
    path: 'README.md',
    needles: [
      'agent-first project operating layer',
      'Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/docs/adoption/codex-install.md',
      'npx @mc-and-his-agents/loom-installer add plugin --host codex',
      'Advanced / Compatibility',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'README.zh-CN.md',
    needles: [
      'agent-first project operating layer',
      'Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/docs/adoption/codex-install.md',
      'npx @mc-and-his-agents/loom-installer add plugin --host codex',
      '高级 / 兼容',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'docs/adoption/codex-install.md',
    needles: [
      'git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom',
      'ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"',
      'Restart Codex',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'canonical skills library',
      'unique root entry',
      'Advanced / Compatibility',
      'npx @mc-and-his-agents/loom-installer add skill <skill-id>',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'skills/README.zh-CN.md',
    needles: [
      'canonical skills library',
      '唯一的 root entry',
      'Advanced / Compatibility',
      'npx @mc-and-his-agents/loom-installer add skill <skill-id>',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'skills/distribution-and-adapter-contract.md',
    needles: [
      '@mc-and-his-agents/loom-installer',
      'upstream `plugins/loom/.codex-plugin/` manifest + canonical `skills/`',
      'repo-scoped `<target>/.agents/skills/<skill-id>/`',
      'main 分支是真相源',
      'publish 成功后再创建 `loom-installer-v<version>` git tag 与同名前缀的 GitHub Release',
    ],
  },
  {
    path: 'packages/loom-installer/README.md',
    needles: [
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`, recommended `3.11+`',
      'add plugin',
      'add skill <skill-id>',
      'payload is generated from the canonical `plugins/loom/.codex-plugin/` manifest and `skills/` sources',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'packages/loom-installer/README.zh-CN.md',
    needles: [
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      'add plugin',
      'add skill <skill-id>',
      'canonical `plugins/loom/.codex-plugin/` manifest 与 `skills/` 源',
      '[English version](./README.md)',
    ],
  },
];

function readRepoFile(relativePath) {
  return readFileSync(join(repoRoot, relativePath), 'utf8');
}

for (const entry of requiredNeedles) {
  if (!existsSync(join(repoRoot, entry.path))) {
    console.error(`doc sync check failed: missing ${entry.path}`);
    process.exit(1);
  }
  const content = readRepoFile(entry.path);
  for (const needle of entry.needles) {
    if (!content.includes(needle)) {
      console.error(`doc sync check failed: ${entry.path} is missing ${JSON.stringify(needle)}`);
      process.exit(1);
    }
  }
}

console.log('doc sync check: OK');
