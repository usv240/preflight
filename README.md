# Preflight — prove high-stakes plans before they touch a person

> **UiPath AgentHack 2026 · Track 3 — UiPath Test Cloud**
> *Branch reality. Break the plan. Prove the outcome. Then act.*

Preflight forks a live case into a disposable digital twin, compiles the case's promises into
**executable outcome obligations**, unleashes adversarial agents to break every dependency, **proves the
outcome through UiPath Test Cloud**, and lets the real action proceed only after the plan survives
rehearsal — or a human accepts a documented exception in **Action Center**, with **UiPath Maestro** as the
governing release gate.

Demo domain: **safe hospital discharge** (100% synthetic data). Preflight validates **operational
readiness only** — it never diagnoses, prescribes, or changes medication, and a clinician stays in control.

---

## The business problem
Enterprises automate consequential, often **irreversible** actions — discharging a patient, settling a
claim, running payroll, releasing a shipment. Today these execute **optimistically**: the workflow assumes
every downstream dependency will hold. When one silently fails — the pharmacy is closed when transport
arrives, a medication isn't covered, a follow-up was "recommended" but never booked — the failure is
discovered *after* it has already harmed someone. **Software is tested before production; human-impacting
plans are not.** Preflight closes that gap.

## What makes it different
- vs. **agent-evaluation tools** (Giskard/LangSmith/Foundry): those test *the agent/model*. Preflight
  tests *the planned real-world outcome of a specific case* and **gates the real action**.
- vs. **UiPath Process Simulation**: that predicts aggregate efficiency from historical data. Preflight
  proves *this one live case's* safety/outcome obligations and produces an executable release gate.

## How it works (the pattern)
```
Live case → FORK twin → COMPILE obligations → CHAOS attack → PROVE (Test Cloud)
          → [GATE] ──fail→ Action Center (human remedy) → re-test ↺
                    └─pass→ Release for real execution → LEARN (regression scenario)
```

## UiPath components used
| Component | Role |
|---|---|
| **Test Cloud / Test Manager** | Core engine — per-case test set, execution, results, traceability (the gate's proof). |
| **Maestro (BPMN + DMN)** | Orchestrates the rehearsal; DMN is the hard release gate; agents = Service Tasks, human = User Task. |
| **Agent Builder** | Low-code agents: the Obligation Compiler (Context-Grounded on policy) and Remedy Proposer. |
| **Coded agent** (+ optional CrewAI/LangChain governed by UiPath) | The chaos / red-team engine that searches failure combinations. |
| **Action Center** | Human-in-the-loop: nurse approves/edits a remedy or accepts a documented exception. |
| **Data Service** | Source of truth for cases, obligations, results, decisions, evidence, regression library. |
| **API Workflows** | Synthetic pharmacy / insurer / transport / scheduling / notification adapters. |
| **UiPath Apps** | The frontend — every value bound to Data Service (no hardcoded data) + an `[i]` help/tour system on every screen. |
| **UiPath for Coding Agents (Claude Code)** | Used to build the engine — see [docs/CODING_AGENT_EVIDENCE.md](docs/CODING_AGENT_EVIDENCE.md). |

**Agent types used: BOTH** — low-code (Agent Builder) **and** coded agents, plus an optional external
framework (CrewAI/LangChain) governed by UiPath, plus a coding agent (Claude Code) used to build it.

Full platform mapping: [docs/UIPATH_MAPPING.md](docs/UIPATH_MAPPING.md).

---

## This repository
This repo contains the **platform-independent reference engine** for Preflight: the exact logic
(compiler, chaos/red-team search, obligation evaluation, gate, remedy, evidence) that is ported onto the
UiPath platform. It runs with **zero third-party dependencies** so judges can verify the core behavior in
seconds, then watch it run on UiPath in the demo video.

```
preflight/
├── engine/            # the reference engine (pure standard library)
│   ├── models.py      # entities = Data Service schema
│   ├── adapters.py    # stub services = API Workflows
│   ├── compiler.py    # case-to-test compiler = Agent Builder agent
│   ├── chaos.py       # chaos/red-team agent = coded agent
│   ├── evaluator.py   # obligation execution = Test Cloud
│   ├── remedy.py      # remedy proposer = Agent Builder agent
│   ├── evidence.py    # evidence pack
│   └── orchestrator.py# the flow = Maestro process
├── data/
│   ├── cases/         # synthetic discharge cases (golden, clean, coverage)
│   ├── policy/        # discharge readiness policy (compiler grounding)
│   └── help/          # [i] help + tour content (backend-served)
├── scripts/run_demo.py
├── tests/test_end_to_end.py
└── docs/              # UiPath mapping + coding-agent evidence
```

## Prerequisites
- Python 3.10+ (developed on 3.12). No `pip install` needed for the reference engine.

## Run it
```bash
cd preflight

# Full narrated rehearsal of the golden case (blocks -> remedy -> re-test -> release)
python scripts/run_demo.py golden_case

# Other cases
python scripts/run_demo.py case_clean      # passes first time (green path)
python scripts/run_demo.py case_coverage   # multiple failures, then recovers

# Tests
python tests/test_end_to_end.py            # or: python -m pytest
```

Expected: `golden_case` is **BLOCKED** on the critical "medication collectable" obligation
(transport arrives 17:15, pharmacy closes 17:00), the nurse approves a 24h-pharmacy remedy, the re-test
passes at 100%, the plan is **RELEASED**, and an evidence pack is written to `out/`.

## Setup on UiPath Automation Cloud
See [docs/UIPATH_MAPPING.md](docs/UIPATH_MAPPING.md) for the component-by-component build/run guide
(Data Service entities, Agent Builder agents, Test Cloud test sets, Maestro process, Action Center app,
UiPath Apps frontend).

## Safety & data
- 100% synthetic data; no real PHI/PII anywhere.
- Preflight validates **operational readiness only**; it does **not** diagnose, prescribe, or change
  medication. Every clinical decision stays with a human.

## License
MIT — see [LICENSE](LICENSE).
