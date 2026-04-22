export type Host = 'codex' | 'claude';
export type Mode = 'plugin' | 'skill';
export type InstallStatus = 'installed' | 'already-installed';

export interface PayloadFileRecord {
  path: string;
  bytes: number;
  sha256: string;
}

export interface PayloadSkillRecord {
  id: string;
  display_name: string;
  contract_version: string;
  relative_path: string;
}

export interface PayloadManifest {
  schema_version: 'loom-installer-payload/v1';
  loom_version: string;
  source_repository: string;
  source_commit: string;
  source_ref: string;
  built_at: string;
  runtime: {
    python_minimum: string;
    python_recommended: string;
  };
  plugin: {
    name: string;
    version: string;
    relative_path: string;
  };
  skills: PayloadSkillRecord[];
  files: PayloadFileRecord[];
}

export interface InstallResult {
  mode: Mode;
  host: Host;
  status: InstallStatus;
  installed_paths: string[];
  verification: string[];
  warnings: string[];
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
