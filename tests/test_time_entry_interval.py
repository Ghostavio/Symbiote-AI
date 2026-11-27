import json
from pathlib import Path
import subprocess
import sys
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts/time-entry-interval.py"


class TimeEntryIntervalTests(unittest.TestCase):
    def run_interval(self, start, end):
        return subprocess.run(
            [sys.executable, str(HELPER), start, end],
            capture_output=True, text=True, timeout=10,
        )

    def test_explicit_offsets_are_normalized_to_utc(self):
        result = self.run_interval("2026-01-14T14:00:00-03:00", "2026-01-14T15:00:00-03:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "duration_seconds": 3600,
            "start_utc": "2026-01-14T17:00:00Z",
            "end_utc": "2026-01-14T18:00:00Z",
        })

    def test_dst_offset_change_uses_elapsed_time(self):
        result = self.run_interval("2026-11-01T01:30:00-04:00", "2026-11-01T01:30:00-05:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["duration_seconds"], 3600)

    def test_rejects_naive_timestamp(self):
        result = self.run_interval("2026-01-14T14:00:00", "2026-01-14T15:00:00Z")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("timestamp inválido", result.stderr)

    def test_rejects_offset_beyond_fourteen_hours(self):
        result = self.run_interval("2026-01-14T14:00:00+14:30", "2026-01-14T15:00:00Z")
        self.assertNotEqual(result.returncode, 0)

    def test_rejects_equal_instants_with_different_zone_notations(self):
        result = self.run_interval("2026-01-14T14:00:00-03:00", "2026-01-14T17:00:00Z")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("instante posterior", result.stderr)

    def test_rejects_negative_duration(self):
        result = self.run_interval("2026-01-14T15:00:00Z", "2026-01-14T14:00:00Z")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("instante posterior", result.stderr)


if __name__ == "__main__":
    unittest.main()
