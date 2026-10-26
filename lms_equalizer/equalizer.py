"""A readable complex-valued LMS linear equalizer."""

from __future__ import annotations

import numpy as np


class LMSLinearEqualizer:
    """Train and run a tap-delay-line LMS equalizer.

    The filter uses the convention

        y[n] = w[n]^H x[n]
        e[n] = d[n] - y[n]
        w[n+1] = w[n] + mu * x[n] * conjugate(e[n])

    where x[n] = [r[n], r[n-1], ..., r[n-M+1]]. The decision delay tells
    the receiver which transmitted symbol y[n] should reproduce: d[n] = s[n-D].
    """

    def __init__(
        self,
        num_taps: int = 9,
        step_size: float = 0.01,
        decision_delay: int | None = None,
    ) -> None:
        # Explicit defaults make the parameters easy to change in a lab session.
        if not isinstance(num_taps, int) or num_taps < 1:
            raise ValueError("num_taps must be a positive integer")
        if not np.isfinite(step_size) or step_size <= 0:
            raise ValueError("step_size must be a positive finite number")

        if decision_delay is None:
            decision_delay = (num_taps - 1) // 2
        if not isinstance(decision_delay, int) or decision_delay < 0:
            raise ValueError("decision_delay must be a non-negative integer")
        if decision_delay >= num_taps:
            raise ValueError("decision_delay should be smaller than num_taps")

        self.num_taps = num_taps
        self.step_size = float(step_size)
        self.decision_delay = decision_delay
        self.weights = np.zeros(num_taps, dtype=np.complex128)
        self.training_mse: list[float] = []

    def reset(self) -> None:
        """Reset all filter weights and clear the learning history."""
        self.weights[:] = 0.0
        self.training_mse = []

    def _input_vector(self, received: np.ndarray, sample_index: int) -> np.ndarray:
        """Return the newest sample first, followed by its previous samples."""
        return received[sample_index - np.arange(self.num_taps)]

    def _first_valid_sample(self) -> int:
        """First index with enough received samples and a valid target symbol."""
        return max(self.num_taps - 1, self.decision_delay)

    def train(
        self,
        received: np.ndarray,
        transmitted_symbols: np.ndarray,
        training_end: int,
        reset_weights: bool = True,
    ) -> np.ndarray:
        """Adapt weights using known transmitted symbols (supervised training).

        ``training_end`` is an exclusive sample index. Only received samples
        before that boundary update the equalizer. The returned array contains
        squared errors observed during training, one value per update.
        """
        received = np.asarray(received, dtype=np.complex128)
        transmitted_symbols = np.asarray(transmitted_symbols, dtype=np.complex128)
        if received.ndim != 1 or transmitted_symbols.ndim != 1:
            raise ValueError("received and transmitted_symbols must be one-dimensional")
        if len(received) != len(transmitted_symbols):
            raise ValueError("received and transmitted_symbols must have equal length")
        if not isinstance(training_end, int) or not 0 <= training_end <= len(received):
            raise ValueError("training_end must be an index within the received packet")

        if reset_weights:
            self.reset()

        squared_errors: list[float] = []
        first_sample = self._first_valid_sample()

        # For every training sample, predict the matching delayed symbol,
        # measure the error, then make a small correction to each filter tap.
        for n in range(first_sample, training_end):
            target_index = n - self.decision_delay
            desired = transmitted_symbols[target_index]
            input_vector = self._input_vector(received, n)
            estimate = np.vdot(self.weights, input_vector)
            error = desired - estimate

            self.weights += self.step_size * input_vector * np.conj(error)
            squared_errors.append(float(np.abs(error) ** 2))

            if not np.all(np.isfinite(self.weights)):
                raise FloatingPointError(
                    "LMS weights became non-finite. Try a smaller --mu value."
                )

        self.training_mse = squared_errors
        return np.asarray(squared_errors, dtype=float)

    def equalize(
        self,
        received: np.ndarray,
        start_sample: int | None = None,
        stop_sample: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Run the current weights without updating them.

        Returns output symbols plus the received-sample indices used to create
        each output. The matching transmitted symbol index is ``index - delay``.
        """
        received = np.asarray(received, dtype=np.complex128)
        if received.ndim != 1:
            raise ValueError("received must be a one-dimensional array")

        if start_sample is None:
            start_sample = self._first_valid_sample()
        else:
            start_sample = max(start_sample, self._first_valid_sample())
        if stop_sample is None:
            stop_sample = len(received)
        if not 0 <= start_sample <= stop_sample <= len(received):
            raise ValueError("sample range must satisfy 0 <= start <= stop <= packet length")

        sample_indices = np.arange(start_sample, stop_sample, dtype=int)
        outputs = np.empty(sample_indices.size, dtype=np.complex128)
        for output_index, n in enumerate(sample_indices):
            outputs[output_index] = np.vdot(
                self.weights, self._input_vector(received, int(n))
            )
        return outputs, sample_indices

    def decision_directed_adapt(
        self,
        received: np.ndarray,
        constellation: np.ndarray,
        start_sample: int,
        stop_sample: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Continue LMS updates without known bits, using detected symbols.

        This is optional. It can track a slowly changing channel after the
        training preamble, but wrong decisions can also make it diverge.
        Outputs are recorded before each corresponding weight update.
        """
        received = np.asarray(received, dtype=np.complex128)
        constellation = np.asarray(constellation, dtype=np.complex128)
        if received.ndim != 1 or constellation.ndim != 1 or constellation.size == 0:
            raise ValueError("received and constellation must be non-empty one-dimensional data")
        if stop_sample is None:
            stop_sample = len(received)
        start_sample = max(start_sample, self._first_valid_sample())
        if not 0 <= start_sample <= stop_sample <= len(received):
            raise ValueError("sample range must satisfy 0 <= start <= stop <= packet length")

        sample_indices = np.arange(start_sample, stop_sample, dtype=int)
        outputs = np.empty(sample_indices.size, dtype=np.complex128)
        for output_index, n in enumerate(sample_indices):
            input_vector = self._input_vector(received, int(n))
            estimate = np.vdot(self.weights, input_vector)
            outputs[output_index] = estimate
            target = constellation[np.argmin(np.abs(constellation - estimate) ** 2)]
            error = target - estimate
            self.weights += self.step_size * input_vector * np.conj(error)

            if not np.all(np.isfinite(self.weights)):
                raise FloatingPointError(
                    "LMS weights became non-finite during decision-directed adaptation. "
                    "Try a smaller --mu value."
                )
        return outputs, sample_indices
