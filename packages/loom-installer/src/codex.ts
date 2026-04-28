import { join } from 'node:path';
import { InstallResult, PayloadManifest, PayloadSkillRecord, ResolvedEnv } from './types.js';
import { InstallerError, copyTree, dirExists, ensureDirectory, fileExists, readJson, replaceTree, writeJson } from './utils.js';

function codexMarketplacePath(targetRoot: string): string {
  return join(targetRoot, '.agents', 'plugins', 'marketplace.json');
}

function parseMarketplace(path: string): Record<string, unknown> | null {
  if (!fileExists(path)) {
    return null;
  }
  return readJson<Record<string, unknown>>(path);
}

function defaultMarketplace() {
  return {
    name: 'loom-local',
    interface: {
      displayName: 'Loom Local Plugins',
    },
    plugins: [],
  };
}

function loomMarketplaceEntry() {
  return {
    name: 'loom',
    source: {
      source: 'local',
      path: './plugins/loom',
    },
    policy: {
      installation: 'AVAILABLE',
      authentication: 'ON_INSTALL',
    },
    category: 'Productivity',
  };
}

function ensureMarketplace(targetRoot: string, force: boolean): string[] {
  const marketplacePath = codexMarketplacePath(targetRoot);
  const marketplace = parseMarketplace(marketplacePath) ?? defaultMarketplace();
  if (!Array.isArray(marketplace.plugins)) {
    throw new InstallerError('Codex marketplace.json must contain a plugins array');
  }
  const expectedPath = './plugins/loom';
  const existing = marketplace.plugins.find(
    (entry) => typeof entry === 'object' && entry !== null && (entry as { name?: string }).name === 'loom',
  ) as { name?: string; source?: { path?: string } } | undefined;
  if (existing && existing.source?.path && existing.source.path !== expectedPath && !force) {
    throw new InstallerError(
      `Codex marketplace already declares loom from a different path: ${existing.source.path}`,
      `refusing to take over non-Loom marketplace entry for loom: ${existing.source.path}`,
    );
  }
  if (!existing) {
    marketplace.plugins.push(loomMarketplaceEntry());
  } else if (force) {
    const index = marketplace.plugins.indexOf(existing as never);
    marketplace.plugins[index] = loomMarketplaceEntry() as never;
  }
  writeJson(marketplacePath, marketplace);
  return [marketplacePath];
}

export function installCodexPlugin(
  targetRoot: string,
  packageRoot: string,
  manifest: PayloadManifest,
  force: boolean,
): InstallResult {
  const pluginSource = join(packageRoot, 'payload', manifest.plugin.relative_path);
  const pluginTarget = join(targetRoot, 'plugins', 'loom');
  const pluginManifestPath = join(pluginTarget, '.codex-plugin', 'plugin.json');
  const installedPaths: string[] = [];
  const warnings: string[] = [];

  if (dirExists(pluginTarget) && !force) {
    if (!fileExists(pluginManifestPath)) {
      throw new InstallerError(
        `target already contains plugins/loom but it is not a Loom plugin: ${pluginTarget}`,
        `refusing to take over non-Loom plugin directory: ${pluginTarget}`,
      );
    }
  }

  if (dirExists(pluginTarget)) {
    replaceTree(pluginSource, pluginTarget);
  } else {
    copyTree(pluginSource, pluginTarget, true);
  }
  installedPaths.push(pluginTarget);
  installedPaths.push(...ensureMarketplace(targetRoot, force));

  const pluginManifest = readJson<{ name?: string }>(pluginManifestPath);
  if (pluginManifest.name !== 'loom') {
    throw new InstallerError('Codex plugin installation drifted: plugin name must stay `loom`');
  }
  warnings.push('Codex plugin install remains repo-local; it does not replace the Python runtime.');

  return {
    mode: 'plugin',
    host: 'codex',
    status: 'installed',
    installed_paths: installedPaths,
    verification: [
      `verified plugin payload at ${pluginTarget}`,
      `verified marketplace entry at ${codexMarketplacePath(targetRoot)}`,
    ],
    warnings,
    fail_closed_reason: null,
  };
}

export function installCodexSkill(
  _env: ResolvedEnv,
  targetRoot: string,
  packageRoot: string,
  skill: PayloadSkillRecord,
  force: boolean,
): InstallResult {
  const skillDirName = skill.id.startsWith('loom-') ? skill.id : `loom-${skill.id}`;
  const sourceDir = join(packageRoot, 'payload', skill.relative_path);
  const targetDir = join(targetRoot, '.agents', 'skills', skillDirName);
  const skillMarkdownPath = join(targetDir, 'SKILL.md');

  ensureDirectory(join(targetRoot, '.agents', 'skills'));
  if (dirExists(targetDir)) {
    if (!force && !fileExists(skillMarkdownPath)) {
      throw new InstallerError(
        `target already contains .agents/skills/${skillDirName} but it is not a Loom skill: ${targetDir}`,
        `refusing to take over non-Loom repo skill directory: ${targetDir}`,
      );
    }
    replaceTree(sourceDir, targetDir);
  } else {
    copyTree(sourceDir, targetDir, true);
  }

  if (!fileExists(skillMarkdownPath)) {
    throw new InstallerError(`Codex repo skill install is missing SKILL.md: ${skillMarkdownPath}`);
  }

  return {
    mode: 'skill',
    host: 'codex',
    status: 'installed',
    installed_paths: [targetDir],
    verification: [
      `verified skill payload at ${targetDir}`,
      `verified repo skill discovery path at ${skillMarkdownPath}`,
    ],
    warnings: ['Codex repo-scoped single-skill install exposes only the named skill, not the full Loom plugin surface.'],
    fail_closed_reason: null,
  };
}
