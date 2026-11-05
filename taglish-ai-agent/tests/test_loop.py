from datetime import datetime

from agent.llm import ScriptedClient, text_response, tool_response
from agent.loop import Agent
from agent.tools import MANILA, ToolRegistry

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=MANILA)


def make_agent(responses, **kwargs):
    client = ScriptedClient(responses)
    agent = Agent(client, ToolRegistry(now=lambda: NOW), now=lambda: NOW, **kwargs)
    return agent, client


def test_plain_reply_no_tools():
    agent, _ = make_agent([text_response("Kumusta po!")])
    r = agent.run("Hi")
    assert r.reply == "Kumusta po!"
    assert r.stopped_reason == "completed"
    assert r.tool_calls == []


def test_tool_call_then_final_answer():
    agent, client = make_agent(
        [
            tool_response("calculate_split", {"total": 1800, "people": 4}),
            text_response("Tig-450 pesos bawat isa."),
        ]
    )
    r = agent.run("Hatiin natin ang 1800 sa 4")
    assert r.stopped_reason == "completed"
    assert r.tool_calls[0]["name"] == "calculate_split"
    assert '"per_person": 450.0' in r.tool_calls[0]["result"]
    # the tool result was fed back to the model
    last_user = client.calls[1]["messages"][-1]
    assert last_user["content"][0]["type"] == "tool_result"


def test_tool_error_is_returned_to_model_for_recovery():
    agent, _ = make_agent(
        [
            tool_response("set_reminder", {"text": "x", "time": "2026-11-01T08:00:00+08:00"}, "a"),
            tool_response("set_reminder", {"text": "x", "time": "2026-11-03T08:00:00+08:00"}, "b"),
            text_response("Done po."),
        ]
    )
    r = agent.run("Remind me")
    assert r.tool_calls[0]["is_error"] is True
    assert r.tool_calls[1]["is_error"] is False
    assert r.stopped_reason == "completed"


def test_repeat_detection_stops_identical_calls():
    same = {"query": "gcash"}
    agent, _ = make_agent([tool_response("search_notes", same, str(i)) for i in range(5)])
    r = agent.run("hanapin", )
    assert r.stopped_reason == "repeat_detected"
    assert len(r.tool_calls) == 2  # max_repeats=2 allowed, third blocked


def test_same_tool_different_args_is_not_a_repeat():
    agent, _ = make_agent(
        [
            tool_response("search_notes", {"query": "gcash"}, "1"),
            tool_response("search_notes", {"query": "meralco"}, "2"),
            tool_response("search_notes", {"query": "grocery"}, "3"),
            text_response("ok"),
        ]
    )
    assert agent.run("hanapin").stopped_reason == "completed"


def test_max_iterations_cap():
    responses = [tool_response("search_notes", {"query": f"q{i}"}, str(i)) for i in range(10)]
    agent, _ = make_agent(responses, max_iterations=3)
    r = agent.run("hanapin")
    assert r.stopped_reason == "max_iterations"
    assert r.iterations == 3


def _send_flow():
    return [
        tool_response("draft_message", {"recipient": "Mama", "body": "Male-late po ako."}, "1"),
        tool_response("send_message", {"draft_id": "draft_1"}, "2"),
        text_response("ok"),
    ]


def test_send_message_denied_without_confirmation():
    agent, _ = make_agent(_send_flow())
    r = agent.run("send it")
    assert r.tool_calls[1]["is_error"] is True
    assert agent.registry.sent == []


def test_send_message_runs_when_confirmed():
    agent, _ = make_agent(_send_flow(), confirm=lambda name, args: True)
    agent.run("send it")
    assert agent.registry.sent == ["draft_1"]


def test_system_prompt_contains_current_date():
    agent, client = make_agent([text_response("hi")])
    agent.run("hi")
    assert "2026-11-02" in client.calls[0]["system"]
