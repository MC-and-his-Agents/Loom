# WI-1742 Contracts

## Ship Closeout Regression Contract

- Ordinary light delivery must complete `ship --apply` with `creates_closeout_pr=false` and `closeout_mode=host_only`.
- Ordinary standard delivery with no release, reinforced, or versioned terminal triggers must also complete without creating a closeout PR.
- After controlled merge, `ship --apply` must consume:
  - host reconciliation sync with `--apply`;
  - closeout check;
  - issue `CLOSED`;
  - PR `MERGED`;
  - merge commit OID;
  - target branch contains merge commit.
- Release or versioned terminal carrier input must block before merge and surface `loom closeout queue status --item <id> --issue <n> --pr <n> --json` as the next action.

## Non-Contract

WI-1742 does not define release publish, npm publish, or GitHub Release behavior. Those remain #1743.
