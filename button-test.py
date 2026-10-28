#import
from machine import Pin # pyright: ignore[reportMissingModuleSource]
import utime # pyright: ignore[reportMissingModuleSource]

#vars
led = Pin("LED", Pin.OUT)

try:
    import max7219
except ImportError:
    for i in range(11):
        led.toggle()
        utime.sleep(0.1)
    raise ImportError("Library max7219 is not installed.")

#buttons
switch_pin1 = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin2 = Pin(15, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin3 = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin4 = Pin(13, Pin.IN, pull=Pin.PULL_DOWN)

#confirm clean setup
led.toggle()
utime.sleep(0.5)
led.toggle()
utime.sleep(0.5)
led.toggle()

utime.sleep(1)

#main
def main():
    print("started")

    while True:
        if switch_pin1.value() and switch_pin2.value() and switch_pin3.value() and switch_pin4.value():
            print("All buttons pressed!")

        elif switch_pin1.value() and switch_pin2.value() and switch_pin3.value():
            print("Buttons 1, 2 and 3 pressed!")

        elif switch_pin1.value() and switch_pin2.value() and switch_pin4.value():
            print("Buttons 1, 2 and 4 pressed!")

        elif switch_pin1.value() and switch_pin3.value() and switch_pin4.value():
            print("Buttons 1, 3 and 4 pressed!")

        elif switch_pin2.value() and switch_pin3.value() and switch_pin4.value():
            print("Buttons 2, 3 and 4 pressed!")

        elif switch_pin1.value() and switch_pin2.value():
            print("Buttons 1 and 2 pressed!")

        elif switch_pin1.value() and switch_pin3.value():
            print("Buttons 1 and 3 pressed!")

        elif switch_pin1.value() and switch_pin4.value():
            print("Buttons 1 and 4 pressed!")

        elif switch_pin2.value() and switch_pin3.value():
            print("Buttons 2 and 3 pressed!")

        elif switch_pin2.value() and switch_pin4.value():
            print("Buttons 2 and 4 pressed!")

        elif switch_pin3.value() and switch_pin4.value():
            print("Buttons 3 and 4 pressed!")

        elif switch_pin1.value():
            print("Button 1 press detected!")

        elif switch_pin2.value():
            print("Button 2 press detected!")

        elif switch_pin3.value():
            print("Button 3 press detected!")

        elif switch_pin4.value():
            print("Button 4 press detected!")

        else:
            print("No buttons pressed")

        utime.sleep(1)


if __name__ == "__main__":
    main()