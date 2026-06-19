# Coding-agent build session log

A high-level, honest record of how the Preflight reference engine was built with **Claude Code**
(Claude Opus 4.8) via UiPath for Coding Agents. Add exported transcript excerpts / screenshots here
before submission as additional evidence (rules accept a prompt log, screenshots, or a README section).

## Build order (each step generated and then verified)
1. Repo scaffold — `LICENSE` (MIT), `.gitignore`, package layout.
2. `engine/models.py` — domain entities mirroring the Data Service schema.
3. `engine/adapters.py` — synthetic pharmacy/insurer/transport/scheduling/notification services.
4. Synthetic data — `data/cases/{golden_case,case_clean,case_coverage}.json`,
   `data/policy/discharge_policy.md`, `data/help/help_content.json`.
5. `engine/loader.py` — data loading.
6. `engine/compiler.py` — policy-grounded case-to-test compiler.
7. `engine/evaluator.py` — obligation execution + readiness scoring (Test Cloud stand-in).
8. `engine/chaos.py` — chaos/red-team mutation search + causal-chain construction.
9. `engine/remedy.py` — operational-only remedy proposer.
10. `engine/evidence.py` — evidence pack builder.
11. `engine/orchestrator.py` — full fork→compile→chaos→prove→gate→remedy→re-test→release→learn flow.
12. `scripts/run_demo.py` — narrated demo runner.
13. `tests/test_end_to_end.py` — 6 end-to-end tests.

## Verification (reproducible)
- `python tests/test_end_to_end.py` → **6/6 tests passed**.
- `python scripts/run_demo.py golden_case` → case **BLOCKED** on the critical "medication collectable"
  obligation (transport arrives 17:15 vs pharmacy closes 17:00) → nurse approves 24h-pharmacy remedy →
  re-test **100%** → **RELEASED** → evidence pack written; 8 regression scenarios learned.

## Honest scope note
This repo is the portable engine and the verifiable coding-agent artifact. The on-platform UiPath build
(Agent Builder agents, Test Cloud test sets, Maestro process + DMN gate, Action Center app, UiPath Apps
frontend) is assembled on UiPath Automation Cloud and shown in the demo video.
