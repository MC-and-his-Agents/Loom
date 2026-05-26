# WI-1066 Plan

1. Read #1066, #1064/#1065 closeout evidence, and current CLI plugin/SKILLS surfaces.
2. Replace `loom host install/verify` installer-shim delegation with CLI-native plugin/SKILLS payload install and verification.
3. Make `loom skills sync/check --target` operate on target repositories, not only the source repository.
4. Teach installed-surface detection to classify installed-state-owned plugin/SKILLS payloads as current.
5. Add CLI contract tests for install, verify, skills check, and detect current classification.
6. Run local validation, open PR, consume PR and merge commit checks, and close #1066 with evidence for #1067.
