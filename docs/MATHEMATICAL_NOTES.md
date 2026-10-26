# LMS Equalizer: Mathematical Notes and Viva Guide

Use this note to understand the implementation. Rephrase the concepts in your own words before using them in your report or presentation.

## 1. Why do we need an equalizer?

A transmitted symbol sequence is denoted by \(a[n]\). A multipath channel may deliver a delayed and attenuated copy of a symbol together with copies of earlier symbols. A simple discrete-time channel model is

\[
r[n] = \sum_{k=0}^{L-1} h[k]a[n-k] + v[n],
\]

where \(h[k]\) are the channel taps, \(L\) is the channel length, and \(v[n]\) is additive noise. The terms involving \(a[n-1], a[n-2],\ldots\) interfere with the current symbol; this is intersymbol interference (ISI).

The simulator uses a causal channel implemented by convolving the transmitted sequence with `channel_taps`, then adds complex AWGN whose power is selected from the requested SNR.

## 2. Linear equalizer model

An equalizer with \(M\) taps uses the current and previous received samples:

\[
\mathbf{x}[n]=[r[n],r[n-1],\ldots,r[n-M+1]]^T.
\]

Its output is

\[
y[n]=\mathbf{w}^H[n]\mathbf{x}[n],
\]

where \(\mathbf{w}[n]\) is the complex tap-weight vector and \(H\) denotes conjugate transpose. The `np.vdot(weights, input_vector)` expression in the code implements this convention.

A decision delay \(D\) aligns the equalizer output with the target symbol:

\[
d[n]=a[n-D].
\]

The center tap is a convenient default delay, but it is a design choice rather than a universal optimum. Different channels can need different delays.

## 3. Error and the LMS update

During training, the receiver knows the transmitted target symbol. It forms the error

\[
e[n]=d[n]-y[n].
\]

The mean-square error objective is

\[
J=E\{|e[n]|^2\}.
\]

Computing the exact expectation would require knowledge of signal statistics. LMS instead uses the current error as a noisy estimate of the gradient and updates the weights sample by sample:

\[
\boxed{\mathbf{w}[n+1]=\mathbf{w}[n]+\mu\mathbf{x}[n]e^*[n]}
\]

for the complex convention used in this project. Here \(\mu>0\) is the step size and \(*\) is complex conjugation. Notice the order in the code: calculate output, calculate error, then update the weights. The output being scored is the output before that sample's update.

## 4. Why does the step size matter?

- A larger \(\mu\) makes larger changes at each update and may converge quickly, but can lead to overshoot, steady oscillation, or divergence.
- A smaller \(\mu\) makes smaller changes and is usually gentler, but it may need more training symbols.
- Stability depends on the input-signal statistics and tap count. A commonly quoted approximate mean-convergence condition is \(0<\mu<2/\lambda_{\max}(R_x)\), where \(R_x=E\{\mathbf{x}\mathbf{x}^H\}\). It is not a universal step-size guarantee for every finite simulation.

The best practice is to compare several values of `--mu`, plot the learning curve, and report the observed trade-off.

## 5. Training and decision-directed modes

**Training-based mode:** the transmitted reference symbols are known. This usually gives reliable adaptation while the training sequence lasts. This project adapts only using received sample indices before `training_end` and evaluates target symbols at or after the training boundary.

**Decision-directed mode:** after training, the equalizer slices its own output to the nearest constellation point and treats that detected point as the target. This is useful when the transmitter's data is unknown and the receiver should continue tracking slow changes. If decisions are wrong, the equalizer can reinforce the errors, so decision-directed adaptation is optional in the runner.

## 6. Performance measures

Bit error rate is

\[
\mathrm{BER}=\frac{\text{incorrect detected bits}}{\text{total measured bits}}.
\]

Normalized RMS error-vector magnitude is

\[
\mathrm{EVM}=\sqrt{\frac{E\{|\hat a[n]-a[n]|^2\}}{E\{|a[n]|^2\}}}.
\]

For both metrics, lower is better. BER measures bit decisions, while EVM also reflects the size of symbol errors before hard decisions.

## 7. Questions to practise for the viva

1. What physical effect does the multipath FIR channel model represent?
2. Why is the equalizer an FIR filter, and what does each tap contribute?
3. Why do we need a decision delay? Where is it set in the code?
4. Derive or explain each part of the LMS update.
5. What is the difference between BER and EVM?
6. Why can increasing `mu` make performance worse?
7. What is the difference between training-based and decision-directed adaptation?
8. Which experiments did you run to show the implementation behaves as expected?
9. What limitations remain in this symbol-spaced simulation?
