import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = Path(".claude/integrations/timetracking")


class SyncWrapperTests(unittest.TestCase):
    def run_wrapper(self, *flags, clockify_status="201", clockify_token="synthetic"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in (
                INTEGRATION / "sync.sh",
                INTEGRATION / "sync-clockify.sh",
                Path("scripts/sync-7pace.sh"),
                Path("scripts/time-entry-interval.py"),
            ):
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / path, root / path)
            curl = root / "curl"
            curl.write_text(
                """#!/bin/bash
while [[ $# -gt 1 ]]; do
  if [[ "$1" == "-d" ]]; then body="$2"; shift; fi
  shift
done
printf '%s\\n' "$body" >> "$REQUESTS"
case "$1" in
  https://api.clockify.me/*) printf '{"id":"clockify"}\\n%s\\n' "$CLOCKIFY_STATUS" ;;
  https://synthetic.invalid/*) printf '{"data":{"id":"7pace"}}\\n201\\n' ;;
  *) exit 99 ;;
esac
""",
                encoding="utf-8",
            )
            curl.chmod(0o755)
            requests = root / "requests.jsonl"
            result = subprocess.run(
                [
                    "/bin/bash", root / INTEGRATION / "sync.sh",
                    "--description", "Sessão original",
                    "--work-item-id", "42",
                    "--start", "2026-01-14T14:00:00-03:00",
                    "--end", "2026-01-14T15:00:00-03:00",
                    *flags,
                ],
                env={
                    "PATH": f"{root}{os.pathsep}{os.environ['PATH']}",
                    "REQUESTS": str(requests),
                    "CLOCKIFY_STATUS": clockify_status,
                    "CLOCKIFY_API_TOKEN": clockify_token,
                    "CLOCKIFY_WORKSPACE_ID": "synthetic",
                    "SEVENPACE_API_TOKEN": "synthetic",
                    "SEVENPACE_BASE_URL": "https://synthetic.invalid",
                },
                capture_output=True,
                text=True,
                timeout=10,
            )
            payloads = (
                [json.loads(line) for line in requests.read_text().splitlines()]
                if requests.exists() else []
            )
            return result, payloads

    def test_retry_only_clockify_reuses_the_original_payload(self):
        failed, original = self.run_wrapper(clockify_status="500")
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(len(original), 2)
        self.assertEqual(original[0]["workItemId"], 42)
        self.assertEqual(original[1]["description"], "42: Sessão original")

        retried, payloads = self.run_wrapper("--provider", "clockify")
        self.assertEqual(retried.returncode, 0, retried.stderr)
        self.assertEqual(payloads, [original[1]])

    def test_7pace_selection_skips_clockify(self):
        result, payloads = self.run_wrapper("--provider", "7pace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]["workItemId"], 42)

    def test_clockify_dry_run_accepts_missing_credentials(self):
        result, payloads = self.run_wrapper(
            "--provider", "clockify", "--dry-run", "--description", "Daily",
            clockify_token="",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payloads, [])
        self.assertIn('"description": "Daily"', result.stdout)

    def test_clockify_retry_fails_when_credentials_are_missing(self):
        result, payloads = self.run_wrapper("--provider", "clockify", clockify_token="")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payloads, [])
        self.assertIn("CLOCKIFY_API_TOKEN", result.stderr)
