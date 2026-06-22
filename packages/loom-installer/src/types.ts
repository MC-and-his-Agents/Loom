export interface InstallResult {
  schema_version: 'loom-installer-result/v1';
  status: 'blocked';
  distribution_layer: 'tombstone-package';
  failed_layer: 'legacy-installer';
  fail_closed_reason: string;
  migration: {
    install_cli: string;
    codex_plugin: string;
    verify: string;
  };
}
