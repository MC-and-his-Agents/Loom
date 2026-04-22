import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { InstallResult, PayloadManifest, PayloadSkillRecord, ResolvedEnv } from './types.js';
import { InstallerError, copyTree, dirExists, ensureDirectory, fileExists, readJson, replaceTree, runCommand, writeJson } from './utils.js';

function claudeEnv(env: ResolvedEnv): NodeJS.ProcessEnv {
  return {
    ...process.env,
    CLAUDE_CONFIG_DIR: env.claudeConfigDir,
  };
}

function claudeMarketplaceRoot(targetRoot: string): string {
  return join(targetRoot, '.claude', 'marketplaces', 'loom-local');
}

function claudeMarketplaceManifest() {
  return {
    $schema: 'https://anthropic.com/claude-code/marketplace.schema.json',
    name: 'loom-local',
    description: 'Repo-local Loom marketplace for plugin installation.',
    owner: {
      name: 'MC and his Agents',
      email: 'opensource@mc-and-his-agents.dev',
    },
    plugins: [
      {
        name: 'loom',
        description: 'Loom repo-local plugin entry',
        source: './plugins/loom',
        category: 'productivity',
        homepage: 'https://github.com/MC-and-his-Agents/Loom',
      },
    ],
  };
}

function runClaude(env: ResolvedEnv, args: string[]): { stdout: string; stderr: string; status: number | null } {
  return runCommand(env.claudeBin, args, claudeEnv(env));
}

function synthesizeClaudePluginManifest(pluginTarget: string): string {
  const codexManifestPath = join(pluginTarget, '.codex-plugin', 'plugin.json');
  if (!fileExists(codexManifestPath)) {
    throw new InstallerError(`Claude plugin install is missing source plugin manifest: ${codexManifestPath}`);
  }
  const codexManifest = readJson<{
    name: string;
    description?: string;
    version?: string;
    author?: { name?: string; email?: string };
  }>(codexManifestPath);
  const claudeManifestPath = join(pluginTarget, '.claude-plugin', 'plugin.json');
  writeJson(claudeManifestPath, {
    name: codexManifest.name,
    description: codexManifest.description ?? 'Loom repo-local plugin entry',
    version: codexManifest.version ?? '0.0.0',
    author: codexManifest.author ?? {
      name: 'MC and his Agents',
      email: 'opensource@mc-and-his-agents.dev',
    },
  });
  return claudeManifestPath;
}

function verifyClaudePluginInstalled(env: ResolvedEnv): void {
  const result = runClaude(env, ['plugin', 'list', '--json']);
  if (result.status !== 0) {
    throw new InstallerError(`claude plugin list failed: ${result.stderr || result.stdout}`.trim());
  }
  let payload: unknown;
  try {
    payload = JSON.parse(result.stdout || '[]');
  } catch {
    throw new InstallerError('claude plugin list --json returned invalid JSON');
  }
  if (!Array.isArray(payload)) {
    throw new InstallerError('claude plugin list --json must return an array');
  }
  const found = payload.some((entry) => {
    if (typeof entry === 'string') {
      return entry === 'loom';
    }
    if (typeof entry !== 'object' || entry === null) {
      return false;
    }
    return (entry as { name?: string }).name === 'loom';
  });
  if (!found) {
    throw new InstallerError('claude plugin verify failed: loom is not listed as installed');
  }
}

export function installClaudePlugin(
  env: ResolvedEnv,
  targetRoot: string,
  packageRoot: string,
  manifest: PayloadManifest,
  force: boolean,
): InstallResult {
  const marketplaceRoot = claudeMarketplaceRoot(targetRoot);
  const marketplaceManifestPath = join(marketplaceRoot, '.claude-plugin', 'marketplace.json');
  const pluginTarget = join(marketplaceRoot, 'plugins', 'loom');
  const pluginSource = join(packageRoot, 'payload', manifest.plugin.relative_path);

  ensureDirectory(join(marketplaceRoot, '.claude-plugin'));
  ensureDirectory(join(marketplaceRoot, 'plugins'));
  if (dirExists(pluginTarget)) {
    if (!force && !fileExists(join(pluginTarget, '.codex-plugin', 'plugin.json'))) {
      throw new InstallerError(
        `existing Claude marketplace plugin is not Loom-managed: ${pluginTarget}`,
        `refusing to take over non-Loom Claude marketplace plugin: ${pluginTarget}`,
      );
    }
    replaceTree(pluginSource, pluginTarget);
  } else {
    copyTree(pluginSource, pluginTarget, true);
  }
  const claudePluginManifestPath = synthesizeClaudePluginManifest(pluginTarget);
  writeJson(marketplaceManifestPath, claudeMarketplaceManifest());

  const addResult = runClaude(env, ['plugin', 'marketplace', 'add', marketplaceRoot]);
  const addOutput = `${addResult.stdout}\n${addResult.stderr}`;
  if (addResult.status !== 0 && !/already exists|already added|already configured/i.test(addOutput)) {
    throw new InstallerError(`claude plugin marketplace add failed: ${addOutput.trim()}`);
  }

  const installResult = runClaude(env, ['plugin', 'install', 'loom@loom-local']);
  const installOutput = `${installResult.stdout}\n${installResult.stderr}`;
  if (installResult.status !== 0 && !/already installed/i.test(installOutput)) {
    throw new InstallerError(`claude plugin install failed: ${installOutput.trim()}`);
  }

  verifyClaudePluginInstalled(env);

  return {
    mode: 'plugin',
    host: 'claude',
    status: /already installed/i.test(installOutput) ? 'already-installed' : 'installed',
    installed_paths: [marketplaceRoot, marketplaceManifestPath, pluginTarget, claudePluginManifestPath],
    verification: [
      `verified marketplace source at ${marketplaceRoot}`,
      `verified Claude plugin manifest at ${claudePluginManifestPath}`,
      'verified `claude plugin list --json` contains loom',
    ],
    warnings: ['Claude plugin install goes through the official CLI and does not replace the Python runtime.'],
    fail_closed_reason: null,
  };
}

export function installClaudeSkill(
  targetRoot: string,
  packageRoot: string,
  skill: PayloadSkillRecord,
  force: boolean,
): InstallResult {
  const sourceDir = join(packageRoot, 'payload', skill.relative_path);
  const targetDir = join(targetRoot, '.claude', 'skills', skill.id);
  const skillMarkdownPath = join(targetDir, 'SKILL.md');

  ensureDirectory(join(targetRoot, '.claude', 'skills'));
  if (dirExists(targetDir)) {
    if (!force && !fileExists(skillMarkdownPath)) {
      throw new InstallerError(
        `existing Claude skill directory is not Loom-managed: ${targetDir}`,
        `refusing to take over non-Loom Claude skill directory: ${targetDir}`,
      );
    }
    replaceTree(sourceDir, targetDir);
  } else {
    copyTree(sourceDir, targetDir, true);
  }

  if (!fileExists(skillMarkdownPath)) {
    throw new InstallerError(`Claude skill install is missing SKILL.md: ${skillMarkdownPath}`);
  }
  if (!readFileSync(skillMarkdownPath, 'utf8').startsWith('---\n')) {
    throw new InstallerError(`Claude skill install must keep YAML frontmatter in ${skillMarkdownPath}`);
  }

  return {
    mode: 'skill',
    host: 'claude',
    status: 'installed',
    installed_paths: [targetDir],
    verification: [
      `verified skill payload at ${targetDir}`,
      `verified discoverable SKILL.md at ${skillMarkdownPath}`,
    ],
    warnings: ['Claude single-skill install relies on project-level `.claude/skills` discovery and does not expose the full Loom plugin surface.'],
    fail_closed_reason: null,
  };
}
