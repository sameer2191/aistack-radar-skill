import subprocess
import unittest
from unittest.mock import patch

from aistack_radar.connectors.http import fetch_json, fetch_text


class HttpFallbackTests(unittest.TestCase):
    def test_fetch_json_falls_back_to_curl_when_urllib_fails(self):
        completed = subprocess.CompletedProcess(
            args=["curl"],
            returncode=0,
            stdout='{"ok": true}',
            stderr="",
        )
        with patch("aistack_radar.connectors.http.urllib.request.urlopen", side_effect=OSError("certificate verify failed")):
            with patch("aistack_radar.connectors.http.shutil.which", return_value="/usr/bin/curl"):
                with patch("aistack_radar.connectors.http.subprocess.run", return_value=completed) as run:
                    payload = fetch_json("https://example.test/data.json", timeout=2)

        self.assertEqual(payload, {"ok": True})
        command = run.call_args.args[0]
        self.assertIn("curl", command[0])
        self.assertIn("https://example.test/data.json", command)

    def test_fetch_text_reports_both_failures(self):
        completed = subprocess.CompletedProcess(
            args=["curl"],
            returncode=60,
            stdout="",
            stderr="SSL certificate problem",
        )
        with patch("aistack_radar.connectors.http.urllib.request.urlopen", side_effect=OSError("certificate verify failed")):
            with patch("aistack_radar.connectors.http.shutil.which", return_value="/usr/bin/curl"):
                with patch("aistack_radar.connectors.http.subprocess.run", return_value=completed):
                    with self.assertRaisesRegex(RuntimeError, "urllib failed"):
                        fetch_text("https://example.test/data.json", timeout=2)


if __name__ == "__main__":
    unittest.main()
