"""
goal_demo.py  V1.0.0
Showcase for goal_explosions.py

Keypad 1:
 * LEFT / RIGHT -> previous / next animation
 * UP / DOWN    -> switch goal side (L / R)
 * ACTION       -> play it
OLED shows the name, LED matrix plays the animation.
"""
from machine import Pin, SPI, ADC, SoftI2C  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
import utime  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
import max7219
from ssd1306 import SSD1306_I2C
import goalexplosions as goal_explosions

# ---------- hardware (same as main.py) ----------
spi = SPI(0, baudrate=10_000_000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
display = max7219.Matrix8x8(spi, Pin(5, Pin.OUT), 1)
display.brightness(10)
display.set_rotation(270)
display.fill(0)
display.show()

i2c = SoftI2C(scl=Pin(14), sda=Pin(15))
oled = SSD1306_I2C(128, 64, i2c)

keypad = ADC(Pin(26))


def read_keypad():
    v = keypad.read_u16()
    if 9200 <= v <= 9522:
        return "UP"
    elif 21300 <= v <= 21452:
        return "DOWN"
    elif 140 <= v <= 280:
        return "LEFT"
    elif 32500 <= v <= 32647:
        return "RIGHT"
    elif 47690 <= v <= 47800:
        return "ACTION"
    return None


def screen_text(text):
    for i in range(8, -len(text) * 8, -1):
        display.fill(0)
        display.text(text, i, 0, 1)
        display.show()
        utime.sleep(0.1)


goal_explosions.setup(display)

# ---------- menu ----------
names = goal_explosions.names()
index = 0
side = "L"


def show_menu(playing=False):
    oled.fill(0)
    oled.text("{}/{}".format(index + 1, len(names)), 0, 0)
    oled.text(names[index][:16], 0, 16)
    oled.text("Side: " + side, 0, 32)
    oled.text("Playing..." if playing else "<> pick OK=play", 0, 48)
    oled.show()


show_menu()

while True:
    key = read_keypad()
    if key:
        if key == "LEFT":
            index = (index - 1) % len(names)
        elif key == "RIGHT":
            index = (index + 1) % len(names)
        elif key in ("UP", "DOWN"):
            side = "R" if side == "L" else "L"
        elif key == "ACTION":
            show_menu(True)
            x = 1 if side == "L" else 6
            goal_explosions.goal_explosion(names[index], x, side, 3)
        show_menu()
        while read_keypad():          # wait for release
            utime.sleep_ms(30)
    utime.sleep_ms(30)