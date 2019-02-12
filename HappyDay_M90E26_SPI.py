# The MIT License (MIT)
#
# Copyright (c) 2017, 2018, 2019 HappyDay
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
====================================================

This is a CircuitPython driver for the ATM90e26 energy reading chip.

* Author(s): HappyDay ported the energyic_SPI.cpp Arduino library by whatnick and
             Ryzee (c 2016).  The energyic_SPI.cpp library is located at this GitHub location:
             https://github.com/whatnick/ATM90E26_Arduino/blob/master/energyic_SPI.cpp
* Version 1.1:
    - changed the get<something>() functions to property getters.
    - updated code based on Pylint 2.0 feedback.
    - changed naming from energyic_SPI to atm90e26 to better reflect what this is.
    - more readable
* Version 1.2:
    - changed using separate spi_device library to using adafruit_bus_device.spi_device. 
    - added initializing the atm90e26.   
"""
import time  # need a bit of delay at the end of initializing the ATM90e26...
from adafruit_bus_device.spi_device import SPIDevice
#### REGISTERS #####
ATM90_SYS_STATUS = 0x01  # System Status
ATM90_SOFT_RESET = 0x00  # Software Reset
ATM90_FUNC_EN = 0x02  # Function Enable
ATM90_SAG_TH = 0x03  # Voltage Sag Threshold
ATM90_CAL_START = 0x20  # Calibration Start Command
ATM90_PL_CONST_H = 0x21  # High Word of PL_Constant
ATM90_PL_CONST_L = 0x22  # Low Word of PL_Constant
ATM90_L_GAIN = 0x23  # L Line Calibration Gain
ATM90_L_PHI = 0x24  # L Line Calibration Angle
ATM90_N_GAIN = 0x25  # N Line Calibration Gain
ATM90_N_PHI = 0x26  # N Line Calibration Angle
ATM90_P_START_TH = 0x27  # Active Startup Power Threshold
ATM90_P_NO_L_TH = 0x28  # Active No-Load Power Threshold
ATM90_Q_START_TH = 0x29  # Reactive Startup Power Threshold
ATM90_Q_NO_L_TH = 0x2A  # Reactive No-Load Power Threshold
ATM90_MMODE = 0x2B  # Metering Mode Configuration
ATM90_CHK_SUM_ONE = 0x2C  # Checksum 1
ATM90_ADJ_START = 0x30  # Measurement calibration startup command, registers 31-3A
ATM90_U_GAIN = 0x31  # Voltage rms Gain
ATM90_I_GAIN_L = 0x32  # L Line Current rms Gain
ATM90_U_OFFSET = 0x34  # Voltage Offset
ATM90_I_OFFSET_L = 0x35  # L line current offset
ATM90_P_OFFSET_L = 0x37  # L Line Active Power Offset
ATM90_Q_OFFSET_L = 0x38  # L Line Reactive Power Offset
ATM90_CHK_SUM_TWO = 0x3B  # Checksum 2
ATM90_EN_STATUS = 0x46  # Metering Status
ATM90_U_RMS = 0x49  # Voltage rms
ATM90_I_RMS = 0x48  # L Line Current rms
ATM90_P_MEAN = 0x4A  # L Line Mean Active Power
ATM90_POWER_F = 0x4D  # L Line Power Factor
ATM90_FREQ = 0x4C  # Voltage frequency
ATM90_AP_ENERGY = 0x40  # Forward Active Energy
ATM90_AN_ENERGY = 0x41  # Reverse Active Energy
SPI_READ = 1
SPI_WRITE = 0


class ATM90e26:
    ##############################################################################

    def __init__(self, spi_bus, cs):
        # TBD: Does SPIDevice return an error if not working?d
        self._device = SPIDevice(
            spi_bus, cs, baudrate=200000, polarity=1, phase=1)
        self.init()

    # TODO: How to tell when initialization failed?
    def init(self):
        # Perform soft reset
        self._spi_rw(SPI_WRITE, ATM90_SOFT_RESET, 0x789A)
        # Voltage sag irq=1, report on warnout pin=1, energy dir change irq=0
        self._spi_rw(SPI_WRITE, ATM90_FUNC_EN, 0x0030)
        # Voltage sag threshhold
        self._spi_rw(SPI_WRITE, ATM90_SAG_TH, 0x1F2F)
        #########################################
        #### Set metering calibration values ####
        #########################################
        # Metering calibration startup command. Register 21 to 2B need to be set
        self._spi_rw(SPI_WRITE, ATM90_CAL_START, 0x5678)
        # PL Constant MSB
        self._spi_rw(SPI_WRITE, ATM90_PL_CONST_H, 0x00B9)
        # PL Constant LSB
        self._spi_rw(SPI_WRITE, ATM90_PL_CONST_L, 0xC1F3)
        # Line calibration gain
        self._spi_rw(SPI_WRITE, ATM90_L_GAIN, 0x1D39)
        # Line calibration angle
        self._spi_rw(SPI_WRITE, ATM90_L_PHI, 0x0000)
        # Active Startup Power Threshold
        self._spi_rw(SPI_WRITE, ATM90_P_START_TH, 0x08BD)
        # Active No-Load Power Threshold
        self._spi_rw(SPI_WRITE, ATM90_P_NO_L_TH, 0x0000)
        # Reactive Startup Power Threshold
        self._spi_rw(SPI_WRITE, ATM90_Q_START_TH, 0x0AEC)
        # Reactive No-Load Power Threshold
        self._spi_rw(SPI_WRITE, ATM90_Q_NO_L_TH, 0x0000)
        # Metering Mode Configuration. All defaults. See pg 3
        self._spi_rw(SPI_WRITE, ATM90_MMODE, 0x9422)
        # Write CSOne, as self calculated
        self._spi_rw(SPI_WRITE, ATM90_CHK_SUM_ONE, 0x4A34)
        #checksum = self._spi_rw(SPI_READ,ATM90_CHK_SUM_ONE,0x0000)
        #print('Checksum 1: ',hex(checksum))
        ##############################################
        # Set measurement calibration values
        ##############################################
        self._spi_rw(SPI_WRITE, ATM90_ADJ_START, 0x5678)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!! Modified Ugain.  See my bitknitting post on this:
        # https://bitknitting.wordpress.com/2017/10/07/trying-out-the-atm90e26-featherwing/
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #self._spi_rw(SPI_WRITE, ATM90_U_GAIN, 0x890F)
        # While I am trying to get the DIN rail to work, put back to what Tisham originally had...
        self._spi_rw(SPI_WRITE,ATM90_U_GAIN, 0xD464)
        # L line current gain
        self._spi_rw(SPI_WRITE, ATM90_I_GAIN_L, 0x6E49)
        # Voltage offset
        self._spi_rw(SPI_WRITE, ATM90_U_OFFSET, 0x0000)
        # L line current offset
        self._spi_rw(SPI_WRITE, ATM90_I_OFFSET_L, 0x0000)
        # L line active power offset
        self._spi_rw(SPI_WRITE, ATM90_P_OFFSET_L, 0x0000)
        # L line reactive power offset
        self._spi_rw(SPI_WRITE, ATM90_Q_OFFSET_L, 0x0000)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!! Modified Checksum two.  See my bitknitting post on this:
        # https://bitknitting.wordpress.com/2017/10/07/trying-out-the-atm90e26-featherwing/
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # as above, I noted I changed the Voltage rms gain so checksum two is back to what Tisham originally had.
        #self._spi_rw(SPI_WRITE, ATM90_CHK_SUM_TWO, 0xE4F4)
        self._spi_rw(SPI_WRITE, ATM90_CHK_SUM_TWO, 0xD294)
        #checksum = self._spi_rw(SPI_READ,ATM90_CHK_SUM_TWO,0x0000)
        #print('Checksum 2: ',hex(checksum))
        # Checks correctness of 21-2B registers and starts normal metering if ok
        self._spi_rw(SPI_WRITE, ATM90_CAL_START, 0x8765)
        # Checks correctness of 31-3A registers and starts normal measurement  if ok
        self._spi_rw(SPI_WRITE, ATM90_ADJ_START, 0x8765)
        # the chip needs a couple of secs to get it's act together.....
        time.sleep(2)
        sys_status = self.sys_status
        if (sys_status & 0xC000):
            print('-->Checksum error 1!')
        if (sys_status & 0x3000):
            print('--->Checksum error 2');    
        #####################################################################################

    @property
    def sys_status(self):
        reading = self._spi_rw(SPI_READ, ATM90_SYS_STATUS, 0xFFFF)
        return reading
        #####################################################################################

    @property
    def meter_status(self):
        reading = self._spi_rw(SPI_READ, ATM90_EN_STATUS, 0xFFFF)
        return reading
        #####################################################################################

    @property
    def line_voltage(self):
        reading = float(self._spi_rw(SPI_READ, ATM90_U_RMS, 0xFFFF))
        reading = reading/100.0
        return reading
        #####################################################################################

    @property
    def line_current(self):
        reading = float(self._spi_rw(SPI_READ, ATM90_I_RMS, 0xFFFF))
        reading = reading/1000
        return reading
        #####################################################################################

    @property
    def active_power(self):
        reading = self._spi_rw(SPI_READ, ATM90_P_MEAN, 0xFFFF)
        return reading
        #####################################################################################

    @property
    def power_factor(self):
        reading = self._spi_rw(SPI_READ, ATM90_POWER_F, 0xFFFF)
        # MSB is signed bit...if negative...
        if reading & 0x8000:
            reading = (reading & 0x7FFF) * -1
        return reading/1000
        #####################################################################################

    @property
    def frequency(self):
        reading = self._spi_rw(SPI_READ, ATM90_FREQ, 0xFFFF)
        return reading/100
        #####################################################################################

    @property
    def import_energy(self):
        reading = self._spi_rw(SPI_READ, ATM90_AP_ENERGY, 0xFFFF)
        return reading * 0.0001  # returns kWh if PL constant set to 1000imp/kWh
        #####################################################################################

    @property
    def export_energy(self):
        reading = self._spi_rw(SPI_READ, ATM90_AN_ENERGY, 0xFFFF)
        return reading * 0.0001  # returns kWh if PL constant set to 1000imp/kWh
        #####################################################################################

    def _spi_rw(self, read, address, value):
        #####################################################################################
        # If read = 1, There needs to be a 1 in the highest bit of the address
        address |= read << 7
        # The Arduino library put us sleeps in...I was getting correct results
        # without adding sleeps???
        # usleep = lambda x: time.sleep(x/1000000.0)
        if read:
            bytes_read = bytearray(2)
            with self._device as spi:
                # delays were in the Arduino library
                # usleep(10)
                spi.write(bytearray([address]))
                # from Arduino lib: "Must wait 4 us for data to become valid"
                # usleep(4)
                spi.readinto(bytes_read)
                if bytes_read[0] == 0xff:  # The CT is facing the wrong way...
                    return -1
                value = int.from_bytes(bytes_read, 'big', True)
                return value
        else:  # Write the two bytes of the value.
            first_byte = value >> 8
            with self._device as spi:
                # usleep(10)
                spi.write(bytearray([address]))
                # usleep(4)
                spi.write(bytearray([first_byte]))
                spi.write(bytearray([value]))
