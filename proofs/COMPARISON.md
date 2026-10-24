# Comparing Three Prime Number Theorem Proof Drafts

## Samples and provenance

All three samples address **“Prove PNT”**, with target

$$\pi(x)\sim\frac{x}{\log x}\qquad(x\to\infty).$$

The author reports using the same underlying model,
`IFM/K2-Horizon-375B-A23B`, with three different ways of managing its context:

- [Standalone LLM](standalone_llm_proof.md): one problem prompt and one proof draft.
- [Planner–executor–responder](planner_executor_proof.md): an ordered plan,
  step-level derivations with required predecessor context, and final synthesis.
- [Math Harness](math_harness_proof.md): subproblems, mathematical objects,
  manipulations, candidate trajectories, local criticism, one permitted local
  mathematical retry, and final stitching.

This assessment concerns only the three linked samples. It records concrete
mathematical findings from their text and available run results. The current set
has not received a joint GPT-6 Instant evaluation. This is a qualitative review,
not a complete independent mathematical audit or a formal correctness certificate.
Sample files retain the model's mathematical and formatting errors without
editorial repair.

### Planner–executor run

The prompt was “Prove PNT,” with exactly five planned steps. Steps 1 and 3 returned
model-labeled drafts. Step 2 identified errors in its planned explicit formula and
returned partial work; steps 4 and 5 were blocked by unresolved prerequisites.
The responder could still correct or replace fragments using its own knowledge.

Its initial JSON synthesis exhausted 32,768 completion tokens. Only final synthesis
was rerun from the saved plan and executor responses, using plain Markdown,
65,536 completion tokens, temperature 1.0, top-p 0.95, high reasoning effort,
a 600-second per-attempt deadline and one transient retry. It finished in about
47 seconds. This demonstrates recovered draft generation, not completed executor
coverage or mathematical certification. The published file is the recovered model
output, copied unchanged.

## Comparative assessment

| Dimension | Standalone LLM | Planner–executor–responder | Math Harness |
|-----------|----------------|----------------------------|--------------|
| Overall finding | PNT deduction invalid as written | Developed contour/zero-sum strategy; mathematical repairs required | Broad intermediate development, requiring corrections |
| Construction | Short contour-shift outline | Five-section contour/zero-sum argument with final synthesis from partial executor work | Development of elementary estimates, transforms, boundary behavior and synthesis |
| Critical analytic bridge | Unsupported contour estimates and a false small-error inference | Truncated explicit formula and a cited quantitative zero-free region, with growing truncation height | Boundary zero-freeness and an explicit Laplace/Tauberian reduction |
| External dependencies | Cites a zero-free region and unspecified estimates | Invokes truncated Perron estimates, contour bounds, the quantitative zero-free region and zero counting without full derivations | Invokes an unproved one-sided Tauberian lemma |
| Self-contained? | No | No | No |
| Main value | Exposes a decisive failure in a concise draft | More explicit development of the zero-sum estimate; shows an executor identifying a false planned claim | Broader elementary/Tauberian material to inspect and develop further |

Using a correctly stated and applicable standard theorem is legitimate mathematical
practice. An unproved external theorem limits self-containedness; it does not by
itself invalidate a theorem-based proof. Conversely, greater breadth or more calls
does not establish greater correctness.

## Findings in the standalone draft

The decisive error is in **Step 4, “Shift of the contour.”** It takes
\(\delta=A/(\log x+B)\) and asserts \(x^{1-\delta}=o(x)\). But

$$\frac{x^{1-\delta}}{x}=\exp(-\delta\log x)\longrightarrow e^{-A}>0.$$

The additional claimed factor \(\log^2 x\) does not repair this error. The draft
also moves an infinite contour to a fixed vertical line without establishing a
zero-free region or integrable bounds along its entire height. The much stronger
error term asserted in Step 5 is not derived from the displayed estimates.

The prime-power estimates and partial-summation claims in Step 1 are not adequately
justified in the text. Although the proof calls itself a self-contained outline,
it cites substantial analytic input and fails at the deduction of \(\psi(x)\sim x\).

## Findings in the planner–executor draft

The planner–executor draft develops the Euler product and logarithmic derivative,
a truncated explicit formula, boundary nonvanishing, a quantitative zero-free region
and a zero-sum estimate, followed by partial summation.

A useful improvement over the standalone draft is **Section 4's growing height**
\(T=\exp(\sqrt{\log x})\). With a suitably justified explicit formula and zero-free
region, its displayed estimate
\(x\exp(-c\sqrt{\log x}/2)\log^2 x=o(x)\) has the required decay. It does not repeat
the standalone draft's constant-exponential-factor mistake.

However, this is still an unverified theorem-based draft, with substantial gaps:

- **Section 2:** truncated Perron and contour-edge bounds are asserted as standard
  estimates without full hypotheses or derivations. Merely choosing a height that
  is not a zero ordinate does not by itself establish uniform logarithmic-derivative
  bounds near zeros. The later choice of height needs to be reconciled with suitable
  contour estimates. The declaration \(1+1/\log x<2\) for every \(x\ge2\) is also
  false for small \(x\), although restricting to large \(x\) repairs that local issue.
- **Section 3:** the term \(\log|\zeta(\sigma+2it)|\) is declared \(O(1)\). If
  \(\zeta(1+2it)=0\), it can instead tend to \(-\infty\). The contradiction can
  use an upper bound, or explicitly include the zero's multiplicity, but the stated
  two-sided boundedness is not justified. At \(t=0\), zeta has a pole; the finite
  nonzero-value statement should exclude that point.
- **Section 4:** the quantitative de la Vallée Poussin zero-free region and
  \(N(T)=O(T\log T)\) are substantial external inputs. The brief reference to a
  standard argument is not their proof. Analytic continuation and values used in
  contour shifting also need establishment or precise citation. Multiplicity
  conventions should be made consistent between the sum and its explicit weights.
- **Section 5:** the conclusion
  \(\pi(\sqrt{x})\log x=O(\sqrt{x})\) needs an upper bound of Chebyshev strength
  that this draft does not establish. The elementary weaker bound
  \(\pi(\sqrt{x})\log x\le\sqrt{x}\log x=o(x)\) would already suffice for the
  transition to \(\theta(x)\sim x\); it should be used unless the stronger bound
  is proved independently.

The strategy is viable with properly stated standard results and local repairs,
but the draft is not established as correct as written.

## Findings in the Math Harness draft

This sample develops more intermediate mathematical material: Chebyshev estimates,
prime-counting equivalences, the Euler product, logarithmic differentiation, a
Mellin representation, zeta continuation, boundary zero-freeness and regularity,
and a more explicit analytic-to-arithmetic reduction. This makes it a mathematically
richer draft and a useful starting point for further proof development.

Its Tauberian section introduces

$$q(y)=e^{-y}A(e^y),\qquad
q(y+h)\ge e^{-h}q(y),\qquad
L(\lambda)=\frac{F(1+\lambda)}{1+\lambda}.$$

These relations expose the intended bridge between monotonicity, a Laplace transform
and the summatory asymptotic. However, **Section 7 does not prove the decisive
one-sided Tauberian lemma**. Its name and reference to a Newman contour argument
are not a precise citation or a derivation of the stated result. Its exact
hypotheses and applicability still need verification. Thus the harness also relies
on substantial external Tauberian input; it has not eliminated that dependency.

Other concrete defects remain:

- **Lemma 1:** the upper bound uses \(\prod_{p\le n}p\le4^n\) without deriving it
  in this document. The lower-bound argument then relies on that upper estimate.
- **Lemma 2:** an expression ends with `O(x^{Therefore`, leaving the estimate and
  transition corrupted. The next section also contains `For σ=Re{s}∞.`
- **Section 4:** the Laurent expansion incorrectly has constant term \(1\).
  The correct expansion is
  \(\zeta(s)=1/(s-1)+\gamma+O(s-1)\), with Euler's constant \(\gamma\).
  The residue remains \(1\), so the intended pole argument is repairable.

The Laurent expansion can be checked against the
[NIST Digital Library of Mathematical Functions, Equation 25.2.4](https://dlmf.nist.gov/25.2.E4).
For an actual short analytic argument and its proved analytic input, see Don Zagier's
[Newman's Short Proof of the Prime Number Theorem](https://sites.math.rutgers.edu/~zeilberg/EM18/zagier.pdf).
That reference does not automatically validate the different lemma stated in this draft.

## What this experiment supports

The standalone deduction fails at a decisive asymptotic step. The planner–executor
draft gives a more developed contour/zero-sum route with the right type of decay,
but relies on substantial analytic inputs and has unresolved justifications and
local defects. Math Harness develops a broader elementary/Tauberian route, with
its own gaps and corrupted expressions.

Math Harness is more extensive in foundational and intermediate development:
it expands Chebyshev estimates, prime-counting equivalences, Mellin transforms
and the Tauberian bridge. Planner–executor makes the contour/zero-sum strategy
more explicit, but relies more heavily on established analytic results as
references, including truncated Perron estimates, contour bounds, the quantitative
zero-free region and zero counting. Neither breadth nor a
standard choice of strategy resolves the identified proof obligations. Both are
useful drafts for repair; **no overall correctness winner is established** for
these samples.

This is one qualitative comparison, not a controlled benchmark:

- The shared model does not imply matched prompts, decoding settings, call counts,
  token budgets, latency or total inference cost.
- The harness sample came from incomplete search: five subproblems received full
  model-critic verdicts, while four retained execution errors. The stitcher used
  assessed selections and available unranked work.
- The planner–executor run also had incomplete execution: only three
  of five steps produced executor responses, one of those was partial, and final
  synthesis independently filled or replaced missing arguments.
- A model's “full” verdict or successful draft status is not a mathematical certificate.
- No repeated-trial success rate or measured architecture-wide advantage is established.

A stronger evaluation would score essential proof obligations, invalid deductions,
the exact statement and use of external theorems, self-containedness, and compute
cost separately, under matched budgets and independent mathematical review.
