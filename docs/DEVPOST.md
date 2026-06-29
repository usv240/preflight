# Devpost submission — Preflight

**Project title:** Preflight — prove high-stakes plans before they touch a person
**Track:** Track 3 — UiPath Test Cloud
**Tagline:** Branch reality. Break the plan. Prove the outcome. Then act.

---

## Inspiration
Enterprises automate consequential, often **irreversible** actions — discharging a patient, settling a
claim, running payroll, releasing a shipment. Today these execute **optimistically**: the workflow assumes
every downstream dependency will hold. When one silently fails — the pharmacy is closed when transport
arrives, a medication isn't covered, a follow-up was "recommended" but never booked — the failure is
discovered *after* it has already harmed someone. Software is tested before it ships to production.
**Human-impacting plans are not.** Preflight closes that gap.

## What it does
Preflight is an **agentic software-testing system** for the *outcome of a live case*. Before a high-stakes
plan executes, it:
1. **Compiles** the governing policy + the case's facts into executable **outcome obligations**.
2. **Generates a Test Manager test case for every obligation** (policy → test scenarios, automatically).
3. Runs an **adversarial "chaos" agent** that mutates dependencies and searches for *cross-system* failure
   cascades a static checklist would miss.
4. **Proves** each obligation, produces an auditable **evidence pack** with the causal failure chain, and
   **gates release**: any Critical failure blocks the real action and routes it to a human with a proposed
   *operational* remedy.
5. On approval, **re-tests**, releases, and **learns a reusable regression scenario**.

**Demo domain:** safe hospital discharge (100% synthetic data). Preflight validates *operational readiness
only* — it never diagnoses, prescribes, or changes medication; a clinician approves every change.

In the demo, patient PT-1041 looks ready to discharge, but Preflight finds a hidden cascade — transport
arrives 17:15, the pharmacy closes 17:00, so a required medication can never be collected — **blocks** the
discharge, a nurse approves switching to a 24-hour pharmacy, Preflight **re-tests to 100%** and **releases**.

## How we built it
- **UiPath Data Fabric** is the system of record: five entities (DischargeCase, Obligation, EvidencePack,
  HumanDecision, HelpContent) hold every case, test result, evidence pack, and decision. Nothing is
  hardcoded — the control view reads it all live.
- **UiPath Test Manager (Test Cloud)** holds the generated test cases (one per obligation), severity-tagged,
  under the "Preflight" project — turning policy/requirements into executable test scenarios.
- **A coded rehearsal agent**, built end-to-end with **Claude Code via UiPath for Coding Agents**: a
  policy-grounded obligation compiler, an adversarial chaos/red-team search that builds causal chains, an
  obligation evaluator, an operational remedy proposer, and the Data Fabric + Test Manager integrations.
- **UiPath Identity / External Application (OAuth client-credentials)** secures all platform access.
- A platform-independent **reference engine** (pure standard library, 6 passing end-to-end tests) encodes
  the same logic and lets anyone verify the core behavior in seconds.

## UiPath components used
- **UiPath Test Manager (Test Cloud)** — agentic test-case generation from policy/obligations (9 test cases).
- **UiPath Data Fabric (Data Service)** — entities, records, live query/insert/update via REST API.
- **UiPath Agent Builder (Studio Web)** — published low-code **Obligation Compiler** agent.
- **Coded agent** (UiPath for Coding Agents / **Claude Code**) — the rehearsal engine + integrations (bonus).
- **External agent framework — LangGraph (LangChain)** — the adversarial red-team agent, governed by UiPath.
- **UiPath Apps** + a live backend-driven dashboard with an `[i]` help system from the `HelpContent` entity.
- **UiPath Identity + External Applications** — OAuth client-credentials API access.

## Agent type
**Both — and a blend.** A published **low-code agent** (Agent Builder) **+** a **coded agent** (rehearsal
engine, built via UiPath for Coding Agents) **+** an **external-framework agent** (LangGraph red-team)
governed by UiPath Data Fabric. Exactly the "blend native + external + coding agents" the hackathon rewards.

## Coding-agent evidence (for the bonus)
The entire rehearsal engine, synthetic data, tests, and UiPath integrations were generated with **Claude
Code** through UiPath for Coding Agents. Evidence: `docs/CODING_AGENT_EVIDENCE.md`, `docs/SESSION_LOG.md`,
the commit history, and the reproducible proof: `python tests/test_end_to_end.py` (6/6) +
`python integration/rehearse_case.py block|release` + `python integration/control_view.py`.

## Challenges
Non-deterministic, cross-system failures don't show up in static checks; we model them as adversarial search
over dependency mutations. Embedding rich JSON in Data Fabric, discovering the exact REST endpoints, OAuth
scopes, entity-level permissions, and Test Manager licensing each took iteration — all solved and documented.

## Accomplishments
A working, end-to-end agentic testing pipeline **running on UiPath**: policy → Test Manager test cases →
adversarial rehearsal → causal-chain evidence in Data Fabric → human gate → release → learned regression.

## What's next
Wrap the rehearsal agent in a **Maestro BPMN** process with an **Action Center** nurse task and a **DMN**
release gate; a **UiPath Apps** front end bound to Data Fabric with contextual help on every screen; and the
same fork→prove→gate pattern applied to claims, payroll, and supply-chain release.

## Try it
Public repo (MIT): **https://github.com/usv240/preflight**. See README for setup; everything runs against
UiPath Automation Cloud with synthetic data.
