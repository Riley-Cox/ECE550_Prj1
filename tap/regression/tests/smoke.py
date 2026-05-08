##########################################################
# PSU ECE510 Post-silicon Validation Projects
# --------------------------------------------------------
# Filename: smoke.py
# --------------------------------------------------------
# Purpose: TAP Controller Smoke Tests
##########################################################
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from tap.common.loopback import *
from tap.common.tap import *
import unittest

class smoke(unittest.TestCase):
    """ smoke/power on tests, hopefully won't produce actual smoke """
    
    def setUp(self):
        """ fires before each test
        Setting up for the test
        """
        log_level = LOG_LEVEL 
        self.logger = get_logger(self.id(), log_level)
        log(self.logger, 'info', '{}Running {}'.format(color_map['highlight'], self.id()))
        self.tap = Tap(log_level=log_level)
        self.loopback_monitor = LoopBack(log_level=log_level)
        self.loopback_monitor.set_monitor()
    
    def tearDown(self):
        """ fires after each test
        Cleaning up after the test
        """
        self.loopback_monitor.remove_monitor()
        self.tap.clean_up()
        log(self.logger, 'info', '{}Done with {}\n'.format(color_map['highlight'], self.id()))    
    
    def testReset(self):
        self.tap.reset()
        self.assertEqual("Test_Logic_Reset", self.loopback_monitor.cur_state)

    def testReset2ShiftIR(self):
        """ Test TAP navigates correctly from Test_Logic_Reset to Shift_IR state """
        self.tap.reset()
        self.assertEqual("Test_Logic_Reset", self.loopback_monitor.cur_state)
        self.tap.reset2ShiftIR()
        self.assertEqual("Shift_IR", self.loopback_monitor.cur_state)

    def testReadDeviceCode(self):
        """ Test reading 32-bit IDCODE from device via JTAG """
        self.tap.reset()
        self.assertEqual("Test_Logic_Reset", self.loopback_monitor.cur_state)
        self.tap.reset2ShiftIR()
        self.assertEqual("Shift_IR", self.loopback_monitor.cur_state)
        # Shift in IDCODE instruction (0b1001 = standard IDCODE for most JTAG devices)
        self.tap.shiftInData('100100')
        # Move from Exit1_IR through to Shift_DR
        self.tap.exit1IR2ShiftDR()
        self.assertEqual("Shift_DR", self.loopback_monitor.cur_state)
        # Read 32-bit device ID code
        device_code = self.tap.shiftOutData(32)
        # Valid IDCODE: not 0 (disconnected) and not 0xFFFFFFFF (no device)
        print(hex(device_code))
        self.assertNotEqual(0, device_code, "Device code should not be zero")
        self.assertNotEqual(0xFFFFFFFF, device_code, "Device code should not be all 1s")
        log(self.logger, 'info', 'Device IDCODE: 0x{:08X}'.format(device_code))
