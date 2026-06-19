# Coding-agent usage & evidence (AgentHack bonus)

Per the AgentHack rules, this documents (a) which coding agent was used, (b) how it contributed, and
(c) verifiable evidence that the output is meaningfully integrated.

## (a) Tool
**Claude Code** (Anthropic's CLI coding agent, model Claude Opus 4.8), used via **UiPath for Coding
Agents** as the supported coding-agent workflow.

## (b) How it contributed
Claude Code designed and generated the Preflight reference engine — the logic that is then ported onto
the UiPath platform — and the synthetic data and tests that prove it works:

| Area | What the coding agent produced |
|---|---|
| Domain model | `engine/models.py` — entities mirroring the Data Service schema. |
| Stub adapters | `engine/adapters.py` — pharmacy/insurer/transport/scheduling/notification (= API Workflows). |
| Case-to-test compiler | `engine/compiler.py` — policy-grounded obligation generation (= Agent Builder agent). |
| Chaos / red-team agent | `engine/chaos.py` — dependency-mutation search + causal-chain construction (= coded agent). |
| Obligation evaluator | `engine/evaluator.py` — obligation execution + readiness scoring (= Test Cloud). |
| Remedy proposer | `engine/remedy.py` — operational-only remedies (= Agent Builder agent). |
| Orchestrator | `engine/orchestrator.py` — fork→compile→chaos→prove→gate→remedy→re-test→release→learn (= Maestro). |
| Evidence pack | `engine/evidence.py` — auditable proof with causal chains. |
| Synthetic data | `data/cases/*.json`, `data/policy/discharge_policy.md`, `data/help/help_content.json`. |
| Tests + demo | `tests/test_end_to_end.py` (6 passing tests), `scripts/run_demo.py`. |

The coding agent also produced the architecture and platform mapping in `docs/UIPATH_MAPPING.md` and the
project design docs.

## (c) Verifiable evidence
- **This entire engine is the output** — every file under `engine/`, `data/`, `tests/`, `scripts/` was
  generated through the coding-agent session and is integrated into the working solution (the tests pass
  and the demo runs end-to-end).
- **Reproducible proof of integration:** run `python tests/test_end_to_end.py` (6/6 pass) and
  `python scripts/run_demo.py golden_case` (blocks → remedy → re-test → release).
- **Prompt/session log:** see `docs/SESSION_LOG.md` (exported transcript excerpts) and the demo video,
  which shows the coding agent being used to build/extend the solution.
- **Commit history** of this repository reflects the agent-authored changes.

> Note: the on-platform UiPath build (Agent Builder agents, Test Cloud test sets, Maestro process,
> Action Center app, UiPath Apps) is assembled on UiPath Automation Cloud and demonstrated in the video;
> this repo is the portable engine + the verifiable coding-agent artifact.
