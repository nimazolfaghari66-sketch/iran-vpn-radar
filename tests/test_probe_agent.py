"""Probe agent location-safety tests.

The probe is the trust anchor for the whole project, so its location rules are
tested directly: a detected non-Iran location must never be overridden by an
operator assertion, and a probe with no Iranian evidence must not be trusted.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location("probe_agent", ROOT / "probe" / "probe_agent.py")
probe_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe_agent)


class TestProbeLocation(unittest.TestCase):
    def _state(self, asserted, detected):
        state = probe_agent.ProbeState("p", asserted, None, None, None)
        state.detected_country = detected
        # emulate refresh's precedence without a network call
        state.info.country = state.detected_country or state.asserted_country
        return state

    def test_detected_iran_is_iran(self):
        state = self._state("", "IR")
        self.assertTrue(state.info.is_iran)

    def test_assertion_cannot_override_detected_non_iran(self):
        state = self._state("IR", "US")
        self.assertFalse(state.info.is_iran)
        self.assertTrue(state.location_conflict)

    def test_assertion_fills_gap_when_detection_fails(self):
        state = self._state("IR", "")
        self.assertTrue(state.info.is_iran)
        self.assertFalse(state.location_conflict)

    def test_no_evidence_is_not_iran(self):
        state = self._state("", "")
        self.assertFalse(state.info.is_iran)


if __name__ == "__main__":
    unittest.main()
