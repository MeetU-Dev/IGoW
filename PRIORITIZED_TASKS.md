IGoW Prototype — Prioritized Workplan

This document records prioritized next steps for the IGoW V1 prototype, ordered by impact and estimated difficulty.

1) Critical fixes (low effort, high impact)
- Fix `mine_block` attempts count (report precise attempts = nonce+1).
- Ensure `Block.verify()` recomputes and validates `fingerprint` (SHA-256 of `image_hex`).
- Ensure `IGoWChain.verify_chain()` compares recomputed fingerprints, not only stored values.
- Rationale: closes small correctness gaps that improve tamper detection reliability.

2) Input validation & safety (low-medium effort)
- Add explicit validation for `difficulty`, `width`, `height` ranges and types.
- Add checks to prevent out-of-bounds indexing when flattening pixel channels.
- Rationale: reduces accidental crashes and ambiguous behavior.

3) Persistence & rollback (medium effort)
- Add JSON save/load for `IGoWChain` and `Block` objects.
- Add `snapshots/` and a simple `save_snapshot()` utility to store a timestamped JSON archive.
- Rationale: provides a quick rollback mechanism and audit trail for the prototype.

4) Tests & CI (medium effort)
- Add unit tests for `generate_image_hash`, `check_difficulty`, `Block.verify()`, `IGoWChain.verify_chain()`.
- Add a lightweight test harness and example outputs.
- Rationale: prevents regressions while we harden the code.

5) UX and separation (medium effort)
- Separate library functions from demo/CLI code.
- Improve printed reports (fix truncated fields or clearly label them as summaries).
- Rationale: clearer structure for reuse and demos.

6) Performance & scaling (medium-high effort)
- Add optional parallel mining worker and benchmarking tool.
- Consider more realistic difficulty scaling or larger images for stronger PoW.
- Rationale: evaluate resource needs and feasibility for stronger security.

7) Security & consensus (high effort)
- Add signatures for blocks (creator identity), trusted checkpoints, and network consensus rules.
- Introduce fork/reorg handling and canonical chain selection.
- Rationale: turn the prototype into a resistant, distributed system.

8) Documentation (low effort)
- Update README with usage, design notes, threat model, and developer setup.

Next actions
- I can start implementing item (1) Critical fixes and (3) Persistence snapshot in small, reviewable patches.
- Tell me which item to start first; I will implement it, run tests, and commit the change.
