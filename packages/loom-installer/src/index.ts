import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync, readdirSync, statSync } from 'node:fs';
import {
  Host,
  CliOptions,
  DistributionLayer,
  InstalledLoomSurfaceStatus,
  InstallResult,
  InstallerOperation,
  Mode,
  PayloadManifest,
  PayloadSkillRecord,
  ResolvedEnv,
  UpgradeEligibility,
  VersionContext,
} from './types.js';
import { InstallerError, assert, dirExists, ensureTargetExists, ensureTargetWritable, fileExists, readJson, runCommand, sha256, writeJson } from './utils.js';
import { loadPayloadManifest, resolveSkillRecord, verifyPayload } from './payload.js';
import { installCodexPlugin, installCodexSkill } from './codex.js';
import { installClaudePlugin, installClaudeSkill } from './claude.js';

const LEGACY_SINGLE_SKILL_REASON =
  'legacy single-skill installation is retired; use the root `loom` CLI and host plugin payload instead';

const DEFAULT_OPTIONS: CliOptions = {
  host: 'auto',
  target: '.',
  force: false,
  json: false,
};

export interface ParsedCommand {
  operation?: InstallerOperation;
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
  if (command !== 'add' && command !== 'upgrade-plan' && command !== 'verify-upgrade') {
    throw new InstallerError(
      'usage: loom-installer add|upgrade-plan|verify-upgrade plugin|skill <skill-id> [--host ...] [--target ...] [--force] [--json]',
    );
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
      operation: command,
      mode: 'plugin',
      options,
    };
  }
  if (subject === 'skill') {
    if (!third) {
      throw new InstallerError(`usage: loom-installer ${command} skill <skill-id>`);
    }
    return {
      operation: command,
      mode: 'skill',
      skillId: third,
      options,
    };
  }
  throw new InstallerError(`unknown ${command} target: ${String(subject)}`);
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

export function ensureClaudeCliWhenNeeded(host: Host, mode: Mode, operation: InstallerOperation, env: ResolvedEnv): void {
  if (operation !== 'add' || host !== 'claude' || mode !== 'plugin') {
    return;
  }
  const result = runCommand(env.claudeBin, ['--version'], process.env);
  if (result.status !== 0) {
    throw new InstallerError(`claude CLI preflight failed: ${result.stderr || result.stdout}`.trim());
  }
}

export function formatResult(result: InstallResult): string {
  const version = result.version_context;
  return [
    `${result.host} ${result.mode} ${result.operation ?? 'add'}: ${result.status}`,
    `layer: ${result.distribution_layer}`,
    ...(result.installed_status
      ? [
          `runtime_state: ${result.installed_status.runtime_state}`,
          `upgrade_eligibility: ${result.installed_status.upgrade_eligibility}`,
        ]
      : []),
    ...(result.changed_paths?.length ? [`changed_paths: ${result.changed_paths.length}`] : []),
    ...(result.drift?.length ? [`drift: ${result.drift.length}`] : []),
    ...(result.rollback_path ? [`rollback_path: ${result.rollback_path}`] : []),
    ...(version
      ? [
          `versions: repo=${version.repo_version} installer=${version.installer_package_version} plugin=${version.plugin_surface_version} registry=${version.skills_registry_version}`,
        ]
      : []),
    ...result.verification.map((line) => `- ${line}`),
    ...result.warnings.map((line) => `! ${line}`),
  ].join('\n');
}

export function runInstaller(parsed: ParsedCommand, envSource: NodeJS.ProcessEnv = process.env, packageRoot?: string): InstallResult {
  const resolvedEnv = resolveEnvironment(envSource);
  const host = selectHost(parsed.options.host, resolvedEnv);
  const operation = parsed.operation ?? 'add';
  const resolvedPackageRoot = packageRoot ?? packageRootFromUrl(import.meta.url);
  const targetRoot = resolve(parsed.options.target);
  if (operation === 'add') {
    ensureTargetWritable(targetRoot);
  } else {
    ensureTargetExists(targetRoot);
  }

  const manifest = loadPayloadManifest(resolvedPackageRoot);
  verifyPayload(resolvedPackageRoot, manifest);
  const warnings = checkPython(resolvedEnv);
  ensureClaudeCliWhenNeeded(host, parsed.mode, operation, resolvedEnv);
  const skill = parsed.mode === 'skill' ? resolveSkillRecord(manifest, parsed.skillId ?? '') : undefined;
  if (parsed.mode === 'skill') {
    const result = legacySingleSkillDiagnostic({
      operation,
      host,
      manifest,
      skill,
      targetRoot,
    });
    result.warnings.unshift(...warnings);
    return result;
  }

  if (operation !== 'add') {
    const result = inspectInstalledSurface({
      operation,
      host,
      parsed,
      packageRoot: resolvedPackageRoot,
      targetRoot,
      manifest,
      skill,
    });
    result.warnings.unshift(...warnings);
    return result;
  }

  const result = installForHost({
    host,
    parsed,
    env: resolvedEnv,
    packageRoot: resolvedPackageRoot,
    targetRoot,
    manifest,
  });
  result.warnings.unshift(...warnings);
  const withContext = withVersionContext(result, manifest, skill);
  writeInstalledSurfaceStatus({
    result: withContext,
    host,
    mode: parsed.mode,
    skill,
    targetRoot,
  });
  return withContext;
}

function payloadVersionContext(manifest: PayloadManifest, skill?: PayloadSkillRecord): VersionContext {
  return {
    ...manifest.version_context,
    source_repository: manifest.source_repository,
    source_commit: manifest.source_commit,
    source_ref: manifest.source_ref,
    ...(skill
      ? {
          skill_package_id: skill.id,
          skill_contract_version: skill.contract_version,
          runtime_core_version: skill.runtime_core_version,
        }
      : {}),
  };
}

function withVersionContext(result: InstallResult, manifest: PayloadManifest, skill?: PayloadSkillRecord): InstallResult {
  return {
    schema_version: 'loom-installer-result/v1',
    operation: 'add',
    ...result,
    version_context: payloadVersionContext(manifest, skill),
  };
}

function distributionLayer(mode: Mode): DistributionLayer {
  return mode === 'plugin' ? 'host-adapter-plugin' : 'legacy-single-skill-diagnostic';
}

function skillDirName(host: Host, skillId: string): string {
  if (host === 'codex') {
    return skillId.startsWith('loom-') ? skillId : `loom-${skillId}`;
  }
  return skillId;
}

function installedRoot(targetRoot: string, host: Host, mode: Mode, skill?: PayloadSkillRecord): string {
  if (mode === 'plugin') {
    return host === 'codex'
      ? join(targetRoot, 'plugins', 'loom')
      : join(targetRoot, '.claude', 'marketplaces', 'loom-local', 'plugins', 'loom');
  }
  assert(skill, 'skill install requires a skill record');
  return host === 'codex'
    ? join(targetRoot, '.agents', 'skills', skillDirName(host, skill.id))
    : join(targetRoot, '.claude', 'skills', skillDirName(host, skill.id));
}

function installedStatusPath(root: string): string {
  return join(root, '.loom-install-status.json');
}

function writeInstalledSurfaceStatus(input: {
  result: InstallResult;
  host: Host;
  mode: Mode;
  skill?: PayloadSkillRecord;
  targetRoot: string;
}): void {
  const root = installedRoot(input.targetRoot, input.host, input.mode, input.skill);
  const statusPath = installedStatusPath(root);
  const status: InstalledLoomSurfaceStatus = {
    schema_version: 'loom-installed-surface-status/v1',
    installed_layer: input.result.distribution_layer,
    host_adapter: input.host,
    mode: input.mode,
    ...(input.skill ? { skill_id: input.skill.id } : {}),
    version_context: input.result.version_context,
    runtime_state: 'ready',
    upgrade_eligibility: 'current',
    evidence: [`installed surface metadata at ${statusPath}`],
    failed_layer: null,
    fail_closed_reason: null,
  };
  writeJson(statusPath, status);
  input.result.installed_paths.push(statusPath);
  input.result.installed_status = status;
}

function sourcePrefix(mode: Mode, manifest: PayloadManifest, skill?: PayloadSkillRecord): string {
  if (mode === 'plugin') {
    return manifest.plugin.relative_path.replace(/\/$/, '');
  }
  assert(skill, 'skill install requires a skill record');
  return skill.relative_path.replace(/\/$/, '');
}

function targetRelativePath(mode: Mode, host: Host, sourcePath: string, manifest: PayloadManifest, skill?: PayloadSkillRecord): string {
  const prefix = sourcePrefix(mode, manifest, skill);
  const suffix = sourcePath.slice(prefix.length).replace(/^\//, '');
  if (mode === 'plugin') {
    return host === 'codex'
      ? join('plugins', 'loom', suffix)
      : join('.claude', 'marketplaces', 'loom-local', 'plugins', 'loom', suffix);
  }
  assert(skill, 'skill install requires a skill record');
  return host === 'codex'
    ? join('.agents', 'skills', skillDirName(host, skill.id), suffix)
    : join('.claude', 'skills', skillDirName(host, skill.id), suffix);
}

function compareInstalledPayload(input: {
  host: Host;
  mode: Mode;
  packageRoot: string;
  targetRoot: string;
  manifest: PayloadManifest;
  skill?: PayloadSkillRecord;
}): string[] {
  const prefix = `${sourcePrefix(input.mode, input.manifest, input.skill)}/`;
  const changed: string[] = [];
  const installed = installedRoot(input.targetRoot, input.host, input.mode, input.skill);
  for (const file of input.manifest.files) {
    if (!file.path.startsWith(prefix)) {
      continue;
    }
    const source = join(input.packageRoot, 'payload', file.path);
    const targetRelative = targetRelativePath(input.mode, input.host, file.path, input.manifest, input.skill);
    const target = join(input.targetRoot, targetRelative);
    if (!fileExists(target) || sha256(source) !== sha256(target)) {
      changed.push(targetRelative);
    }
  }
  for (const cachePath of collectPythonCacheArtifacts(installed, input.targetRoot)) {
    changed.push(cachePath);
  }
  return changed.sort();
}

function collectPythonCacheArtifacts(root: string, targetRoot: string): string[] {
  if (!existsSync(root)) {
    return [];
  }
  const found: string[] = [];
  const visit = (directory: string): void => {
    for (const entry of readdirSync(directory)) {
      const path = join(directory, entry);
      const stat = statSync(path);
      if (stat.isDirectory()) {
        if (entry === '__pycache__') {
          found.push(relative(targetRoot, path));
          continue;
        }
        visit(path);
        continue;
      }
      if (entry.endsWith('.pyc') || entry.endsWith('.pyo') || entry.endsWith('.pyd')) {
        found.push(relative(targetRoot, path));
      }
    }
  };
  visit(root);
  return found;
}

function statusFailureResult(input: {
  operation: InstallerOperation;
  host: Host;
  mode: Mode;
  skill?: PayloadSkillRecord;
  manifest: PayloadManifest;
  rollbackPath?: string;
  reason: string;
  evidence: string[];
}): InstallResult {
  const available = payloadVersionContext(input.manifest, input.skill);
  const rollbackPath = input.rollbackPath ?? null;
  const installedStatus = {
    schema_version: 'loom-installed-surface-status/v1' as const,
    installed_layer: distributionLayer(input.mode),
    host_adapter: input.host,
    mode: input.mode,
    ...(input.skill ? { skill_id: input.skill.id } : {}),
    version_context: null,
    runtime_state: 'blocked' as const,
    upgrade_eligibility: 'incompatible' as const,
    evidence: input.evidence,
    failed_layer: 'installed-surface',
    fail_closed_reason: input.reason,
  };
  return {
    schema_version: 'loom-installer-result/v1',
    operation: input.operation,
    mode: input.mode,
    host: input.host,
    distribution_layer: distributionLayer(input.mode),
    status: 'blocked',
    installed_paths: rollbackPath ? [rollbackPath] : [],
    verification: input.evidence,
    warnings: [],
    version_context: null,
    installed_status: installedStatus,
    available_version_context: available,
    changed_paths: [],
    drift: [],
    rollback_path: rollbackPath,
    rehearsal: {
      schema_version: 'loom-upgrade-rehearsal/v1',
      mutates_target: false,
      changed_paths: [],
      drift: [],
      rollback_path: rollbackPath,
    },
    failed_layer: 'installed-surface',
    fail_closed_reason: input.reason,
  };
}

function legacySingleSkillDiagnostic(input: {
  operation: InstallerOperation;
  host: Host;
  manifest: PayloadManifest;
  skill?: PayloadSkillRecord;
  targetRoot: string;
}): InstallResult {
  const available = payloadVersionContext(input.manifest, input.skill);
  const root = input.skill ? installedRoot(input.targetRoot, input.host, 'skill', input.skill) : input.targetRoot;
  const statusPath = installedStatusPath(root);
  const hasLegacyStatus = fileExists(statusPath);
  const evidence = [
    LEGACY_SINGLE_SKILL_REASON,
    `migration diagnostic for legacy skill surface${input.skill ? ` ${input.skill.id}` : ''}`,
  ];
  let installedStatus: InstalledLoomSurfaceStatus | undefined;
  if (hasLegacyStatus) {
    const legacyStatus = readJson<InstalledLoomSurfaceStatus>(statusPath);
    installedStatus = {
      ...legacyStatus,
      installed_layer: 'legacy-single-skill-diagnostic',
      runtime_state: 'blocked',
      upgrade_eligibility: 'incompatible',
      evidence: [
        `read legacy single-skill status metadata at ${statusPath}`,
        'legacy skill metadata is retained only for migration diagnostics',
      ],
      failed_layer: 'distribution-layer',
      fail_closed_reason: LEGACY_SINGLE_SKILL_REASON,
    };
    evidence.push(`read legacy single-skill status metadata at ${statusPath}`);
  }

  return {
    schema_version: 'loom-installer-result/v1',
    operation: input.operation,
    mode: 'skill',
    host: input.host,
    distribution_layer: 'legacy-single-skill-diagnostic',
    status: 'blocked',
    installed_paths: [],
    verification: evidence,
    warnings: ['single-skill install and upgrade surfaces are retired; current Loom distribution is CLI + host plugin payload'],
    version_context: null,
    installed_status: installedStatus,
    available_version_context: available,
    changed_paths: [],
    drift: [],
    rollback_path: hasLegacyStatus ? root : null,
    rehearsal: {
      schema_version: 'loom-upgrade-rehearsal/v1',
      mutates_target: false,
      changed_paths: [],
      drift: [],
      rollback_path: hasLegacyStatus ? root : null,
    },
    failed_layer: 'distribution-layer',
    fail_closed_reason: LEGACY_SINGLE_SKILL_REASON,
  };
}

function sameVersionContext(left: VersionContext | null, right: VersionContext): boolean {
  if (!left) {
    return false;
  }
  const keys: (keyof VersionContext)[] = [
    'repo_version',
    'installer_package_version',
    'plugin_surface_version',
    'host_adapter_version',
    'skills_registry_version',
    'runtime_core_version',
    'skill_contract_version',
    'skill_package_id',
  ];
  return keys.every((key) => left[key] === right[key]);
}

function inspectInstalledSurface(input: {
  operation: InstallerOperation;
  host: Host;
  parsed: ParsedCommand;
  packageRoot: string;
  targetRoot: string;
  manifest: PayloadManifest;
  skill?: PayloadSkillRecord;
}): InstallResult {
  const root = installedRoot(input.targetRoot, input.host, input.parsed.mode, input.skill);
  const statusPath = installedStatusPath(root);
  const available = payloadVersionContext(input.manifest, input.skill);
  if (!fileExists(statusPath)) {
    return statusFailureResult({
      operation: input.operation,
      host: input.host,
      mode: input.parsed.mode,
      skill: input.skill,
      manifest: input.manifest,
      rollbackPath: root,
      reason: `installed Loom status metadata is missing: ${relative(input.targetRoot, statusPath)}`,
      evidence: [`missing installed status metadata at ${statusPath}`],
    });
  }

  let installedStatus = readJson<NonNullable<InstallResult['installed_status']>>(statusPath);
  if (
    installedStatus.schema_version !== 'loom-installed-surface-status/v1' ||
    installedStatus.host_adapter !== input.host ||
    installedStatus.mode !== input.parsed.mode ||
    installedStatus.installed_layer !== distributionLayer(input.parsed.mode) ||
    !installedStatus.version_context
  ) {
    return statusFailureResult({
      operation: input.operation,
      host: input.host,
      mode: input.parsed.mode,
      skill: input.skill,
      manifest: input.manifest,
      rollbackPath: root,
      reason: `installed Loom status metadata is inconsistent: ${relative(input.targetRoot, statusPath)}`,
      evidence: [`inconsistent installed status metadata at ${statusPath}`],
    });
  }
  if (input.skill && installedStatus.skill_id !== input.skill.id) {
    return statusFailureResult({
      operation: input.operation,
      host: input.host,
      mode: input.parsed.mode,
      skill: input.skill,
      manifest: input.manifest,
      rollbackPath: root,
      reason: `installed Loom skill metadata does not match ${input.skill.id}`,
      evidence: [`skill metadata mismatch at ${statusPath}`],
    });
  }

  const changedPaths = compareInstalledPayload({
    host: input.host,
    mode: input.parsed.mode,
    packageRoot: input.packageRoot,
    targetRoot: input.targetRoot,
    manifest: input.manifest,
    skill: input.skill,
  });
  const versionMatches = sameVersionContext(installedStatus.version_context, available);
  const eligibility: UpgradeEligibility = changedPaths.length === 0 && versionMatches ? 'current' : versionMatches ? 'drift' : 'upgrade-available';
  const drift = eligibility === 'drift' ? changedPaths : [];
  const runtimeState = eligibility === 'drift' ? 'blocked' : 'ready';
  const rollbackPath = changedPaths.length > 0 ? root : null;
  const failClosedReason = eligibility === 'drift' ? 'installed Loom payload drifted from its recorded version context' : null;
  installedStatus = {
    ...installedStatus,
    runtime_state: runtimeState,
    upgrade_eligibility: eligibility,
    evidence: [`read installed status metadata at ${statusPath}`, `compared installed payload under ${root}`],
    failed_layer: failClosedReason ? 'installed-surface' : null,
    fail_closed_reason: failClosedReason,
  };

  return {
    schema_version: 'loom-installer-result/v1',
    operation: input.operation,
    mode: input.parsed.mode,
    host: input.host,
    distribution_layer: distributionLayer(input.parsed.mode),
    status: input.operation === 'verify-upgrade' ? (failClosedReason ? 'blocked' : 'verified') : failClosedReason ? 'blocked' : 'planned',
    installed_paths: [root, statusPath],
    verification: [
      `read installed status metadata at ${statusPath}`,
      `compared ${changedPaths.length} changed path(s) without mutating target`,
    ],
    warnings: [],
    version_context: installedStatus.version_context,
    installed_status: installedStatus,
    available_version_context: available,
    changed_paths: changedPaths,
    drift,
    rollback_path: rollbackPath,
    rehearsal: {
      schema_version: 'loom-upgrade-rehearsal/v1',
      mutates_target: false,
      changed_paths: changedPaths,
      drift,
      rollback_path: rollbackPath,
    },
    failed_layer: failClosedReason ? 'installed-surface' : null,
    fail_closed_reason: failClosedReason,
  };
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
    ? installCodexSkill(env, targetRoot, packageRoot, skill, parsed.options.force)
    : installClaudeSkill(targetRoot, packageRoot, skill, parsed.options.force);
}
