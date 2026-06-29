# Preflight — 5-Minute Demo Script
# Shot-by-shot · Click-by-click · Word-for-word

> Record at 1080p, no background music. Keep your voice calm and conversational — tell a story, not a sales pitch.
> Total target: under 5:00. Timings are guides, not hard stops.

---

## BEFORE YOU HIT RECORD — Setup (do once, ~3 min)

Open a terminal in the `preflight/` folder and run:
```bash
python integration/rehearse_case.py block
python integration/control_view.py
```
Confirm the output shows **STATUS: Blocked  READINESS: 88.9%  VERDICT: RED**. This is your demo starting state.

Open these tabs in your browser and keep them ready (don't close between runs):
- **Tab A** — Data Fabric: `staging.uipath.com/hackathon26_850/DefaultTenant/dataservice_`
  - Navigate into DischargeCase entity, have PT-1041 row visible
- **Tab B** — Test Manager: `staging.uipath.com/hackathon26_850/DefaultTenant/testmanager_/PRF/testcases`
  - 9 test cases should be visible
- **Tab C** — Test Manager Requirements: `staging.uipath.com/hackathon26_850/DefaultTenant/testmanager_/PRF/requirements`
  - PRF:10 requirement visible
- **Tab D** — Dashboard: open `out/preflight_dashboard.html` in browser (will be RED at start)

Keep the terminal visible in one half of your screen, browser in the other.

---

## 0:00 – 0:35 | THE HOOK — Tell the story of what goes wrong

**[Screen: show your terminal or a blank screen. Speak directly to camera or just narrate.]**

Say this word for word (or close to it):

> *"I want to tell you about a patient. Let's call her Mrs. Chen. She's 72, recovering from a hip replacement,
> and her doctor has signed the discharge papers. Everything looks good on the chart. Her medications are
> prescribed. Transport is booked. A follow-up is in the system.*
>
> *She goes home. Two hours later, her daughter calls the pharmacy. The medication isn't there.*
>
> *What happened? The transport was booked for 5:15 PM. The pharmacy closes at 5:00 PM. By the time
> Mrs. Chen arrived, the shutters were down. Nobody caught it. The prescription, the transport booking,
> the pharmacy hours — they all lived in different systems. No single checklist spans all three.*
>
> *This is not a hypothetical. Cross-system failures like this happen in hospitals, in insurance,
> in payroll, in supply chains — every time we automate an irreversible action and assume every
> downstream dependency will hold. Software is tested before it ships to production.
> Human-impacting plans are not. That's the gap Preflight closes."*

---

## 0:35 – 1:05 | WHAT PREFLIGHT IS — The one-sentence idea

**[Screen: keep terminal visible, or show the architecture slide from your deck]**

> *"Preflight is an agentic software-testing system — but not for software. It tests the planned
> real-world outcome of a live case before anyone acts on it.*
>
> *Here's how it works in one sentence: take a live case, compile the governing policy into executable
> test cases in UiPath Test Manager, unleash an adversarial agent to find the failure cascades,
> prove every dependency holds — and gate the real action behind a human until it does.*
>
> *Everything runs on UiPath Automation Cloud. Data Fabric is the live system of record.
> Test Manager is where the test cases live. And the entire rehearsal engine was built with
> Claude Code through UiPath for Coding Agents.*
>
> *Let me show you the real thing."*

---

## 1:05 – 2:10 | THE LIVE CATCH — RED state, causal chain

**[Terminal is in focus. Type the command slowly so viewers can read it.]**

Type and run:
```bash
python integration/control_view.py
```

Wait for it to print. Then point your cursor at (or read aloud) each section as you speak:

> *"This is patient PT-1041. Completely synthetic — no real patient data, ever. On the surface,
> she looks ready. Nine obligations compiled from the discharge policy. Eight pass."*

**[Point at or highlight the FAIL line:]**
```
![FAIL] (Critical) The patient can physically collect medication
```

> *"One fails. Critical severity. 'The patient can physically collect medication.' Not a vague warning —
> Preflight gives us the exact causal chain."*

**[Slowly read the causal chain section out loud:]**
```
-> Transport pickup 16:40 + 35m travel -> arrival 17:15
-> Pharmacy closes 17:00
-> Arrival 17:15 is AFTER close 17:00 -> medication not collectable
```

> *"Transport leaves at 4:40, takes 35 minutes, arrives at 5:15. Pharmacy closes at 5:00.
> That's it. That's Mrs. Chen's problem, caught before she ever left the building.*
>
> *This cascade crosses three systems — scheduling, transport, and pharmacy — and Preflight's
> chaos agent found it by adversarially mutating every dependency combination.*
>
> *Now let me show you where this all lives."*

**[Switch to browser — Tab A: Data Fabric]**

Click into the **DischargeCase** entity. Point at PT-1041's row.

> *"Every case, every obligation, every evidence pack lives here in UiPath Data Fabric.
> Nothing is hardcoded in the UI. The control view you just saw reads all of this live."*

Click into the **Obligation** entity. Scroll to show the failing row.

> *"Each obligation is a record. Status, severity, the why — all queryable, auditable, persistent."*

Click into the **EvidencePack** entity. Show the row for PT-1041.

> *"And the evidence pack — the causal chain, the verdict, the timestamp — stored for compliance
> and audit. This is what you hand a regulator if they ask why a discharge was delayed."*

---

## 2:10 – 2:55 | TEST CLOUD IS THE HEART — Test Manager + Requirements

**[Switch to browser — Tab B: Test Manager → Test Cases]**

> *"Now here's the Track 3 core. Before any of this rehearsal ran, an agent read the discharge
> readiness policy — seven rules about medications, transport, follow-ups, instructions — and
> automatically generated these nine test cases in UiPath Test Manager."*

**[Hover over the test cases one by one, or slowly scroll through them:]**

> *"Each one is severity-tagged. The five Critical ones are the patient-safety obligations.
> The High ones are operational. The Medium is the escalation path.*
>
> *This is exactly what the Track 3 brief asks for: 'evaluate requirements and turn them into
> meaningful test scenarios.' An agent did this. No test engineer wrote a single line of these."*

**[Switch to Tab C: Test Manager → Requirements → click on PRF:10]**

> *"And every one of those test cases is linked back to the governing policy Requirement —
> PRF:10, Safe Discharge Readiness Policy. Full traceability: from the policy rule, to the
> obligation, to the test case, to the evidence. That's what managed testing looks like."*

---

## 2:55 – 3:40 | THE HUMAN GATE — Nurse approves the remedy

**[Switch back to terminal]**

> *"Because a Critical test failed, Preflight does not discharge the patient. It blocks the
> real action and routes it to a human — in this case, a nurse — with a proposed operational
> remedy: switch to a 24-hour in-network pharmacy.*
>
> *And I want to be very clear about what Preflight does NOT do. It does not suggest a different
> medication. It does not change the dose. It does not touch anything clinical. It proposes only
> operational fixes — and a human signs off on every one."*

Type and run:
```bash
python integration/rehearse_case.py release
```

Watch the output print. Then say:

> *"The nurse has approved. Preflight applies the remedy — switches the collection pharmacy —
> and immediately re-tests every obligation against the new reality."*

---

## 3:40 – 4:20 | PROVEN SAFE — GREEN, released, regression learned

**[Still in terminal. Run:]**
```bash
python integration/control_view.py
```

Point at the output:

> *"Nine from nine. Readiness 100%. Verdict: GREEN. Released.*
>
> *And look — Preflight learned eight reusable regression scenarios from this case.
> The next time a transport booking and a pharmacy hours mismatch appear together,
> the system already knows what to look for."*

**[Run:]**
```bash
python integration/build_dashboard.py
```

**[Switch to browser — Tab D: refresh `out/preflight_dashboard.html`]**

> *"Here's the live dashboard — pulling directly from Data Fabric and Test Manager.
> The RED banner has flipped to GREEN. PT-1041: Released. Every obligation a green tick."*

**[Click one of the [i] info buttons on the dashboard]**

> *"The [i] buttons pull contextual help from the HelpContent entity in Data Fabric.
> Even the onboarding content is governed by the platform — no hardcoded strings."*

---

## 4:20 – 5:00 | BUILT WITH A CODING AGENT + THE BIG PICTURE

**[Switch to terminal. Run:]**
```bash
python tests/test_end_to_end.py
```

Wait for the 6/6 output. Then:

> *"Six tests. Six pass. The entire engine — the policy compiler, the chaos agent, the obligation
> evaluator, the remedy proposer, the Data Fabric and Test Manager integrations — was built
> with Claude Code through UiPath for Coding Agents.*
>
> *We have three kinds of agents working together: a low-code Obligation Compiler in Agent Builder,
> a coded rehearsal agent built with Claude Code, and an external LangGraph red-team agent
> that does the adversarial search — all governed by UiPath.*
>
> *And the pattern is not specific to hospitals. Claims settlement. Payroll runs. Emergency
> benefit payments. Supply chain release. Any enterprise action that is irreversible, that
> crosses multiple systems, that can harm someone if a hidden dependency fails —
> Preflight can test that outcome before anyone acts on it.*
>
> *We don't predict that a plan is safe. We prove that every dependency it relies on survived
> rehearsal — and we do it before anyone acts.*
>
> *Preflight. The missing layer between a prototype on a laptop and a plan you can trust
> with a patient. Thank you."*

---

## QUICK RECOVERY GUIDE (if something breaks mid-demo)

| Problem | Fix |
|---|---|
| `control_view.py` shows GREEN not RED | Run `python integration/rehearse_case.py block` first, then re-run |
| Data Fabric shows no rows | Run `python integration/seed_data.py` to re-seed |
| Test Manager shows 0 test cases | Run `python integration/tm_sync.py` to regenerate |
| Dashboard still RED after release | Run `python integration/build_dashboard.py` then hard-refresh browser (Ctrl+Shift+R) |
| Terminal font too small | Zoom in: Ctrl + `+` in terminal before recording |

---

## Q&A answers (for judges after Phase 2 live presentation)

**"Why not just a checklist?"**
> *"A checklist checks each system in isolation. The failure here is a cascade — transport timing
> times out against pharmacy hours. You can't catch that with a column on a spreadsheet. You need
> adversarial search across dependency combinations, which is what the chaos agent does."*

**"Where does the human fit in?"**
> *"The human is the gate. Preflight never releases the real action on its own. It can block,
> it can propose a remedy, but a human approves every single change. That's by design."*

**"Could this work outside healthcare?"**
> *"Yes — the domain is just the demo. The pattern is: irreversible action, multiple external
> dependencies, cross-system failure risk. Claims, payroll, supply chain release, emergency
> payments — same pattern, same Preflight."*

**"How is this different from process simulation?"**
> *"Process simulation predicts aggregate efficiency from historical data. Preflight proves
> this one specific live case's outcome obligations — before it executes. Real-time,
> case-specific, not statistical."*

**"What's the production roadmap?"**
> *"Wrap the rehearsal in a Maestro BPMN process with a DMN release gate and an Action Center
> nurse task. Connect the evidence pack to Orchestrator Test Automation so results flow back
> into Test Cloud natively. The design is in the repo — it's the obvious next step."*
