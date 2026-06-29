# Preflight — prove high-stakes plans before they touch a person

> **UiPath AgentHack 2026 · Track 3 — UiPath Test Cloud**
> *Branch reality. Break the plan. Prove the outcome. Then act.*

Preflight is an **agentic software-testing system** for the *outcome of a live case*. Before a high-stakes
plan executes, it compiles the governing policy into **executable Test Manager test cases**, unleashes an
adversarial agent to break every dependency, proves each obligation, records an auditable **evidence pack**
with the causal failure chain in **UiPath Data Fabric**, and **gates release** behind a human.

Demo domain: **safe hospital discharge** (100% synthetic data). Preflight validates **operational readiness
only** — it never diagnoses, prescribes, or changes medication, and a clinician approves every change.

---

## The business problem
Enterprises automate consequential, often **irreversible** actions — discharging a patient, settling a
claim, running payroll, releasing a shipment. They execute **optimistically**: the workflow assumes every
downstream dependency will hold. When one silently fails — the pharmacy is closed when transport arrives, a
medication isn't covered, a follow-up was "recommended" but never booked — the failure is found *after* it
has already harmed someone. **Software is tested before production; human-impacting plans are not.**

## What makes it different
- vs. **agent-evaluation tools** (Giskard/LangSmith/Foundry): those test *the agent/model*. Preflight tests
  *the planned real-world outcome of a specific case* and **gates the real action**.
- vs. **UiPath Process Simulation**: that predicts aggregate efficiency from historical data. Preflight
  proves *this one live case's* outcome obligations and produces an executable release gate.

## How it works
```
Live case → COMPILE policy into outcome obligations
          → GENERATE a Test Manager test case per obligation   (Test Cloud)
          → CHAOS agent mutates dependencies, finds cross-system cascades
          → PROVE each obligation → evidence pack + causal chain (Data Fabric)
          → [GATE] Critical fail → human remedy → re-test ↺
                   all pass     → Release → LEARN regression scenario
```

The hidden flaw in the demo case: transport arrives **17:15**, the pharmacy closes **17:00**, so a required
medication can never be collected — a three-system cascade no static checklist catches.

## UiPath components used
| Component | Role in Preflight |
|---|---|
| **UiPath Test Manager (Test Cloud)** | Agentic test-case generation — one severity-tagged test case per obligation, under the `Preflight` project. All 9 test cases linked to the governing **Requirement** (PRF:10 "Safe Discharge Readiness Policy") for full traceability from policy → test case. |
| **UiPath Data Fabric (Data Service)** | System of record: `DischargeCase`, `Obligation`, `EvidencePack`, `HumanDecision`, `HelpContent`. Live query/insert/update via REST. No hardcoded data. |
| **UiPath Agent Builder (Studio Web)** | Published low-code **Obligation Compiler** agent — turns a discharge plan + policy into structured obligations (the "requirements → test scenarios" step). |
| **Coded agent** (UiPath for Coding Agents / Claude Code) | The rehearsal engine: compiler, chaos search, evaluator, remedy, evidence + the Data Fabric / Test Manager integrations. |
| **External agent framework — LangGraph (LangChain)** | The adversarial **red-team agent** (`plan→attack→judge→record` StateGraph), governed by UiPath: reads the case and writes findings back to Data Fabric. |
| **UiPath Apps + live dashboard** | A backend-driven UI (App Studio app + a live web dashboard reading Data Fabric/Test Manager) with an `[i]` help system served from the `HelpContent` entity. |
| **UiPath Identity / External Applications** | OAuth client-credentials auth for all platform API access. |

**Agent types: BOTH (and more).** Low-code (**Agent Builder** Obligation Compiler) **+** coded (rehearsal
engine, built via **UiPath for Coding Agents**) **+** an **external framework** (LangGraph red-team agent)
governed by UiPath. Claude Code (coding agent) built the solution — see
[docs/CODING_AGENT_EVIDENCE.md](docs/CODING_AGENT_EVIDENCE.md).

**Production roadmap (designed):** wrap the flow in a **Maestro BPMN** process with a **DMN** release gate
and an **Action Center** nurse task; report results into Test Cloud via Orchestrator Test Automation.

---

## Repository layout
```
preflight/
├── engine/            # platform-independent reference engine (pure stdlib, 6 passing tests)
│   ├── models.py compiler.py chaos.py evaluator.py remedy.py evidence.py orchestrator.py
├── integration/       # UiPath platform integration (live)
│   ├── uipath_client.py   # OAuth + Data Fabric + Test Manager REST client
│   ├── seed_data.py       # seed synthetic cases + help content into Data Fabric
│   ├── rehearse_case.py    # rehearsal coded agent: block / release stages (writes back to Data Fabric)
│   ├── tm_sync.py         # generate Test Manager test cases from a case's obligations
│   ├── requirements_sync.py # link test cases to governing Requirement in Test Manager
│   ├── redteam_agent.py   # external-framework (LangGraph) red-team agent, governed by UiPath
│   ├── control_view.py    # live rehearsal status read from Data Fabric + Test Manager
│   └── build_dashboard.py # generate the live web dashboard (HTML) from Data Fabric + Test Manager
├── data/              # synthetic cases, discharge policy, help/tour content
├── scripts/run_demo.py  tests/test_end_to_end.py
└── docs/              # UiPath mapping, coding-agent evidence, demo script, Devpost, deck
```

## Prerequisites
- Python 3.10+ (no third-party packages required).
- For the **platform** parts: a UiPath Automation Cloud tenant with Data Fabric + Test Manager, an External
  Application (client-credentials) with `DataFabric.Data.*` and `TM.*` scopes, and a `Preflight` Test Manager
  project. Copy `integration/.env.example` → `integration/.env` and fill in your App ID/secret.

## Run it
**Offline reference engine (no platform needed):**
```bash
cd preflight
python tests/test_end_to_end.py            # 6/6 tests
python scripts/run_demo.py golden_case      # narrated block → remedy → re-test → release
```

**On the UiPath platform (with `.env` configured):**
```bash
python integration/seed_data.py            # seed Data Fabric (one-time)
python integration/tm_sync.py              # generate Test Manager test cases
python integration/requirements_sync.py    # link test cases to governing Requirement (policy traceability)
python integration/rehearse_case.py block   # rehearse → catch flaw → BLOCK the case
python integration/redteam_agent.py         # external-framework (LangGraph) red-team attacks (writes findings to Data Fabric)
python integration/build_dashboard.py       # generate the live web dashboard (out/preflight_dashboard.html)
python integration/control_view.py          # live status: RED / Blocked + causal chain
python integration/rehearse_case.py release # apply approved remedy → re-test → RELEASE
python integration/build_dashboard.py        # regenerate → dashboard flips to GREEN / Released
```
Open `out/preflight_dashboard.html` in a browser for the backend-driven UI with `[i]` help.
External-framework agent needs `pip install -r integration/requirements.txt` (langgraph).

## Safety & data
100% synthetic data; no real PHI/PII. Preflight validates **operational readiness only**; it does **not**
diagnose, prescribe, or change medication. Every clinical decision stays with a human.

## License
MIT — see [LICENSE](LICENSE).
