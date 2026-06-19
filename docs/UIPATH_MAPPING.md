# UiPath platform mapping

How the reference engine in this repo maps to UiPath Automation Cloud components for the AgentHack
submission. The offline engine is the contract; the UiPath build implements the same contract on-platform.

## Engine module → UiPath component
| Reference module | UiPath implementation | Notes |
|---|---|---|
| `engine/models.py` | **Data Service** entities | `DischargeCase`, `PlanItem`, `Obligation`, `ChaosScenario`, `TestRun`, `HumanDecision`, `EvidencePack`, `RegressionScenario`. |
| `engine/adapters.py` | **API Workflows** | `PharmacyService`, `InsurerService`, `TransportService`, `SchedulingService`, `NotificationService`. Read/write `DependencyState`. |
| `engine/compiler.py` | **Agent Builder** agent (low-code) | Grounded on `data/policy/discharge_policy.md` via **Context Grounding** so it cannot invent policy. |
| `engine/chaos.py` | **Coded agent** (optionally CrewAI/LangChain governed by UiPath) | Searches dependency mutations for cascading failures; emits causal chains. |
| `engine/evaluator.py` | **Test Cloud / Test Manager** | Each obligation = a parameterized test case; a rehearsal = a test set execution. |
| `engine/remedy.py` | **Agent Builder** agent (low-code) | Proposes operational remedies only; output goes to Action Center. |
| `engine/orchestrator.py` | **Maestro** process (BPMN + DMN) | Service Tasks (agents), User Task (nurse), DMN = the gate, loop = re-test. |
| `engine/evidence.py` | **Data Service** + **UiPath Apps** evidence screen | Causal chains + audit trail + verdict. |
| `data/help/help_content.json` | **Data Service** `HelpContent` entity | Bound to the `[i]` info button + guided tour in UiPath Apps. |

## Maestro process (BPMN) — node by node
1. **Start** — case reaches `ReadyForDischarge` (Data Service trigger).
2. **Service Task: Fork twin** — coded workflow duplicates the case (`isShadow=true`).
3. **Service Task: Compile obligations** — Agent Builder compiler → `Obligation` rows.
4. **Service Task: Generate test set** — map obligations → Test Manager test cases (per case).
5. **Service Task: Chaos search** — coded/external agent → `ChaosScenario` rows.
6. **Service Task: Run Test Cloud** — execute test set; poll results (~20s); write `TestRun`.
7. **DMN Gate** — decision table on results: any **Critical** fail ⇒ **Block**; else evaluate.
   - **Pass** → **Release** (execute real plan) → `EvidencePack(verdict=green)`.
   - **Block** → **User Task (Action Center)** with Remedy Proposer suggestion.
8. **After human decision** → apply remedy to twin → **loop to step 6** (re-test).
9. **Learn** → write `RegressionScenario` on resolution.

### Gate policy (matches `discharge_policy.md`)
- Any **Critical** obligation failing ⇒ hard **Block** (not waivable by exception).
- Non-critical only ⇒ human may approve remedy or **accept a documented exception** with named accountability.

## Frontend (UiPath Apps) — no hardcoded data
Every control's Data Source binds to a Data Service entity or a process call:
- Dashboard table → `DischargeCase`; status/score are live fields.
- Case detail → `PlanItem` + `Obligation` filtered by `caseId`.
- Rehearsal (live) → process state + `ChaosScenario` / `TestRun`.
- Evidence → `EvidencePack` (+ causal graph from `causalChain`).
- Nurse review → live **Action Center** task + `HumanDecision`.
- Regression library → `RegressionScenario`.
- Every screen: `[i]` info button + "Take the tour", content bound from the `HelpContent` entity.

## Coding-agent feasibility spike (run the hour Labs access lands)
Two load-bearing assumptions to verify (fallbacks in IMPLEMENTATION_PLAN.md §10):
1. Create/assign Test Manager test cases via API (else: pre-create a parameterized test set; API only
   triggers + reads results).
2. Maestro DMN can hard-block release on a Test Cloud result (else: coded decision step + status flag).
