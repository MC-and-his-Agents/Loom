export type Host = 'codex' | 'claude';
export type Mode = 'plugin' | 'skill';
export type InstallStatus = 'installed' | 'already-installed';
export type DistributionLayer = 'host-adapter-plugin' | 'generated-single-skill';

export interface PayloadFileRecord {
  path: string;
  bytes: number;
  sha256: string;
}

export interface PayloadSkillRecord {
  id: string;
  display_name: string;
  contract_version: string;
  skill_package_version: string;
  runtime_core_version: string;
  package_metadata: string;
  runtime_root: string;
  launcher: string;
  relative_path: string;
}

export interface VersionContext {
  repo_version: string;
  installer_package_version: string;
  plugin_surface_version: string;
  host_adapter_version: string;
  skills_registry_version: string;
  runtime_core_version: string;
  source_repository?: string;
  source_commit?: string;
  source_ref?: string;
  skill_package_version?: string;
  skill_contract_version?: string;
  skill_package_id?: string;
}

export interface PayloadManifest {
  schema_version: 'loom-installer-payload/v1';
  loom_version: string;
  source_repository: string;
  source_commit: string;
  source_ref: string;
  built_at: string;
  version_context: VersionContext;
  runtime: {
    python_minimum: string;
    python_recommended: string;
  };
  plugin: {
    name: string;
    version: string;
    host_adapter_version: string;
    relative_path: string;
  };
  skills: PayloadSkillRecord[];
  files: PayloadFileRecord[];
}

export interface InstallResult {
  mode: Mode;
  host: Host;
  distribution_layer: DistributionLayer;
  status: InstallStatus;
  installed_paths: string[];
  verification: string[];
  warnings: string[];
  version_context: VersionContext | null;
  failed_layer: string | null;
  fail_closed_reason: string | null;
}

export interface CliOptions {
  host: Host | 'auto';
  target: string;
  force: boolean;
  json: boolean;
}

export interface ResolvedEnv {
  homeDir: string;
  codexHome: string;
  claudeConfigDir: string;
  pythonBin: string;
  claudeBin: string;
}
