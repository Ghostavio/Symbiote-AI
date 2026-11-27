import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync-7pace.sh"


class SevenPaceSyncTests(unittest.TestCase):
    def run_sync(self, *flags, legacy_env=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            script = shutil.copyfile(SCRIPT, scripts / SCRIPT.name)
            curl = scripts / "curl"
            curl.write_text('#!/bin/sh\nprintf "%s\\n" "curl chamado" >&2\nexit 99\n')
            curl.chmod(0o755)
            if legacy_env is not None:
                env_file = root / ".claude/integrations/timetracking/.env"
                env_file.parent.mkdir(parents=True)
                env_file.write_text(legacy_env)
            env = {
                name: value for name, value in os.environ.items()
                if not name.startswith("SEVENPACE_")
            }
            env["PATH"] = f"{scripts}{os.pathsep}{env['PATH']}"
            return subprocess.run(
                [
                    "/bin/bash", script,
                    "--description", "Exemplo de simulação",
                    "--start", "2026-01-14T14:00:00Z",
                    "--end", "2026-01-14T15:00:00Z",
                    "--work-item-id", "42",
                    *flags,
                ],
                env=env, capture_output=True, text=True, timeout=10,
            )

    def test_dry_run_ignores_legacy_credentials_and_never_calls_curl(self):
        result = self.run_sync(
            "--dry-run", "--activity-type", "Reunião", legacy_env="exit 98\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("curl chamado", result.stderr)
        payload, _ = json.JSONDecoder().raw_decode(
            result.stdout[result.stdout.index("{"):]
        )
        self.assertEqual(payload["workItemId"], 42)
        self.assertEqual(payload["length"], 3600)
        self.assertEqual(payload["activityTypeId"], "<7PACE_ACTIVITY_ID_REUNIAO>")

    def test_live_run_requires_token(self):
        result = self.run_sync()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("SEVENPACE_API_TOKEN não configurado", result.stderr)
        self.assertNotIn("curl chamado", result.stderr)
