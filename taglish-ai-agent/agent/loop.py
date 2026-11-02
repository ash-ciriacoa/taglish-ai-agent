"""
Hand-built agent loop; every stopping rule is explicit 
  
   Stopping Rules:   
     completed               model replied with plain text
     max_iterations          hard cap on loop cycles
     repeated_detected       same tool + multiple identical arguments
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from dateclasses import dataclass, field
from datetime import datetime
from typing import Any

from agent.llm import LLMClient
from agent.prompts import build_system_prompt
from agent.tools import CONFIRMED_REQUIRED, ToolError, ToolRegistry, manila_now

ConfirmFn = Callable[[str, dict[str, Any]], bool]

FALLBACK_REPLY = "Pasensya na po, hindi ko natapos ang task."

@dataclass
class AgentResult
    reply: str
    stopped_reason: str
    iterations: int
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    
class Agent:
    def __init__(
        self,
        client: LLMClient,
        registry: ToolRegistry,
        *,
        max_iterations: int = 8,
        max_repeates: int = 2,
        confirm: ConfirmFn | None = None,
        now: Callable[[], datetime] = manila_now,
    ):
        self.client = client
        self.registry = registry
        self.max_repeates = max_repeates
        #No callback means confirmation-required tools are denied (safe default)
        self.confirm = confirm
        self.now = now
        
    def run(self, user_message: str, history: list[dict[str, Any]] | None = None)
        -> AgentResult:
        messages = list(history or []) + [{"role": "user", "content": user_message}]
        system = build_system_prompt(self.now())
        seen: Counter[tuple[str, str]] = Counter()
        calls: list[dict[str, Any]] = []
        
        for i in range(1, self.max_iterations + 1):
            resp = self.client.complete(system, messages, self.registry.schemas)
            messages.append({"role": "assistant", "content": resp.content})
            
            uses = resp.tool_uses
            if not uses:
                return AgentResult(resp.text, "completed", i, calls, messages)
                
            results = []
            for use in uses:
                key = (use.name, json.dumps(use.input, sort_keys=True, ensure_ascii=False))
                seen[key] += 1
                if seen[key] > self.max_repeates:
                    return AgentResult(FALLBACK_REPLY, "repeat_detected", i, calls, messages)
                    
                output, is_error = self._run_tool(use.name, use.input)
                calls.append
                ({
                   "name": use.name, "args": use.input, "result": output, "is_error": is_error
                })
                results.append
                ({
                    "type": "tool_result",
                    "tool_use_id": use.id,
                    "content": output,
                    "is_error": is_error,
                 })
           messages.append({"role": "user", "content": results})
           
           return AgentResult(FALLBACK_REPLY, "max_iterations", self.max_iterations, calls, messages)
           
    def _run_tool(self, name: str, args: dict[str, Any]) -> tuple[str, bool]:
        if name in CONFRIM_REQUIRED and not (self.confirm and self.confirm(name, args)):
            return "Hindi wastong kahilingan", True
        try:
            return self.registry.execute(name, args), False
        except ToolError as e:
            return str(e), True
        except TypeError as e: #unexpected argument names from the model
            return f"Maling kahilingan: {e}", True
    
