# Minimal Planner–Executor–Responder

A minimal port of the author's `math_agent/planner_executor` workflow. The folder
and Python module use the requested spelling: **`planner_executer`**.

```bash
uv sync
export IFM_API_KEY="your-key-here"
uv run python -m planner_executer \
  --problem "Prove PNT" \
  --output-dir result/planner_pnt \
  --max-steps 8 --request-timeout 600 --api-retries 2
```

The output directory must not already exist. It receives `proof.md` and `run.json`.
The latter retains the plan, step outputs, unresolved obligations and API diagnostics.
The `.env` file is not loaded automatically.

## Flow

1. The planner produces ordered claims, assumptions, dependencies and completion
   conditions. Dependencies must refer to unique earlier step identifiers.
2. The executor processes steps sequentially. Each model call receives the original
   problem, its local step and only its required predecessor outputs. A partial or
   failed prerequisite blocks dependent execution; independent steps continue.
3. The responder receives the original problem, ordered claims and assumptions,
   and mathematical derivations. Operational errors and gap ledgers stay in the
   saved results. It may correct or complete partial work and writes a standalone
   draft. If synthesis fails, available derivations are retained in the output.

There is no critic, automatic replanning, parallel execution or interrupted-run
resume. Model `draft` status is not mathematical certification. Final
`status: complete` means synthesis returned; `search_status` separately reports
whether all executor outputs had `draft` status.

## Shared API protections

The port reuses `math_agent.model.IFMModel` with planner-specific instructions:
`langchain_openai.ChatOpenAI`, `https://api.ifm.ai/v1`, model
`IFM/K2-Horizon-375B-A23B`, and `IFM_API_KEY` from the environment.

`--request-timeout` defaults to 900 seconds per attempt, `--api-retries` to 2,
`--max-tokens` to 32768, `--synthesis-max-tokens` to 65536, and `--max-steps` to 8
(maximum 32). Final synthesis uses plain Markdown rather than JSON, with the
source workflow's IFM sampling settings: temperature 1.0, top-p 0.95 and high
reasoning effort. Its separate token budget avoids constraining proof prose to
the planning/execution budget, but does not guarantee valid or complete output. Total deadlines,
cancellation, bounded transient retries, `Retry-After`, backoff and rate-limit
cooldown are shared with Math Harness. Invalid or truncated outputs are rejected.

The sampling settings follow the [official model card](https://huggingface.co/IFM/K2-Horizon-375B-A23B).
IFM documents reasoning effort in its [reasoning reference](https://docs.ifm.ai/docs/reasoning.md).

## Scope of the port

The source's SQLite artifact store, identifier-backed control state, schema
hierarchy, metrics infrastructure and global token budget are omitted. Ordinary dictionaries and one three-node
LangGraph retain the mathematical workflow. Planning and execution use JSON;
the responder uses plain proof prose through the shared adapter. This port introduces no new
dependencies and does not import files from the original repository.

The published [planner–executor proof sample](../proofs/planner_executor_proof.md)
was produced with the original implementation, **not this minimal port**. The
sample is not evidence that this port reproduces its mathematical performance.

Run the offline tests from the repository root:

```bash
uv run python -m unittest discover -s tests -v
```
