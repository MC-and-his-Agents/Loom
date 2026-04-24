import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { execFileSync, spawnSync } from 'node:child_process';
import { detectHosts, parseCli, resolveEnvironment, runInstaller, selectHost } from '../src/index.js';
import type { ParsedCommand } from '../src/index.js';

function fixtureRoot(): string {
  return mkdtempSync(join(tmpdir(), 'loom-installer-'));
}

function packageRoot(): string {
  return process.cwd();
}

function resolveTestPython(): string {
  if (process.env.LOOM_INSTALLER_TEST_PYTHON_BIN) {
    return process.env.LOOM_INSTALLER_TEST_PYTHON_BIN;
  }
  for (const candidate of ['python3.11', 'python3.12', 'python3.10']) {
    const result = spawnSync(candidate, ['-c', 'import sys; print(sys.version_info[:2])'], { encoding: 'utf8' });
    if (result.status === 0) {
      return candidate;
    }
  }
  throw new Error('tests require python3.10+; set LOOM_INSTALLER_TEST_PYTHON_BIN');
}

function prepareEnv(base: string): NodeJS.ProcessEnv {
  const home = join(base, 'home');
  mkdirSync(home, { recursive: true });
  return {
    ...process.env,
    HOME: home,
    CODEX_HOME: join(home, '.codex'),
    CLAUDE_CONFIG_DIR: join(home, '.claude'),
    LOOM_INSTALLER_PYTHON_BIN: resolveTestPython(),
  };
}

function writeCodexMarketplace(repoRoot: string, marketplace: unknown): string {
  const marketplacePath = join(repoRoot, '.agents', 'plugins', 'marketplace.json');
  mkdirSync(join(repoRoot, '.agents', 'plugins'), { recursive: true });
  writeFileSync(marketplacePath, JSON.stringify(marketplace, null, 2));
  return marketplacePath;
}

function writeFakeClaude(binDir: string, logPath: string): string {
  const scriptPath = join(binDir, 'claude');
  writeFileSync(
    scriptPath,
    `#!/bin/sh\nset -eu\nprintf '%s\\n' "$*" >> ${JSON.stringify(logPath)}\nif [ "$1" = "--version" ]; then\n  echo '2.1.0'\n  exit 0\nfi\nif [ "$1" = "plugin" ] && [ "$2" = "list" ] && [ "$3" = "--json" ]; then\n  echo '[{"name":"loom"}]'\n  exit 0\nfi\nexit 0\n`,
    { mode: 0o755 },
  );
  return scriptPath;
}

test('detectHosts and selectHost fail closed on conflicts', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  mkdirSync(envSource.CLAUDE_CONFIG_DIR!, { recursive: true });
  const env = resolveEnvironment(envSource);
  assert.deepEqual(detectHosts(env), ['codex', 'claude']);
  assert.throws(() => selectHost('auto', env), /both Codex and Claude/);
});

test('parseCli supports plugin and skill flows', () => {
  const plugin = parseCli(['add', 'plugin', '--host', 'codex', '--json']);
  assert.equal(plugin.mode, 'plugin');
  assert.equal(plugin.options.host, 'codex');
  assert.equal(plugin.options.json, true);

  const skill = parseCli(['add', 'skill', 'loom-review', '--target', '/tmp/repo']);
  assert.equal(skill.mode, 'skill');
  assert.equal(skill.skillId, 'loom-review');
  assert.equal(skill.options.target, '/tmp/repo');
});

test('payload manifest excludes python cache artifacts', () => {
  const manifest = JSON.parse(readFileSync(join(packageRoot(), 'payload', 'manifest.json'), 'utf8'));
  assert.equal(Array.isArray(manifest.files), true);
  assert.equal(manifest.files.some((entry: { path: string }) => entry.path.includes('__pycache__') || entry.path.endsWith('.pyc')), false);
});

test('payload manifest tracks loom-spec-review as a public skill', () => {
  const manifest = JSON.parse(readFileSync(join(packageRoot(), 'payload', 'manifest.json'), 'utf8'));
  assert.equal(Array.isArray(manifest.skills), true);
  assert.equal(
    manifest.skills.some((entry: { id: string; relative_path: string }) => entry.id === 'loom-spec-review' && entry.relative_path === 'skills/loom-spec-review'),
    true,
  );
});

test('payload bundles shared references and runtime paths required by install layout', () => {
  assert.equal(
    existsSync(join(packageRoot(), 'payload', 'plugin', 'loom', 'skills', 'shared', 'references', 'harness', 'execution-context.md')),
    true,
  );
  assert.equal(
    existsSync(
      join(
        packageRoot(),
        'payload',
        'skills',
        'loom-init',
        '.loom-runtime',
        'shared',
        'references',
        'templates',
        'implementation-contract-template.md',
      ),
    ),
    true,
  );
  assert.equal(
    existsSync(
      join(packageRoot(), 'payload', 'skills', 'loom-init', '.loom-runtime', 'loom-spec-review', 'references', 'input-signals.md'),
    ),
    true,
  );
});

test('package bin target matches the built CLI entrypoint', () => {
  const packageJson = JSON.parse(readFileSync(join(packageRoot(), 'package.json'), 'utf8'));
  const cliEntry = packageJson.bin?.['loom-installer'];
  assert.equal(typeof cliEntry, 'string');
  assert.equal(cliEntry, 'dist/src/cli.js');
  assert.equal(existsSync(join(packageRoot(), cliEntry)), true);
  assert.deepEqual(packageJson.repository, {
    type: 'git',
    url: 'https://github.com/MC-and-his-Agents/Loom.git',
    directory: 'packages/loom-installer',
  });
});

test('codex plugin install writes marketplace entry', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  const parsed: ParsedCommand = {
    mode: 'plugin',
    options: {
      host: 'codex',
      target: repoRoot,
      force: false,
      json: false,
    },
  };
  const result = runInstaller(parsed, envSource, packageRoot());
  const marketplace = JSON.parse(readFileSync(join(repoRoot, '.agents', 'plugins', 'marketplace.json'), 'utf8'));
  assert.equal(result.host, 'codex');
  assert.equal(marketplace.plugins[0].name, 'loom');
  assert.equal(marketplace.plugins[0].source.path, './plugins/loom');
});

test('codex plugin install fails closed on marketplace conflicts without force', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  writeCodexMarketplace(repoRoot, {
    name: 'custom-marketplace',
    plugins: [
      {
        name: 'loom',
        source: {
          source: 'local',
          path: './plugins/not-loom',
        },
      },
    ],
  });

  const parsed: ParsedCommand = {
    mode: 'plugin',
    options: {
      host: 'codex',
      target: repoRoot,
      force: false,
      json: false,
    },
  };

  assert.throws(() => runInstaller(parsed, envSource, packageRoot()), /already declares loom from a different path/);
});

test('codex plugin install lets --force take over conflicting marketplace entry', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  writeCodexMarketplace(repoRoot, {
    name: 'custom-marketplace',
    plugins: [
      {
        name: 'loom',
        source: {
          source: 'local',
          path: './plugins/not-loom',
        },
      },
    ],
  });

  const parsed: ParsedCommand = {
    mode: 'plugin',
    options: {
      host: 'codex',
      target: repoRoot,
      force: true,
      json: false,
    },
  };

  const result = runInstaller(parsed, envSource, packageRoot());
  const marketplace = JSON.parse(readFileSync(join(repoRoot, '.agents', 'plugins', 'marketplace.json'), 'utf8'));
  assert.equal(result.mode, 'plugin');
  assert.equal(marketplace.plugins[0].source.path, './plugins/loom');
});

test('codex skill install writes skills.config entry', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  writeFileSync(join(envSource.CODEX_HOME!, 'config.toml'), 'model = "gpt-5"\n', 'utf8');

  const parsed: ParsedCommand = {
    mode: 'skill',
    skillId: 'loom-review',
    options: {
      host: 'codex',
      target: repoRoot,
      force: false,
      json: false,
    },
  };
  const result = runInstaller(parsed, envSource, packageRoot());
  const config = readFileSync(join(envSource.CODEX_HOME!, 'config.toml'), 'utf8');
  assert.equal(result.mode, 'skill');
  assert.match(config, /\[\[skills\.config\]\]/);
  assert.match(config, /loom-review\/SKILL\.md/);
  assert.match(config, /enabled = true/);
});

test('codex skill install fails closed on conflicting skills.config entry without force', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  writeFileSync(
    join(envSource.CODEX_HOME!, 'config.toml'),
    [
      'model = "gpt-5"',
      '',
      '[[skills.config]]',
      'path = "/tmp/other/loom-review/SKILL.md"',
      'enabled = true',
      '',
    ].join('\n'),
    'utf8',
  );

  const parsed: ParsedCommand = {
    mode: 'skill',
    skillId: 'loom-review',
    options: {
      host: 'codex',
      target: repoRoot,
      force: false,
      json: false,
    },
  };

  assert.throws(() => runInstaller(parsed, envSource, packageRoot()), /already has loom-review from a different path/);
});

test('codex skill install lets --force take over conflicting skills.config entry', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  writeFileSync(
    join(envSource.CODEX_HOME!, 'config.toml'),
    [
      'model = "gpt-5"',
      '',
      '[[skills.config]]',
      'path = "/tmp/other/loom-review/SKILL.md"',
      'enabled = true',
      '',
    ].join('\n'),
    'utf8',
  );

  const parsed: ParsedCommand = {
    mode: 'skill',
    skillId: 'loom-review',
    options: {
      host: 'codex',
      target: repoRoot,
      force: true,
      json: false,
    },
  };

  const result = runInstaller(parsed, envSource, packageRoot());
  const config = readFileSync(join(envSource.CODEX_HOME!, 'config.toml'), 'utf8');
  assert.equal(result.mode, 'skill');
  assert.doesNotMatch(config, /\/tmp\/other\/loom-review\/SKILL\.md/);
  assert.match(config, /loom-review\/SKILL\.md/);
});

test('single-skill installs stay scoped to the named skill for codex', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  const parsed: ParsedCommand = {
    mode: 'skill',
    skillId: 'loom-init',
    options: {
      host: 'codex',
      target: repoRoot,
      force: false,
      json: false,
    },
  };

  const result = runInstaller(parsed, envSource, packageRoot());
  assert.equal(result.mode, 'skill');
  assert.match(result.warnings[0] ?? '', /only the named skill, not the full Loom plugin surface/);
  assert.equal(existsSync(join(repoRoot, 'plugins', 'loom')), false);
  assert.equal(existsSync(join(repoRoot, '.agents', 'plugins', 'marketplace.json')), false);
});

test('claude plugin install assembles marketplace and calls claude CLI', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CLAUDE_CONFIG_DIR!, { recursive: true });
  const repoRoot = join(base, 'repo');
  const binDir = join(base, 'bin');
  const logPath = join(base, 'claude.log');
  mkdirSync(repoRoot, { recursive: true });
  mkdirSync(binDir, { recursive: true });
  envSource.LOOM_INSTALLER_CLAUDE_BIN = writeFakeClaude(binDir, logPath);

  const parsed: ParsedCommand = {
    mode: 'plugin',
    options: {
      host: 'claude',
      target: repoRoot,
      force: false,
      json: false,
    },
  };
  const result = runInstaller(parsed, envSource, packageRoot());
  const marketplace = JSON.parse(readFileSync(join(repoRoot, '.claude', 'marketplaces', 'loom-local', '.claude-plugin', 'marketplace.json'), 'utf8'));
  const pluginManifest = JSON.parse(readFileSync(join(repoRoot, '.claude', 'marketplaces', 'loom-local', 'plugins', 'loom', '.claude-plugin', 'plugin.json'), 'utf8'));
  const log = readFileSync(logPath, 'utf8');
  assert.equal(result.host, 'claude');
  assert.equal(marketplace.name, 'loom-local');
  assert.equal(pluginManifest.name, 'loom');
  assert.match(log, /plugin marketplace add/);
  assert.match(log, /plugin install loom@loom-local/);
});

test('single-skill installs stay scoped to the named skill for claude', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CLAUDE_CONFIG_DIR!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  const parsed: ParsedCommand = {
    mode: 'skill',
    skillId: 'loom-init',
    options: {
      host: 'claude',
      target: repoRoot,
      force: false,
      json: false,
    },
  };

  const result = runInstaller(parsed, envSource, packageRoot());
  assert.equal(result.mode, 'skill');
  assert.match(result.warnings[0] ?? '', /does not expose the full Loom plugin surface/);
  assert.equal(existsSync(join(repoRoot, '.claude', 'skills', 'loom-init', 'SKILL.md')), true);
  assert.equal(existsSync(join(repoRoot, '.claude', 'marketplaces', 'loom-local')), false);
});

test('cli emits structured json on success', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  const output = execFileSync(
    process.execPath,
    ['dist/src/cli.js', 'add', 'plugin', '--host', 'codex', '--target', repoRoot, '--json'],
    {
      cwd: packageRoot(),
      env: envSource,
      encoding: 'utf8',
    },
  );
  const payload = JSON.parse(output);
  assert.equal(payload.host, 'codex');
  assert.equal(payload.mode, 'plugin');
  assert.equal(payload.fail_closed_reason, null);
});
