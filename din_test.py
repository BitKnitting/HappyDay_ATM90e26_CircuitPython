import digitalio
import board
import busio
from HappyDay_M90E26_SPI import ATM90e26
import time
# Get an instance of the SPI class with the SPI pins set.
spi_bus = busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
# set up the CS pin.  
cs = digitalio.DigitalInOut(board.D10)
# Create an instance of the energy sensor associated with UC_SAMP / M90E26 M2 (on layout)
# This calls the init method...
energy_sensor = ATM90e26(spi_bus,cs)
# Tisham's code (https://bit.ly/2tfo6vQ) notes the first meter with ESP826 has to be initialized twice?
# hmmm.... well, I'm not using the ESP826, but i'll initialize again...
time.sleep(.8)
energy_sensor.init()
sys_status  = energy_sensor.sys_status
meter_status = energy_sensor.meter_status
line_voltage = energy_sensor.line_voltage
print('system status: 0x{:x} \nmeter status: 0x{:x}\nline voltage: {}'.format(sys_status,meter_status,line_voltage))
