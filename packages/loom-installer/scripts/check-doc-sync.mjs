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
      'npm install -g @mc-and-his-agents/loom',
      'loom host install --host codex --mode plugin --target . --apply --json',
      '`loom-installer` is not part of the primary install journey',
      'Loom CLI release surface',
      'loom-installer deprecated legacy line',
      'src/skills/',
      'docs/adoption/unified-install-experience.md',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'README.zh-CN.md',
    needles: [
      'agent-first project operating layer',
      'npm install -g @mc-and-his-agents/loom',
      'loom host install --host codex --mode plugin --target . --apply --json',
      '`loom-installer` 不属于 primary install journey',
      'Loom CLI 发布面',
      'loom-installer deprecated legacy line',
      'src/skills/',
      'docs/adoption/unified-install-experience.md',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'docs/adoption/codex-install.md',
    needles: [
      'The npm installer is not the Codex default path',
      'npm install -g @mc-and-his-agents/loom',
      'loom host install --host codex --mode plugin --target . --apply --json',
      'loom host verify --host codex --mode plugin --target . --json',
      'CLI-managed payloads',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'generated, checked-in Loom skills install surface',
      'src/skills/',
      'loom-package.json',
      'unique root entry',
      'Advanced / Compatibility',
      'npx @mc-and-his-agents/loom-installer add skill <skill-id>',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'skills/README.zh-CN.md',
    needles: [
      '生成且提交的 skills install surface',
      'src/skills/',
      'loom-package.json',
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
      'upstream `plugins/loom/.codex-plugin/` manifest + generated root `skills/`',
      'distribution_layer',
      'version_context',
      'repo-scoped `<target>/.agents/skills/<skill-id>/`',
      'main 分支是 validation truth source',
      '最后一个 active installer baseline 是 `@mc-and-his-agents/loom-installer` `0.1.119` / `loom-installer-v0.1.119`',
    ],
  },
  {
    path: 'docs/adoption/version-authority-map.md',
    needles: [
      'Versions are not globally synchronized',
      'Loom CLI release candidate',
      'Deprecated installer legacy artifact',
      'plugin surface version',
      'skill_package_version',
    ],
  },
  {
    path: 'docs/adoption/loom-cli-release-surface.md',
    needles: [
      'The `loom` CLI release line is the primary release line',
      'GitHub `v*` tag and GitHub Release',
      'Installer npm state is never publish evidence for this judgment',
      '`loom-installer` is a deprecated legacy artifact',
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
      'The default Loom install model is the root `loom` CLI package',
      'deprecated legacy artifact kept only',
      'payload is generated from the canonical `plugins/loom/.codex-plugin/` manifest and the checked-in generated `skills/` install surface',
      'distribution_layer',
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
      'Loom 默认安装模型是根 `loom` CLI package',
      'deprecated legacy artifact，只为历史兼容证据',
      'canonical `plugins/loom/.codex-plugin/` manifest 与已提交的生成 `skills/` install surface',
      'distribution_layer',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'docs/adoption/unified-install-experience.md',
    needles: ['root CLI install', 'src/skills/', 'skills/<skill-id>', 'loom-init', 'single-skill'],
  },
  {
    path: 'docs/adoption/single-skill-contract.md',
    needles: ['loom-package.json', '.loom-runtime/', 'fail closed', 'make skills-check'],
  },
  {
    path: 'docs/adoption/version-authority-map.md',
    needles: ['Versions are not globally synchronized', 'Loom CLI release candidate', 'Deprecated installer legacy artifact', 'plugin surface version', 'skill_package_version'],
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
