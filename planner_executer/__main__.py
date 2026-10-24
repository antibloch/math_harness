"""Run with python -m planner_executer --problem ... --output-dir ..."""
import argparse
import asyncio
import json
from pathlib import Path

from math_agent.__main__ import positive, nonnegative
from .graph import run_agent
from .model import PlannerModel


async def main():
    parser = argparse.ArgumentParser(description="Sequential planner–executor–responder proof drafts")
    parser.add_argument("--problem", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--max-steps", type=positive, default=8)
    parser.add_argument("--request-timeout", type=positive, default=900)
    parser.add_argument("--api-retries", type=nonnegative, default=2)
    parser.add_argument("--max-tokens", type=positive, default=32768)
    args = parser.parse_args()
    if args.max_steps > 32:
        parser.error("--max-steps must be at most 32")
    try:
        model = PlannerModel(timeout=args.request_timeout, api_retries=args.api_retries,
                             max_tokens=args.max_tokens)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        # Refuse to overwrite any prior run directory.
        args.output_dir.mkdir(parents=True, exist_ok=False)
        result = await run_agent(model, args.problem, max_steps=args.max_steps)
        result["llm_errors"] = model.errors
        (args.output_dir / "run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        (args.output_dir / "proof.md").write_text(result["solution"].rstrip() + "\n")
        print(result["status"])
        print(f"Saved: {args.output_dir / 'proof.md'}")
    finally:
        await model.aclose()
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
