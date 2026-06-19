"""End-to-end tests for the Preflight engine.

Runnable two ways:
    python -m pytest                 (from the preflight/ directory)
    python tests/test_end_to_end.py  (no pytest required)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.compiler import compile_obligations
from engine.evaluator import run_test_set
from engine.loader import list_cases, load_case
from engine.models import CaseStatus, Decision, ObligationStatus, Severity
from engine.orchestrator import rehearse


def _approve(failed, proposed, attempt):
    return {"decision": Decision.APPROVE_REMEDY.value, "approver": "test-nurse"}


def _reject(failed, proposed, attempt):
    return {"decision": Decision.REJECT.value, "approver": "test-nurse"}


def test_golden_case_blocks_then_releases():
    """The hidden transport/pharmacy flaw must be caught, blocked, remedied, then released."""
    case = load_case("golden_case")

    # Baseline (no remedy) must FAIL on the critical collectability obligation.
    obligations = compile_obligations(case)
    baseline = run_test_set(case, obligations)
    assert baseline.overall_status == ObligationStatus.FAIL.value
    crit_fail = [r for r in baseline.results
                 if r.status == ObligationStatus.FAIL.value and r.severity == Severity.CRITICAL.value]
    assert any("collect" in r.obligation_text.lower() for r in crit_fail), \
        "expected the medication-collectable obligation to fail"

    # With nurse approval, the rehearsal must end RELEASED and the final run must pass.
    result = rehearse(case, _approve)
    assert result.status == CaseStatus.RELEASED.value, f"expected RELEASED, got {result.status}"
    assert result.runs[-1].overall_status == ObligationStatus.PASS.value
    assert len(result.runs) >= 2, "expected at least one re-test after remedy"
    assert result.evidence.verdict == "green"
    assert result.case.readiness_score == 100.0
    assert len(result.regression) >= 1, "a resolved failure should be learned as a regression scenario"


def test_golden_case_stays_blocked_if_rejected():
    case = load_case("golden_case")
    result = rehearse(case, _reject)
    assert result.status == CaseStatus.BLOCKED.value
    assert result.evidence.verdict == "red"


def test_clean_case_passes_first_time():
    case = load_case("case_clean")
    result = rehearse(case, _reject)  # rejecter never gets called if nothing fails
    assert result.status == CaseStatus.RELEASED.value
    assert len(result.runs) == 1, "clean case should need no re-test"
    assert result.evidence.verdict == "green"


def test_coverage_case_finds_multiple_failures_and_recovers():
    """Coverage denial + wrong-language instructions + missing owner -> all caught, then remedied."""
    case = load_case("case_coverage")
    obligations = compile_obligations(case)
    baseline = run_test_set(case, obligations)
    failed_types = {r.type for r in baseline.results if r.status == ObligationStatus.FAIL.value}
    assert "MED_COVERED" in failed_types
    assert "INSTRUCTIONS_ACCESSIBLE" in failed_types
    assert "DEPENDENCY_OWNED" in failed_types

    result = rehearse(case, _approve)
    assert result.status == CaseStatus.RELEASED.value
    assert result.runs[-1].overall_status == ObligationStatus.PASS.value


def test_chaos_finds_causal_chain_on_golden():
    case = load_case("golden_case")
    obligations = compile_obligations(case)
    from engine.chaos import search
    scenarios, log = search(case, obligations)
    assert scenarios, "chaos should surface at least the latent failure"
    # at least one scenario should describe the transport-after-close causal chain
    assert any(any("AFTER close" in step for step in s.causal_chain) for s in scenarios)


def test_all_cases_load():
    names = list_cases()
    assert {"golden_case", "case_clean", "case_coverage"}.issubset(set(names))
    for n in names:
        c = load_case(n)
        assert c.world and c.plan_items


# Allow running without pytest.
if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failures}/{len(fns)} tests passed")
    raise SystemExit(1 if failures else 0)
