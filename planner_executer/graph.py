"""Ordered planning, dependency-local execution, and final synthesis."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from math_agent.graph import text


class State(TypedDict, total=False):
    problem: str
    steps: list[dict]
    outputs: list[dict]
    status: str
    search_status: str
    solution: str
    error: str


def strings(value):
    if not isinstance(value, list):
        raise ValueError("Expected a list of strings")
    return [text(item) for item in value]


def identifier(value):
    return str(value) if type(value) is int else text(value)


def validate_plan(response, max_steps):
    if not isinstance(response, dict):
        raise ValueError("Planner must return a JSON object")
    steps = response.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= max_steps:
        raise ValueError("Plan must contain 1 through max_steps steps")
    result, seen = [], set()
    for step in steps:
        ident = identifier(step["id"])
        dependencies = step.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise ValueError("Expected a list of dependency identifiers")
        dependencies = [identifier(value) for value in dependencies]
        if ident in seen or len(set(dependencies)) != len(dependencies) or not set(dependencies) <= seen:
            raise ValueError("Step identifiers must be unique; dependencies must identify earlier steps")
        result.append({"id": ident, "claim": text(step["claim"]),
                       "assumptions": strings(step.get("assumptions", [])),
                       "dependencies": dependencies,
                       "completion_condition": text(step["completion_condition"])})
        seen.add(ident)
    return result


async def run_agent(model, problem, *, max_steps=8):
    """Run all stages sequentially; retain partial work if execution fails."""
    if type(max_steps) is not int or not 1 <= max_steps <= 32:
        raise ValueError("max_steps must be an integer from 1 through 32")
    state = {"problem": text(problem), "steps": [], "outputs": []}

    async def planner(state):
        response = await model("planner", {"original_problem": state["problem"], "max_steps": max_steps})
        return {"steps": validate_plan(response, max_steps)}

    async def executor(state):
        outputs = {}
        for step in state["steps"]:
            predecessors = {ident: outputs[ident] for ident in step["dependencies"]}
            if any(output["status"] != "draft" for output in predecessors.values()):
                output = {"proof": "", "status": "partial", "unresolved_obligations": [step["claim"]],
                          "error": "Blocked by an unresolved prerequisite"}
            else:
                try:
                    response = await model("executor", {"original_problem": state["problem"],
                                           "step": step, "required_predecessor_proofs": predecessors})
                    proof = text(response["proof"])
                    status = response["status"]
                    gaps = strings(response.get("unresolved_obligations", []))
                    if status not in ("draft", "partial") or (status == "draft") != (not gaps):
                        raise ValueError("Executor status and unresolved obligations disagree")
                    output = {"proof": proof, "status": status, "unresolved_obligations": gaps}
                except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                    output = {"proof": "", "status": "partial", "unresolved_obligations": [step["claim"]],
                              "error": str(exc)}
            outputs[step["id"]] = output
        return {"outputs": [{"step_id": ident, **output} for ident, output in outputs.items()]}

    async def responder(state):
        # Match the source workflow's synthesis boundary: mathematical prose,
        # ordered goals and assumptions, without operational error/gap ledgers.
        response = await model("responder", {
            "original_problem": state["problem"],
            "ordered_plan": [{"claim": step["claim"], "assumptions": step["assumptions"]}
                             for step in state["steps"]],
            "executor_outputs": [{"proof": output["proof"]} for output in state["outputs"]],
        })
        return {"solution": text(response["proof"]), "status": "complete",
                "search_status": "full" if all(o["status"] == "draft" for o in state["outputs"])
                else "incomplete"}

    graph = StateGraph(State)
    for name, node in (("planner", planner), ("executor", executor), ("responder", responder)):
        graph.add_node(name, node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "responder")
    graph.add_edge("responder", END)
    try:
        async for update in graph.compile().astream(state, stream_mode="updates"):
            for delta in update.values():
                state.update(delta)
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        retained = "\n\n".join(o["proof"] for o in state["outputs"] if o["proof"])
        state.update(status="error", search_status="incomplete", error=str(exc),
                     solution="Final synthesis unavailable. Retained step outputs follow.\n\n" + retained)
    return state
