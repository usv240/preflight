# Preflight — presentation deck content (paste into the official template)

> ~10 slides. Keep text sparse on-slide; speaker notes in *italics*.

## Slide 1 — Title
**Preflight**
Prove high-stakes plans before they touch a person.
UiPath AgentHack 2026 · Track 3 — UiPath Test Cloud · Team Preflight
*Branch reality. Break the plan. Prove the outcome. Then act.*

## Slide 2 — The problem
Enterprises automate **irreversible** actions — discharge, claims, payroll, shipments.
They execute **optimistically**. A hidden dependency fails → discovered **after** harm.
**Software is tested before production. Human-impacting plans are not.**

## Slide 3 — The idea (one line)
**Test the planned real-world *outcome* of a live case — before acting — and gate release behind a human.**
Not testing the software. Testing the *world the plan depends on*.

## Slide 4 — How it works (pattern)
Live case → **compile** policy into outcome obligations → **generate Test Manager test cases** →
**adversarial chaos** finds cross-system failure cascades → **prove** + evidence → **GATE**:
fail → human remedy → re-test ↺ ; pass → release → **learn** regression.

## Slide 5 — Demo: caught & blocked
Patient looks ready. Preflight: **BLOCKED, 88%**.
Causal chain: transport 17:15 vs pharmacy closes 17:00 → **medication never collectable**.
*A three-system cascade no checklist catches.* (screenshot: control view RED + Data Fabric)

## Slide 6 — Test Cloud is the heart
An agent turned the **policy into 9 executable Test Manager test cases** (severity-tagged).
"Evaluate requirements and turn them into meaningful test scenarios." — done automatically.
(screenshot: Test Manager Preflight project)

## Slide 7 — Human gate + proven safe
Critical fail → withhold discharge → nurse approves an **operational** remedy (24h pharmacy).
Re-test → **100%, GREEN, Released** + 8 reusable regression scenarios.
**"We don't predict safety. We prove every dependency survived rehearsal."**

## Slide 8 — Built on UiPath (deep + a blend of agents)
- **Test Manager (Test Cloud)** — agentic test-case generation (9 test cases)
- **Data Fabric** — live system of record (no hardcoded data)
- **Agent Builder** — published low-code Obligation Compiler agent
- **Coded agent** via **UiPath for Coding Agents (Claude Code)** — the rehearsal engine ✅ bonus
- **External framework — LangGraph** red-team agent, governed by UiPath
- **UiPath Apps** + live `[i]`-help dashboard · **Identity/External Apps** OAuth
→ low-code **+** coded **+** external **+** coding agent — the exact blend the rubric rewards.
Reproducible: 6/6 tests, live block→release, red-team writes findings to Data Fabric.

## Slide 9 — Impact & roadmap
Wedge: hospital discharge (CMS readmissions, AHRQ RED).
Generalizes to claims settlement, payroll, emergency payments, supply-chain release.
Next: Maestro BPMN + Action Center gate + UiPath Apps front end with contextual help.

## Slide 10 — Close
**Preflight** — the missing layer between a prototype on a laptop and a plan you can trust with a patient.
Repo (MIT): <GitHub URL> · Synthetic data · Never diagnoses or prescribes.
