"""
Connections: MAX7219 LED Matrix to Raspberry Pi Pico W

 * VCC -> VBUS (5V, physical pin 40)
 * GND -> GND (physical pin 3)
 * DIN -> GPIO3 (physical pin 5)
 * CS  -> GPIO5 (physical pin 7)
 * CLK -> GPIO2 (physical pin 4)

Connections: Push Button 1

 * One side      -> 3V3 OUT (physical pin 36) [note] cannot be changed
 * Opposite side -> GP14 (GPIO19, physical pin 19) [note] this can be easily changes using vars

Button configuration:
 * GP19 uses an internal pull-down resistor.
 * Released: reads 0
 * Pressed: reads 1
"""
#import 
from machine import Pin, SPI # pyright: ignore[reportMissingModuleSource]
import utime # pyright: ignore[reportMissingModuleSource]
led = Pin("LED", Pin.OUT)
led.toggle()
try:
    import max7219
except:
    for i in range(11):
        led.toggle()
        utime.sleep(0.1)
    raise ImportError("Library max7219 is not installed.")

#vars
brightness = 10 #between 0 and 15
switch_pin1 = 14
intro_message = "SEGA"

# vars check
if brightness < 0 or brightness >15:
    for i in range(6):
        led.toggle()
        utime.sleep(0.5)
    raise ValueError("Brightness must been 0 and 15") #should exit

# autoconfig
spi = SPI(0,baudrate=10_000_000,polarity=1,phase=0,sck=Pin(2),mosi=Pin(3))
ss = Pin(5, Pin.OUT)
switch_pin1 = Pin(switch_pin1, Pin.IN, pull=Pin.PULL_DOWN)
display = max7219.Matrix8x8(spi, ss, 1)

display.brightness(brightness)
display.set_rotation(270)  # Zet de rotatie op 270 graden, dan is pixel (0,0) links bovenin.

# Clear the display.
display.fill(0)
display.show()

#confirm clean setup
led.toggle()
utime.sleep(0.5)
led.toggle()
utime.sleep(0.5)
led.toggle()

def preset(var):
    if var == "checkmark":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 1, 1, 0],
            [1, 0, 0, 0, 1, 1, 0, 0],
            [1, 1, 0, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0]
        ]
    elif var == "cross":
        display.fill(0)
        matrix_LIST = [
            [1, 1, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 1, 1]
        ]
    else:
        raise ValueError(f"{var} is not found!")
    
    display.write_matrix(matrix_LIST)
    display.show()
    return "code 0"

def screen_text(text):
    length = len(text)
    column = (length * 8)
    while True:
        for i in range(32, -column, -1):
            display.fill(0)
            display.text(text, i, 0, 1)
            display.show()
            utime.sleep(0.1)
        break

def screensaver():
    while True:
        for x in range(8):
            for y in range(8):
                display.fill(0)
                display.pixel(x,y,1)
                display.show()
                utime.sleep(0.1)
                if switch_pin1.value():
                    return "code 0"

def screen_rotation():
    while True:
        display.fill(0)
        display.pixel(3, 0, 1)
        display.pixel(4, 0, 1)
        display.show()
        if switch_pin1.value():
            while switch_pin1.value():
                utime.sleep(0.1)
            display.pixel(3, 3, 1)
            display.pixel(4, 3, 1)
            display.pixel(3, 4, 1)
            display.pixel(4, 4, 1)
            rotation = (display.rotation + 90) % 360
            display.set_rotation(rotation)
            display.show()
            display.pixel(3, 3, 0)
            display.show()
            utime.sleep(0.25)
            display.pixel(4, 3, 0)
            display.show()
            utime.sleep(0.25)
            display.pixel(3, 4, 0)
            display.show()
            utime.sleep(0.25)
            display.pixel(4, 4, 0)
            display.show()
            utime.sleep(0.25)
            if switch_pin1.value():
                return f"selected rotation: {display.rotation}" 
            display.fill(0)
            display.show()

def main():
    screen_text(intro_message)
    screen_rotation()
    preset("checkmark")
    utime.sleep(1)
    screensaver()


if __name__ == "__main__":
    main()