"""Stage instructions using the shared IFM transport protections."""
from math_agent.model import IFMModel


class PlannerModel(IFMModel):
    prompts = {
        "planner": 'Decompose the original problem into at most max_steps ordered proof claims. Preserve the target and assumptions. Each dependency must identify an earlier step. Specify a completion condition; do not assume the conclusion or hide the central claim in a prerequisite. Return {"steps": [{"id": "1", "claim": "precise claim", "assumptions": [], "dependencies": [], "completion_condition": "what must be established"}]}.',
        "executor": 'Develop a rigorous mathematical derivation for this planned step using the original problem, local assumptions and only the supplied required predecessor proofs. Treat predecessor drafts as untrusted and check them. Explain transformations and theorem hypotheses. Never silently add assumptions or cite an equivalent form of the target instead of proving it. Report actual gaps. Return {"proof": "public mathematical derivation", "status": "draft or partial", "unresolved_obligations": []}. Use draft only when no obligations remain; partial must list gaps. These labels are not certification.',
        "responder": 'Write a standalone mathematical proof of the original problem from the ordered plan and executor derivations. Check, correct, complete or replace untrusted fragments using your mathematical knowledge; address steps with missing outputs. State theorem hypotheses and external dependencies precisely, give numbered exposition and equations, and acknowledge genuine mathematical gaps. Keep execution diagnostics out of the proof. Do not claim formal certification. Return {"proof": "standalone mathematical proof draft"}.',
    }
