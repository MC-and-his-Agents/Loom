# Research

- Finding: closeout check for issue #1544 was blocked because WI-1529 and WI-1540 historical recovery text mentioned `#1544`, while WI-1544 had canonical ownership evidence.
- Finding: treating all issue mentions equally over-weights stale downstream lists and makes terminal closeout readback brittle.
- Decision: canonical issue-number carrier path, canonical item id, and exact associated artifact issue locator outrank historical recovery text references.
- Decision: weak-only lookup remains supported for legacy retained carriers when no stronger competing candidate exists.
- Source: #1542, #1544 closeout readback on `origin/main@0bd2cbfa`, `test/retained_item_lookup_test.py`.
