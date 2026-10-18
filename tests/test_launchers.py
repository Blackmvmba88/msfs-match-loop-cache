"""Offline regression checks; never opens Chrome or contacts Xbox."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / "scripts"
        shutil.copytree(ROOT / "scripts", self.scripts)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.volume = self.root / "USB with spaces"
        self.volume.mkdir()
        self.capture = self.root / "args"
        self.env = dict(os.environ, USB_VOLUME=str(self.volume),
                        PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        CAPTURE=str(self.capture))
        # Replace only the installation check in this isolated fixture.
        path = self.scripts / "launch_chrome_game_cache.sh"
        path.write_text(path.read_text().replace(
            '/Applications/Google Chrome.app', str(self.volume)))

    def mock(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/bash\n' + body)
        path.chmod(0o755)

    def run_script(self, name):
        return subprocess.run(["bash", str(self.scripts / name)],
                              env=self.env, capture_output=True, text=True)

    def test_dedicated_instance_and_argument_boundaries(self):
        self.mock("open", 'printf "%s\\n" "$@" > "$CAPTURE"\n')
        result = self.run_script("launch_chrome_game_cache.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.capture.read_text().splitlines()
        self.assertEqual(args[:3], ["-na", "Google Chrome", "--args"])
        self.assertIn("--user-data-dir=" + str(self.volume / "ChromeGameCache/profile"), args)
        self.assertNotIn("--disable-renderer-backgrounding", args)
        self.assertTrue((self.volume / "ChromeGameCache/.last-launch").exists())

    def test_failed_open_is_not_recorded_as_launch(self):
        self.mock("open", "exit 7\n")
        self.assertEqual(self.run_script("launch_chrome_game_cache.sh").returncode, 7)
        self.assertFalse((self.volume / "ChromeGameCache/.last-launch").exists())

    def test_http_errors_propagate_with_bounded_request(self):
        self.mock("curl", 'printf "%s\\n" "$@" > "$CAPTURE"\nexit 22\n')
        result = self.run_script("network_check.sh")
        self.assertEqual(result.returncode, 22)
        args = self.capture.read_text().splitlines()
        self.assertIn("--fail", args)
        self.assertIn("-sS", args)
        self.assertEqual(args[args.index("--connect-timeout") + 1], "10")
        self.assertEqual(args[args.index("--max-time") + 1], "30")


if __name__ == "__main__":
    unittest.main()
