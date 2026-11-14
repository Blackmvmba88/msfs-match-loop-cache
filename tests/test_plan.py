import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from play_check import build_plan

class PlanTests(unittest.TestCase):
    def report(self, **changes):
        r = dict(chromeInstalled=True, internalFreeGiB=30, usbConnected=True, usbFreeGiB=20, power='AC', routerProbe={'state':'not-requested'})
        r.update(changes)
        return r
    def test_critical_disk_blocks(self):
        self.assertEqual(build_plan(self.report(internalFreeGiB=1))['readiness'], 'blocked')
    def test_missing_browser_blocks(self):
        self.assertEqual(build_plan(self.report(chromeInstalled=False))['readiness'], 'blocked')
    def test_missing_usb_requires_review_not_block(self):
        self.assertEqual(build_plan(self.report(usbConnected=False))['readiness'], 'review')
    def test_unknown_network_never_claims_stream_quality(self):
        plan = build_plan(self.report())
        self.assertEqual(plan['streamQuality'], 'unmeasured')
        self.assertIn('network-unmeasured', [x['code'] for x in plan['issues']])
