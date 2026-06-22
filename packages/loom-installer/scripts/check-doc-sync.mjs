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
      'loom host install --host codex --scope user --apply --json',
      'CLI-first',
      'metadata-only repository adoption',
      'global `loom` command',
      'Codex user-level plugin',
      'Work Item',
      'gate chain',
      'docs/adoption/unified-install-experience.md',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'README.zh-CN.md',
    needles: [
      '智能体优先的项目运营层',
      'npm install -g @mc-and-his-agents/loom',
      'loom host install --host codex --scope user --apply --json',
      '命令行优先设计',
      '仅元数据的仓库采用',
      '全局 `loom` 命令',
      'Codex 用户级插件',
      '工作项',
      '固定门控链',
      'docs/adoption/unified-install-experience.md',
      '[英文版本](./README.md)',
    ],
  },
  {
    path: 'docs/adoption/codex-install.md',
    needles: [
      'The npm installer is not the Codex default path',
      'npm install -g @mc-and-his-agents/loom',
      'loom host install --host codex --scope user --apply --json',
      'loom host verify --host codex --target . --json',
      'CLI-managed payloads',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'generated, checked-in Loom skills install surface',
      'src/skills/',
      'Codex user plugin payload',
      'not a self-contained single-skill',
      'loom-package.json',
      '.loom-runtime/',
      'unique root entry',
      'plugins/loom/skills/',
      'Target repositories use metadata-only adoption',
      '[中文版本](./README.zh-CN.md)',
    ],
  },
  {
    path: 'skills/README.zh-CN.md',
    needles: [
      'generated skills mirror',
      'src/skills/',
      'Codex 用户级 plugin',
      'single-skill package',
      'loom-package.json',
      '.loom-runtime/',
      '唯一的 root entry',
      'plugins/loom/skills/',
      'metadata-only adoption',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'skills/distribution-and-adapter-contract.md',
    needles: [
      'Codex 用户级 plugin payload',
      '`plugins/loom/.codex-plugin/plugin.json`',
      '`plugins/loom/skills/`',
      '`plugins/loom/skills/registry.json`',
      'single-skill package artifacts',
      '用户级 plugin 安装不写目标仓库',
      'plugin payload 不含 single-skill package artifacts',
    ],
  },
  {
    path: 'docs/adoption/version-authority-map.md',
    needles: [
      'Versions are not globally synchronized',
      'Loom CLI release candidate',
      'Deprecated installer legacy artifact',
      'plugin surface version',
      'Plugin payload version',
      'plugin_payload_hash',
      'single-skill install is not a current Loom distribution surface',
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
      'Codex user plugin payload from the',
      'plugins/loom/skills/',
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
      'Codex 用户级 plugin payload',
      'plugins/loom/skills/',
      'distribution_layer',
      '[English version](./README.md)',
    ],
  },
  {
    path: 'docs/adoption/unified-install-experience.md',
    needles: ['root CLI install', 'src/skills/', 'Codex user-level plugin payload', 'loom-init', 'single-skill'],
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
