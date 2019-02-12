# Thanks to Those That Went Before
## Tisham Dhar
Tisham Dhar has made it easy for us to use the ATM90E26 electricity metering IC in our project.  I have used both his Featherwing implementation and the DIN rail implementation.  Currently, I am interested in the DIN rail implementation because this implementation will allow me to plug in his hw into a junction box (you know - the thing with all the circuit breakers typically in your garage....).  While I personally believe Tisham's documentation could use improvement (after all - Tisham is an exceptional engineer - it is not easy to be exceptional in both engineering and documentation) I found Tisham's resources to be very useful:

- [Crowd Supply web site](https://www.crowdsupply.com/whatnick/atm90e26-energy-monitor-kits)  
- [DIN meter on GitHub](https://github.com/whatnick/din_meter_atm90e26)  
- [DIN power on GitHub](https://github.com/whatnick/din_power_atm90e26.git)  
- [micropython library for the M90E26](https://github.com/whatnick/DIN_Wemos_ATM90E26_upy)

# About this Library
This library abstracts the ATM90E26 meter on top of the SPI interface. It makes it easy from REPL or from a CircuitPython file (e.g.: main.py) to access the ATM90E26.

## Which one to use?
### Older

I have an "older" and "newer" library.  The older library is [HappyDay_atm90e26.py](https://github.com/BitKnitting/HappyDay_ATM90e26_CircuitPython/blob/master/HappyDay_atm90e26.py).  This worked great with Tisham's Featherwing...
### Newer
For my most recent project I am using [HappyDay_M90E26_SPI.py](https://github.com/BitKnitting/HappyDay_ATM90e26_CircuitPython).  I was having challenges getting expected readings (e.g.: line_voltage was giving me 0 when I should have gotten something like 124).  I made what I think of as minor cleanup to the init() method (mainly setting Checksum Two back to Tisham's original values).  It worked so...YIPPEE!
# CircuitPython Library
No that I had a .py library, I needed to get it into .mpy format.  .mpy format dramatically shrinks the file size prior to copying it within the lib subdirectory of the CircuitPython hw.  For this I used the [mpy cross executable](https://github.com/BitKnitting/HappyDay_ATM90e26_CircuitPython/blob/master/mpy-cross).  ```e.g.: $ ./mpy-cross HappyDay_M90E26_SPY.py``` from a terminal line.
# CircuitPython Version
The version of CircuitPython I am currently using is 3.1.2.
# Example Circuit Python code
I used [din_test.py](https://github.com/BitKnitting/HappyDay_ATM90e26_CircuitPython/blob/master/din_test.py) to test.  Here's some values I got:
```
sys_status  = energy_sensor.sys_status
meter_status = energy_sensor.meter_status
line_voltage = energy_sensor.line_voltage
print('system status: 0x{:x} \nmeter status: 0x{:x}\nline voltage: {}'.format(sys_status,meter_status,line_voltage))
system status: 0x2 
meter status: 0x800
line voltage: 240.13 
```
