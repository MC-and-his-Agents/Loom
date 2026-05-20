import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
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
  assert.equal(plugin.operation, 'add');
  assert.equal(plugin.mode, 'plugin');
  assert.equal(plugin.options.host, 'codex');
  assert.equal(plugin.options.json, true);

  const skill = parseCli(['add', 'skill', 'loom-review', '--target', '/tmp/repo']);
  assert.equal(skill.operation, 'add');
  assert.equal(skill.mode, 'skill');
  assert.equal(skill.skillId, 'loom-review');
  assert.equal(skill.options.target, '/tmp/repo');

  const plan = parseCli(['upgrade-plan', 'plugin', '--host', 'codex', '--target', '/tmp/repo', '--json']);
  assert.equal(plan.operation, 'upgrade-plan');
  assert.equal(plan.mode, 'plugin');

  const verify = parseCli(['verify-upgrade', 'skill', 'loom-init', '--host', 'claude']);
  assert.equal(verify.operation, 'verify-upgrade');
  assert.equal(verify.mode, 'skill');
  assert.equal(verify.skillId, 'loom-init');
});

test('payload manifest excludes python cache artifacts', () => {
  const manifest = JSON.parse(readFileSync(join(packageRoot(), 'payload', 'manifest.json'), 'utf8'));
  assert.equal(Array.isArray(manifest.files), true);
  assert.equal(manifest.files.some((entry: { path: string }) => entry.path.includes('__pycache__') || entry.path.endsWith('.pyc')), false);
});

test('payload manifest tracks loom-spec-review as a public skill', () => {
  const manifest = JSON.parse(readFileSync(join(packageRoot(), 'payload', 'manifest.json'), 'utf8'));
  assert.equal(Array.isArray(manifest.skills), true);
  const skill = manifest.skills.find((entry: { id: string }) => entry.id === 'loom-spec-review');
  assert.equal(skill.relative_path, 'skills/loom-spec-review');
  assert.equal(skill.package_metadata, 'loom-package.json');
  assert.equal(skill.runtime_root, '.loom-runtime');
  assert.equal(typeof skill.skill_package_version, 'string');
  assert.equal(typeof skill.runtime_core_version, 'string');
  assert.equal(typeof manifest.version_context.repo_version, 'string');
  assert.equal(typeof manifest.version_context.installer_package_version, 'string');
  assert.equal(typeof manifest.version_context.plugin_surface_version, 'string');
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
  assert.equal(result.distribution_layer, 'host-adapter-plugin');
  assert.equal(result.version_context?.plugin_surface_version, '0.4.0');
  assert.equal(result.installed_status?.schema_version, 'loom-installed-surface-status/v1');
  assert.equal(result.installed_status?.runtime_state, 'ready');
  assert.equal(marketplace.plugins[0].name, 'loom');
  assert.equal(marketplace.plugins[0].source.path, './plugins/loom');
});

test('upgrade-plan reports current installed plugin without mutating target', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  runInstaller(
    {
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  const plan = runInstaller(
    {
      operation: 'upgrade-plan',
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  assert.equal(plan.operation, 'upgrade-plan');
  assert.equal(plan.status, 'planned');
  assert.equal(plan.installed_status?.upgrade_eligibility, 'current');
  assert.deepEqual(plan.changed_paths, []);
  assert.deepEqual(plan.drift, []);
  assert.equal(plan.rehearsal?.mutates_target, false);
  assert.equal(plan.rollback_path, null);
});

test('upgrade-plan reports available payload and changed paths', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  runInstaller(
    {
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );
  const statusPath = join(repoRoot, 'plugins', 'loom', '.loom-install-status.json');
  const status = JSON.parse(readFileSync(statusPath, 'utf8'));
  status.version_context.installer_package_version = '0.0.0';
  writeFileSync(statusPath, `${JSON.stringify(status, null, 2)}\n`, 'utf8');
  writeFileSync(join(repoRoot, 'plugins', 'loom', 'skills', 'registry.json'), '{"registry_version":"0.0.0"}\n', 'utf8');

  const plan = runInstaller(
    {
      operation: 'upgrade-plan',
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  assert.equal(plan.status, 'planned');
  assert.equal(plan.installed_status?.upgrade_eligibility, 'upgrade-available');
  assert.equal(plan.changed_paths?.includes(join('plugins', 'loom', 'skills', 'registry.json')), true);
  assert.equal(plan.rollback_path, join(repoRoot, 'plugins', 'loom'));
});

test('verify-upgrade fails closed when installed payload drifts from recorded metadata', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  runInstaller(
    {
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );
  writeFileSync(join(repoRoot, 'plugins', 'loom', 'skills', 'registry.json'), '{"registry_version":"drift"}\n', 'utf8');

  const verify = runInstaller(
    {
      operation: 'verify-upgrade',
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  assert.equal(verify.status, 'blocked');
  assert.equal(verify.installed_status?.runtime_state, 'blocked');
  assert.equal(verify.installed_status?.upgrade_eligibility, 'drift');
  assert.equal(verify.drift?.includes(join('plugins', 'loom', 'skills', 'registry.json')), true);
  assert.equal(verify.failed_layer, 'installed-surface');
  assert.match(verify.fail_closed_reason ?? '', /drifted/);
  assert.equal(verify.rollback_path, join(repoRoot, 'plugins', 'loom'));
});

test('verify-upgrade fails closed on installed Python cache residue', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  runInstaller(
    {
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );
  const cacheDir = join(repoRoot, 'plugins', 'loom', 'skills', 'shared', 'scripts', '__pycache__');
  mkdirSync(cacheDir, { recursive: true });
  writeFileSync(join(cacheDir, 'loom_check.cpython-314.pyc'), 'cache');

  const verify = runInstaller(
    {
      operation: 'verify-upgrade',
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  assert.equal(verify.status, 'blocked');
  assert.equal(verify.installed_status?.upgrade_eligibility, 'drift');
  assert.equal(verify.drift?.includes(join('plugins', 'loom', 'skills', 'shared', 'scripts', '__pycache__')), true);
});

test('verify-upgrade fails closed when installed version metadata is missing', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

  runInstaller(
    {
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );
  rmSync(join(repoRoot, 'plugins', 'loom', '.loom-install-status.json'));

  const verify = runInstaller(
    {
      operation: 'verify-upgrade',
      mode: 'plugin',
      options: {
        host: 'codex',
        target: repoRoot,
        force: false,
        json: false,
      },
    },
    envSource,
    packageRoot(),
  );

  assert.equal(verify.status, 'blocked');
  assert.equal(verify.installed_status?.upgrade_eligibility, 'incompatible');
  assert.equal(verify.failed_layer, 'installed-surface');
  assert.match(verify.fail_closed_reason ?? '', /metadata is missing/);
  assert.equal(verify.rollback_path, join(repoRoot, 'plugins', 'loom'));
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

test('codex skill install writes repo-scoped .agents skill', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });

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
  const skillPath = join(repoRoot, '.agents', 'skills', 'loom-review', 'SKILL.md');
  assert.equal(result.mode, 'skill');
  assert.equal(result.distribution_layer, 'generated-single-skill');
  assert.equal(result.version_context?.skill_package_id, 'loom-review');
  assert.equal(typeof result.version_context?.skill_package_version, 'string');
  assert.equal(existsSync(skillPath), true);
  assert.equal(existsSync(join(envSource.CODEX_HOME!, 'config.toml')), false);
});

test('codex skill install fails closed on conflicting repo skill directory without force', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  mkdirSync(join(repoRoot, '.agents', 'skills', 'loom-review'), { recursive: true });
  writeFileSync(join(repoRoot, '.agents', 'skills', 'loom-review', 'README.md'), '# Not a Loom skill\n', 'utf8');

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

  assert.throws(() => runInstaller(parsed, envSource, packageRoot()), /not a Loom skill/);
});

test('codex skill install lets --force take over conflicting repo skill directory', () => {
  const base = fixtureRoot();
  const envSource = prepareEnv(base);
  mkdirSync(envSource.CODEX_HOME!, { recursive: true });
  const repoRoot = join(base, 'repo');
  mkdirSync(repoRoot, { recursive: true });
  mkdirSync(join(repoRoot, '.agents', 'skills', 'loom-review'), { recursive: true });
  writeFileSync(join(repoRoot, '.agents', 'skills', 'loom-review', 'README.md'), '# Not a Loom skill\n', 'utf8');

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
  const skillPath = join(repoRoot, '.agents', 'skills', 'loom-review', 'SKILL.md');
  assert.equal(result.mode, 'skill');
  assert.equal(existsSync(skillPath), true);
  assert.equal(existsSync(join(repoRoot, '.agents', 'skills', 'loom-review', 'README.md')), false);
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
  assert.equal(existsSync(join(repoRoot, '.agents', 'skills', 'loom-init', 'SKILL.md')), true);
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
  assert.equal(payload.distribution_layer, 'host-adapter-plugin');
  assert.equal(payload.version_context.plugin_surface_version, '0.4.0');
  assert.equal(payload.failed_layer, null);
  assert.equal(payload.fail_closed_reason, null);
});
