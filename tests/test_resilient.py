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
