import { join } from 'node:path';
import { PayloadManifest } from './types.js';
import { InstallerError, dirExists, fileExists, readJson, sha256 } from './utils.js';

export function loadPayloadManifest(packageRoot: string): PayloadManifest {
  const manifestPath = join(packageRoot, 'payload', 'manifest.json');
  if (!fileExists(manifestPath)) {
    throw new InstallerError(`payload manifest is missing: ${manifestPath}`);
  }
  return readJson<PayloadManifest>(manifestPath);
}

export function verifyPayload(packageRoot: string, manifest: PayloadManifest): void {
  if (manifest.schema_version !== 'loom-installer-payload/v1') {
    throw new InstallerError(`unsupported payload schema: ${manifest.schema_version}`);
  }
  const payloadRoot = join(packageRoot, 'payload');
  const pluginPath = join(payloadRoot, manifest.plugin.relative_path);
  if (!dirExists(pluginPath)) {
    throw new InstallerError(`plugin payload is missing: ${pluginPath}`);
  }
  for (const skill of manifest.skills) {
    const skillPath = join(payloadRoot, skill.relative_path);
    if (!dirExists(skillPath)) {
      throw new InstallerError(`skill payload is missing: ${skillPath}`);
    }
  }
  for (const file of manifest.files) {
    const absolute = join(payloadRoot, file.path);
    if (!fileExists(absolute)) {
      throw new InstallerError(`payload file is missing: ${file.path}`);
    }
    const actualSha = sha256(absolute);
    if (actualSha !== file.sha256) {
      throw new InstallerError(`payload checksum drift detected for ${file.path}`);
    }
  }
}

export function resolveSkillRecord(manifest: PayloadManifest, skillId: string) {
  const skill = manifest.skills.find((candidate) => candidate.id === skillId);
  if (!skill) {
    throw new InstallerError(`unknown skill id: ${skillId}`, `unknown skill id: ${skillId}`);
  }
  return skill;
}
