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
predecessors, and one remediation command. `consequences` contains only
diagnostics causally bound to that primary; independent lower-priority facts
use `suppressed_diagnostics`. The deprecated v1 `secondary_causes` field
remains a compatibility alias for both lists through v0.30 and is removed no
earlier than v0.31 after consumers migrate. Public consumers accept and
normalize legacy v1, but malformed assertions fail closed. Fallback is
remediation, not another top-level failure. The delivery gate still never
evaluates product acceptance, while the public acceptance adapter uses the
independent `product_acceptance` failure domain.

## Lifecycle admission

`loom route --issue <FR>` remains the planning/proposal entrypoint and only
creates native Work Items with explicit `--apply`. `loom-host-lifecycle-admission/v1`
consumes that same native admission result before an execution entrypoint acts
on the host subject. An explicit `--fr <FR>` remains compatible, while the
default path classifies `--issue <work-item-or-fr>` so omitting `--fr` cannot
bypass admission:

```text
loom build --issue <work-item-or-fr> ...
loom ship --issue <work-item-or-fr> ...
loom pre-review --issue <work-item-or-fr> ...
loom closeout --issue <work-item-or-fr> ...
```

The GitHub issue type/labels determine whether the subject is a Phase, FR, or
Work Item. The caller does not choose that type by selecting a flag. If an
execution entrypoint has neither an explicit FR nor a primary issue, Loom
reads the explicit PR or current branch, resolves exactly one PR, and consumes
that PR's native GitHub closing-issue relation. It never treats PR body text as
subject proof. Missing, unreadable, or ambiguous host context fails closed with
`missing_subject` before reading repository carriers.

- A planning FR can pass without a Work Item.
- A Phase cannot be the primary implementation subject.
- An FR with existing Work Items returns `work_item_required`; the caller must
  bind one Work Item rather than execute the FR itself.
- An executing FR without a native typed Work Item child returns
  `needs_breakdown` with one `primary_remediation`; it performs no carrier
  write. This is independent of a route plan marker, so a valid native WI is
  never rejected merely because it was created outside a previous Loom apply.
- An existing Work Item produces `not_applicable` for this additional check,
  so the admission contract adds no new gate.

This contract does not implement a product acceptance adapter, create a
review ledger, or authorize WebEnvoy runtime actions.
