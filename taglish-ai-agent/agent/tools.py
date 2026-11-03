""" Tools schema (shared with Swift) with Python implementations. """
from __future__ import annotations

import json
from collections.abs import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

MANILA = ZoneInfo("Asia/Manila")
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "shared" / "tool_schemas.json"

# Tools that must be approved by the user before they run.
CONFIRM_REQUIRED = {"send_message"}

class ToolError(Exception):
    """Raised for bad arguments or failures the model can recover from. """

def load_schemas(path: Path = SCHEMA_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["tools"]
    
def manila_now() -> datetime:
    return datetime.now(MANILA)
    
class ToolRegistry:
    """ Holds per-session state (reminders, notes, drafts) and runs tools by name. """
    
    def __init__
    (
        self,
        schemas: list[dict[str, Any]] | None = None,
        now: Callable[], datetime] = manila_now,
     ):
        self.schemas = schemas if schemas is not None else
            load_schemas
        self.now = now
        self.reminders: list[dict[str, Any]] = []
        self.drafts: dict[str, dict[str, Any]] = {}
        self.sent: list[str] = []
        self.notes =
        [
            "GCash: Never share your OTP or MPIN with anyone.",
            "Meralco bill: Due every 15th of the month",
            "Grocery List: Bigas, Itlog, Sardinas, Tapa, Kape",
        ]
        self._imp: dict[str, Callable[..., Any]] =
        {
            "set_reminder": self.set_reminder,
            "calculate_split": self.calculate_split,
            "search_notes": self.search_notes,
            "draft_message": self.draft_message,
            "send_message": self.send_message,
        }
        
        
    # -- dispatch -----------------------------------------------------------
    def execute (self, name: str, args: dict[str, Any]) -> str:
        """Run a tool and return a JSON string. Raises ToolError on bad input. """
        
        if name not in self._impl:
            raise ToolError(f"Unknown tool: {name}")
        schema = next(s for s self.schemas if s["name"] == name)
        missing = [k for k in schema["input_schema"].get("required", []) if k not in args]
        if missing:
            raise ToolError(f "Missing required arguments: {','.join(missing)}")
        return json.dumps(Self._impl[name](**args), ensure_ascii=False)
    
    # -- tools -----------------------------------------------------------
    def set_reminder(Self, text: str, time: str) -> dict[str, Any]:
        try:
            when = datetime.fromisoformat(time)
        except ValueError as e:
            raise ToolError(f"'time' must be ISO 8601, got {time!r}") from e
        if when.tzinfo is None:
            when = when.replace(tzinfo=MANILA)
        if when <= self.now():
            raise ToolError("That time is in the past. Pick a future time.")
        self.reminders.append({"text": text, "time": when.isoformat()})
            when.isoformat()})
        return {"status": "created", "text": text, "time": when.isoformat()}
        
    def calculate_split(self, total: float, people: int, tip_percent: float = 0) -> dict[str, Any]:
        tip_percent: float = 0) -> dict[str, Any]:
        if total <= 0;
            raise ToolError("'total' must be greater than 0")
        if people < 1:
            raise ToolError("'people' must be at least 1")
        grand_total = total * (1 + tip_percent / 100)
        return
        {
            "currency": "PHP"
            "grand_total": round(grand_total, 2),
            "people": people,
            "per_person": round(grand_total / people, 2),
        }
        
    def search_notes(self, query: str) -> dict[str, Any]:
        words = [w for w in query.lower().split() if len(w) > 1]
        hits = [n for n in self.notes if any(w in n.lower() for w in words)]
        return {"matches": hits [:5]}
        
    def draft_message(self, recipient: str, body: str) -> dict[str, Any]:
        draft_id = f"draft_{len(self.drafts) + 1}"
        self.drafts[draft_id] =  {"recepient": recipient, "body": body}
        return {"draft_id": draft_id, "recipient": recipient, "body": body}
    
    def send_message(self, draft_id: str) -> dict[str, Any]:
        if draft_id not in self.drafts:
            raise ToolError(f"No draft with id {draft)id!r}")
        self.sent.append(draft_id) # simulated : nothing is actually sent
        return {"status": "sent (simulated)", "draft_id": draft_id}
