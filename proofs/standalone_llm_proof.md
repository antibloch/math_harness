# Standalone underlying model proof

Prompt: Prove PNT

Independently certified: no.

The Prime Number Theorem (PNT) states that the prime‑counting function π(x) satisfies

    π(x) ~ x / log x   as x → ∞,

i.e. the ratio π(x) / (x / log x) tends to 1.  A standard proof proceeds via complex analysis and the non‑vanishing of the Riemann zeta‑function ζ(s) on the line Re(s)=1.  Below is a self‑contained outline of the argument.

1. **Chebyshev’s functions.**  Define

       ψ(x) = Σ_{p^k ≤ x} log p   (sum over prime powers),
       θ(x) = Σ_{p ≤ x} log p.

   Both ψ and θ are monotone and satisfy ψ(x) = θ(x) + O(√x).  Moreover, π(x) = θ(x)/log x + O(θ(x)/log^2 x), so it suffices to prove ψ(x) ~ x.

2. **Integral representation.**  For Re(s) > 1 the Dirichlet series for ζ(s) is

       ζ(s) = Σ_{n=1}^∞ n^{-s} = ∏_{p} (1 - p^{-s})^{-1}.

   Taking logarithmic derivatives gives

       -ζ'(s)/ζ(s) = Σ_{n=1}^∞ Λ(n) n^{-s},

   where Λ(n) is the von Mangoldt function (Λ(p^k)=log p, otherwise 0).  By Perron’s formula, for x>1 and c>1,

       ψ(x) = (1/2π i) ∫_{c-i∞}^{c+i∞} (-ζ'(s)/ζ(s)) x^{s}/s ds.

3. **Zero‑free region.**  The key analytic input is that ζ(s) has no zeros on the line Re(s)=1.  This follows from the classical zero‑free region of Hadamard–de la Vallée‑Poussin: there exist constants A,B>0 such that ζ(s)≠0 for

       σ > 1 - A / (log |t| + B)   (σ=Re(s), t=Im(s)).

   Consequently, -ζ'(s)/ζ(s) is analytic in a neighbourhood of the line σ=1 except for a simple pole at s=1 with residue 1.

4. **Shift of the contour.**  Move the line of integration in Perron’s formula left to σ = 1 - δ, where δ = A/(log x + B).  The integrand has a simple pole at s=1, contributing the main term x.  The integral over the new vertical line is bounded by

       O( x^{1-δ} ∫_{-∞}^{∞} |ζ'(σ+it)/ζ(σ+it)| / |σ+it| dt ).

   Using the zero‑free region and standard estimates for ζ(s) in that region, the integral is O( x^{1-δ} log^2 x ).  Since δ ≍ 1/ log x, we have x^{1-δ} = x·e^{-δ log x} = x·e^{-A+o(1)} = o(x).

5. **Error term.**  The contribution from the horizontal segments at height ±T (with T chosen as a power of x) is also O( x^{1-δ} log^2 x ).  Hence

       ψ(x) = x + O( x·e^{-c√{log x}} )

   for some constant c>0.  In particular ψ(x) ~ x.

6. **From ψ to π.**  Since ψ(x) = θ(x) + O(√x) and θ(x) = Σ_{p≤x} log p, partial summation yields

       π(x) = θ(x)/log x + ∫_{2}^{x} θ(t)/(t log^2 t) dt.

   Substituting θ(t) = t + o(t) gives

       π(x) = x/ log x + o( x/ log x ).

   Therefore π(x) ~ x / log x, which is the Prime Number Theorem.

Thus, using the analytic properties of the Riemann zeta‑function—specifically its non‑vanishing on Re(s)=1—we have proved that the number of primes up to x is asymptotic to x / log x.
