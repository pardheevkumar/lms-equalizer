"""Small automated checks for modulation, channel, and LMS behavior."""

import unittest
import numpy as np

from lms_equalizer.channel import apply_multipath_channel
from lms_equalizer.equalizer import LMSLinearEqualizer
from lms_equalizer.modulation import demodulate_symbols, modulate_bits
from lms_equalizer.simulation import run_simulation


class ModulationTests(unittest.TestCase):
    def test_modulate_then_demodulate_recovers_bits(self):
        rng = np.random.default_rng(22)
        for modulation, width in [("bpsk", 1), ("qpsk", 2), ("16qam", 4)]:
            bits = rng.integers(0, 2, 400 * width, dtype=np.int8)
            received_symbols = modulate_bits(bits, modulation)
            recovered_bits = demodulate_symbols(received_symbols, modulation)
            np.testing.assert_array_equal(recovered_bits, bits)

    def test_invalid_bit_length_is_rejected(self):
        with self.assertRaises(ValueError):
            modulate_bits(np.array([1, 0, 1]), "qpsk")


class ChannelTests(unittest.TestCase):
    def test_noiseless_identity_channel(self):
        symbols = np.array([1, -1, 1j, -1j], dtype=np.complex128)
        received, clean = apply_multipath_channel(
            symbols, channel_taps=[1.0], snr_db=None
        )
        np.testing.assert_allclose(received, symbols)
        np.testing.assert_allclose(clean, symbols)


class EqualizerTests(unittest.TestCase):
    def test_identity_channel_lms_learns_delayed_symbol(self):
        rng = np.random.default_rng(9)
        bits = rng.integers(0, 2, 5000, dtype=np.int8)
        symbols = modulate_bits(bits, "bpsk")
        received, _ = apply_multipath_channel(symbols, [1.0], None, rng)

        equalizer = LMSLinearEqualizer(num_taps=5, step_size=0.03, decision_delay=2)
        equalizer.train(received, symbols, training_end=3500)
        output, sample_indices = equalizer.equalize(received, start_sample=3500 + 2)
        target = symbols[sample_indices - equalizer.decision_delay]
        self.assertLess(np.mean(np.abs(output - target) ** 2), 0.03)

    def test_lms_reduces_ber_on_default_multipath_example(self):
        result = run_simulation(
            modulation="qpsk",
            snr_db=20,
            num_symbols=10000,
            num_taps=9,
            step_size=0.01,
            train_fraction=0.60,
            seed=31,
        )
        self.assertLess(result.ber_after, result.ber_before)

    def test_all_modulations_run_with_finite_metrics(self):
        cases = [("bpsk", 15.0, 0.008), ("qpsk", 20.0, 0.01), ("16qam", 25.0, 0.003)]
        for modulation, snr_db, step_size in cases:
            with self.subTest(modulation=modulation):
                result = run_simulation(
                    modulation=modulation,
                    snr_db=snr_db,
                    num_symbols=2500,
                    num_taps=7,
                    step_size=step_size,
                    train_fraction=0.60,
                    seed=51,
                )
                self.assertTrue(np.isfinite(result.ber_before))
                self.assertTrue(np.isfinite(result.ber_after))
                self.assertTrue(np.isfinite(result.evm_before))
                self.assertTrue(np.isfinite(result.evm_after))
                self.assertGreater(result.target_indices.size, 0)

    def test_decision_directed_mode_runs(self):
        result = run_simulation(
            modulation="qpsk",
            snr_db=12,
            num_symbols=2500,
            num_taps=7,
            step_size=0.005,
            train_fraction=0.60,
            decision_directed=True,
            seed=19,
        )
        self.assertTrue(np.isfinite(result.ber_after))
        self.assertTrue(np.isfinite(result.evm_after))

    def test_bad_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            LMSLinearEqualizer(num_taps=0)
        with self.assertRaises(ValueError):
            LMSLinearEqualizer(num_taps=5, step_size=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
