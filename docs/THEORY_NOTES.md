# LMS equalizer from zero — simple notes and matrix method

## 1. What is the problem?

A transmitted symbol $s[n]$ enters a channel. If the channel delays some energy, the sample received at time $n$ also contains parts of previous symbols. That is **ISI** (inter-symbol interference). A linear equalizer learns weights that reduce this distortion.

For the `mild` channel:

$$r[n]=0.90s[n]+0.65s[n-1]-0.35s[n-2]+v[n].$$

Here $v[n]$ is AWGN noise. The channel is a linear system with impulse response $h=[0.90,0.65,-0.35]$.

## 2. Input as a column vector

For **3 taps** (just to see the matrix easily):

$$\mathbf{x}[n]=\begin{bmatrix}r[n]\\r[n-1]\\r[n-2]\end{bmatrix},\qquad
\mathbf{w}[n]=\begin{bmatrix}w_0[n]\\w_1[n]\\w_2[n]\end{bmatrix}.$$

Output $y[n]=\mathbf{w}^H[n]\mathbf{x}[n]$. Superscript $H$ means **transpose and complex conjugate**. For a real signal, it is simply transpose.

The reference symbol is $d[n]=s[n-D]$ where $D$ is the desired decision delay. The instantaneous error is:

$$e[n]=d[n]-y[n].$$

## 3. Relation to Wiener filter

Wiener filtering minimizes the expected squared error:

$$J(\mathbf{w})=E[|d-\mathbf{w}^H\mathbf{x}|^2].$$

Define the autocorrelation matrix and cross-correlation vector:

$$\mathbf{R}=E[\mathbf{x}\mathbf{x}^H],\qquad \mathbf{p}=E[\mathbf{x}d^*].$$

Then the optimal constant weights satisfy the matrix equation:

$$\boxed{\mathbf{R}\mathbf{w}_{\rm opt}=\mathbf{p}}.$$

**Connection:** LMS tries to approach the Wiener solution **without explicitly forming and inverting $\mathbf R$**.

## 4. Derive the update (important for exam/viva)

Expanding the objective:

$$J=E[|d|^2]-\mathbf{w}^H\mathbf p-\mathbf p^H\mathbf w+\mathbf w^H\mathbf R\mathbf w.$$

Complex gradient:

$$\frac{\partial J}{\partial \mathbf{w}^*}=\mathbf R\mathbf w-\mathbf p.$$

Instantaneous gradient estimate:

$$\mathbf R\mathbf w-\mathbf p\;\approx\;-\mathbf x[n]e^*[n].$$

Gradient descent with step size $\mu$:

$$\boxed{\mathbf w[n+1]=\mathbf w[n]+\mu\mathbf x[n]e^*[n].}$$

For **BPSK** all vectors are usually real, so $e^*=e$. For **QPSK**, complex conjugation is essential.

## 5. 3-tap LMS update written component-wise

With $\mathbf{x}[n]=[r[n],r[n-1],r[n-2]]^T$:

$$\begin{bmatrix}w_0[n+1]\\w_1[n+1]\\w_2[n+1]\end{bmatrix}
=\begin{bmatrix}w_0[n]\\w_1[n]\\w_2[n]\end{bmatrix}
+\mu e^*[n]\begin{bmatrix}r[n]\\r[n-1]\\r[n-2]\end{bmatrix}.$$

This is the exact idea used by the 9-tap code.

## 6. Why step size matters

Small $\mu$: tends to give smaller fluctuations but slower learning. Large $\mu$: often faster early response, but excessive fluctuations or instability. The common idealized mean-convergence guideline is $0<\mu<2/\lambda_{\max}(\mathbf R)$. It is **not** a guaranteed safe range for every real finite data set.

## 7. Why train then freeze?

- Training: desired $d[n]$ is known, so calculate $e[n]$ and update $\mathbf w$.
- Test: receiver does *not* know the transmitted test symbols. It must use the learned weights **without updates from true test labels**.
- Afterwards only, calculate BER/EVM using the saved reference test bits.

## 8. Performance terms

- **MSE:** average $|e[n]|^2$; training graph should generally decrease and then settle.
- **BER:** wrong bits / tested bits; lower is better.
- **RMS EVM:** normalized size of symbol errors in the I/Q plane; lower is better.
- **Tap length:** number of equalizer weights; too short leaves ISI, too many may increase complexity and noise enhancement.

## 9. Assumptions you should disclose

The model presumes one sample per symbol, correct timing and phase, known preamble, AWGN, and a fixed channel. It is **not** a complete wireless modem. A true eye diagram usually needs oversampled pulse-shaped data; none is claimed from symbol-spaced samples.
