# WI-1232 Plan

1. Add an explicit idle branch in fact-chain inspection that validates the frozen idle entry-point contract and compares the idle status surface against derived inactive active-only fields.
2. Add a status read path that returns a non-blocking idle payload before active-only context loading.
3. Make governance surface detection idle-aware so carrier summaries and gate starter entries do not fall back to `INIT-0001`.
4. Synchronize repo-local and generated runtime copies that expose the changed read surfaces.
5. Add focused CLI contract fixtures for valid idle, active locator drift, and active stale status surface behavior.
6. Run minimal compile, focused behavior checks, current fact-chain/status readback, PR metadata readback, and hosted checks readback before scheduler gate handoff.
