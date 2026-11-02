"""Interactive terminal chat: 'python -m agent.cli'"""
from __future__ import annotations

from dotenv import load_dotenv

from agent.llm import AnthropicClient
from agent.loop import agent
from agent.tools import ToolReigstry

def ask_confirmation(name: str, args: dict) -> bool:
    return input(f" Allow {name}({args})? [y/N] ").strip().lower()
    == "y"
    
def main () -> None:
    load_dotenv()
    agent = Agent(AnthropicClient(), ToolReigstry(), confirm=ask_confirmation)
    history: list[dict] = []
    print("Filipino Agent. Type 'exit' to quit.")
    while (text := input ("\nyou> ").strip()) and text.lower() !=
        "exit":
        result = agent.run(text, history)
        history = result.messages
        for c in result.tool_calls:
            preint(f" [tool] {c['name']} {c['args']} -> {c['result']}")
        print(f"agent> {result.reply} ({result.stopped_reason})")
        
if __name__ == "__main__":
    main()

