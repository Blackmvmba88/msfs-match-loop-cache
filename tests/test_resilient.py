import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import json

spec = importlib.util.spec_from_file_location('launcher', Path(__file__).resolve().parents[1] / 'scripts/launch_resilient.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RecoveryTests(unittest.TestCase):
    def test_timeout_after_open_does_not_trigger_second_launch(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'browser_state', return_value='closed'), patch.object(m.subprocess, 'run', side_effect=subprocess.TimeoutExpired('open', 20)) as run:
            self.assertEqual(m.launch(Path(tmp)), 'requested-launch-timeout')
            self.assertEqual(run.call_count, 1)

    def test_process_check_failure_after_open_does_not_trigger_fallback(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'browser_state', return_value='closed'), patch.object(m.subprocess, 'run', side_effect=[subprocess.CompletedProcess([], 0), PermissionError]) as run:
            self.assertEqual(m.launch(Path(tmp)), 'requested-process-check-unavailable')
            self.assertEqual(run.call_count, 2)

    def test_existing_adata_session_never_opens_another_window(self):
        root = Path('/Volumes/ADATA SC740/ChromeGameCache')
        result = subprocess.CompletedProcess([], 0, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --user-data-dir=' + str(root / 'profile') + ' --no-first-run\n')
        with patch.object(m.subprocess, 'run', return_value=result) as run:
            self.assertEqual(m.launch(root), 'existing-profile-active')
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[0][0], 'ps')

    def test_normal_chrome_is_preserved_instead_of_spawning_profile(self):
        result = subprocess.CompletedProcess([], 0, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --flag-switches-begin\n')
        with patch.object(m.subprocess, 'run', return_value=result) as run:
            self.assertEqual(m.launch(Path('/unused')), 'existing-browser-review-needed')
        self.assertEqual(run.call_count, 1)

    def test_unavailable_inspection_does_not_open_or_fallback(self):
        with patch.object(m.subprocess, 'run', side_effect=PermissionError):
            self.assertEqual(m.launch(Path('/unused')), 'inspection-unavailable-no-launch')

    def test_command_text_mentioning_chrome_is_not_a_browser(self):
        result = subprocess.CompletedProcess([], 0, 'python -c print("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --user-data-dir=/unused/profile")\n')
        with patch.object(m.subprocess, 'run', return_value=result):
            self.assertEqual(m.browser_state(Path('/unused/profile')), 'closed')

    def test_missing_usb_uses_mac(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.Path, 'home', return_value=Path(tmp)), patch.dict(m.os.environ, {'USB_VOLUME': tmp + '/missing'}), patch('sys.argv', ['launcher']), patch.object(m, 'launch', return_value='process-observed') as launch:
            self.assertEqual(m.main(), 0)
            self.assertIn('BlackMambaFlightKit/browser', str(launch.call_args.args[0]))

    def test_usb_failure_falls_back_and_keeps_both_attempts(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.Path, 'home', return_value=Path(tmp)), patch.dict(m.os.environ, {'USB_VOLUME': tmp}), patch('sys.argv', ['launcher']), patch.object(m, 'launch', side_effect=[subprocess.CalledProcessError(1, 'open'), 'process-observed']):
            self.assertEqual(m.main(), 0)
            result = json.loads((Path(tmp) / 'Library/Application Support/BlackMambaFlightKit/last-launch.json').read_text())
            self.assertEqual([a['state'] for a in result['attempts']], ['failed', 'process-observed'])
            self.assertFalse(result['gameVerified'])

    def test_uncertain_launch_does_not_start_duplicate_session(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.Path, 'home', return_value=Path(tmp)), patch.dict(m.os.environ, {'USB_VOLUME': tmp}), patch('sys.argv', ['launcher']), patch.object(m, 'launch', return_value='requested-process-not-observed') as launch:
            self.assertEqual(m.main(), 2)
            self.assertEqual(launch.call_count, 1)


if __name__ == '__main__':
    unittest.main()
