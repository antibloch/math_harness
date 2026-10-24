import argparse
import asyncio
import json
from pathlib import Path

from .demo import DEMO_PROBLEM, DemoModel
from .graph import run_agent
from .model import IFMModel


def positive(value):
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return result


def nonnegative(value):
    result = int(value)
    if result < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return result


def save_proof(result):
    root = Path("result")
    root.mkdir(exist_ok=True)
    index = 1
    while True:
        run_dir = root / f"run_{index}"
        try:
            run_dir.mkdir()
            break
        except FileExistsError:
            index += 1
    proof = run_dir / "proof.md"
    content = result["solution"]
    if result["status"] != "complete":
        content = f"# {result['status'].capitalize()}\n\n{content}"
    proof.write_text(content.rstrip() + "\n", encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return proof


async def main():
    parser = argparse.ArgumentParser(description="Branching LangGraph mathematical agent")
    parser.add_argument("problem", nargs="?")
    parser.add_argument("--demo", action="store_true", help="Run a fixed even-integer fixture, without a real model")
    parser.add_argument("--subproblems", "--i", type=positive, default=2)
    parser.add_argument("--objects", "--j", type=positive, default=2)
    parser.add_argument("--manipulations", "--k", type=positive, default=2)
    parser.add_argument("--request-timeout", type=positive, default=900,
                        help="IFM total deadline per API attempt in seconds (default: 900)")
    parser.add_argument("--api-retries", type=nonnegative, default=2,
                        help="Retries per transient API failure, separate from mathematical retry (default: 2)")
    parser.add_argument("--max-tokens", type=positive, default=32768,
                        help="Maximum completion tokens per IFM request (default: 32768)")
    parser.add_argument("--output", type=Path, help="Save complete results as JSON")
    args = parser.parse_args()
    if args.demo and args.problem and args.problem != DEMO_PROBLEM:
        parser.error("--demo supports only its fixed even-integer problem")
    if not args.demo and not args.problem:
        parser.error("provide a mathematical problem or use --demo")
    try:
        model = DemoModel() if args.demo else IFMModel(max_tokens=args.max_tokens,
                                                     timeout=args.request_timeout,
                                                     api_retries=args.api_retries)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        result = await run_agent(model, args.problem or DEMO_PROBLEM,
                                 subproblems=args.subproblems, objects=args.objects,
                                 manipulations=args.manipulations)
    finally:
        if isinstance(model, IFMModel):
            await model.aclose()
    if isinstance(model, IFMModel):
        result["llm_errors"] = model.errors
    proof = save_proof(result)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(result["status"])
    print(result["solution"])
    print(f"Saved: {proof}")
    if result.get("error"):
        print(result["error"])
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
