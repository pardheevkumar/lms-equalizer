# LMS Equalizer — 25 likely viva questions (simple answers)

**1. What is LMS?**  Least Mean Squares is a simple adaptive-filter algorithm that changes FIR weights to reduce instantaneous squared error.

**2. What is an equalizer?**  A filter that compensates for distortion produced by a communication channel.

**3. What is ISI?**  Inter-symbol interference: nearby symbols affect the received sample at the current symbol time.

**4. What is the channel model?**  $r[n]=\sum h[k]s[n-k]+v[n]$. Here $v[n]$ is AWGN.

**5. Why do you use BPSK?**  It is real-valued and easiest to debug; one bit per symbol.

**6. Why add QPSK?**  QPSK uses complex I/Q samples and shows the correct complex LMS update; two bits per symbol.

**7. What are LMS inputs?**  A vector of current and delayed received symbols, $\mathbf{x}[n]$.

**8. What are weights?**  FIR tap coefficients $\mathbf w[n]$, learned through training.

**9. State the equalizer output.**  $y[n]=\mathbf w^H[n]\mathbf x[n]$.

**10. State the error.**  $e[n]=d[n]-y[n]$; the desired reference is $d[n]=s[n-D]$.

**11. State the LMS update.**  $\mathbf w[n+1]=\mathbf w[n]+\mu\mathbf x[n]e^*[n]$.

**12. Why the complex conjugate?**  Because the output is $\mathbf w^H\mathbf x$; correct complex gradient descent uses $e^*$.

**13. What is $\mu$?**  The learning rate / step size. It controls how fast and smoothly LMS adapts.

**14. What happens when $\mu$ is too large?**  Higher residual fluctuations and possibly divergence or instability.

**15. What happens when $\mu$ is very small?**  LMS may learn too slowly within the available training interval.

**16. What is Wiener–Hopf?**  The optimal stationary linear filter satisfies $\mathbf R\mathbf w=\mathbf p$.

**17. What are $\mathbf R$ and $\mathbf p$?**  $\mathbf R=E[\mathbf x\mathbf x^H]$, $\mathbf p=E[\mathbf x d^*]$.

**18. LMS vs Wiener filter?**  Wiener needs correlations/matrix solution; LMS approximates the gradient with each input sample.

**19. What is training?**  The receiver already knows reference symbols during a preamble, so it can calculate error and update coefficients.

**20. Why freeze the weights?**  The receiver does not know true test bits. Using those bits to update the filter would leak answers into evaluation.

**21. What is decision delay $D$?**  The desired recovery time offset. Here $D=2$ makes a causal FIR equalizer estimate earlier transmitted symbols.

**22. What is BER?**  Number of incorrect detected bits divided by total reference bits tested.

**23. What is EVM?**  RMS distance of detected complex symbol estimates from ideal symbols, normalized by reference-symbol power.

**24. Why is there an MSE floor?**  Noise and remaining ISI prevent the FIR filter from removing every error.

**25. Are these wireless measurement results?**  No. They are reproducible symbol-rate Python simulations assuming synchronized, phase-aligned BPSK/QPSK, fixed FIR channels and AWGN.

### Extra challenge: why can raw BER increase when SNR increases?

The selected ISI channel can produce a wrong raw sign even with zero noise: delayed symbols can outweigh the current one. At some intermediate SNR, random noise can accidentally reverse a subset of these wrong hard decisions; therefore an ISI-limited *unequalized* BER curve can be non-monotonic. The plot does **not** follow the usual AWGN-only $Q$-function curve.

### Extra challenge: why no eye diagram?

An eye diagram needs waveforms sampled multiple times per symbol (usually after pulse shaping). Our model has exactly one sample per symbol, so no eye diagram is claimed; waveform and QPSK constellation plots are correct for this scope.
