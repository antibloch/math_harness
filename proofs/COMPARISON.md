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

The author compared these drafts using **GPT-6 Instant** and supplied its assessment.
The comparison below summarizes that assessment and records concrete issues visible
in the submitted files. It is not a new GPT-6 Instant evaluation, a complete
independent mathematical audit, or a formal correctness certificate. The three
sample files are preserved without correcting their mathematical or formatting errors.

## Comparative assessment

| Dimension | Standalone LLM | Planner–executor–responder | Math Harness |
|-----------|----------------|----------------------------|--------------|
| Overall finding | PNT deduction invalid as written | Strongest correctness baseline in the supplied review | Richest intermediate development, requiring corrections |
| Construction | Short contour-shift outline | Ordered classical analytic proof | Broader development of estimates, transforms, boundary behavior and synthesis |
| Critical analytic bridge | Unsupported contour estimates and a false small-error inference | Boundary zero-freeness followed by a cited Wiener–Ikehara theorem | Boundary zero-freeness and an explicit Laplace/Tauberian reduction |
| External dependencies | Cites a zero-free region and unspecified estimates | Invokes the substantial Wiener–Ikehara theorem without proof | Invokes an unproved one-sided Tauberian lemma |
| Self-contained? | No | No | No |
| Main value | Exposes a decisive failure in a concise draft | Best existing theorem-based baseline among these samples | More mathematical material to inspect and develop further |

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

This is the more standard classical route. It develops the Euler product and
meromorphic continuation, proves boundary nonvanishing with
\(3+4\cos\phi+\cos2\phi\ge0\), obtains the logarithmic derivative, applies
Wiener–Ikehara, and uses partial summation to conclude PNT.

Its principal external input is **Section 4, the Wiener–Ikehara Tauberian theorem**.
The theorem does substantial work in turning analytic boundary information into
an asymptotic for a nonnegative summatory function. The draft states and invokes
it rather than proving it. The comparison therefore credits this sample as the
strongest theorem-based correctness baseline, while recognizing its reliance on
major cited machinery.

For precision, the theorem's boundary hypothesis should be written in terms of the
continuous extension of \(F(s)-R/(s-1)\), rather than relying on the informal phrase
“continuous except for a simple pole.” In this application, the continuation and
zero-free arguments give local holomorphic regularity after subtracting the pole.
Statements about \(\zeta(1+it)\) should explicitly exclude \(t=0\), where there is
a pole rather than a finite nonzero value. These clarifications do not replace
the missing proof of Wiener–Ikehara.

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

The supplied review favors **planner–executor for current theorem-based correctness**
and **Math Harness for breadth of mathematical development**. The standalone sample
does not establish its conclusion. The harness's additional structure provides
more material for inspection and repair, but its final output is not yet a
complete, reliable, self-contained proof.

This is one qualitative comparison, not a controlled benchmark:

- The shared model does not imply matched prompts, decoding settings, call counts,
  token budgets, latency or total inference cost.
- The harness sample came from incomplete search: five subproblems received full
  model-critic verdicts, while four retained execution errors. The stitcher used
  assessed selections and available unranked work.
- A model's “full” verdict or successful draft status is not a mathematical certificate.
- No repeated-trial success rate or measured architecture-wide advantage is established.

A stronger evaluation would score essential proof obligations, invalid deductions,
the exact statement and use of external theorems, self-containedness, and compute
cost separately, under matched budgets and independent mathematical review.
