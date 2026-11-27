import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".claude/integrations/timetracking/sync-clockify.sh"
)
INTERVAL_HELPER = Path(__file__).resolve().parents[1] / "scripts/time-entry-interval.py"


class ClockifySyncTests(unittest.TestCase):
    def run_sync(self, status, body, *flags, start="2026-01-14T14:00:00Z", end="2026-01-14T15:00:00Z"):
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            script_dir = sandbox / ".claude/integrations/timetracking"
            script_dir.mkdir(parents=True)
            script = shutil.copyfile(SCRIPT, script_dir / SCRIPT.name)
            helper_dir = sandbox / "scripts"
            helper_dir.mkdir()
            shutil.copyfile(INTERVAL_HELPER, helper_dir / INTERVAL_HELPER.name)
            curl = sandbox / "curl"
            curl.write_text(
                '#!/bin/sh\nprintf "%s\\n%s\\n" "$MOCK_BODY" "$MOCK_STATUS"\n'
            )
            curl.chmod(0o755)
            env = {
                **os.environ,
                "PATH": f"{sandbox}{os.pathsep}{os.environ['PATH']}",
                "CLOCKIFY_API_TOKEN": "synthetic",
                "CLOCKIFY_WORKSPACE_ID": "synthetic",
                "CLOCKIFY_PROJECT_ID": "",
                "MOCK_STATUS": str(status),
                "MOCK_BODY": body,
            }
            return subprocess.run(
                [
                    "bash", script,
                    "--description", "Synthetic example",
                    "--start", start,
                    "--end", end,
                    *flags,
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_created_entry_returns_success(self):
        result = self.run_sync(201, '{"id":"synthetic-entry"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("synthetic-entry", result.stdout)

    def test_http_error_returns_failure(self):
        result = self.run_sync(500, '{"message":"synthetic failure"}')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("ERRO 500", result.stderr)

    def test_dry_run_returns_success_even_when_mock_provider_would_fail(self):
        result = self.run_sync(500, '{"message":"synthetic failure"}', "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertNotIn("ERRO 500", result.stderr)

    def test_dry_run_normalizes_z_and_explicit_offsets_to_utc(self):
        result = self.run_sync(
            500, '{"message":"synthetic failure"}', "--dry-run",
            start="2026-01-14T14:00:00-03:00", end="2026-01-14T15:00:00-03:00",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"start": "2026-01-14T17:00:00Z"', result.stdout)
        self.assertIn('"end": "2026-01-14T18:00:00Z"', result.stdout)

    def test_invalid_or_reversed_interval_fails_before_curl(self):
        for start, end in (
            ("2026-01-14T14:00:00", "2026-01-14T15:00:00Z"),
            ("2026-01-14T15:00:00Z", "2026-01-14T14:00:00Z"),
        ):
            with self.subTest(start=start, end=end):
                result = self.run_sync(
                    201, '{"id":"should-not-be-returned"}',
                    start=start, end=end,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("should-not-be-returned", result.stdout)
