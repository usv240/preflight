# Preflight — 5-Minute Demo Script
# Simple · Human · Story-first

> One golden rule: speak like you're telling a friend what went wrong.
> Not a product pitch. A story. Then the proof.
> Record at 1080p. No music. Speak slowly.

---

## SETUP — Before you hit record

**Run in terminal:**
```bash
cd preflight
python integration/rehearse_case.py block
python integration/control_view.py
```
Must show: **STATUS: Blocked | READINESS: 88.9% | VERDICT: RED**

**Open these browser tabs:**
- Tab 1 → Data Fabric entities (DischargeCase, Obligation, EvidencePack)
- Tab 2 → Test Manager → PRF → Test Cases (9 rows)
- Tab 3 → Test Manager → PRF → Requirements → PRF:10
- Tab 4 → `out/preflight_dashboard.html`

**Slides:** Have the deck open on screen.

---

## 0:00 – 0:45 | THE STORY — Make them feel it

**[Show Slide 1 — Title]**

> *"Hi. Before I show you anything technical — I want to tell you about Mrs. Chen."*

**[Switch to Slide 2 — Problem column]**

> *"Mrs. Chen is 72. Hip replacement. Doctor signed the discharge papers.
> Medications prescribed. Transport booked. Everything looked fine.*
>
> *She went home.*
>
> *Two hours later — her daughter called the pharmacy.*
> *The medication wasn't there.*
>
> *Why? Transport was booked for 5:15 PM. Pharmacy closes at 5:00 PM.*
> *By the time she arrived — it was shut.*
>
> *Nobody caught it.*
> *Because the transport, the prescription, and the pharmacy hours
> each lived in a different system.*
> *No single person or checklist saw all three at once.*
>
> *This happens. In hospitals. In insurance. In payroll. In supply chains.*
> *Every time a business automates something irreversible,
> they assume everything downstream will work out.*
>
> *Usually it does. Until it doesn't.*
>
> *Software gets tested before it goes live.*
> *These plans don't.*
> *Preflight changes that."*

**[Point to Solution column — one sentence]**

> *"Preflight is a safety rehearsal for high-stakes plans —
> before the action happens, it tests whether the plan will actually work.
> Let me show you."*

---

## 0:45 – 1:50 | THE CATCH — Show the live failure

**[Switch to terminal. Zoom in font. Type slowly.]**

```bash
python integration/control_view.py
```

Wait for output. Then speak calmly:

> *"This is PT-1041. A synthetic patient — no real data, ever.*
> *Preflight just ran a rehearsal on her discharge plan.*
> *Nine checks. Eight passed."*

**[Pause. Point at the FAIL line:]**
```
![FAIL] (Critical) The patient can physically collect medication
```

> *"One failed. Critical.*
> *'The patient can physically collect medication.'*
> *Here's exactly why."*

**[Read each line of the causal chain slowly — one breath per line:]**
```
Transport pickup 16:40 + 35m travel → arrival 17:15
Pharmacy closes 17:00
Arrival 17:15 is AFTER close 17:00 → medication not collectable
```

> *"Transport leaves at 4:40.*
> *Takes 35 minutes.*
> *Arrives at 5:15.*
> *Pharmacy closes at 5:00.*
>
> *That's Mrs. Chen's problem.*
> *Caught. Before she left the building.*
>
> *Now — let me show you where this all lives on UiPath."*

---

## 1:50 – 2:25 | DATA FABRIC — The live system of record

**[Switch to Tab 1 — Data Fabric]**

Click **DischargeCase** → show PT-1041 row, Status = Blocked.

> *"Every case is a live record in UiPath Data Fabric. Status: Blocked.*
> *Nothing hardcoded — what you saw in the terminal came from here."*

Click **Obligation** → show the failing MEDICATION_COLLECTABLE row.

> *"Each check is a record. The severity, the result, the reason.*
> *Auditable. Queryable."*

Click **EvidencePack** → show PT-1041 row.

> *"And the evidence pack — the exact failure chain, the verdict, the timestamp.*
> *This is what you show a regulator if they ask why a discharge was held."*

---

## 2:25 – 3:05 | TEST MANAGER — Requirements became test cases

**[Switch to Tab 2 — Test Manager Test Cases]**

> *"Here's the Track 3 core.*
>
> *An agent read the discharge policy — seven rules — and turned them into
> nine live test cases inside UiPath Test Manager.*
> *Automatically. No test engineer wrote a single line."*

**[Scroll slowly through the 9 cases]**

> *"Each one severity-tagged.*
> *Five Critical. Two High. One Medium.*
> *And the failing one — medication-collectable — that's Mrs. Chen's test.*
> *That's the one that blocked her discharge."*

**[Switch to Tab 3 — Requirements → click PRF:10]**

> *"And every test case links back to the governing policy requirement — PRF:10.*
> *From policy rule to test case to evidence.*
> *Full traceability. Built by an agent."*

---

## 3:05 – 3:45 | THE HUMAN GATE — A nurse decides

**[Switch back to terminal]**

> *"Because that test failed — Preflight did not discharge the patient.*
> *It blocked the action and sent it to a nurse*
> *with a simple proposed fix: switch to a 24-hour pharmacy.*
>
> *Preflight never touches the clinical side.*
> *No medication changes. No dosage changes.*
> *Operational fixes only.*
> *And a human always approves.*
>
> *The nurse approved."*

**[Type and run:]**
```bash
python integration/rehearse_case.py release
```

> *"Remedy applied. Preflight re-tests everything."*

---

## 3:45 – 4:25 | GREEN — Proven safe

**[Run:]**
```bash
python integration/control_view.py
```

> *"Nine from nine. 100%. GREEN. Released.*
>
> *And Preflight stored eight regression scenarios from this case —
> so if transport and pharmacy hours ever conflict again,
> the system already knows to look for it.*
>
> *We didn't predict Mrs. Chen would be safe.*
> *We proved it — before she left the ward."*

**[Run:]**
```bash
python integration/build_dashboard.py
```

**[Switch to Tab 4 — hard refresh dashboard]**

> *"Live dashboard — straight from Data Fabric and Test Manager.*
> *RED flipped to GREEN. PT-1041: Released."*

**[Click a [i] button]**

> *"Even these help tips come live from Data Fabric.*
> *Zero hardcoded strings anywhere in this system."*

---

## 4:25 – 5:00 | THE CLOSE — Simple and big

**[Run:]**
```bash
python tests/test_end_to_end.py
```

> *"Six tests. Six pass.*
>
> *Everything you just saw — the compiler, the chaos agent,
> the test case generator, the evidence pack, every UiPath integration —
> was built with Claude Code through UiPath for Coding Agents.*
>
> *Three agents working together:*
> *a low-code agent in Agent Builder,*
> *a coded agent built with Claude Code,*
> *and an external LangGraph red-team agent —*
> *all governed and audited through UiPath.*
>
> *Mrs. Chen's story is just the demo.*
> *The same rehearsal works for an insurance payout —*
> *is the policy documentation complete before funds move?*
> *For payroll — does every dependency hold?*
> *For supply chain — is every handoff confirmed?*
>
> *Any plan that is irreversible.*
> *Any plan that crosses multiple systems.*
> *Any plan that harms someone if it fails.*
>
> *Preflight tests it first.*
>
> *The missing layer between a prototype on a laptop*
> *and a plan you can trust with a patient.*
>
> *Thank you."*

---

## IF SOMETHING BREAKS

| Problem | Fix |
|---|---|
| Output shows GREEN not RED | `python integration/rehearse_case.py block` then re-run |
| Terminal text too small | Ctrl + scroll up before recording |
| Dashboard still RED | `python integration/build_dashboard.py` then Ctrl+Shift+R |
| Data Fabric empty | `python integration/seed_data.py` |
| Test Manager empty | `python integration/tm_sync.py` |

---

## ONE-LINE SUMMARY (for Q&A)

> *"Preflight is a safety rehearsal for high-stakes plans —
> it turns policy into UiPath Test Manager test cases,
> attacks the plan with a chaos agent,
> proves every dependency holds,
> and blocks release until a human approves the fix."*

---

## Q&A ANSWERS

**"Why not a checklist?"**
> *"A checklist checks one system. This failure crossed three —
> transport timing, pharmacy hours, and medication pickup.
> You need adversarial search to find that cascade.
> That's what the chaos agent does."*

**"How is this different from process simulation?"**
> *"Simulation predicts aggregate patterns from historical data.
> Preflight proves this one specific live case — right now, before it executes."*

**"Where does the human fit?"**
> *"Preflight can block and propose — but it cannot release.
> A human approves every change. Always."*

**"Does it work outside healthcare?"**
> *"Yes. Claims, payroll, supply chain — same pattern.
> Any irreversible action that crosses systems and can harm someone if it fails."*

**"What's the production roadmap?"**
> *"Maestro BPMN process with a DMN release gate,
> a real Action Center nurse task,
> and results flowing back into Test Cloud via Orchestrator."*
