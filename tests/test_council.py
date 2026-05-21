"""Smoke tests for BFT Progress Council MCP voters."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    _voter_repetition,
    _voter_outcome_diversity,
    _voter_goal_alignment,
    _voter_action_velocity,
    _voter_artefact_growth,
    _SESSIONS,
    start_session,
    record_action,
    council_vote,
    estimate_tokens_saved,
    list_voters,
)


def test_repetition_voter_progress_with_diversity():
    actions = [
        {"action": "edit file.py", "outcome": ""},
        {"action": "run test", "outcome": ""},
        {"action": "fix bug", "outcome": ""},
        {"action": "commit", "outcome": ""},
        {"action": "push", "outcome": ""},
    ]
    v, _ = _voter_repetition(actions, "deploy fix")
    assert v == "PROGRESS"


def test_repetition_voter_stall_on_repetition():
    actions = [
        {"action": "retry call", "outcome": ""},
        {"action": "retry call", "outcome": ""},
        {"action": "retry call", "outcome": ""},
        {"action": "retry call", "outcome": ""},
        {"action": "retry call", "outcome": ""},
    ]
    v, _ = _voter_repetition(actions, "deploy fix")
    assert v == "STALL"


def test_outcome_diversity_blocked_on_repeated_errors():
    actions = [
        {"action": "call API", "outcome": "429 rate limit error"},
        {"action": "call API", "outcome": "429 rate limit error"},
        {"action": "call API", "outcome": "429 rate limit error"},
        {"action": "call API", "outcome": "429 rate limit error"},
        {"action": "call API", "outcome": "429 rate limit error"},
    ]
    v, _ = _voter_outcome_diversity(actions, "fetch data")
    assert v == "BLOCKED"


def test_goal_alignment_drift_detected():
    actions = [
        {"action": "browse cat videos on youtube", "outcome": ""},
        {"action": "google holiday destinations", "outcome": ""},
        {"action": "check email inbox", "outcome": ""},
        {"action": "scroll twitter feed", "outcome": ""},
        {"action": "look at memes", "outcome": ""},
    ]
    v, _ = _voter_goal_alignment(actions, "fix authentication bug in JWT validator")
    assert v == "DRIFT"


def test_action_velocity_stall_on_rapid_fire():
    import time
    base = time.time()
    actions = [
        {"action": "spin1", "outcome": "", "ts": base + 0.1},
        {"action": "spin2", "outcome": "", "ts": base + 0.3},
        {"action": "spin3", "outcome": "", "ts": base + 0.5},
        {"action": "spin4", "outcome": "", "ts": base + 0.7},
        {"action": "spin5", "outcome": "", "ts": base + 0.9},
    ]
    v, _ = _voter_action_velocity(actions, "do work")
    assert v == "STALL"


def test_artefact_growth_stall_with_no_writes():
    actions = [
        {"action": "read file", "outcome": ""},
        {"action": "view docs", "outcome": ""},
        {"action": "check status", "outcome": ""},
        {"action": "list contents", "outcome": ""},
        {"action": "show config", "outcome": ""},
    ]
    v, _ = _voter_artefact_growth(actions, "ship feature")
    assert v == "STALL"


def test_artefact_growth_progress_with_commits():
    actions = [
        {"action": "edit code", "outcome": ""},
        {"action": "write tests", "outcome": ""},
        {"action": "commit", "outcome": ""},
        {"action": "push", "outcome": ""},
        {"action": "deploy", "outcome": ""},
    ]
    v, _ = _voter_artefact_growth(actions, "ship feature")
    assert v == "PROGRESS"


def test_end_to_end_session_records_and_votes():
    _SESSIONS.clear()
    r1 = start_session("fix EU AI Act Article 50 watermarking bug")
    sid = r1["session_id"]
    for _ in range(6):
        record_action(sid, "retry", "still failing")
    verdict = council_vote(sid, lookback=6)
    # 3+ voters should flag halt verdict
    assert verdict["verdict"] in ("STALL", "BLOCKED")
    assert verdict["action_recommended"].startswith("halt") or verdict["action_recommended"] == "escalate_to_human"
    assert "signed_attestation" in verdict


def test_token_savings_estimator():
    _SESSIONS.clear()
    r1 = start_session("test goal")
    sid = r1["session_id"]
    for _ in range(8):
        record_action(sid, "retry", "error")
    council_vote(sid, lookback=8)
    saved = estimate_tokens_saved(sid)
    assert saved["halts_triggered"] >= 1
    assert saved["tokens_likely_saved"] > 0


def test_list_voters_count():
    r = list_voters()
    assert r["council_size"] == 5
    assert len(r["voters"]) == 5


if __name__ == "__main__":
    # Inline runner
    import inspect, traceback
    g = dict(globals())
    fns = [v for k, v in g.items() if k.startswith("test_") and inspect.isfunction(v)]
    passed = 0
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"✓ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {fn.__name__}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
