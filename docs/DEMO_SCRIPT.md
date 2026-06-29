# Preflight — 5-minute demo script (shot-by-shot)

> Target: < 5:00. Record screen at 1080p. Speak the **bold** lines (or paraphrase). Everything shown is
> live on UiPath Automation Cloud + synthetic data. Keep two browser tabs open: **Data Fabric** (DischargeCase)
> and **Test Manager** (Preflight project), plus a terminal in `preflight/`.

## Pre-flight checklist (do once before recording)
```bash
cd preflight
python integration/rehearse_case.py block     # ensure golden case is in the BLOCKED demo state
python integration/control_view.py            # confirm it prints RED/Blocked
```
- Test Manager → Preflight project → Test Cases: confirm 9 cases show.
- Data Fabric → DischargeCase → confirm PT-1041 status = Blocked.

---

## 0:00–0:30  Hook (title slide)
**"Enterprises automate irreversible actions every day — discharging a patient, settling a claim, running
payroll. They execute *optimistically*, and when a hidden dependency fails, we find out *after* it has
already harmed someone. Software is tested before it ships to production. Human-impacting plans are not.
Preflight fixes that."**

## 0:30–1:10  What Preflight is (1 architecture slide)
**"Preflight is an agentic software-testing system. Before a high-stakes plan executes, it forks the case,
compiles the governing policy into executable test cases, unleashes an adversarial agent to break every
dependency, proves the outcome through UiPath Test Cloud, and gates release behind a human. Built on UiPath:
Data Fabric is the system of record, Test Manager holds the test cases, and the rehearsal agent was built
with Claude Code through UiPath for Coding Agents."**

## 1:10–2:10  The live case — caught and blocked (control view + Data Fabric)
Run:
```bash
python integration/control_view.py
```
**"Here's a real synthetic patient, PT-1041. On the surface, ready for discharge. Preflight says: BLOCKED,
88% ready. One Critical obligation failed — 'the patient can physically collect medication.' Look at the
causal chain the chaos agent found: transport arrives 17:15, but the pharmacy closes 17:00. The medication
can never be collected. A cascade across three systems that no single checklist would catch."**

Switch to **Data Fabric** tab → open `DischargeCase` → show PT-1041 (status Blocked), then `Obligation`
(the failing row), then `EvidencePack` (verdict red, causal chain).
**"All of this is live in UiPath Data Fabric — nothing hardcoded."**

## 2:10–2:55  Test Cloud — policy turned into test cases (Test Manager)
Switch to **Test Manager** → Preflight project → Test Cases (9 rows).
**"This is the Track-3 heart. An agent read the discharge-readiness policy and generated nine executable
test cases in Test Manager — one per obligation, severity-tagged. Turning requirements into meaningful test
scenarios, automatically. The failing one is the medication-collectable test."**

## 2:55–3:40  The human gate (Action Center concept) + approve
**"Because a Critical test failed, Preflight withholds the real discharge and routes it to a nurse with a
proposed *operational* remedy — switch to a 24-hour in-network pharmacy. Never a clinical decision; the
clinician stays in control. The nurse approves."**
Run:
```bash
python integration/rehearse_case.py release
```
**"That's the approved remedy being applied and the plan re-tested."**

## 3:40–4:25  Proven safe — released (control view flips GREEN)
Run:
```bash
python integration/control_view.py
```
**"Re-rehearsed. Every obligation passes, readiness 100%, verdict GREEN — released for real execution. And
Preflight learned eight reusable regression scenarios so this class of failure can't recur silently."**
Flip to **Data Fabric** → PT-1041 now Released / EvidencePack green.
**"We don't *predict* this patient will be safe. We *prove* every known dependency required for a safe
transition survived rehearsal — before anyone acts."**

## 4:25–5:00  Built with a coding agent + impact (close)
Show terminal `python tests/test_end_to_end.py` (6/6 pass) **or** the README coding-agent section.
**"The entire rehearsal engine was built with Claude Code via UiPath for Coding Agents — compiler, chaos
agent, evaluator, evidence, and the Data Fabric and Test Manager integrations. The pattern generalizes to
any irreversible action: claims, payroll, supply chain. Preflight is the missing layer between a prototype
on a laptop and a plan you can trust with a patient. Thank you."**

---

## If asked in Q&A
- **Where's the orchestration?** UiPath Data Fabric + Test Manager are the governed backbone; the rehearsal
  runs as a coded agent (UiPath for Coding Agents). Production path: wrap it in a Maestro BPMN process with
  an Action Center user task and a DMN release gate (designed, see IMPLEMENTATION_PLAN.md).
- **Is it safe for healthcare?** 100% synthetic data; validates operational readiness only; never diagnoses
  or prescribes; a human approves every change.
- **Why not just a checklist?** The failure is a *cross-system cascade* (transport vs pharmacy hours) found
  by adversarial search, not a static field check.
