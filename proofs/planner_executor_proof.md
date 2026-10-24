# Proof of the Prime Number Theorem

We prove
\[
\pi(x)\sim \frac{x}{\log x}\qquad (x\to\infty).
\]

## Notation

For \(\Re s>1\),
\[
\zeta(s)=\sum_{n=1}^\infty \frac1{n^s}.
\]
The von Mangoldt function is
\[
\Lambda(n)=
\begin{cases}
\log p,& n=p^k\text{ for a prime }p\text{ and }k\ge 1,\\
0,& \text{otherwise}.
\end{cases}
\]
Define
\[
\psi(x)=\sum_{n\le x}\Lambda(n),\qquad 
\theta(x)=\sum_{p\le x}\log p.
\]

---

## 1. Euler product and logarithmic derivative

Let \(s=\sigma+it\) with \(\sigma>1\). Since \(\sum n^{-\sigma}<\infty\), the series for \(\zeta(s)\) converges absolutely. For any finite set of primes \(P\),
\[
\prod_{p\in P}(1-p^{-s})^{-1}
=\sum_{\substack{n\ge1\\ p\mid n\Rightarrow p\in P}}\frac1{n^s},
\]
by unique factorization. Letting \(P\) exhaust all primes and using absolute convergence,
\[
\zeta(s)=\prod_p (1-p^{-s})^{-1}.
\]

Taking logarithms and differentiating termwise,
\[
-\frac{\zeta'(s)}{\zeta(s)}
=\sum_p \frac{(\log p)p^{-s}}{1-p^{-s}}
=\sum_{n=1}^\infty \Lambda(n)n^{-s}.
\]
Moreover,
\[
-\frac{\zeta'(s)}{\zeta(s)}
=\sum_p (\log p)p^{-s}
+\sum_p \frac{(\log p)p^{-2s}}{1-p^{-s}}.
\]
The remainder is bounded uniformly for \(\sigma>1\):
\[
\left|\sum_p \frac{(\log p)p^{-2s}}{1-p^{-s}}\right|
\le 2\sum_p (\log p)p^{-2\sigma}
\le 2\sum_{n=2}^\infty (\log n)n^{-2}<\infty.
\]
Hence
\[
-\frac{\zeta'(s)}{\zeta(s)}
=\sum_{n=1}^\infty \Lambda(n)n^{-s}
=\sum_p (\log p)p^{-s}+O(1).
\]

---

## 2. Truncated explicit formula

Put
\[
\Psi(s)=-\frac{\zeta'(s)}{\zeta(s)}.
\]
For \(x\ge 2\), let
\[
c=1+\frac1{\log x},
\]
so \(1<c<2\), and define
\[
I_T(x)=\frac1{2\pi i}\int_{c-iT}^{c+iT}\Psi(s)\frac{x^s}{s}\,ds.
\]
The truncated Perron formula gives
\[
\psi_0(x)=I_T(x)+O\!\left(\frac{x}{T}\log^2(xT)+\log x\right),
\]
where \(\psi_0(x)=\frac12(\psi(x+)+\psi(x-))\). Since \(\psi(x)-\psi_0(x)=O(\log x)\),
\[
\psi(x)=I_T(x)+O\!\left(\frac{x}{T}\log^2(xT)+\log x\right).
\]

Choose \(T\ge2\) so that no nontrivial zero of \(\zeta\) has imaginary part \(\pm T\). Shift the contour to the rectangle with vertices \(c-iT,c+iT,-1+iT,-1-iT\). Inside, \(\Psi(s)x^s/s\) has poles at:

- \(s=1\), where \(\Psi(s)\) has residue \(1\), so the residue is \(x\);
- each nontrivial zero \(\rho\) with \(|\Im\rho|<T\), counted with multiplicity \(m_\rho\), where the residue is \(-m_\rho x^\rho/\rho\);
- \(s=0\), where the residue is \(-\log(2\pi)\), since \(\zeta'(0)/\zeta(0)=\log(2\pi)\).

There are no trivial zeros inside the rectangle because its left edge is \(\Re s=-1\). The standard estimates on the horizontal and left vertical edges give
\[
I_T(x)=x-\sum_{|\Im\rho|<T}m_\rho\frac{x^\rho}{\rho}
-\log(2\pi)
+O\!\left(\frac{x}{T}\log^2(xT)+\log^2(xT)\right).
\]
The term \(-\log(2\pi)\) and the earlier \(O(\log x)\) are absorbed into \(O(\log^2(xT))\). Thus
\[
\psi(x)=x-\sum_{|\Im\rho|\le T}m_\rho\frac{x^\rho}{\rho}
+O\!\left(\frac{x}{T}\log^2(xT)+\log^2(xT)\right),
\]
with zeros counted with multiplicity and an indentation used if a zero ordinate coincides with the prescribed height.

---

## 3. Nonvanishing on \(\Re(s)=1\)

For \(\sigma>1\),
\[
\log\zeta(\sigma)=\sum_{n=2}^\infty \frac{\Lambda(n)}{n^\sigma\log n},
\]
and
\[
\Re\log\zeta(\sigma+it)
=\sum_{n=2}^\infty \frac{\Lambda(n)\cos(t\log n)}{n^\sigma\log n}.
\]
For every real \(\theta\),
\[
3+4\cos\theta+\cos 2\theta
=3+4\cos\theta+(2\cos^2\theta-1)
=2(1+\cos\theta)^2\ge0.
\]
Since \(\Lambda(n)\ge0\), define
\[
H(\sigma)=3\log\zeta(\sigma)+4\Re\log\zeta(\sigma+it)+\Re\log\zeta(\sigma+2it).
\]
Then \(H(\sigma)\ge0\) for all \(\sigma>1\).

Suppose \(t\ne0\) and \(\zeta(1+it)=0\) with multiplicity \(m\ge1\). Let \(\sigma=1+\varepsilon\), \(\varepsilon\to0+\). Then
\[
\log\zeta(\sigma)=-\log\varepsilon+O(1),
\]
\[
\Re\log\zeta(\sigma+it)=\log|\zeta(\sigma+it)|\le m\log\varepsilon+O(1),
\]
and, since \(1+2it\) is not the pole \(s=1\),
\[
\Re\log\zeta(\sigma+2it)=O(1).
\]
Therefore
\[
H(\sigma)\le 3(-\log\varepsilon-O(1))+4(m\log\varepsilon+O(1))+O(1)
=(-3+4m)\log\varepsilon+O(1).
\]
Since \(m\ge1\), we have \(-3+4m\ge1\), and as \(\varepsilon\to0+\), \(\log\varepsilon\to-\infty\). Hence \(H(\sigma)\to-\infty\), contradicting \(H(\sigma)\ge0\). For \(t=0\), \(\zeta\) has a simple pole at \(s=1\), not a zero. Thus
\[
\zeta(1+it)\ne0\qquad\text{for all }t\in\mathbb R.
\]

---

## 4. Zero-free region and \(\psi(x)\sim x\)

We use the classical zero-free region of de la Vallée Poussin:

> **Theorem.** There is a constant \(c>0\) such that
> \[
> \zeta(s)\ne0\qquad\text{for }\sigma\ge 1-\frac{c}{\log(|t|+2)}.
> \]

> *Proof sketch.* This follows from the inequality of Step 3, the functional equation for \(\zeta\), and Hadamard's factorization theorem; the argument is standard and can be found in any textbook on analytic number theory.

We also use the standard zero-counting estimate
\[
N(T)=\#\{\rho:\zeta(\rho)=0,\ 0<\Re\rho<1,\ |\Im\rho|\le T\}=O(T\log T).
\]

Choose
\[
T=\exp(\sqrt{\log x}).
\]
Then
\[
\log(xT)=\log x+\sqrt{\log x}=O(\log x).
\]
For any zero \(\rho=\beta+i\gamma\) with \(|\gamma|\le T\), the zero-free region gives
\[
\beta\le 1-\frac{c}{\log(|\gamma|+2)}
\le 1-\frac{c}{\log(T+2)}.
\]
Since \(\log(T+2)=\sqrt{\log x}+O(1)\),
\[
|x^\rho|=x^\beta
\le x\exp\!\left(-\frac{c\log x}{\sqrt{\log x}+O(1)}\right)
\le x e^{-(c/2)\sqrt{\log x}}
\]
for large \(x\). By partial summation from \(N(T)=O(T\log T)\),
\[
\sum_{|\gamma|\le T}\frac1{|\rho|}=O(\log^2 T)=O(\log^2 x).
\]
Therefore
\[
\left|\sum_{|\gamma|\le T}m_\rho\frac{x^\rho}{\rho}\right|
\le x e^{-(c/2)\sqrt{\log x}}\,O(\log^2 x)=o(x).
\]
The error terms are
\[
O\!\left(\frac{x}{T}\log^2(xT)+\log^2(xT)\right)
=O\!\left(x e^{-\sqrt{\log x}}\log^2 x+\log^2 x\right)=o(x).
\]
Thus the explicit formula yields
\[
\psi(x)=x+o(x).
\]

---

## 5. Conversion to primes

We first relate \(\psi(x)\) and \(\theta(x)\). For prime powers with exponent \(k\ge2\), the prime \(p\) satisfies \(p\le\sqrt{x}\), and the number of such powers is at most \(\log x/\log p\). Hence
\[
\psi(x)-\theta(x)
=\sum_{\substack{p^k\le x\\ k\ge2}}\log p
\le \sum_{p\le\sqrt{x}}\frac{\log x}{\log p}\log p
=\pi(\sqrt{x})\log x
=O(\sqrt{x}).
\]
Thus
\[
\theta(x)=\psi(x)+O(\sqrt{x})=x+o(x).
\]

By partial summation,
\[
\pi(x)=\sum_{p\le x}1
=\frac{\theta(x)}{\log x}
+\int_2^x \frac{\theta(t)}{t\log^2 t}\,dt+O(1).
\]
Since \(\theta(t)=t+o(t)\),
\[
\frac{\theta(x)}{\log x}
=\frac{x}{\log x}+o\!\left(\frac{x}{\log x}\right),
\]
and
\[
\int_2^x \frac{\theta(t)}{t\log^2 t}\,dt
=\int_2^x \frac{dt}{\log^2 t}
+o\!\left(\int_2^x \frac{dt}{\log^2 t}\right)
=O\!\left(\frac{x}{\log^2 x}\right)
=o\!\left(\frac{x}{\log x}\right).
\]
Therefore
\[
\pi(x)=\frac{x}{\log x}+o\!\left(\frac{x}{\log x}\right).
\]

This is the Prime Number Theorem. \(\square\)
