import type { InstallResult } from './types.js';

export const TOMBSTONE_REASON =
  '@mc-and-his-agents/loom-installer is retired; use @mc-and-his-agents/loom and `loom host ...` instead.';

export function isJson(argv: string[]): boolean {
  return argv.includes('--json');
}

export function runInstaller(): InstallResult {
  return {
    schema_version: 'loom-installer-result/v1',
    status: 'blocked',
    distribution_layer: 'tombstone-package',
    failed_layer: 'legacy-installer',
    fail_closed_reason: TOMBSTONE_REASON,
    migration: {
      install_cli: 'npm install -g @mc-and-his-agents/loom',
      codex_plugin: 'loom host install --host codex --scope user --apply --json',
      verify: 'loom host verify --host codex --scope user --json',
    },
  };
}

export function formatResult(result: InstallResult): string {
  return [
    'loom-installer: retired',
    result.fail_closed_reason,
    `install CLI: ${result.migration.install_cli}`,
    `Codex plugin: ${result.migration.codex_plugin}`,
    `verify: ${result.migration.verify}`,
  ].join('\n');
}
