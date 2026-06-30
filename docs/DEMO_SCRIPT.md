# Preflight — 5-Minute Demo Script
# Story-driven · Click-by-click · Word-for-word

> Record screen at 1080p. No background music.
> One golden rule: speak slowly. Pause after every key moment. Let it land.

---

## SETUP — Do this BEFORE you hit record (5 min)

**Terminal:**
```bash
cd preflight
python integration/rehearse_case.py block
python integration/control_view.py
```
Confirm output says: **STATUS: Blocked  |  READINESS: 88.9%  |  VERDICT: RED**

**Browser tabs — open all four, keep them ready:**
- Tab 1 → Data Fabric: `staging.uipath.com/hackathon26_850/DefaultTenant/dataservice_`
- Tab 2 → Test Manager Test Cases: `staging.uipath.com/hackathon26_850/DefaultTenant/testmanager_/PRF/testcases`
- Tab 3 → Test Manager Requirements: `staging.uipath.com/hackathon26_850/DefaultTenant/testmanager_/PRF/requirements`
- Tab 4 → Dashboard: open `out/preflight_dashboard.html` in browser

**Screen layout:** Terminal on left half, browser on right half.

**Presentation deck:** Have the Google Slides deck open and ready to share screen.

---

## 0:00 – 0:40 | SLIDE 1 + 2 — The Story Begins

**[Show Slide 1 — Title slide]**

> *"Hi. I want to start with a story."*

**[Switch to Slide 2 — Problem / Solution. Point to the Problem column.]**

> *"Mrs. Chen is 72. She just had a hip replacement. Her doctor signed the discharge papers.
> Everything looks good — medications prescribed, transport booked, follow-up in the system.*
>
> *She goes home.*
>
> *Two hours later, her daughter calls the pharmacy. The medication isn't there.*
>
> *What happened? Transport was booked for 5:15 PM. The pharmacy closes at 5:00 PM.
> By the time Mrs. Chen arrived — shutters were down.*
>
> *Nobody caught it. Because the transport booking, the prescription, and the pharmacy hours
> all lived in three different systems. No single checklist spans all three.*
>
> *This is not a hospital problem. This is an enterprise problem.
> Every time we automate an irreversible action — a discharge, a claim, a payroll run —
> we assume every downstream dependency will hold.*
>
> *Software is tested before it ships to production.
> Human-impacting plans are not.*
>
> *That is the gap. And that is what Preflight closes."*

**[Point to the Solution column.]**

> *"Preflight tests the planned real-world outcome of a live case — before anyone acts on it.
> Not the software. The world the plan depends on.
> Let me show you the real thing."*

---

## 0:40 – 1:50 | TERMINAL — The Live Catch

**[Switch to terminal. Make font large — Ctrl + scroll up. Type slowly.]**

Type and run:
```bash
python integration/control_view.py
```

Wait for it to print fully. Then speak — go line by line:

> *"This is patient PT-1041. Completely synthetic — no real patient data, ever.*
>
> *On the surface — nine obligations checked. Eight pass."*

**[Pause. Point at or slowly read the FAIL line:]**
```
![FAIL] (Critical) The patient can physically collect medication
```

> *"One fails. Critical. 'The patient can physically collect medication.'*
>
> *Now look at what Preflight found — the exact causal chain."*

**[Read the causal chain slowly, one line at a time:]**
```
Transport pickup 16:40 + 35m travel → arrival 17:15
Pharmacy closes 17:00
Arrival 17:15 is AFTER close 17:00 → medication not collectable
```

> *"Transport leaves at 4:40. Takes 35 minutes. Arrives at 5:15.*
> *Pharmacy closes at 5:00.*
> *That's it. That's Mrs. Chen's problem — caught before she ever left the building.*
>
> *This is a three-system cascade. Scheduling, transport, and pharmacy.
> Preflight's adversarial chaos agent found it by stress-testing every
> dependency combination — the same way a good engineer would break a system in staging.*
>
> *Except this isn't staging. This is a live patient plan.*
>
> *And Preflight caught it. Now let me show you where all of this lives."*

---

## 1:50 – 2:30 | DATA FABRIC — Nothing is Hardcoded

**[Switch to browser Tab 1 — Data Fabric]**

Click on **DischargeCase** entity. Show PT-1041 row.

> *"Every case lives here in UiPath Data Fabric. Status: Blocked.
> Nothing hardcoded — the terminal you just saw reads all of this live."*

Click on **Obligation** entity. Scroll to the failing row — MEDICATION_COLLECTABLE.

> *"Each obligation is a record. Severity, status, the reason it failed.
> All queryable. All auditable."*

Click on **EvidencePack** entity. Show PT-1041's row.

> *"And here's the evidence pack — the causal chain, the verdict, the timestamp.
> This is what you hand a regulator if they ask why a discharge was delayed.*
>
> *Now — here's the Track 3 heart of Preflight."*

---

## 2:30 – 3:10 | TEST MANAGER — Policy Became Test Cases

**[Switch to browser Tab 2 — Test Manager Test Cases]**

> *"Before any of this rehearsal ran, an agent read the discharge readiness policy —
> seven rules about medications, transport, follow-ups, and instructions —
> and automatically generated these nine test cases in UiPath Test Manager.*
>
> *One per obligation. Severity-tagged. No test engineer wrote a single line."*

**[Hover slowly over each test case as you count them]**

> *"Five Critical. Two High. One Medium. And the failing one — right there —
> medication-collectable. That's Mrs. Chen's test. That's the one that blocked the discharge."*

**[Switch to Tab 3 — Requirements → click PRF:10]**

> *"And every one of those nine test cases is linked to this Requirement —
> PRF:10, Safe Discharge Readiness Policy.*
>
> *Full traceability. From the policy rule, to the test case, to the evidence pack.
> That's what managed testing looks like — and an agent built it automatically."*

---

## 3:10 – 3:50 | THE HUMAN GATE — Nurse Takes Control

**[Switch back to terminal]**

> *"Because a Critical test failed, Preflight does something important.*
> *It does NOT discharge the patient.*
>
> *It blocks the real action — and routes it to a human.*
> *In this case, a nurse. With a proposed remedy:*
> *switch to a 24-hour in-network pharmacy.*
>
> *And I want to be very clear about what Preflight does NOT do.*
> *It does not suggest a different medication.*
> *It does not change the dose. It does not touch anything clinical.*
> *It proposes only operational fixes.*
> *A human — always — signs off.*
>
> *The nurse approves."*

**[Type and run slowly:]**
```bash
python integration/rehearse_case.py release
```

Watch the output. Then:

> *"Remedy applied. Plan updated. Preflight immediately re-tests
> every obligation against the new reality."*

---

## 3:50 – 4:30 | GREEN — Proven Safe, Released

**[Type and run:]**
```bash
python integration/control_view.py
```

**[Point at the output — read it out:]**

> *"Nine from nine. Readiness: 100%. Verdict: GREEN. Released.*
>
> *And Preflight learned eight reusable regression scenarios from this case.*
> *The next time a transport booking conflicts with pharmacy hours —
> the system already knows what to look for.*
>
> *We didn't predict Mrs. Chen would be safe.*
> *We proved it — before she left the ward."*

**[Run:]**
```bash
python integration/build_dashboard.py
```

**[Switch to Tab 4 — refresh `out/preflight_dashboard.html`]**

> *"Here's the live dashboard — reading directly from Data Fabric and Test Manager.*
> *RED has flipped to GREEN. PT-1041: Released.*"*

**[Click one of the [i] info buttons]**

> *"Even these help tooltips are served live from the HelpContent entity in Data Fabric.
> Zero hardcoded strings anywhere."*

---

## 4:30 – 5:00 | THE BIGGER PICTURE — Close Strong

**[Stay on dashboard or switch to terminal. Run:]**
```bash
python tests/test_end_to_end.py
```

**[Show 6/6 passing]**

> *"Six tests. Six pass. The entire engine —
> the policy compiler, the chaos agent, the obligation evaluator,
> the remedy proposer, the Data Fabric and Test Manager integrations —
> was built with Claude Code through UiPath for Coding Agents.*
>
> *Three kinds of agents working together:
> a low-code Obligation Compiler in Agent Builder,
> a coded rehearsal engine built with Claude Code,
> and a LangGraph red-team agent doing the adversarial search —
> all governed by UiPath.*
>
> *And Mrs. Chen's story is just the demo.*
> *The same pattern works for insurance claims — is the policy documentation complete before payout?*
> *For payroll — does every dependency hold before funds move?*
> *For supply chain — is every handoff confirmed before a shipment releases?*
>
> *Any action that is irreversible, crosses multiple systems,
> and can harm someone if a dependency fails —
> Preflight can test that outcome before anyone acts.*
>
> *We don't predict that a plan is safe.*
> *We prove every dependency it relies on survived rehearsal —
> before anyone acts on it.*
>
> *Preflight. The missing layer between a prototype on a laptop
> and a plan you can trust with a patient.*
>
> *Thank you."*

---

## QUICK RECOVERY — If something breaks

| Problem | Fix in 10 seconds |
|---|---|
| `control_view.py` shows GREEN not RED | Run `python integration/rehearse_case.py block` first |
| Terminal font too small | Ctrl + scroll up before recording |
| Dashboard still RED after release | Run `build_dashboard.py` then Ctrl+Shift+R to hard refresh |
| Data Fabric shows no rows | Run `python integration/seed_data.py` to re-seed |
| Test Manager shows 0 test cases | Run `python integration/tm_sync.py` |

---

## THE ONE-MINUTE VERSION (if asked to summarise in Q&A)

> *"A patient looked ready to discharge. Preflight found her transport arrived after
> the pharmacy closed — medication could never be collected. It blocked the discharge,
> routed it to a nurse with a proposed fix, the nurse approved, Preflight re-tested,
> reached 100%, and released. The entire thing runs on UiPath — Data Fabric, Test Manager,
> Agent Builder, and a LangGraph external agent — and was built with Claude Code
> through UiPath for Coding Agents."*

---

## Q&A ANSWERS — For Phase 2 live judging

**"Why not just a checklist?"**
> *"A checklist checks one system at a time. This failure is a cascade across three —
> transport timing against pharmacy hours. You need adversarial search across
> dependency combinations to find it. That's what the chaos agent does."*

**"How is this different from process simulation?"**
> *"Process simulation predicts aggregate efficiency from historical data.
> Preflight proves this one specific live case's outcome — in real time,
> before it executes. Not statistical. Specific."*

**"Where does the human fit in?"**
> *"The human is the gate. Preflight can block and propose — but it cannot release.
> A human approves every single change. That's by design."*

**"Could this work outside healthcare?"**
> *"Yes — the domain is just the demo. Claims, payroll, supply chain —
> same pattern. Any irreversible action that crosses multiple systems
> and can harm someone if a dependency fails."*

**"What's next?"**
> *"Wrap the rehearsal in a Maestro BPMN process with a DMN release gate
> and a real Action Center nurse task. Connect results to Orchestrator
> Test Automation so they flow back into Test Cloud natively."*
