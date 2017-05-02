"""Basic testing for AlazarTech card"""
from unittest import TestCase
import unittest
import json

from place.scripts.scan import ScanFromJSON
from place.automate.osci_card.utility import getNamesOfConstantsThatStartWith

JSON_TEST_STR = """
{
"scan_type": "SCAN_POINT_TEST",
"controller_name": "BasicController",
"controller_config":
    {
    "clock_source": "INTERNAL_CLOCK",
    "sample_rate": "SAMPLE_RATE_10MSPS",
    "clock_edge": "CLOCK_EDGE_RISING",
    "decimation": 0,

    "analog_inputs": [
        {"input_channel": "CHANNEL_A",
         "input_coupling": "DC_COUPLING",
         "input_range": "INPUT_RANGE_PM_800_MV",
         "input_impedance": "IMPEDANCE_50_OHM"}],

    "trigger_operation": "TRIG_ENGINE_OP_J",
    "trigger_engine_1": "TRIG_ENGINE_J",
    "trigger_source_1": "TRIG_CHAN_A",
    "trigger_slope_1": "TRIGGER_SLOPE_POSITIVE",
    "trigger_level_1": 128,
    "trigger_engine_2": "TRIG_ENGINE_K",
    "trigger_source_2": "TRIG_DISABLE",
    "trigger_slope_2": "TRIGGER_SLOPE_POSITIVE",
    "trigger_level_2": 128
    }
}
"""

class TestOsciCardUtilities(TestCase):
    """Test class"""
    def test0001_constants_starting(self):
        """ensures we can get constants starting with a specific value"""
        self.assertEqual(len(getNamesOfConstantsThatStartWith('POWER')), 2)

    def test0002_json_init(self):
        """Test that JSON is processing our string correctly"""
        dat = json.loads(JSON_TEST_STR)
        self.assertEqual(dat, json.loads(json.dumps(dat)))

    def test0003_json_test1(self):
        """Test that we can perform a point scan with JSON input"""
        scan = ScanFromJSON(JSON_TEST_STR)
        scan.run()

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)