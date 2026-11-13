import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('check', Path(__file__).resolve().parents[1] / 'scripts/play_check.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CheckTests(unittest.TestCase):
    def test_ping_loss_and_variation(self):
        result = m.ping_summary('8 packets transmitted, 7 packets received, 12.5% packet loss\nround-trip min/avg/max/stddev = 1.0/2.0/3.0/0.4 ms')
        self.assertEqual(result, {'lossPercent': 12.5, 'averageMs': 2.0, 'variationMs': 0.4})

    def test_failed_ping_does_not_invent_latency(self):
        self.assertIsNone(m.ping_summary('permission denied')['averageMs'])

    def test_missing_usb_and_unknown_network_are_explicit(self):
        with patch.object(m.Path, 'is_dir', return_value=False), patch.object(m, 'storage', return_value=2), patch.object(m, 'command', return_value=(1, 'unavailable')):
            report = m.collect(network=True)
        self.assertFalse(report['usbConnected'])
        self.assertIsNone(report['usbFreeGiB'])
        self.assertEqual(report['routerProbe']['state'], 'unavailable')
        self.assertGreaterEqual(len(report['recommendations']), 2)
