import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Host, CliOptions, InstallResult, Mode, PayloadManifest, ResolvedEnv } from './types.js';
import { InstallerError, assert, dirExists, ensureTargetWritable, runCommand } from './utils.js';
import { loadPayloadManifest, resolveSkillRecord, verifyPayload } from './payload.js';
import { installCodexPlugin, installCodexSkill } from './codex.js';
import { installClaudePlugin, installClaudeSkill } from './claude.js';

const DEFAULT_OPTIONS: CliOptions = {
  host: 'auto',
  target: '.',
  force: false,
  json: false,
};

export interface ParsedCommand {
  mode: Mode;
  skillId?: string;
  options: CliOptions;
}

export function packageRootFromUrl(moduleUrl: string): string {
  return resolve(dirname(fileURLToPath(moduleUrl)), '..', '..');
}

export function resolveEnvironment(env: NodeJS.ProcessEnv = process.env): ResolvedEnv {
  const homeDir = env.HOME ?? '';
  assert(homeDir, 'HOME is required');
  return {
    homeDir,
    codexHome: env.CODEX_HOME ?? join(homeDir, '.codex'),
    claudeConfigDir: env.CLAUDE_CONFIG_DIR ?? join(homeDir, '.claude'),
    pythonBin: env.LOOM_INSTALLER_PYTHON_BIN ?? 'python3',
    claudeBin: env.LOOM_INSTALLER_CLAUDE_BIN ?? 'claude',
  };
}

export function detectHosts(env: ResolvedEnv): Host[] {
  const hosts: Host[] = [];
  if (dirExists(env.codexHome)) {
    hosts.push('codex');
  }
  if (dirExists(env.claudeConfigDir)) {
    hosts.push('claude');
  }
  return hosts;
}

export function selectHost(requested: CliOptions['host'], env: ResolvedEnv): Host {
  if (requested !== 'auto') {
    return requested;
  }
  const detected = detectHosts(env);
  if (detected.length === 1) {
    return detected[0];
  }
  if (detected.length === 0) {
    throw new InstallerError('auto host detection failed: no supported host was detected');
  }
  throw new InstallerError('auto host detection found both Codex and Claude; pass --host explicitly');
}

export function parseCli(argv: string[]): ParsedCommand {
  const command = argv[0];
  const subject = argv[1];
  const third = argv[2];
  const rest = subject === 'plugin' ? argv.slice(2) : argv.slice(3);
  if (command !== 'add') {
    throw new InstallerError('usage: loom-installer add plugin|skill <skill-id> [--host ...] [--target ...] [--force] [--json]');
  }
  const options: CliOptions = { ...DEFAULT_OPTIONS };
  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (token === '--host') {
      const next = rest[index + 1];
      if (next !== 'auto' && next !== 'codex' && next !== 'claude') {
        throw new InstallerError(`unsupported --host value: ${String(next)}`);
      }
      options.host = next;
      index += 1;
      continue;
    }
    if (token === '--target') {
      const next = rest[index + 1];
      if (!next) {
        throw new InstallerError('--target requires a value');
      }
      options.target = next;
      index += 1;
      continue;
    }
    if (token === '--force') {
      options.force = true;
      continue;
    }
    if (token === '--json') {
      options.json = true;
      continue;
    }
    throw new InstallerError(`unknown option: ${token}`);
  }

  if (subject === 'plugin') {
    return {
      mode: 'plugin',
      options,
    };
  }
  if (subject === 'skill') {
    if (!third) {
      throw new InstallerError('usage: loom-installer add skill <skill-id>');
    }
    return {
      mode: 'skill',
      skillId: third,
      options,
    };
  }
  throw new InstallerError(`unknown add target: ${String(subject)}`);
}

export function checkPython(env: ResolvedEnv): string[] {
  const result = runCommand(
    env.pythonBin,
    ['-c', 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")'],
    process.env,
  );
  if (result.status !== 0) {
    throw new InstallerError(`python preflight failed: ${result.stderr || result.stdout}`.trim());
  }
  const match = result.stdout.trim().match(/^(\d+)\.(\d+)\.(\d+)$/);
  if (!match) {
    throw new InstallerError(`python preflight returned an invalid version: ${result.stdout.trim()}`);
  }
  const major = Number(match[1]);
  const minor = Number(match[2]);
  if (major < 3 || (major === 3 && minor < 10)) {
    throw new InstallerError(`python ${result.stdout.trim()} is unsupported; require >= 3.10`);
  }
  const warnings: string[] = [];
  if (major === 3 && minor < 11) {
    warnings.push(`python ${result.stdout.trim()} is supported, but 3.11+ is recommended`);
  }
  return warnings;
}

export function ensureClaudeCliWhenNeeded(host: Host, mode: Mode, env: ResolvedEnv): void {
  if (host !== 'claude' || mode !== 'plugin') {
    return;
  }
  const result = runCommand(env.claudeBin, ['--version'], process.env);
  if (result.status !== 0) {
    throw new InstallerError(`claude CLI preflight failed: ${result.stderr || result.stdout}`.trim());
  }
}

export function formatResult(result: InstallResult): string {
  return [
    `${result.host} ${result.mode}: ${result.status}`,
    ...result.verification.map((line) => `- ${line}`),
    ...result.warnings.map((line) => `! ${line}`),
  ].join('\n');
}

export function runInstaller(parsed: ParsedCommand, envSource: NodeJS.ProcessEnv = process.env, packageRoot?: string): InstallResult {
  const resolvedEnv = resolveEnvironment(envSource);
  const host = selectHost(parsed.options.host, resolvedEnv);
  const resolvedPackageRoot = packageRoot ?? packageRootFromUrl(import.meta.url);
  const targetRoot = resolve(parsed.options.target);
  ensureTargetWritable(targetRoot);

  const manifest = loadPayloadManifest(resolvedPackageRoot);
  verifyPayload(resolvedPackageRoot, manifest);
  const warnings = checkPython(resolvedEnv);
  ensureClaudeCliWhenNeeded(host, parsed.mode, resolvedEnv);

  const result = installForHost({
    host,
    parsed,
    env: resolvedEnv,
    packageRoot: resolvedPackageRoot,
    targetRoot,
    manifest,
  });
  result.warnings.unshift(...warnings);
  return result;
}

function installForHost(input: {
  host: Host;
  parsed: ParsedCommand;
  env: ResolvedEnv;
  packageRoot: string;
  targetRoot: string;
  manifest: PayloadManifest;
}): InstallResult {
  const { host, parsed, env, packageRoot, targetRoot, manifest } = input;
  if (parsed.mode === 'plugin') {
    return host === 'codex'
      ? installCodexPlugin(targetRoot, packageRoot, manifest, parsed.options.force)
      : installClaudePlugin(env, targetRoot, packageRoot, manifest, parsed.options.force);
  }
  const skill = resolveSkillRecord(manifest, parsed.skillId ?? '');
  return host === 'codex'
    ? installCodexSkill(env, packageRoot, skill, parsed.options.force)
    : installClaudeSkill(targetRoot, packageRoot, skill, parsed.options.force);
}
