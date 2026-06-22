export type Host = 'codex' | 'claude';
export type Mode = 'plugin' | 'skill';
export type InstallerOperation = 'add' | 'upgrade-plan' | 'verify-upgrade';
export type InstallStatus = 'installed' | 'already-installed' | 'planned' | 'verified' | 'blocked';
export type DistributionLayer = 'host-adapter-plugin' | 'generated-single-skill';
export type RuntimeState = 'ready' | 'blocked' | 'unknown';
export type UpgradeEligibility = 'current' | 'upgrade-available' | 'drift' | 'incompatible' | 'unknown';

export interface PayloadFileRecord {
  path: string;
  bytes: number;
  sha256: string;
}

export interface PayloadSkillRecord {
  id: string;
  display_name: string;
  contract_version: string;
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
  /** Legacy installed metadata only. It is ignored for freshness decisions. */
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
  schema_version?: 'loom-installer-result/v1';
  operation?: InstallerOperation;
  mode: Mode;
  host: Host;
  distribution_layer: DistributionLayer;
  status: InstallStatus;
  installed_paths: string[];
  verification: string[];
  warnings: string[];
  version_context: VersionContext | null;
  installed_status?: InstalledLoomSurfaceStatus;
  available_version_context?: VersionContext;
  changed_paths?: string[];
  drift?: string[];
  rollback_path?: string | null;
  rehearsal?: UpgradeRehearsalEvidence;
  failed_layer: string | null;
  fail_closed_reason: string | null;
}

export interface InstalledLoomSurfaceStatus {
  schema_version: 'loom-installed-surface-status/v1';
  installed_layer: DistributionLayer;
  host_adapter: Host;
  mode: Mode;
  skill_id?: string;
  version_context: VersionContext | null;
  runtime_state: RuntimeState;
  upgrade_eligibility: UpgradeEligibility;
  evidence: string[];
  failed_layer: string | null;
  fail_closed_reason: string | null;
}

export interface UpgradeRehearsalEvidence {
  schema_version: 'loom-upgrade-rehearsal/v1';
  mutates_target: false;
  changed_paths: string[];
  drift: string[];
  rollback_path: string | null;
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
