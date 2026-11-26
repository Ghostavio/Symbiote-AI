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


class ClockifySyncTests(unittest.TestCase):
    def run_sync(self, status, body, *flags):
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            script = shutil.copyfile(SCRIPT, sandbox / SCRIPT.name)
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
                    "--start", "2026-01-14T14:00:00Z",
                    "--end", "2026-01-14T15:00:00Z",
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
