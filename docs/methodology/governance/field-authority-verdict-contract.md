# Field Authority And Independent Verdicts

`loom-field-authority-verdict/v1` keeps delivery governance from becoming a
claim of product completion. It is a read-only contract, not a registry or a
repository carrier.

| Field | Owner | Freshness | Values |
| --- | --- | --- | --- |
| `work_item_scope` | GitHub Issue | live readback | host-defined scope |
| `delivery_state` | GitHub delivery host facts | live readback | `not_evaluated`, `implementing`, `pr_ready`, `merged`, `delivery_closed_out` |
| `product_acceptance` | product acceptance adapter | adapter-declared | `not_evaluated`, `not_required`, `pending`, `passed`, `failed`, `blocked`, `waived` |
| `reconciliation_state` | reconciliation evaluator | current evaluation | `not_evaluated`, `pending`, `consistent`, `drifted` |
| PR/head/check/merge | GitHub Pull Request | live readback | host-defined facts |
| workstation session | workstation | session-local | local execution context |
| historical audit | Git or Actions history | immutable history | retained historical facts |

The three verdict fields are orthogonal. A merged PR, a green delivery gate,
or carrier closeout never changes `product_acceptance`; product acceptance is
not evaluated by the delivery gate. A reconciliation verdict reports agreement
between its inputs and never upgrades delivery or product acceptance.

## Typed locators

The canonical locator is `owner/repo/type/id`, which is globally unique across
repositories and object types. Supported types are `issue`, `phase`, `fr`,
`work_item`, `pr`, and `project`; a bare number is never accepted. New output
and PR bindings always render the canonical form, for example
`MC-and-his-Agents/Loom/work_item/2043`.

Legacy `type:number` values remain read-compatible through the v0.30.x line so
existing retained evidence can be consumed and rewritten. They are never
rendered by current code and will be rejected from v0.31.0. PR metadata already
requires the canonical form; compatibility only applies to non-authoritative
legacy reads.

## PR intent and failure output

An implementation PR carries one typed `Work Item: owner/repo/work_item/id` plus
the policy intent that GitHub cannot supply (governance intensity, change
class, suite path, review/release policy). Branch, head SHA, checks, merge
commit, and merge state are read directly from GitHub and are rejected when
authored in either the metadata block or as PR binding truth. Gate failures use
`loom-failure-envelope/v1`: exactly one primary cause names its failure
domain, cause class, owner, retryability, transience, details, causal
predecessors, and one remediation command. Additional diagnostics are listed
only as `consequences` bound to that primary cause; fallback is remediation,
not another top-level failure. The delivery gate still never evaluates
product acceptance, while the public acceptance adapter uses the independent
`product_acceptance` failure domain.

## Lifecycle admission

`loom route --issue <FR>` remains the planning/proposal entrypoint and only
creates native Work Items with explicit `--apply`. `loom-host-lifecycle-admission/v1`
consumes that same native admission result before an execution entrypoint acts
on the explicit `--fr <FR>` locator:

```text
loom build --fr <FR> ...
loom ship --fr <FR> ...
loom pre-review --fr <FR> ...
loom closeout --fr <FR> ...
```

`--issue` remains the existing Work Item/host-binding locator and does not add
this lifecycle gate. This avoids treating an untyped bare issue number as an
FR; only `--fr` invokes FR breakdown admission at execution time.

- A planning FR can pass without a Work Item.
- An executing FR without a native typed Work Item child returns
  `needs_breakdown` with one `primary_remediation`; it performs no carrier
  write. This is independent of a route plan marker, so a valid native WI is
  never rejected merely because it was created outside a previous Loom apply.
- An existing Work Item produces `not_applicable` for this additional check,
  so the admission contract adds no new gate.

This contract does not implement a product acceptance adapter, create a
review ledger, or authorize WebEnvoy runtime actions.
