import unittest
import numpy as np
from lms_equalizer import (CHANNELS, add_awgn, demodulate,
                           lms_equalizer, modulate, simulate)


class TestModem(unittest.TestCase):
    def test_roundtrip(self):
        rng = np.random.default_rng(3)
        for scheme in ("BPSK", "QPSK"):
            bits = rng.integers(0, 2, size=2000)
            np.testing.assert_array_equal(demodulate(modulate(bits, scheme), scheme), bits)

    def test_unit_average_power(self):
        for scheme in ("BPSK", "QPSK"):
            symbols = modulate(np.array([0, 0, 0, 1, 1, 0, 1, 1]), scheme)
            self.assertAlmostEqual(np.mean(np.abs(symbols)**2), 1.0)

    def test_no_awgn_infinite_snr(self):
        x = np.array([1.0, -1.0, 1.0])
        y = add_awgn(x, float("inf"), np.random.default_rng(0))
        np.testing.assert_array_equal(x, y)


class TestLMS(unittest.TestCase):
    def test_complex_gradient_one_step(self):
        # y=w^H x, w_new=w+mu*x*conj(error), after the first valid tap window.
        x = np.array([1+1j, 2-1j])
        d = np.array([0j, 1+2j])
        out = lms_equalizer(x, d, mu=0.1, num_taps=2, train_stop=2)
        expected = 0.1*np.array([2-1j, 1+1j])*(1-2j)
        np.testing.assert_allclose(out.weights, expected)

    def test_frozen_weights_independent_of_test_targets(self):
        x = np.random.default_rng(0).standard_normal(200)
        d = np.roll(x, 1)
        d2 = d.copy()
        d2[120:] = 1e3
        a = lms_equalizer(x, d, mu=0.01, num_taps=5, train_stop=120)
        b = lms_equalizer(x, d2, mu=0.01, num_taps=5, train_stop=120)
        np.testing.assert_allclose(a.output, b.output)
        np.testing.assert_allclose(a.weights, b.weights)

    def test_noiseless_identity_channel(self):
        ex = simulate("BPSK", snr_db=100, channel="flat", delay=0,
                      mu=0.025, num_taps=5, n_train=1500, n_test=1000)
        self.assertLess(ex.equalized_evm, 0.01)
        self.assertEqual(ex.equalized_ber, 0)

    def test_heldout_metrics_and_complex_support(self):
        ex = simulate("QPSK", snr_db=12, seed=9)
        self.assertEqual(ex.test_indices.size, 9000)
        self.assertTrue(np.iscomplexobj(ex.lms.weights))
        self.assertTrue(np.isfinite(ex.equalized_evm))
        self.assertTrue(0 <= ex.equalized_ber <= 1)

    def test_bpsk_and_qpsk_improvement(self):
        for scheme in ("BPSK", "QPSK"):
            ex = simulate(scheme, snr_db=12, seed=5)
            self.assertLess(ex.equalized_evm, ex.raw_evm)
            self.assertLess(ex.equalized_ber, ex.raw_ber)


if __name__ == "__main__":
    unittest.main()
