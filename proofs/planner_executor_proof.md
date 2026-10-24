# Prime Number Theorem

**Theorem.** Let \(\pi(x)\) denote the number of primes \(p\le x\). Then
\[
\pi(x)\sim \frac{x}{\log x}\qquad (x\to\infty).
\]

---

## 1. The Riemann zeta function and its Euler product

For \(\Re(s)>1\), define
\[
\zeta(s)=\sum_{n=1}^\infty n^{-s},\qquad n^{-s}=e^{-s\log n}.
\]
If \(s=\sigma+it\) with \(\sigma>1\), then \(|n^{-s}|=n^{-\sigma}\), and \(\sum_{n=1}^\infty n^{-\sigma}\) converges by the integral test. Hence \(\zeta(s)\) is well defined and the series converges absolutely for \(\Re(s)>1\).

For a real number \(y\ge 2\), consider the finite Euler product
\[
P_y(s)=\prod_{p\le y}(1-p^{-s})^{-1}.
\]
Since \(|p^{-s}|=p^{-\sigma}<1\), each factor is the absolutely convergent geometric series
\[
(1-p^{-s})^{-1}=\sum_{k=0}^\infty p^{-ks}.
\]
Expanding the finite product and using unique factorization,
\[
P_y(s)=\sum_{\substack{n\ge 1\\ p\mid n\Rightarrow p\le y}} n^{-s}.
\]
As \(y\to\infty\), the set of integers counted in the sum increases to all positive integers. More precisely, if \(\varepsilon>0\), choose \(N\) such that \(\sum_{n>N}n^{-\sigma}<\varepsilon\). If \(y\ge N\), then every \(n\le N\) has all prime factors \(\le y\), so the omitted terms satisfy
\[
|P_y(s)-\zeta(s)|\le \sum_{n\notin S_y}n^{-\sigma}\le \sum_{n>N}n^{-\sigma}<\varepsilon.
\]
Thus \(P_y(s)\to \zeta(s)\), and therefore
\[
\zeta(s)=\prod_{p}\left(1-p^{-s}\right)^{-1},\qquad \Re(s)>1.
\]
Since \(\sum_p p^{-\sigma}<\infty\), the infinite product converges absolutely and no factor is zero. Hence
\[
\zeta(s)\neq 0\qquad (\Re(s)>1).
\]

---

## 2. Meromorphic continuation to \(\Re(s)>0\)

For \(\Re(s)>1\), Euler–Maclaurin summation gives
\[
\sum_{n=1}^N n^{-s}
=
\int_1^N x^{-s}\,dx+\frac{1+N^{-s}}2
-s\int_1^N \left(\{x\}-\frac12\right)x^{-s-1}\,dx,
\]
where \(\{x\}=x-\lfloor x\rfloor\). Letting \(N\to\infty\),
\[
\zeta(s)=\frac{1}{s-1}+\frac12
+s\int_1^\infty \left(\frac12-\{x\}\right)x^{-s-1}\,dx.
\]
Rewriting,
\[
\zeta(s)=\frac{1}{s-1}+1-s\int_1^\infty \{x\}x^{-s-1}\,dx.
\tag{1}
\]
The integral converges uniformly on compact subsets of \(\Re(s)>0\), because
\[
\left|\{x\}x^{-s-1}\right|\le x^{-\sigma-1},\qquad
\int_1^\infty x^{-\sigma-1}\,dx=\frac1\sigma<\infty.
\]
Thus the right-hand side of (1) is meromorphic on \(\Re(s)>0\), with the only singularity at \(s=1\), where it has a simple pole with residue \(1\). Therefore \(\zeta(s)\) extends meromorphically to \(\Re(s)>0\), with a single simple pole at \(s=1\) of residue \(1\).

---

## 3. Nonvanishing of \(\zeta\) on the line \(\Re(s)=1\)

We prove that
\[
\zeta(1+it)\neq 0\qquad (t\in\mathbb R).
\]
The case \(t=0\) is immediate because \(\zeta\) has a pole, not a zero, at \(s=1\).

Assume \(t\neq 0\). For \(\sigma>1\), define
\[
F_t(\sigma)=\log|\zeta(\sigma+it)|.
\]
Using the Euler product,
\[
\log \zeta(\sigma+it)
=
\sum_{p}\sum_{m=1}^\infty \frac{1}{m p^{m(\sigma+it)}},
\]
so
\[
F_t(\sigma)=\sum_{p}\sum_{m=1}^\infty
\frac{\cos(mt\log p)}{m p^{m\sigma}}.
\]
The trigonometric identity
\[
3+4\cos\phi+\cos 2\phi=2(1+\cos\phi)^2\ge 0
\]
applied with \(\phi=mt\log p\) gives
\[
3F_0(\sigma)+4F_t(\sigma)+F_{2t}(\sigma)
=
\sum_{p}\sum_{m=1}^\infty
\frac{3+4\cos(mt\log p)+\cos(2mt\log p)}
{m p^{m\sigma}}
\ge 0.
\tag{2}
\]

Suppose, for contradiction, that \(\zeta(1+it)=0\), and let \(k\ge 1\) be its order. Since \(\zeta\) is meromorphic and not identically zero,
\[
\zeta(s)=c(s-(1+it))^k+O\left((s-(1+it))^{k+1}\right),
\qquad c\neq 0,
\]
as \(s\to 1+it\). Along \(s=\sigma+it\) with \(\sigma\downarrow 1\),
\[
F_t(\sigma)=k\log(\sigma-1)+O(1)
=-k\log\frac1{\sigma-1}+O(1).
\tag{3}
\]
At \(s=1\),
\[
\zeta(s)=\frac1{s-1}+O(1),
\]
so
\[
F_0(\sigma)=\log|\zeta(\sigma)|
=\log\frac1{\sigma-1}+O(1).
\tag{4}
\]
Since \(t\neq 0\), the point \(1+2it\neq 1\), and \(\zeta\) is holomorphic there. Let \(\ell\ge 0\) be the order of the zero of \(\zeta\) at \(1+2it\), with \(\ell=0\) if the value is nonzero. Then
\[
F_{2t}(\sigma)=-\ell\log\frac1{\sigma-1}+O(1).
\tag{5}
\]
Combining (3), (4), and (5),
\[
3F_0(\sigma)+4F_t(\sigma)+F_{2t}(\sigma)
=
(3-4k-\ell)\log\frac1{\sigma-1}+O(1).
\]
Since \(k\ge 1\) and \(\ell\ge 0\), the coefficient \(3-4k-\ell\le -1\). Hence as \(\sigma\downarrow 1\), the right-hand side tends to \(-\infty\), contradicting (2). Therefore no such \(t\neq 0\) exists, and
\[
\zeta(1+it)\neq 0\qquad (t\in\mathbb R).
\]

---

## 4. The Wiener–Ikehara Tauberian theorem

We use the following standard Tauberian theorem.

**Theorem (Wiener–Ikehara).** Let \((a_n)_{n\ge 1}\) be a sequence of nonnegative real numbers, and set
\[
A(x)=\sum_{n\le x}a_n.
\]
Suppose the Dirichlet series
\[
F(s)=\sum_{n=1}^\infty a_n n^{-s}
\]
converges for \(\Re(s)>1\). If \(F(s)\) extends to a function continuous on \(\Re(s)\ge 1\) except for a simple pole at \(s=1\) with residue \(R\), then
\[
A(x)\sim R x\qquad (x\to\infty).
\]

---

## 5. Application to the von Mangoldt function

Define the von Mangoldt function
\[
\Lambda(n)=
\begin{cases}
\log p,& n=p^k\text{ for some prime }p\text{ and }k\ge 1,\\
0,& \text{otherwise}.
\end{cases}
\]
For \(\Re(s)>1\),
\[
\log \zeta(s)
=
\sum_p \log\left(1-p^{-s}\right)^{-1}
=
\sum_p\sum_{m=1}^\infty \frac{1}{m p^{ms}}.
\]
Differentiating termwise,
\[
\frac{\zeta'(s)}{\zeta(s)}
=
-\sum_p\sum_{m=1}^\infty (\log p)p^{-ms}
=
-\sum_{n=1}^\infty \Lambda(n)n^{-s}.
\]
Thus
\[
-\frac{\zeta'(s)}{\zeta(s)}
=
\sum_{n=1}^\infty \Lambda(n)n^{-s},
\qquad \Re(s)>1.
\]
The coefficients \(\Lambda(n)\) are nonnegative, and the series converges absolutely for \(\Re(s)>1\) because \(\Lambda(n)\le \log n\) and \(\sum_{n=1}^\infty (\log n)n^{-\sigma}<\infty\) for \(\sigma>1\).

By Section 3, \(\zeta(s)\) has no zeros on \(\Re(s)\ge 1\). The only singularity of \(-\zeta'(s)/\zeta(s)\) on \(\Re(s)\ge 1\) is at \(s=1\). Near \(s=1\),
\[
\zeta(s)=\frac1{s-1}+O(1),
\qquad
\zeta'(s)=-\frac1{(s-1)^2}+O\left(\frac1{s-1}\right),
\]
so
\[
-\frac{\zeta'(s)}{\zeta(s)}
=
\frac1{s-1}+O(1).
\]
Hence \(-\zeta'(s)/\zeta(s)\) has a simple pole at \(s=1\) with residue \(1\), and is holomorphic, hence continuous, elsewhere on \(\Re(s)\ge 1\).

Applying the Wiener–Ikehara theorem with \(a_n=\Lambda(n)\) and \(R=1\), we obtain
\[
\sum_{n\le x}\Lambda(n)\sim x.
\]
Let
\[
\psi(x)=\sum_{n\le x}\Lambda(n)=\sum_{p^k\le x}\log p.
\]
Then
\[
\psi(x)\sim x.
\tag{6}
\]

---

## 6. From \(\psi(x)\sim x\) to \(\pi(x)\sim x/\log x\)

Define the Chebyshev function
\[
\theta(x)=\sum_{p\le x}\log p.
\]
Since
\[
\psi(x)=\sum_{k\ge 1}\theta\left(x^{1/k}\right),
\]
we have
\[
\psi(x)=\theta(x)+\theta\left(x^{1/2}\right)+\theta\left(x^{1/3}\right)+\cdots.
\]
For \(k\ge 2\),
\[
\theta\left(x^{1/k}\right)
\le \pi\left(x^{1/k}\right)\log\left(x^{1/k}\right)
\le x^{1/k}\frac{\log x}{k}.
\]
Therefore
\[
\sum_{k=2}^\infty \theta\left(x^{1/k}\right)
=O\left(x^{1/2}\log x\right)=o(x).
\]
Indeed, the \(k=2\) term is \(O(\sqrt{x}\log x)\), while the \(O(\log x)\) terms with \(k\ge3\) contribute at most \(O(x^{1/3}(\log x)^2)=o(\sqrt{x}\log x)\). Thus (6) gives
\[
\theta(x)\sim x.
\tag{7}
\]

We now use partial summation. Since \(\theta\) is a step function with jumps \(\log p\) at primes,
\[
\pi(x)=\sum_{p\le x}1
=
\int_{2^-}^x \frac{1}{\log t}\,d\theta(t).
\]
Integration by parts, with the lower endpoint at \(2^-\) and \(\theta(2^-)=0\), yields the exact identity
\[
\pi(x)
=
\frac{\theta(x)}{\log x}
+
\int_2^x \frac{\theta(t)}{t(\log t)^2}\,dt.
\tag{8}
\]

Equation (7) already implies \(\theta(t)=O(t)\). Using this in (8),
\[
\int_2^x \frac{\theta(t)}{t(\log t)^2}\,dt
=
O\left(\int_2^x \frac{dt}{(\log t)^2}\right)
=
O\left(\frac{x}{(\log x)^2}\right)
=
o\left(\frac{x}{\log x}\right).
\]
Together with (7), the first term in (8) satisfies
\[
\frac{\theta(x)}{\log x}\sim \frac{x}{\log x}.
\]
Therefore
\[
\pi(x)\sim \frac{x}{\log x},
\]
which is the Prime Number Theorem.
