# Regression Surface Contract

本文件冻结 Loom 对 black-box long-running regression bucket split 的最小共享合同。

它只定义：

- regression bucket 与 named surface 的稳定词表
- split surface 必须产出的最小 evidence schema
- fast validation 与 full validation 的消费边界

它不定义：

- 具体实现 Work Item 如何拆代码
- docs landing / inventory 的逐项落地顺序
- 新的 top-level gate taxonomy
- repo-specific CI job 名称或宿主门禁配置

## 1. 目标与边界

本合同服务 #1256 及其 core chain：

- #1264 taxonomy
- #1265 evidence schema
- #1266 fast/full policy

shared contract 的目的不是减少覆盖，而是把现有重型回归检查拆成可诊断、可并行、可逐面读取的 surface，同时保留 full coverage 作为 merge-ready / release authoritative gate。

禁止把 split 当成 coverage removal 策略：

- 不允许因为 surface 拆分而删除原有必须覆盖的行为范围
- 不允许把 fast validation 冒充 full validation
- 不允许把 closeout convenience check 当成 release readiness 证明

## 2. Stable Vocabulary

### 2.1 Regression bucket

`regression bucket` 是一个当前仍以单命令或重型检查面承载、但内部已包含多个可分离行为面的 black-box validation cluster。

bucket 的特点：

- 对调用者通常表现为一个高成本命令、job 或 gate
- 内部混合多个 scenario / fixture group / validation concern
- 失败时诊断粒度不够，无法快速判断哪一类行为退化

当前 contract batch 记录的 bucket examples：

- `daily-execution-cli`
- `check-cli-contract`
- `source-self-fixture`
- `repo-local-cli`
- `demo-bootstrap`

这些名字是当前 Loom 已知 bucket label，不代表未来 core 只能有这四类。

### 2.2 Named surface

`named surface` 是从某个 regression bucket 中抽出的、可单独运行、可单独计时、可单独报告结果、可被 full validation 重新聚合消费的稳定验证面。

named surface 必须满足：

- 有稳定 label
- 有明确 parent bucket
- 有单一主要诊断目标
- 能输出 comparable evidence
- 被 full validation 明确保留或聚合

named surface 不是：

- 任意一次性调试命令
- 临时 grep / scratch script
- 只存在于会话里的口头分组

### 2.3 Sub-scenario

`sub-scenario` 是 named surface 内更细的行为样本、fixture path、case group 或 validation step。

它可以用于：

- 暴露 surface 内部进度
- 标记具体失败定位
- 解释 aggregate command 如何消费多个子面

它不是新的 top-level surface；它从属于某个 named surface。

### 2.4 Fixture group

`fixture group` 是一组共享 setup、shared sample、或共同验证意图的 sub-scenario 集合。

fixture group 主要用于：

- source-self / check-cli-contract 一类 fixture-rich surface 的组织
- inventory 与后续实现拆分时的 ownership 边界

fixture group 是组织词，不自动等于 gate 或 release surface。

### 2.5 Fast validation

`fast validation` 是为了本地迭代、PR 准备、或 contract-focused readback 而运行的较小 surface set。

fast validation 可以：

- 缩小本轮执行需要重跑的 surface 范围
- 暴露 progress、timing、failure summary
- 作为 pre-review / local debugging / narrow PR iteration 的输入

fast validation 不可以：

- 证明 full coverage 已完成
- 单独放行 merge-ready 或 release
- 覆盖未运行 surface 的 authoritative result

### 2.6 Full validation

`full validation` 是保留完整 surface coverage 的 authoritative aggregate validation。

full validation 必须：

- 覆盖当前 bucket 所要求的全部 named surfaces，或明确聚合到等价 full gate
- 为 merge-ready、release readiness、或显式 full gate decision 提供权威输入
- 在 output 中保留各 surface 的逐面 evidence，而不是只压成单字符串结论

### 2.7 Closeout evidence

`closeout evidence` 是 closeout / reconciliation / retained validation 在收口时消费的已发生结果证明。

closeout evidence 可以消费 split surface 结果，但不能把一次 fast local run 直接提升为 full validation authoritative truth，除非 owning gate 明确声明该对象本来就只要求 contract-only surface。

## 3. Minimum Evidence Schema

每个 named surface 至少要输出以下字段；本合同只冻结字段语义，不强制具体 carrier：

| Field | Required | Meaning |
| --- | --- | --- |
| `bucket_label` | yes | surface 所属 regression bucket |
| `surface_label` | yes | stable named surface label |
| `surface_kind` | yes | `named_surface` 或 `aggregate_surface` |
| `scenario_label` | yes | 当前 scenario / fixture group / sub-scenario label；若是 aggregate surface，可用 aggregate scenario 名 |
| `command` | yes | 实际运行命令或稳定入口名 |
| `result` | yes | `pass` / `block` / `advisory` / `not_applicable` |
| `elapsed_ms` | yes | 当前 surface 或子面耗时，单位毫秒 |
| `started_at` | recommended | 开始时间 |
| `finished_at` | recommended | 结束时间 |
| `failure_summary` | conditional | 失败或 advisory 时的人类可读摘要 |
| `failure_taxonomy` | conditional | 已有稳定 taxonomy / failure kind 列表；不得自创第二套顶层 taxonomy |
| `source_locator` | recommended | 相关 fixture、contract、doc 或 generated locator |
| `validator_mode` | recommended | 例如 `repo-local-cli`、`source-self-fixture` 等执行模式 |
| `is_aggregate` | yes | 是否为聚合 surface 输出 |
| `subsurface_count` | conditional | aggregate command 聚合的 child surface 数量 |
| `subsurface_results` | conditional | aggregate command 的 child surface evidence 摘要 |

补充规则：

- `surface_label` 必须稳定到可以跨本地与 CI 对比
- `scenario_label` 必须能区分 aggregate surface 与内部 sub-scenario
- `elapsed_ms` 必须对每个 emitted surface 可读，不能只给总时长
- `failure_summary` 可以简短，但不能空到无法诊断
- 若已有 Loom core taxonomy 或 failure kind，surface evidence 必须复用；不得把 repo-specific job name 提升为 core taxonomy

## 4. Aggregate Command Contract

当一个命令一次运行多个 surfaces 时，它是 `aggregate_surface`。

aggregate command 必须：

- 报告自身 aggregate result
- 报告每个 child named surface 的 `surface_label`、`result`、`elapsed_ms`
- 在 child 失败时保留 child failure summary
- 允许调用者判断是哪个 child surface 触发 full gate block

aggregate command 不得：

- 只输出最终 pass/block 而隐藏 child surface
- 把所有 child failure 压成不可读的大段原始日志
- 因为 child surface 未运行就默认其为 pass

## 5. Fast / Full Validation Policy

### 5.1 Fast validation 的允许场景

以下场景可以使用 fast validation：

- 本地迭代时，只验证当前变更直接触及的 regression surface
- PR 准备阶段，需要快速判断当前合同或实现是否击穿某个 surface
- inventory / contract / docs 变更，需要读取 surface contract 是否保持稳定
- review 前的 focused proof，需要补充最小可验证证据

fast validation 的输出必须明确自己是 fast surface proof，而不是 full coverage proof。

### 5.2 Full validation 的必需场景

以下场景必须要求 full validation 或等价 full aggregate proof：

- merge-ready
- release readiness
- source repo 的 full self-check
- 明确声明需要 authoritative bucket coverage 的 closeout / retained validation gate

full validation remains required even when fast surfaces all pass.

### 5.3 与现有 Loom source-surface 的对应关系

当前 Loom source repo 已有稳定 surface vocabulary，可直接作为 policy anchor：

| Surface selector | Policy role |
| --- | --- |
| `contract-only` | fast validation / closeout-friendly contract proof |
| `daily-execution-cli-fast` | fast validation，面向 daily-execution-cli bucket 的常用本地 runtime smoke；不得作为 merge-ready / release proof |
| `daily-execution-cli-full` | authoritative bucket validation，面向 daily-execution-cli bucket 的完整命令与负向 fixture set |
| `bootstrap-regression` | targeted heavier validation，面向 demo/bootstrap regression |
| `distribution-regression` | targeted heavier validation，面向 installer / distribution / release-adjacent regression |
| `review-run` | targeted source-self fixture validation，面向 review-run fixture diagnostics |
| `merge-gate` | targeted source-self fixture validation，面向 PR gate / merge-ready / controlled merge fixture diagnostics |
| `closeout-reconciliation` | targeted source-self fixture validation，面向 closeout / reconciliation fixture diagnostics |
| `source-self-fixture` | heavy fixture surface，面向 Loom source repo 深层行为样本 |
| `full` | authoritative full validation |

其中：

- `contract-only` 默认不是 release proof
- `daily-execution-cli-fast` 只运行 `runtime-smoke` 子集，用于本地迭代；`daily-execution-cli-full` 和既有 `merge-gate` surface 必须继续覆盖 daily-execution-cli 的完整命令 set、fact-chain/provenance 负向 fixture、authoring fixture 与 merge-ready 相关检查
- `review-run`、`merge-gate`、`closeout-reconciliation` 是 `source-self-fixture` 的可聚合 child surfaces
- `source-self-fixture`、`bootstrap-regression`、`distribution-regression` 是可选 targeted heavy surfaces，不自动等于 full
- `full` 仍是 source profile 默认 authoritative aggregate validation

### 5.4 Merge-ready / release authority

merge-ready 与 release 判断必须消费 full validation 或显式等价的全量 surface aggregation。

以下证据单独存在时都不够：

- 单个 named surface pass
- 单次 fast validation pass
- closeout-friendly contract-only pass
- 历史 stale run

### 5.5 Daily execution CLI evidence requirements

`daily-execution-cli-fast` 与 `daily-execution-cli-full` 必须在证据中保留不同角色：

| Surface | Expected evidence | Valid consumers | Not valid for |
| --- | --- | --- | --- |
| `daily-execution-cli-fast` | command、surface selector、`runtime-smoke` scope、result、elapsed time、failure summary when blocked、current `HEAD` / PR head binding | local iteration、focused proof、pre-review context、troubleshooting a touched runtime surface | merge-ready pass、release / no-release judgment、full bucket closeout basis |
| `daily-execution-cli-full` | command、surface selector、full bucket scope、result、elapsed time、child surface or scenario failure summary、current `HEAD` / PR head binding | authoritative daily-execution-cli bucket proof, merge-ready evidence input, release/no-release evidence input, closeout retained validation input | replacing review, PR metadata preflight, hosted checks, fact-chain, controlled merge, or scheduler-owned gates |

When a Work Item cites both surfaces, the validation summary must state whether
the fast run is only focused proof and whether the full run is the retained
authority. If the full run is intentionally omitted, the summary must identify
the owning gate or scope rationale that makes full daily-execution-cli coverage
not required for that item; otherwise merge-ready must treat the evidence as
incomplete.

Troubleshooting signals should stay surface-specific:

- `daily-execution-cli-fast` failure means the touched runtime smoke path is
  broken or the local runtime/bootstrap fixture is unreadable; rerun the same
  fast surface after fixing the focused cause.
- `daily-execution-cli-full` failure means the full daily-execution-cli bucket
  is not authoritative for merge-ready; classify the failed child scenario or
  fixture group before rerunning heavy validation.
- Hosted `repo-local-cli` or `loom-check` failure is a host/CI readback signal,
  not proof that the local fast or full run was skipped; read the hosted command
  group, PR head, and required-check freshness separately.
- PR metadata, fact-chain, review, release/no-release, and scheduler-owned gate
  failures must remain separate findings. They cannot be repaired by rerunning
  `daily-execution-cli-fast` or `daily-execution-cli-full` alone.

### 5.6 Demo bootstrap evidence requirements

`demo-bootstrap` 是 Loom source repo 的 checked-in demo fixture
validation bucket。它的 aggregate entry remains:

```bash
python3 tools/check_demo_bootstrap_fixture.py
make loom-demo-new-project-check
```

The aggregate command must continue to fail closed and emit child evidence for
all current named surfaces when `--show-surface-evidence` is requested. The
targeted local surface entries are:

| Surface | Command | Diagnostic role | Closeout evidence role |
| --- | --- | --- | --- |
| `demo-bootstrap-generation` | `python3 tools/check_demo_bootstrap_fixture.py --surface generation` or `make loom-demo-new-project-generation-check` | Rebuilds the demo bootstrap in an isolated target and isolates bootstrap command failure from tree drift. | Focused proof for generation behavior; not a replacement for aggregate demo bootstrap evidence. |
| `demo-bootstrap-canonicalization` | `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization` or `make loom-demo-new-project-canonicalization-check` | Verifies host/runtime dynamic `init-result.json` sections are canonicalized before drift comparison. | Focused proof for dynamic-field canonicalization diagnostics. |
| `demo-bootstrap-fixture-drift` | `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift` or `make loom-demo-new-project-fixture-drift-check` | Compares the isolated generated tree with the stable checked-in `examples/new-project` fixture after canonicalization. | Focused proof for stable fixture drift. |
| `demo-bootstrap-examples-cleanliness` | `python3 tools/check_demo_bootstrap_fixture.py --surface cleanliness` or `make loom-demo-new-project-cleanliness-check` | Proves the validation run leaves tracked `examples/new-project` status unchanged. | Focused proof for fixture cleanliness and workspace residue. |

Parent closeout for the demo bootstrap split must retain both layers:

- focused evidence for each named surface above, bound to the current PR head;
- aggregate evidence from `tools/check_demo_bootstrap_fixture.py --surface
  aggregate` or `make loom-demo-new-project-check`, so generation,
  canonicalization, fixture drift, and examples cleanliness stay consumed as one
  fail-closed bucket.

The stable fixture must only be refreshed intentionally through:

```bash
make loom-demo-new-project-sync
```

Running a targeted or aggregate demo bootstrap validation command must not dirty
tracked `examples/new-project` paths.

## 6. Command Matrix Consumption

命令矩阵与后续 CLI/test tooling 应遵守：

- command help / matrix 需要能表达 fast vs full surface 选择
- local aliases 或 repo-local commands 可以暴露 focused surface selector
- aggregate validation output 必须保留 child surface evidence
- docs / tests 只能引用本合同的词表，不再各自重写定义

本合同当前只冻结 shared semantics，不新增具体 CLI 子命令名。

## 7. Test And Verification Convention

合同变更至少要验证：

```bash
git diff --check
```

若本批变更只涉及 docs / matrix / contract 引用，最小 focused verification 可停留在：

- `git diff --check`
- 必要的 cross-reference / wording readback

若后续实现触及 CLI/test tooling，则应补：

- `python3 tools/check_cli_contract.py`
- 或对应 `loom_check --profile source --source-surface ...` focused surface checks

是否运行 full source self-check 取决于实现是否改变 runtime / tooling 行为；纯合同冻结不默认要求 full heavy validation。
