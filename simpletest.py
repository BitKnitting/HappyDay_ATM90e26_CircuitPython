
import digitalio
import board
import busio
from HappyDay_ATM90e26 import ATM90e26
import time
# Set pin 8 to high as discussed here:
# https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module
# /pinouts#rfm-slash-semtech-radio-module
pin_8 = digitalio.DigitalInOut(RFM69_CS)
pin_8.value = True
spi_bus = busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D10)
energy_sensor = ATM90e26(spi_bus,cs)
sys_status  = energy_sensor.sys_status
meter_status = energy_sensor.meter_status
print('system status: 0x{:x} meter status: 0x{:x}'.format(sys_status,meter_status))
