##########################################################
# PSU ECE510 Post-silicon Validation Project 1
# --------------------------------------------------------
# Filename: tap.py
# --------------------------------------------------------
# Purpose: TAP Controler Class
##########################################################

from tap.common.tap_gpio import *
from tap.log.logging_setup import *
import time

class Tap(Tap_GPIO):
    """ Class for JTAG TAP Controller"""

    def __init__(self,log_level=logging.INFO):
        """ initialize TAP """
        self.logger = get_logger(__file__,log_level)
        self.max_length = 1000

        #set up the RPi TAP pins
        Tap_GPIO.__init__(self)

    def toggle_tck(self, tms, tdi):
        """ toggle TCK for state transition 

        :param tms: data for TMS pin
        :type tms: int (0/1)
        :param tdi: data for TDI pin
        :type tdi: int (0/1)

        """
        set_io_data(tms, tdi, 0)
        set_io_data(tms, tdi, 1)
        set_io_data(tms, tdi, 0)
        
        pass
       
    def reset(self):
        """ set TAP state to Test_Logic_Reset """
        # assert TMS for 5 TCKs in a row
        for i in range(5):
            self.toggle_tck(1, 0)
        pass

    def reset2ShiftIR(self):
        """ shift TAP state from reset to shiftIR """
        toggle_tck(0, 0)
        toggle_tck(1, 0)
        toggle_tck(1, 0)
        toggle_tck(0, 0)
        toggle_tck(0, 0)
        pass 

    def exit1IR2ShiftDR(self):
        """ shift TAP state from exit1IR to shiftDR """
        
        toggle_tck(1, 0)
        toggle_tck(1, 0)
        toggle_tck(1, 0)
        toggle_tck(0, 0)
        toggle_tck(0, 0)
        pass

    def exit1DR2ShiftIR(self):
        """ shift TAP state from exit1DR to shiftIR """
        toggle_tck(1, 0)
        toggle_tck(1, 0)
        toggle_tck(1, 0)
        toggle_tck(0, 0)
        toggle_tck(0, 0)
        pass

    def shiftInData(self, tdi_str):    
        """ shift in IR/DR data

        :param tdi_str: TDI data to shift in
        :type tdo_str: str

        """
        
        for i in range(5):
            x = int(tdi_str[i])
            toggle_tck(0,x)
        toggle_tck(1, int(tdi_str[5]))
        pass

    def shiftOutData(self, length):
        """ get IR/DR data

        :param length: chain length        
        :type length: int
        :returns: int - TDO data

        """
        x = 0
        for i in range(length-1):
             x = (x >> 1) | read_tdo_data()
             self.toggle_tck(0, 0)
        
        x = (x >> 1) | read_tdo_data()
        toggle_tck(1, 0)
             

        return x

    def getChainLength(self):
        """ get chain length

        :returns: int -- chain length	

        """
        self.reset()
        self.reset2ShiftIR()
        
        for i in range(self.maz_length -1):
            self.toggle_tck(0, 1)
            self.toggle_tck(1, 1)
            
        self.exit1IR2ShiftDR()
        
        for i in range(self.max_length - 1):
                self.togle_tck(0, 0)
                self.toggle_tck(0, 0)
        
        self.toggle_tck(0, 1)
        
        chain_length = 0
        for i in range(self.max_length):
            tdo_bit = read_tdo_data()
            self.toggle_tck(0, 0)
            if tdo_bit:
                chain_lemgth = i + 1
                break
            
        self.reset()

        return chain_length
