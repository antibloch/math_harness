"""Deterministic responses for exercising the graph without a model or credentials."""
DEMO_PROBLEM = "Prove that the sum of two even integers is even."


class DemoModel:
    async def __call__(self, stage, payload):
        count = payload.get("count", 1)
        if stage == "decompose":
            return {"subproblems": [f"Establish the representation of the even summands using integer multiples of two (route {i})." for i in range(1, count + 1)]}
        if stage == "objects":
            return {"objects": [f"Integer multiples x=2a and y=2b, where a,b are integers (representation {i})." for i in range(1, count + 1)]}
        if stage == "manipulations":
            return {"manipulations": [f"Use the definition of an even integer to express both summands as multiples of two (method {i})." for i in range(1, count + 1)]}
        if stage == "trajectory":
            return {"proof": "Since x and y are even integers, by definition there are integers a and b with x=2a and y=2b."}
        if stage == "critic":
            return {"best_id": payload["candidates"][0]["id"], "verdict": "full",
                    "feedback": "The required integer representations follow directly from the definition of evenness."}
        if stage == "stitch":
            return {"solution": "Let x and y be even integers. There exist integers a and b with x=2a and y=2b. Then x+y=2(a+b). Since a+b is an integer, x+y is even."}
        raise ValueError(f"Unknown demo stage {stage}")
