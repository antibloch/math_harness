"""Sequential LangGraph search with isolated subproblem history."""
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class SearchState(TypedDict, total=False):
    problem: str
    subproblem: dict
    attempt: int
    history: list[dict]
    objects: list[str]
    manipulations: list[dict]
    candidates: list[dict]
    review: dict
    execution_error: str | None


class AgentState(TypedDict, total=False):
    problem: str
    subproblems: list[dict]
    results: list[dict]
    status: str
    search_status: str
    solution: str
    error: str


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected nonempty model text")
    return value.strip()


def normalized(value):
    return re.sub(r"\s+", " ", value).strip().casefold()


def items(response, key, count):
    values = response.get(key)
    if not isinstance(values, list) or len(values) != count:
        raise ValueError(f"Expected exactly {count} {key}")
    values = [text(v) for v in values]
    if len({normalized(v) for v in values}) != count:
        raise ValueError(f"Duplicate {key}")
    return values


def stitch_context(state):
    """Keep one assessed selection per goal, or explicitly unranked input."""
    branches = {r["subproblem"]["id"]: r for r in state.get("results", [])}
    goals = state.get("subproblems") or [r["subproblem"] for r in branches.values()]
    groups = []
    for goal in sorted(goals, key=lambda s: s["id"]):
        branch = branches.get(goal["id"], {})
        group = {"subproblem": goal}
        # A failed replacement must not replace the previous assessed best with
        # an unrelated new candidate that happens to reuse its local identifier.
        selected = None
        review = None
        for attempt in reversed(branch.get("history", [])):
            review = attempt["review"]
            selected = next((c for c in attempt["candidates"] if c["id"] == review["best_id"]), None)
            if selected is not None:
                break
        if selected is None and branch.get("best"):
            selected, review = branch["best"], branch["review"]
        if selected is not None:
            group.update(selection="critic_selected", trajectory=selected,
                         verdict=review["verdict"], feedback=review["feedback"])
        else:
            candidates = branch.get("candidates", [])
            group.update(selection="unranked" if candidates else "none", candidates=candidates)
        groups.append(group)
    return {"problem": state["problem"], "results": groups}


async def stitch(model, state):
    """Draft from settled search state; also usable on a saved run without search."""
    context = stitch_context(state)
    response = await model("stitch", context)
    if not isinstance(response, dict):
        raise ValueError("stitch: expected a JSON object")
    return {"status": "complete", "solution": text(response.get("solution")),
            "search_status": "full" if state.get("results") and
            len(state["results"]) == len(context["results"]) and
            all(r["status"] == "full" for r in state["results"]) else "incomplete"}


def build_agent(model, *, subproblems=2, objects=2, manipulations=2):
    """Build sequential decomposition, branch search, and final stitching."""
    for name, value in dict(subproblems=subproblems, objects=objects,
                            manipulations=manipulations).items():
        if type(value) is not int or value < 1:
            raise ValueError(f"{name} must be a positive integer")

    async def call(stage, payload):
        response = await model(stage, payload)
        if not isinstance(response, dict):
            raise ValueError(f"{stage}: expected a JSON object")
        return response

    def context(state):
        return {key: state[key] for key in ("problem", "subproblem", "attempt", "history")}

    async def generate_objects(state):
        response = await call("objects", {**context(state), "count": objects})
        values = items(response, "objects", objects)
        old = {normalized(o) for attempt in state["history"] for o in attempt["objects"]}
        if any(normalized(o) in old for o in values):
            raise ValueError("Retry reused a previous mathematical object")
        return {"objects": values}

    async def generate_routes(state):
        operations, candidates, errors = [], [], []
        old = {normalized(m["text"]) for a in state["history"] for m in a["manipulations"]}
        for object_id, obj in enumerate(state["objects"], 1):
            try:
                response = await call("manipulations", {**context(state), "object": obj,
                                      "object_id": object_id, "count": manipulations})
                values = items(response, "manipulations", manipulations)
                if any(normalized(value) in old for value in values):
                    raise ValueError("Retry reused a previous manipulation")
            except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                errors.append(str(exc))
                continue
            for manipulation_id, value in enumerate(values, 1):
                operation = {"object_id": object_id, "object": obj,
                             "manipulation_id": manipulation_id, "text": value}
                operations.append(operation)
                try:
                    response = await call("trajectory", {**context(state), **operation})
                    candidates.append({**operation, "id": f"{object_id}.{manipulation_id}",
                                       "proof": text(response.get("proof"))})
                except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                    errors.append(str(exc))
        return {"manipulations": operations, "candidates": candidates,
                "execution_error": "; ".join(dict.fromkeys(errors)) or None}

    async def criticize(state):
        review = await call("critic", {**context(state), "candidates": state["candidates"]})
        if review.get("best_id") not in {c["id"] for c in state["candidates"]}:
            raise ValueError("Critic selected an unknown candidate")
        if review.get("verdict") not in ("full", "partial"):
            raise ValueError("Critic verdict must be full or partial")
        review = {"best_id": review["best_id"], "verdict": review["verdict"],
                  "feedback": text(review.get("feedback"))}
        attempt = {"attempt": state["attempt"], "objects": state["objects"],
                   "manipulations": state["manipulations"], "candidates": state["candidates"],
                   "review": review}
        return {"review": review, "history": [*state["history"], attempt]}

    def after_critic(state):
        return "retry" if state["review"]["verdict"] == "partial" and state["attempt"] == 0 else END

    def retry(state):
        return {"attempt": 1}

    branch = StateGraph(SearchState)
    for name, fn in (("objects", generate_objects), ("routes", generate_routes),
                     ("critic", criticize), ("retry", retry)):
        branch.add_node(name, fn)
    branch.add_edge(START, "objects")
    branch.add_edge("objects", "routes")
    branch.add_conditional_edges("routes",
                                 lambda state: END if state["execution_error"] is not None else "critic",
                                 ["critic", END])
    branch.add_conditional_edges("critic", after_critic, ["retry", END])
    branch.add_edge("retry", "objects")
    search = branch.compile()

    async def decompose(state):
        response = await call("decompose", {"problem": text(state["problem"]), "count": subproblems})
        goals = items(response, "subproblems", subproblems)
        return {"subproblems": [{"id": i, "goal": goal} for i, goal in enumerate(goals, 1)]}

    async def search_subproblem(state):
        # Save completed node updates so an execution failure retains earlier work,
        # including a partial first attempt if generating its replacement fails.
        current = dict(state)
        try:
            async for update in search.astream(state, stream_mode="updates"):
                for delta in update.values():
                    current.update(delta)
            if current.get("execution_error") is not None:
                return {**current, "status": "error", "error": current["execution_error"]}
            review = current["review"]
            best = next(c for c in current["candidates"] if c["id"] == review["best_id"])
            result = {**current, "status": review["verdict"], "best": best}
        except (ValueError, KeyError, TypeError, RuntimeError) as exc:
            result = {**current, "status": "error", "error": str(exc)}
        return result

    async def search_all(state):
        results = []
        for subproblem in state["subproblems"]:
            result = await search_subproblem({"problem": state["problem"],
                       "subproblem": subproblem, "attempt": 0, "history": []})
            results.append(result)
        return {"results": results}

    async def join(state):
        return await stitch(call, state)

    graph = StateGraph(AgentState)
    graph.add_node("decompose", decompose)
    graph.add_node("search", search_all)
    graph.add_node("join", join)
    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "search")
    graph.add_edge("search", "join")
    graph.add_edge("join", END)
    return graph.compile()


async def run_agent(model, problem, **options):
    """Return state including results; global execution failures have status error."""
    graph = build_agent(model, **options)
    state = {"problem": text(problem), "results": []}
    try:
        async for update in graph.astream(state, stream_mode="updates"):
            for delta in update.values():
                if "results" in delta:
                    state["results"].extend(delta["results"])
                state.update({k: v for k, v in delta.items() if k != "results"})
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        state.update(status="error", error=str(exc), solution="Execution failed; available work is retained.")
    state["results"].sort(key=lambda r: r["subproblem"]["id"])
    return state
