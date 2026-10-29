"""
Connections: MAX7219 LED Matrix to Raspberry Pi Pico W

 * VCC -> VBUS (5V, physical pin 40)
 * GND -> GND (physical pin 3)
 * DIN -> GPIO3 (physical pin 5)
 * CS  -> GPIO5 (physical pin 7)
 * CLK -> GPIO2 (physical pin 4)

Connections: OLED SSD1306 I2C Display
 * VCC -> 3V3 OUT (physical pin 36)
 * GND -> GND (physical pin 38)
 * SCL -> GPIO7 (physical pin 10)
 * SDA -> GPIO6 (physical pin 9)

Connections: Analog Keypad 1
 * VCC    -> 3V3 OUT (physical pin 36)
 * GND    -> GND
 * Signal -> GP26 (ADC0, physical pin 31)

Connections: Analog Keypad 2
 * VCC    -> 3V3 OUT (physical pin 36)
 * GND    -> GND
 * Signal -> GP27 (ADC1, physical pin 32)
"""
#import
from machine import Pin, SPI, ADC, SoftI2C  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
import utime # pyright: ignore[reportMissingImports, reportMissingModuleSource]
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

try:
    from ssd1306 import SSD1306_I2C
except:
    for i in range(5):
        led.toggle()
        utime.sleep(1)
    raise ImportError("Library ssd1306 is not installed.")

#vars
brightness = 10 #between 0 and 15
keypad_pin1 = 26  # GP26 / ADC0, physical pin 31
keypad_pin2 = 27  # GP27 / ADC1, physical pin 32
intro_message = "SEGA"

#oled
WIDTH = 128
HEIGHT = 64
oled_pin_SCL = 7
oled_pin_SDA = 6

#pong
difficulty = 3
modifier = 1
bot = "R" # L, R, Both or None

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
if brightness < 0 or brightness > 15:
    for i in range(6):
        led.toggle()
        utime.sleep(0.5)
    raise ValueError("Brightness must be between 0 and 15")

if bot not in ("L", "R", "Both", None):
    raise ValueError('bot must be "L", "R", "Both" or None')

# autoconfig
spi = SPI(0, baudrate=10_000_000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)
keypad_1 = ADC(Pin(keypad_pin1))
keypad_2 = ADC(Pin(keypad_pin2))
display = max7219.Matrix8x8(spi, ss, 1)
display.brightness(brightness)
display.set_rotation(270)  # Default @ 270
i2c = SoftI2C(scl=Pin(oled_pin_SCL), sda=Pin(oled_pin_SDA))
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Clear the display.
display.fill(0)
display.show()
oled.fill(0)
oled.show()

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

def read_keypad(keypad):
    value = keypad.read_u16()
    if 9200 <= value <= 9522:
        return "UP"
    elif 21300 <= value <= 21452:
        return "DOWN"
    elif 140 <= value <= 280:
        return "LEFT"
    elif 32500 <= value <= 32647:
        return "RIGHT"
    elif 47690 <= value <= 47800:
        return "ACTION"
    return None

def screen_text(text):
    length = len(text)
    column = length * 8
    for i in range(32, -column, -1):
        display.fill(0)
        display.text(text, i, 0, 1)
        display.show()
        utime.sleep(0.1)

def screensaver():
    while True:
        for x in range(8):
            for y in range(8):
                display.fill(0)
                display.pixel(x, y, 1)
                display.show()
                utime.sleep(0.1)
                if read_keypad(keypad_1) == "ACTION":
                    return "code 0"

def screen_rotation():
    while True:
        display.fill(0)
        display.pixel(3, 0, 1)
        display.pixel(4, 0, 1)
        display.show()
        if read_keypad(keypad_1) == "ACTION":
            while read_keypad(keypad_1) == "ACTION":
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
            if read_keypad(keypad_1) == "ACTION":
                preset("checkmark")
                return f"selected rotation: {display.rotation}"
            display.fill(0)
            display.show()

def draw_paddle(player, axis): # display.pixel (x, y, on_off)
    if player == 1:
        for i in range(8):
            display.pixel(0, i, 0)
        for i in range(axis - 1, axis + 2):
            display.pixel(0, i, 1)
    elif player == 2:
        for i in range(8):
            display.pixel(7, i, 0)
        for i in range(axis - 1, axis + 2):
            display.pixel(7, i, 1)

def draw_ball(side, curve, axis_ball, count):
    global axis_p1, axis_p2, score, reset, difficulty, modifier, bot
    if count <= difficulty:
        display.pixel(axis_ball[0], axis_ball[1], 1)
        return side, curve, axis_ball, count + modifier
    else:
        count = 0
        for x in range(1, 7):
            for y in range(0, 8):
                display.pixel(x, y, 0)

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
            if bot == "L" or bot == "Both":
                side = "R"
            else:
                hit = abs(axis_ball[1] - axis_p1) <= 1
                if hit:
                    offset = axis_ball[1] - axis_p1
                    if abs(offset) == 1:
                        curve = 2 if offset > 0 else -2
                    else:
                        curve = -1
                    side = "R"
                else:
                    score[1] += 1
                    reset = True

        elif axis_ball[0] == 6 and side == "R":
            if bot == "R" or bot == "Both":
                side = "L"
            else:
                hit = abs(axis_ball[1] - axis_p2) <= 1
                if hit:
                    offset = axis_ball[1] - axis_p2
                    if abs(offset) == 1:
                        curve = 2 if offset > 0 else -2
                    else:
                        curve = -1
                    side = "L"
                else:
                    score[0] += 1
                    reset = True

    display.pixel(axis_ball[0], axis_ball[1], 1)
    if axis_ball[1] <= 0 or axis_ball[1] >= 7:
        curve = -(curve)
    if axis_ball[1] < 0:
        axis_ball[1] = 0
    elif axis_ball[1] > 7:
        axis_ball[1] = 7
    return side, curve, axis_ball, count

def pong():
    global axis_p1, axis_p2, axis_ball, side_ball, curve_ball, score, reset, count, modifier, difficulty
    oled.fill(0)
    oled.text("0-0", 0, 0)
    oled.show()
    while True:
        display.fill(0)
        if reset:
            reset = False
            oled.fill(0)
            oled.text(f"{score[0]}-{score[1]}", 0, 0)
            oled.show()
            screen_text(f"{score[0]}-{score[1]}")
            curve_ball = 1 if random.randint(0, 1) else -1 # Noosphere-chat recommendation (https://noosphere-chat.pages.dev/)
            axis_ball = [5, 6]
            axis_p1 = 4
            axis_p2 = 3
            side_ball = "L"
            count = 0

        draw_paddle(1, axis_p1)
        draw_paddle(2, axis_p2)
        side_ball, curve_ball, axis_ball, count = draw_ball(side_ball, curve_ball, axis_ball, count)
        display.show()
        utime.sleep(0.1)

        key1 = read_keypad(keypad_1)
        key2 = read_keypad(keypad_2)

        if key1 == "ACTION":
            break
        elif key1 == "UP":
            axis_p1 -= 1
        elif key1 == "DOWN":
            axis_p1 += 1

        if key2 == "UP":
            axis_p2 -= 1
        elif key2 == "DOWN":
            axis_p2 += 1

        if axis_p1 <= 0:
            axis_p1 = 1
        elif axis_p1 >= 7:
            axis_p1 = 6

        if axis_p2 <= 0:
            axis_p2 = 1
        elif axis_p2 >= 7:
            axis_p2 = 6

    oled.fill(0)
    oled.show()

def main():
    oled.fill(0)
    oled.text("Welcome!", 0, 0)
    oled.show()
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
    display.show()
    utime.sleep(1)

if __name__ == "__main__":
    main()
