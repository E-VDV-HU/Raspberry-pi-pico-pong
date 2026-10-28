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
import random
led = Pin("LED", Pin.OUT)
led.on()
try:
    import max7219
except:
    for i in range(11):
        led.toggle()
        utime.sleep(0.1)
    raise ImportError("Library max7219 is not installed.")

#vars
brightness = 10 #between 0 and 15

#player 1 / main controller
switch_pin1 = 14
switch_pin2 = 15

#player 2
switch_pin3 = 12
switch_pin4 = 13
intro_message = "SEGA"

#pong
difficulty = 5
modifier = 1
#pong defaults
axis_p1 = 4
axis_p2 = 3
axis_ball = [5,6] # default
side_ball = "L" #L or R
curve_ball = 1
score = [0,0] # [player 1,player2]
reset = False
count = 0

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
switch_pin2 = Pin(switch_pin2, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin3 = Pin(switch_pin3, Pin.IN, pull=Pin.PULL_DOWN)
switch_pin4 = Pin(switch_pin4, Pin.IN, pull=Pin.PULL_DOWN)
display = max7219.Matrix8x8(spi, ss, 1)

display.brightness(brightness)
display.set_rotation(270)  # Default @ 270
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
    # Up
    elif var == "arrow" or var == "arrow_u":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]

    # Down
    elif var == "arrow_d":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ]

    # Left
    elif var == "arrow_l":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0]
        ]

    # Right
    elif var == "arrow_r":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0]
        ]
        
    else:
        for i in range(10):
            led.toggle()
            utime.sleep(0.1)
        raise ValueError(f"{var} is not found!")
    
    display.write_matrix(matrix_LIST)
    display.show()
    pass

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
            utime.sleep(0.25)
            display.show()
            if switch_pin1.value():
                preset("checkmark")
                return f"selected rotation: {display.rotation}" 
            display.fill(0)
            display.show()

def draw_paddle(player, axis): # display.pixel (x, y, on_off)
    if player == 1:
        for i in range(8):
            display.pixel(0,i,0)
        for i in range(axis - 1, axis + 2):
            display.pixel(0,i,1)
    elif player == 2:
        for i in range(8):
            display.pixel(7,i,0)
        for i in range(axis - 1, axis + 2):
            display.pixel(7,i,1)

def draw_ball(side, curve, axis_ball, count):
    global axis_p1, axis_p2, score, reset, difficulty, modifier
    if count <= difficulty:
        display.pixel(axis_ball[0],axis_ball[1],1)
        return side, curve, axis_ball, count + modifier
    else:
        count = 0
        for x in range(1,7):
            for y in range(0,8):
                display.pixel(x,y,0)
        if side == "L":
            axis_ball[0] -= 1
        elif side == "R":
            axis_ball[0] += 1
        axis_ball[1] += curve
        if axis_ball[1] < 0:
            axis_ball[1] = 0
        elif axis_ball[1] > 7:
            axis_ball[1] = 7

        if axis_ball[0] == 1 and side == "L": 
            hit = abs(axis_ball[1] - axis_p1) <= 1
            
            if hit:
                if side == "L":
                    side = "R"
                else:
                    side = "L"
            else:
                if axis_ball[0] <= 1:
                    score[1] += 1
                if axis_ball[0] >= 6:
                    score[0] += 1
                reset = True
        
        elif axis_ball[0] == 6 and side == "R":
            hit = abs(axis_ball[1] - axis_p2) <= 1
            
            if hit:
                if side == "L":
                    side = "R"
                else:
                    side = "L"
            else:
                if axis_ball[0] <= 1:
                    score[1] += 1
                if axis_ball[0] >= 6:
                    score[0] += 1
                reset = True

    display.pixel(axis_ball[0],axis_ball[1],1)
    if axis_ball[1] == 0 or axis_ball[1] == 7:
        curve = -(curve)
    return side,curve,axis_ball,count

            
def pong():
    global axis_p1,axis_p2,axis_ball,side_ball,curve_ball,score,reset,count, modifier, difficulty
    while True:
        display.fill(0)
        if reset:
            reset = False
            screen_text(f"{score[0]}-{score[1]}")
            curve_ball = 1 if random.randint(0, 1) else -1 # Noosphere-chat recommendation (https://noosphere-chat.pages.dev/)
            axis_ball = [5,6]
            axis_p1 = 4
            axis_p2 = 3
            side_ball = "L"

        draw_paddle(1,axis_p1)
        draw_paddle(2,axis_p2)
        side_ball, curve_ball, axis_ball, count = draw_ball(side_ball, curve_ball, axis_ball, count)
        display.show()
        utime.sleep(0.1)
        if switch_pin1.value() and switch_pin2.value():
            break
        elif switch_pin1.value():
            axis_p1 -= 1
            if axis_p1 <= 0:
                axis_p1 = 1
            elif axis_p1 >= 7:
                axis_p1 = 6
        elif switch_pin2.value():
            axis_p1 += 1
            if axis_p1 <= 0:
                axis_p1 = 1
            elif axis_p1 >= 7:
                axis_p1 = 6
        if switch_pin3.value():
            axis_p2 -= 1
            if axis_p2 <= 0:
                axis_p2 = 1
            elif axis_p2 >= 7:
                axis_p2 = 6
        elif switch_pin4.value():
            axis_p2 += 1
            if axis_p2 <= 0:
                axis_p2 = 1
            elif axis_p2 >= 7:
                axis_p2 = 6
    display.show()

def main():
    screen_text(intro_message)
    screen_rotation() 
    utime.sleep(1)
    display.fill(0)
    display.show()
    pong()
    preset("cross")
    utime.sleep(1)
    screensaver()
    preset("cross")
    utime.sleep(1)
    display.fill(0)
    display.show
    utime.sleep(1)


if __name__ == "__main__":
    main()