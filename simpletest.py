
import digitalio
import board
import busio
from HappyDay_ATM90e26 import ATM90e26

spi_bus = busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D10)
energy_sensor = ATM90e26(spi_bus,cs)
sys_status = energy_sensor.sys_status
meter_status = energy_sensor.meter_status
