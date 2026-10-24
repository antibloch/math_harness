Architecture approved by the user on 2026-10-24, review version 3 (stitcher correction):
/tmp/architecture-review-stitcher-WoqnOf/review-v3.excalidraw

Source: math_agent_architecture.png. Corrected ranges: subproblems 1 through i,
objects 1 through j per subproblem, manipulations and matching trajectories
1 through k per object. Each subproblem owns its candidates, critic and retry.

LangGraph decomposes, runs isolated subproblem searches sequentially, and joins
their terminal results. A branch graph generates objects, generates manipulations
per object, develops one trajectory per manipulation, then compares all local
candidates in its critic. The original subproblem context reaches every trajectory.
A partial verdict loops once to objects with the failed attempt and critic feedback.
Other branches do not restart. A full verdict terminates that branch.

The final join waits for every branch and always calls the IFM stitcher. It receives
original problem, all subproblem goals, and each latest successful critic selection
(full or partial). If a retry fails, the earlier assessed selection survives. Without
a selection, generated candidates are supplied as unranked context; without any
candidate, the subproblem goal is still included. The final model checks, completes,
corrects or replaces arguments using its mathematical knowledge and drafts one
standalone proof. Provider failures remain execution errors, never partial verdicts
or reasons to add a mathematical retry.

The previous full-only gate is removed. A successful draft has status complete;
search_status separately records full or incomplete search. proof.md contains the
model prose; run.json keeps search results, verdicts and provider diagnostics.
Draft generation does not certify mathematical correctness. If stitching itself
fails, preserve all settled branch results with an explicit execution error.
The stitch(model, state) function also drafts from saved state without rerunning
search. No additional ranking call, agent or persistence framework is introduced.

Implementation uses direct functions, ordinary dictionaries, two graph builders,
one IFM adapter using langchain_openai.ChatOpenAI and a command line. No persistence or additional agents.
Subproblems run one at a time. Each object generates its manipulations, and each
manipulation develops its trajectory before the next object starts. Explicit loops
replace concurrent tasks, dispatch, semaphores and result reducers. The critic
compares local candidates after route generation. Successful outputs survive a
failed sibling request; remaining routes are still attempted. The final stitcher
runs after all subproblems settle. Counts and provenance are validated
at model boundaries. Exact repeats are
rejected; semantic novelty remains a model responsibility.

Acceptance: verify i*j*k initial trajectories; every candidate reaches only its own
critic; partial triggers at most one local retry; full siblings remain unchanged;
original-problem context reaches stitch; exhaustion preserves candidates; execution
errors remain distinguishable; run a deterministic end-to-end example. A live model
run requires configured endpoint/model credentials. A full verdict is not a proof
certificate.

Provider configured on 2026-10-24: IFM, https://api.ifm.ai/v1, model
IFM/K2-Horizon-375B-A23B, authenticated from IFM_API_KEY.

API requests are strictly sequential; there is no concurrency setting.
Each API attempt has a total deadline of 900 seconds by default; stalled calls
are cancelled and may be retried. Connection, write and pool waits stay
bounded. Transport recovery retries a failed transient request at most twice,
honors Retry-After and shares cooldown across routes. Successful stages are not
restarted; transport retries never consume a mathematical retry. Permanent errors,
truncated output and explicit exhausted daily quotas are terminal. Wait requests
longer than five minutes are reported rather than automatically waited out.
Per-attempt failures and recovery status remain in run.json.

Version 3 acceptance: exactly one final model call after all routes settle; all goals
and original problem present; selected partial trajectories and earlier selections
survive failed retries; failed critics supply unranked candidates; empty branches
supply goals; drafted prose reaches proof.md while diagnostics remain in run.json.
