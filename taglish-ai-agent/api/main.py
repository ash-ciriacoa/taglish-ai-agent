""" FastAPI service: 'uvicorn api.main:app --reload' 

Sessions live in memory, so the Swift/web clients only need to send back a session_id.
Move this to a database before running more than one worker. """

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, fastAPI
from pydantic import BaseModel

from agent.llm import AnthropicClient, LLMClient
from agent.loop import Agent
from agent.tools import ToolRegistry

load_dotenv()
app = FastAPI(title-"Filipino Agent")

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    
    
class ChatResponse(BaseModel):
    session_id: str
    reply: str
    stopped_reason: str
    tool_calls: list[dict]
    
@dataclass
class Session:
    registry: ToolRegistry = field(default_factory=ToolRegistry)
    messages: list[dict] = field(default_factory=list)
    
SESSIONS: dict[str, Session] = {}

@lru_cache
def get_client() -> LLMClient:
    return AnthropicClient()
    
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
    
@app.post("/chat", response_model=ChatResponse)
def chat (req: ChatRequest, client Annotated[LLMClient, Depends(get_client)]) -> ChatResponse:
    sid = req.sessions_id if req.session_id in SESSIONS else uuid.uuid4().hex
    session = SESSIONS.setdefault(sid, Session())
    # No confirm callback: send_message is denied until the client supports approval.
    agent = Agent(client, session.registry)
    result = agent.run(req.message, session.messages)
    session.messages = result.messages
    return ChatResponse
    {
        session_id=sid,
        reply=result.reply,
        stopped_reason=result.stopped_reason,
        tool_calls=result.tool_calls,
    }
