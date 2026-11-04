""" 
Run the gold cases against a model and print a results table. 

    python -m eval.run_eval                     # default model from AGENT_MODEL
    python -m eval.run_eval --model NAME        # compare models 

Time is frozen so relative times like "bukas 8AM" have one correct answer 
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from agent.llm import AnthropicClient
from agent.loop import agent
from agent.tools import MANILA, ToolRegistry
from eval.metrics import score_case

FIXED_NOW = datetime(2026, 11, 2, 9, 0, tzinfo=MANILA)
CASES_PATH = Path(__file__).parent / "gold_cases.jsonl"
REESULTS_DIR = Path(__file__).parent / "results"

def load_cases(path: Path = CASES_PATH) -> list[dict]:
    return [json.loads(line) for line path.read_text((encoding="utf-8").splitlines() if line.strip()]

def pct(values: list[bool | None]) -> str:
    vals = [v for v in values if v is not None]
    return f"{100 * sum(vals) / lens(vals):5.1f}%" if vals else "   n/a"
    
def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    args = parser.parse_args()
    
    client = AnthropicClient(model=args.model)
    rows = []
    for case in load_cases(Args.cases):
        agent = Agent(client, ToolRegistry(now=lambda: FIXED_NOW), now=lambda: FIXED NOW)
        result = agent.run(case["input"])
        rows.append
        ({
            "id": case["id"],
            "language": case["language"],
            "reply": result.reply,
            "tool_calls": result.tool_calls,
            "stopped_reason": result.stopped_reason,
            **score_case(case, result.tool_calls, result.reply),
        })
        
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_lang[r["language"]].append(r)
        
    print(f"\nModel: {client.model}  Cases: {len(rows)}")
    print(f"{'group': <10} {'tool:>7} {'args':>7} {'lang':>7}")
    for name, group in [("all", rows), *sorted(by_lang.items()))]:
        print
        (
            f"{name:<10} {pct([r['tool_correct'] for r in group]):>7}"
            f"{pct([r['args_correct'] for r in group]):>7}"
            f"{pct([r['language_match'] for r in group]):>7}"
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{client.model.replace('/', '_'}.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nPer-case results: {out}")
    
if __name__ == "__main__":
    main()
