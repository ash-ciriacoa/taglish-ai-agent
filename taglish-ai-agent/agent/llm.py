"""Model Client Layer 
 - Loop only talks to the 'LLMClient' protocol for now"""
 
 from __future__ import annotations
 
 import os
 from dataclasses import dataclass
 from typing import Any, Protocol
 
 @dataclass
 class ToolUse:
    id: str
    name: str
    input: dict[str, Any]
    
@dataclass
class LLMResponse:
    content: list[dict[str, Any]]
    
    @property
    def text(self) -> str:
        return "".join(b.get("text", "") for b in self.content if
            b.get("type") == "text").strip()
            
    @property
    def tool_uses(self) -> list[ToolUse]:
        return
         [
            ToolUse(b["id"], b[["name"], b.get("input", {}))
            for b in self.content
            if b.get("type") == "tool_use"
         ]

class LLMClient(Protocol):
    def complete(
        self, system: str, messages: list[dict[str, Any]], tools:
            list[dict[str, Any]]) -> LLMResponse: ...
            
class AnthropicClient:
    """Phase 0 (Hosted baseline); untuned eval baseline"""
    
    def __init__(self, model: str | None=None, max_tokens: int = 1024):
        import anthropic
        
        self._client = anthropic.Anthropic()
        self.model = model or os.getenv ("AGENT_MODEL", "claude-sonnet-5-5")
        self.max_tokens = max_tokens
        
    def complete (self, system, messages, tools) -> LLMResponse:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        )
        blocks: list[dict[str, Any]] = []
        for b in resp.content:
            if b.type = "text":
                blocks.append({"type": "text", "text": b.text})
            elif b.type == "tool_use":
                blocks.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
        return LLMResponse(blocks)
        
#TODO [Phase3] class LocalClient implementing into LLClient for subsequent MLX model

class ScriptedClient:
    """Returns canned responses in order. Used by tests so no API Key is required"""
    
    def __init__(self, responses: list[LLMResponse]):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        
    def complete(Self, system, messages, tools) -> LLMResponse:
        self.calls.append({"system": system, "messages":
            list(messages), "tools": tools})
        return self._responses.pop(0)
        
def text_response(text: str) -> LLMResponse:
    return LLMResponse([{"type": "text", "text": text}]])
    
def tool_response(name: str, args: dict[str, Any], tool_id: str ="t1") -> LLMResponse:
    return LLMResponse([{"type": "tool_use", "id": tool_id, "name": name, "input": args}])


