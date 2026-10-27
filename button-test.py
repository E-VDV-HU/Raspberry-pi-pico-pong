#import 
from machine import Pin, SPI # pyright: ignore[reportMissingModuleSource]
import utime # pyright: ignore[reportMissingModuleSource]
led = Pin("LED", Pin.OUT)
led.on()
try:
    import max7219
except:
    for i in range(11):
        led.toggle()
        utime.sleep(0.1)
    raise ValueError("Library max7219 is not installed.")

#vars
switch_pin1 = 14
switch_pin2 = 15

switch_pin1 = Pin(switch_pin1, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin2 = Pin(switch_pin2, Pin.IN, pull=Pin.PULL_DOWN)

#confirm clean setup
led.toggle()
utime.sleep(0.5)
led.toggle()
utime.sleep(0.5)
led.toggle()

utime.sleep(1)
def main():
    print("started")
    while True:
        if switch_pin2.value() and switch_pin1.value():
            print("Both buttons pressed")
        elif switch_pin1.value():
            print("Button 1 press detected!")
        elif switch_pin2.value():
            print("Button 2 press detected!")
        else:
            print("not found")
        utime.sleep(1)

if __name__ == "__main__":
    main()