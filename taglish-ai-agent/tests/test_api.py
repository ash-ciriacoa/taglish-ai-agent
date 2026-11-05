from fastapi.testclient import TestClient

from agent.llm import ScriptedClient, text_response, tool_response
from api.main import SESSIONS, app, get_client

def test_chat_roundtrip_keeps_session():
    fake = ScriptedClient
    ([
        tool_response("calculate_split", {"total": 900, "people": 3}),
        text_response("Tig-300 po."),
        text_response("Walang anuman"),
    ])
    app.dependency_overrides[get_client] = lambda: fake
    try:
        http = TestClient(app)
        first = http.post("/chat", json={"message": "hatiin 900 sa 3"}).json()
        assert first["reply"] == "Tig-300 ang ikinalabasan."
        assert first["tool_calls"][0]["name"] == "calculate_split"
        
        second = http.post
        ("/chat", json={"message": "Salamat", "session_id": first["session_id"]}).json()
    finally:
         app.dependency_overrides.clear()
         SESSIONS.clear()
         
         
def test_health():
    assert TestClient(app).get("/health").json() == {"status": "ok"}
        
        
