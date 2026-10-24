# Agent Architecture

![Agent architecture](math_agent_architecture.png)

This source figure describes the logical search branches. The current implementation
executes all branches sequentially:

1. Decompose the original problem into `i` subproblems.
2. For each subproblem, generate `j` mathematical objects. For each object,
   generate `k` manipulations and develop one candidate trajectory per manipulation.
3. The local critic selects the strongest trajectory. A partial verdict triggers
   one retry with the previous attempt and critic feedback; a full verdict ends
   that subproblem's search.
4. After all subproblems settle, the stitcher receives the original problem,
   every subproblem goal, and its latest critic-selected trajectory. If no
   selection exists, available candidates are supplied as unranked context;
   otherwise the goal alone is retained. The stitcher drafts a standalone proof.

API failures are separate from mathematical verdicts. Requests have cancellable
total deadlines and bounded transient retries, with rate-limit backoff. Remaining
routes continue after an execution error, and available work is retained for
stitching. An execution error ends that branch without a critic review or a new
mathematical retry; an earlier critic selection remains available if present.

The figure's branches do not imply concurrent API calls. The current stitcher
also accepts incomplete search results. A generated draft or a critic's full
verdict does not certify mathematical correctness.
