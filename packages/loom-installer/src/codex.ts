import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { InstallResult, PayloadManifest, PayloadSkillRecord, ResolvedEnv } from './types.js';
import { InstallerError, copyTree, dirExists, ensureDirectory, fileExists, readJson, replaceTree, writeJson } from './utils.js';

interface CodexSkillBlock {
  raw: string;
  path: string | null;
  enabled: boolean | null;
}

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
  if (existing && existing.source?.path && existing.source.path !== expectedPath) {
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

function parseSkillBlocks(content: string): CodexSkillBlock[] {
  const lines = content.split('\n');
  const blocks: CodexSkillBlock[] = [];
  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index].trim() !== '[[skills.config]]') {
      continue;
    }
    const blockLines = [lines[index]];
    index += 1;
    while (index < lines.length && !lines[index].trim().startsWith('[[')) {
      blockLines.push(lines[index]);
      index += 1;
    }
    index -= 1;
    const raw = blockLines.join('\n');
    const pathMatch = raw.match(/^path\s*=\s*"([^"]+)"/m);
    const enabledMatch = raw.match(/^enabled\s*=\s*(true|false)/m);
    blocks.push({
      raw,
      path: pathMatch?.[1] ?? null,
      enabled: enabledMatch ? enabledMatch[1] === 'true' : null,
    });
  }
  return blocks;
}

function upsertSkillBlock(configPath: string, desiredSkillPath: string, skillId: string, force: boolean): void {
  const content = fileExists(configPath) ? readFileSync(configPath, 'utf8') : '';
  const blocks = parseSkillBlocks(content);
  const skillDir = skillId.startsWith('loom-') ? skillId : `loom-${skillId}`;
  const conflicting = blocks.filter((block) => {
    if (!block.path) {
      return false;
    }
    return block.path.endsWith(`/${skillDir}/SKILL.md`) && block.path !== desiredSkillPath;
  });
  if (conflicting.length > 0 && !force) {
    throw new InstallerError(
      `Codex already has ${skillId} from a different path`,
      `Codex already has ${skillId} from a different path`,
    );
  }

  let nextContent = content;
  for (const block of conflicting) {
    nextContent = nextContent.replace(`${block.raw}\n`, '').replace(block.raw, '');
  }

  const existingBlock = parseSkillBlocks(nextContent).find((block) => block.path === desiredSkillPath);
  if (existingBlock) {
    const enabledBlock = existingBlock.raw.match(/^enabled\s*=\s*false/m)
      ? existingBlock.raw.replace(/^enabled\s*=\s*false/m, 'enabled = true')
      : existingBlock.enabled === null
        ? `${existingBlock.raw}\nenabled = true`
        : existingBlock.raw;
    nextContent = nextContent.replace(existingBlock.raw, enabledBlock);
  } else {
    if (nextContent && !nextContent.endsWith('\n')) {
      nextContent += '\n';
    }
    nextContent += `\n[[skills.config]]\npath = ${JSON.stringify(desiredSkillPath)}\nenabled = true\n`;
  }

  ensureDirectory(join(configPath, '..'));
  writeFileSync(configPath, nextContent.replace(/^\n+/, ''), 'utf8');
}

function verifySkillEnabled(configPath: string, desiredSkillPath: string): boolean {
  const content = fileExists(configPath) ? readFileSync(configPath, 'utf8') : '';
  return parseSkillBlocks(content).some((block) => block.path === desiredSkillPath && block.enabled !== false);
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
  env: ResolvedEnv,
  packageRoot: string,
  skill: PayloadSkillRecord,
  force: boolean,
): InstallResult {
  const skillDirName = skill.id.startsWith('loom-') ? skill.id : `loom-${skill.id}`;
  const sourceDir = join(packageRoot, 'payload', skill.relative_path);
  const targetDir = join(env.codexHome, 'skills', skillDirName);
  const skillMarkdownPath = join(targetDir, 'SKILL.md');
  const configPath = join(env.codexHome, 'config.toml');

  ensureDirectory(join(env.codexHome, 'skills'));
  if (dirExists(targetDir)) {
    if (!force && !fileExists(skillMarkdownPath)) {
      throw new InstallerError(
        `existing Codex skill directory is not Loom-managed: ${targetDir}`,
        `refusing to take over non-Loom Codex skill directory: ${targetDir}`,
      );
    }
    replaceTree(sourceDir, targetDir);
  } else {
    copyTree(sourceDir, targetDir, true);
  }

  ensureDirectory(env.codexHome);
  upsertSkillBlock(configPath, skillMarkdownPath, skill.id, force);
  if (!verifySkillEnabled(configPath, skillMarkdownPath)) {
    throw new InstallerError(`Codex config did not enable ${skill.id}`);
  }

  return {
    mode: 'skill',
    host: 'codex',
    status: 'installed',
    installed_paths: [targetDir, configPath],
    verification: [
      `verified skill payload at ${targetDir}`,
      `verified skills.config entry for ${skill.id}`,
    ],
    warnings: ['Codex single-skill install exposes only the named skill, not the full Loom plugin surface.'],
    fail_closed_reason: null,
  };
}
