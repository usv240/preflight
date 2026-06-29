"""Generate a polished Preflight web dashboard from LIVE UiPath data.

Reads DischargeCase / Obligation / EvidencePack / HumanDecision / HelpContent from Data Fabric and the
Test Manager test-case count, then renders a single self-contained HTML file (CSS + tiny JS for the [i]
help popovers). Nothing is hardcoded — re-run before vs. after the gate and the dashboard flips RED→GREEN.

    python integration/build_dashboard.py [patientAlias]
    -> writes out/preflight_dashboard.html  (open in a browser)
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "integration"))
from uipath_client import UiPathClient  # noqa: E402

GOLDEN = "PT-1041 (synthetic)"


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def help_map(c: UiPathClient) -> dict:
    rows = c.query("HelpContent")
    return {r.get("screenKey"): r for r in rows}


def info_btn(help_row: dict | None) -> str:
    if not help_row:
        return ""
    body = (f"<b>{esc(help_row.get('title'))}</b><br><br>"
            f"<u>What it is</u><br>{esc(help_row.get('whatItIs'))}<br><br>"
            f"<u>How to use</u><br>{esc(help_row.get('howToUse'))}<br><br>"
            f"<u>Next</u><br>{esc(help_row.get('nextStep'))}")
    return (f'<span class="info"><button class="i" onclick="tog(this)">i</button>'
            f'<span class="pop">{body}</span></span>')


def main() -> int:
    alias = sys.argv[1] if len(sys.argv) > 1 else GOLDEN
    c = UiPathClient()
    cases = c.query("DischargeCase", "patientAlias", "=", alias)
    if not cases:
        print(f"Case '{alias}' not found"); return 1
    case = cases[0]
    cid = case["Id"]
    obligations = c.query("Obligation", "caseId", "=", cid)
    evidence = c.query("EvidencePack", "caseId", "=", cid)
    decisions = c.query("HumanDecision", "caseId", "=", cid)
    helps = help_map(c)
    ev = evidence[0] if evidence else {}
    dec = decisions[0] if decisions else {}

    pid = c.tm_project_id("Preflight")
    tc_count = 0
    if pid:
        st, payload = c.tm_request("GET", f"/testcase/project/{pid}/search?pageSize=50")
        tc_count = len(payload.get("data", [])) if isinstance(payload, dict) else 0

    verdict = (ev.get("verdict") or "?").lower()
    status = case.get("status", "?")
    score = case.get("readinessScore", 0)
    is_red = verdict == "red"
    chains = json.loads(ev.get("causalChains") or "[]") if ev else []

    # obligation rows
    obl_rows = ""
    for o in sorted(obligations, key=lambda x: (x.get("severity", ""), x.get("type", ""))):
        passed = o.get("status") == "Pass"
        chip = '<span class="chip pass">PASS</span>' if passed else '<span class="chip fail">FAIL</span>'
        detail = f'<div class="why">{esc(o.get("detail"))}</div>' if not passed else ""
        obl_rows += (f'<tr class="{"failrow" if not passed else ""}"><td>{chip}</td>'
                     f'<td><span class="sev sev-{esc(o.get("severity","").lower())}">'
                     f'{esc(o.get("severity"))}</span></td>'
                     f'<td>{esc(o.get("text"))}{detail}</td></tr>')

    chain_html = ""
    if chains and is_red:
        steps = "".join(f'<li>{esc(s)}</li>' for s in chains[0])
        chain_html = (f'<div class="card chain">'
                      f'<h3>Causal failure chain {info_btn(helps.get("evidence"))}</h3>'
                      f'<ol>{steps}</ol></div>')

    remedy_actions = ""
    try:
        rem = json.loads(dec.get("proposedRemedy") or "{}")
        remedy_actions = "".join(f"<li>{esc(a)}</li>" for a in rem.get("actions", []))
    except Exception:  # noqa: BLE001
        pass

    verdict_banner = ("BLOCKED — real discharge withheld until obligations pass or a human signs off"
                      if is_red else "RELEASED — every dependency proven; safe to execute")

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preflight — Discharge Readiness Rehearsal</title>
<style>
:root{{--bg:#0b1020;--card:#141b2e;--line:#243049;--ink:#e8edf7;--mut:#9fb0d0;
--green:#1db981;--red:#ef4d62;--amber:#f2b34b;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 'Segoe UI',system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px}}
.top{{display:flex;align-items:center;gap:14px;margin-bottom:6px}}
.logo{{font-weight:800;font-size:26px;letter-spacing:.5px}}
.tag{{color:var(--mut)}} .sub{{color:var(--mut);font-size:13px;margin-bottom:18px}}
.banner{{padding:14px 18px;border-radius:12px;font-weight:700;margin:14px 0 22px;
border:1px solid var(--line)}}
.banner.red{{background:rgba(239,77,98,.12);border-color:var(--red);color:#ffd7dd}}
.banner.green{{background:rgba(29,185,129,.12);border-color:var(--green);color:#cffbe9}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.card.full{{grid-column:1/-1}}
h3{{margin:0 0 12px;font-size:15px;color:var(--ink);display:flex;align-items:center;gap:8px}}
.kv{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed var(--line)}}
.kv:last-child{{border:0}} .kv b{{color:var(--ink)}} .mut{{color:var(--mut)}}
.badge{{padding:3px 10px;border-radius:999px;font-weight:700;font-size:12px}}
.badge.red{{background:rgba(239,77,98,.18);color:#ff9aa8}}
.badge.green{{background:rgba(29,185,129,.18);color:#7ff0c8}}
.score{{font-size:34px;font-weight:800}}
table{{width:100%;border-collapse:collapse}} td{{padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
.chip{{padding:2px 9px;border-radius:6px;font-weight:700;font-size:12px}}
.chip.pass{{background:rgba(29,185,129,.16);color:#7ff0c8}}
.chip.fail{{background:rgba(239,77,98,.18);color:#ff9aa8}}
.sev{{font-size:11px;color:var(--mut)}} .sev-critical{{color:#ff9aa8}}
.failrow{{background:rgba(239,77,98,.06)}} .why{{color:var(--mut);font-size:12.5px;margin-top:3px}}
.chain ol{{margin:0;padding-left:18px}} .chain li{{margin:6px 0;color:#ffd7dd}}
.info{{position:relative;display:inline-block}}
.i{{width:18px;height:18px;border-radius:50%;border:1px solid var(--mut);background:transparent;
color:var(--mut);font-style:italic;font-weight:700;cursor:pointer;font-size:12px;line-height:1}}
.pop{{display:none;position:absolute;top:24px;left:0;z-index:9;width:300px;background:#0f1626;
border:1px solid var(--line);border-radius:10px;padding:12px;color:var(--mut);font-size:12.5px;
box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.pop.show{{display:block}} .pop u{{color:var(--ink)}}
.footer{{color:var(--mut);font-size:12px;margin-top:22px;text-align:center}}
.pill{{display:inline-block;background:rgba(242,179,75,.15);color:#ffd9a1;padding:2px 10px;border-radius:999px;font-size:12px}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo">Preflight</div>
<div class="tag">Discharge Readiness Rehearsal {info_btn(helps.get("dashboard"))}</div></div>
<div class="sub">Live from UiPath Data Fabric + Test Manager · synthetic data · validates operational
readiness only — never diagnoses or prescribes</div>

<div class="banner {'red' if is_red else 'green'}">{esc(verdict_banner)}</div>

<div class="grid">
  <div class="card">
    <h3>Case {info_btn(helps.get("case"))}</h3>
    <div class="kv"><span class="mut">Patient</span><b>{esc(case.get("patientAlias"))}</b></div>
    <div class="kv"><span class="mut">Status</span>
      <span class="badge {'red' if is_red else 'green'}">{esc(status)}</span></div>
    <div class="kv"><span class="mut">Verdict</span><b>{esc(verdict.upper())}</b></div>
    <div class="kv"><span class="mut">Test Cloud</span><b>{tc_count} test cases generated</b></div>
  </div>
  <div class="card" style="text-align:center">
    <h3>Readiness</h3>
    <div class="score" style="color:{'var(--red)' if is_red else 'var(--green)'}">{esc(score)}%</div>
    <div class="mut">{sum(1 for o in obligations if o.get('status')=='Pass')}/{len(obligations)} obligations proven</div>
  </div>
</div>

<div class="card full" style="margin-top:16px">
  <h3>Outcome obligations {info_btn(helps.get("rehearsal"))}
    <span class="pill">mirrored as Test Manager test cases</span></h3>
  <table>{obl_rows}</table>
</div>

<div class="grid" style="margin-top:16px">
  {chain_html or ''}
  <div class="card">
    <h3>Human gate · Action Center {info_btn(helps.get("nurseReview"))}</h3>
    <div class="kv"><span class="mut">Decision</span><b>{esc(dec.get("decision") or "—")}</b></div>
    <div class="kv"><span class="mut">Approver</span><b>{esc(dec.get("approverAlias") or "(pending)")}</b></div>
    <div style="margin-top:10px" class="mut">Proposed operational remedy (no clinical change):</div>
    <ul class="mut">{remedy_actions or '<li>—</li>'}</ul>
  </div>
</div>

<div class="footer">Preflight · UiPath AgentHack 2026 · Track 3 — Test Cloud ·
We don't predict the patient will be safe; we prove every dependency survived rehearsal.</div>
</div>
<script>
function tog(b){{var p=b.parentElement.querySelector('.pop');
document.querySelectorAll('.pop').forEach(function(x){{if(x!==p)x.classList.remove('show')}});
p.classList.toggle('show');}}
document.addEventListener('click',function(e){{if(!e.target.closest('.info'))
document.querySelectorAll('.pop').forEach(function(x){{x.classList.remove('show')}});}});
</script></body></html>"""

    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    path = out / "preflight_dashboard.html"
    path.write_text(page, encoding="utf-8")
    print(f"Wrote {path}  (verdict={verdict.upper()}, status={status}, score={score}%, testcases={tc_count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
