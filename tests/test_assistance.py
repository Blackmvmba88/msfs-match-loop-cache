import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import launch_resilient as m

class AssistanceTests(unittest.TestCase):
    def test_switch_persists_without_opening_browser(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.Path, 'home', return_value=Path(tmp)), patch.object(m, 'launch') as launch:
            local = Path(tmp) / 'Library/Application Support/BlackMambaFlightKit'
            for mode, expected in [('off', False), ('on', True)]:
                with patch('sys.argv', ['launcher', '--assistance', mode]):
                    self.assertEqual(m.main(), 0)
                self.assertEqual(m.load_settings(local)['smart'], expected)
            launch.assert_not_called()
    def test_disabled_game_skips_preflight(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.Path, 'home', return_value=Path(tmp)), patch.object(m, 'launch', return_value='existing-profile-active'), patch.object(m, 'load_settings', return_value={'smart':False}), patch('play_check.collect') as collect, patch('sys.argv', ['launcher', '--local', '--game']):
            self.assertEqual(m.main(), 0)
            collect.assert_not_called()
