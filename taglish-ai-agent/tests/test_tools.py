import json
from datetime import datetime

import pytest

from agent.tools import MANILA, ToolError, ToolRegistry

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=MANILA)


@pytest.fixture
def reg():
    return ToolRegistry(now=lambda: NOW)


def test_schemas_load_and_match_implementations(reg):
    assert {s["name"] for s in reg.schemas} == set(reg._impl)


def test_calculate_split(reg):
    out = json.loads(reg.execute("calculate_split", {"total": 1800, "people": 4}))
    assert out["per_person"] == 450.0


def test_calculate_split_with_tip(reg):
    out = json.loads(reg.execute("calculate_split", {"total": 1000, "people": 4, "tip_percent": 10}))
    assert out["per_person"] == 275.0


def test_calculate_split_rejects_zero_people(reg):
    with pytest.raises(ToolError):
        reg.execute("calculate_split", {"total": 100, "people": 0})


def test_reminder_created(reg):
    reg.execute("set_reminder", {"text": "bayad kuryente", "time": "2026-11-03T08:00:00+08:00"})
    assert reg.reminders[0]["text"] == "bayad kuryente"


def test_reminder_in_past_rejected(reg):
    with pytest.raises(ToolError, match="past"):
        reg.execute("set_reminder", {"text": "x", "time": "2026-11-01T08:00:00+08:00"})


def test_missing_required_argument(reg):
    with pytest.raises(ToolError, match="Missing"):
        reg.execute("set_reminder", {"text": "x"})


def test_unknown_tool(reg):
    with pytest.raises(ToolError, match="Unknown"):
        reg.execute("launch_rocket", {})


def test_search_notes(reg):
    out = json.loads(reg.execute("search_notes", {"query": "GCash"}))
    assert any("GCash" in m for m in out["matches"])


def test_draft_then_send(reg):
    d = json.loads(reg.execute("draft_message", {"recipient": "Mama", "body": "Male-late po ako."}))
    reg.execute("send_message", {"draft_id": d["draft_id"]})
    assert reg.sent == [d["draft_id"]]
