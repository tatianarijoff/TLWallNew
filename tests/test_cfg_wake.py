"""
Unit tests for the wake-related configuration reading in CfgIo.

Covers the functionality added for time-domain wake calculations:

* ``read_calc_flag()``  -- the CalcWake flag (impedance / wake / both),
  including the default (flag absent) and the invalid-value error.
* ``read_times()``      -- building a Times object from [time_info] or
  from a default (no section).
* ``read_wall_and_wake()`` -- the high-level entry point that builds a
  TlWall and/or a TLWallWake object according to the CalcWake flag.

The tests use the real ``.cfg`` files under ``tests/input/wake/`` for the
main scenarios and ``tempfile`` for the edge cases, mirroring the style
of ``test_cfg.py``.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.cfg_io import (
    CfgIo,
    ConfigurationError,
    CALC_IMPEDANCE,
    CALC_WAKE,
    CALC_BOTH,
)
from pytlwall.times import Times
from pytlwall.tlwall import TlWall
from pytlwall.tlwall_wake import TLWallWake


# Directory holding the real .cfg files used by these tests.
WAKE_INPUT_DIR = Path(__file__).parent / "input" / "wake"


class TestReadCalcFlag(unittest.TestCase):
    """Test the CalcWake flag reading."""

    def test_flag_wake(self):
        """A cfg with CalcWake = wake is read as 'wake'."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "wake_only.cfg"))
        self.assertEqual(cfg.read_calc_flag(), CALC_WAKE)

    def test_flag_both(self):
        """A cfg with CalcWake = both is read as 'both'."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "wake_both.cfg"))
        self.assertEqual(cfg.read_calc_flag(), CALC_BOTH)

    def test_flag_absent_defaults_to_impedance(self):
        """When the CalcWake option is absent, the default is 'impedance'."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "impedance_default.cfg"))
        self.assertEqual(cfg.read_calc_flag(), CALC_IMPEDANCE)

    def test_flag_case_insensitive(self):
        """The flag value is read case-insensitively."""
        config_text = """
[base_info]
component_name = test

[calc_info]
CalcWake = WAKE
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        try:
            cfg = CfgIo(temp_file)
            self.assertEqual(cfg.read_calc_flag(), CALC_WAKE)
        finally:
            os.unlink(temp_file)

    def test_flag_invalid_raises(self):
        """An unrecognised CalcWake value raises ConfigurationError."""
        config_text = """
[base_info]
component_name = test

[calc_info]
CalcWake = nonsense
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        try:
            cfg = CfgIo(temp_file)
            with self.assertRaises(ConfigurationError):
                cfg.read_calc_flag()
        finally:
            os.unlink(temp_file)


class TestReadTimes(unittest.TestCase):
    """Test the read_times method."""

    def test_read_times_from_time_info(self):
        """read_times builds a Times object from a [time_info] section."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "wake_only.cfg"))
        times = cfg.read_times()

        self.assertIsInstance(times, Times)
        self.assertEqual(times.tmin_exp, -11)
        self.assertEqual(times.tmax_exp, -3)
        self.assertEqual(times.n_points, 801)
        self.assertEqual(len(times), 801)

    def test_read_times_default(self):
        """read_times returns a default Times object when no section is present."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "impedance_default.cfg"))
        times = cfg.read_times()

        self.assertIsInstance(times, Times)
        self.assertGreater(len(times), 0)


class TestReadWallAndWake(unittest.TestCase):
    """Test the high-level read_wall_and_wake method."""

    def test_impedance_only(self):
        """With no flag, only a TlWall is built (impedance scenario)."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "impedance_default.cfg"))
        result = cfg.read_wall_and_wake()

        self.assertEqual(result['calc_flag'], CALC_IMPEDANCE)
        self.assertIsInstance(result['wall'], TlWall)
        self.assertIsNone(result['wake'])

    def test_wake_only(self):
        """With CalcWake = wake, only a TLWallWake is built."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "wake_only.cfg"))
        result = cfg.read_wall_and_wake()

        self.assertEqual(result['calc_flag'], CALC_WAKE)
        self.assertIsNone(result['wall'])
        self.assertIsInstance(result['wake'], TLWallWake)

    def test_both(self):
        """With CalcWake = both, both a TlWall and a TLWallWake are built."""
        cfg = CfgIo(str(WAKE_INPUT_DIR / "wake_both.cfg"))
        result = cfg.read_wall_and_wake()

        self.assertEqual(result['calc_flag'], CALC_BOTH)
        self.assertIsInstance(result['wall'], TlWall)
        self.assertIsInstance(result['wake'], TLWallWake)


if __name__ == '__main__':
    unittest.main(verbosity=2)
