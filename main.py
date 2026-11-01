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
 * SCL -> GPIO14 (physical pin 19)
 * SDA -> GPIO15 (physical pin 20)

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
import goalexplosions as goal_explosions # Goal explosions, custom driver.
import json
import os

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
oled_pin_SCL = 14
oled_pin_SDA = 15

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
scored = None

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
goal_explosions.setup(display)
try:
    os.stat("stats.json")
except OSError:
    with open("stats.json", "w") as file:
        json.dump({
            "players": {
                "1": {
                    "equipped_explosion": "wave",
                    "total_goals": 0
                },
                "2": {
                    "equipped_explosion": "wave",
                    "total_goals": 0
                }
            }
        }, file)


with open("stats.json", "r") as file:
    stats = json.load(file)["players"]

# Clear the display @ boot.
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
    elif var == "menu_PLAY":
        display.fill(0)
        matrix_LIST = [
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
    elif var == "menu_BP":
        matrix_LIST = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 1, 0, 1, 1, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
    elif var == "menu_ROTATION":
        matrix_LIST = [
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
    elif var == "menu_STATS": 
        matrix_LIST = [
            [0, 1, 0, 0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0]
        ]
    elif var == "menu_EXIT":
        matrix_LIST = [
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0]
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
    oled.fill(0)
    oled.text("Press [ACTION]", 0,0)
    oled.text("to rotate.", 0,16)
    oled.text("Hold [ACTION]", 0,32)
    oled.text("after to confirm.",0,48)
    oled.show()
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
    global axis_p1, axis_p2, score, reset, difficulty, modifier, bot, scored
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
                    scored = "R"

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
                    scored = "L"

    display.pixel(axis_ball[0], axis_ball[1], 1)
    if axis_ball[1] <= 0 or axis_ball[1] >= 7:
        curve = -(curve)
    if axis_ball[1] < 0:
        axis_ball[1] = 0
    elif axis_ball[1] > 7:
        axis_ball[1] = 7
    return side, curve, axis_ball, count

def pong():
    global axis_p1, axis_p2, axis_ball, side_ball, curve_ball, score, reset, count, modifier, difficulty, scored
    oled.fill(0)
    oled.text("0-0", 0, 0)
    oled.show()
    while True:
        display.fill(0)
        if reset:
            reset = False
            player = "1" if scored == "L" else "2"
            stats[player]["total_goals"] += 1
            with open("stats.json", "w") as file:
                json.dump({"players": stats}, file)
            goal_explosions.goal_explosion(stats[player]["equipped_explosion"], scored, 3)
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

def menu():
    page = 0
    display.fill(0)
    def page_render(page):
        if page == 0:
            preset("menu_PLAY")
            oled.fill(0)
            oled.text("Play Pong", 0, 0)
            oled.show()
        elif page == 1:
            preset("menu_BP")
            oled.fill(0)
            oled.text("THE PONG PASS(R)", 0, 0)
            oled.text("COPYRIGHT IDI(TM)", 0, 16)
            oled.show()
        elif page == 2:
            preset("menu_ROTATION")
            oled.fill(0)
            oled.text("Select rotation", 0, 0)
            oled.show()
        elif page == 3:
            preset("menu_STATS")
            oled.fill(0)
            oled.text("Show stats", 0, 0)
            oled.show()
        elif page == 4:
            preset("menu_EXIT")
            oled.fill(0)
            oled.text("Exit to screensaver", 0, 0)
            oled.show()

    page_render(page)

    while True:
        if read_keypad(keypad_1) == "LEFT":
            page -= 1
            if page <= -1:
                page = 4
            page_render(page)
            utime.sleep(0.1)
        elif read_keypad(keypad_1) == "RIGHT":
            page += 1
            if page >= 5:
                page = 0
            page_render(page)
            utime.sleep(0.1)
        elif read_keypad(keypad_1) == "ACTION":
            if page == 0:
                pong()
            elif page == 1:
                battlepass()
                utime.sleep(1)
            elif page == 2:
                screen_rotation()
                utime.sleep(1)
            elif page == 3:
                show_stats()
                utime.sleep(1)
            elif page == 4:
                break

def battlepass():
    names = goal_explosions.names()

    if not names:
        oled.fill(0)
        oled.text("No explosions", 0, 0)
        oled.show()
        utime.sleep(2)
        return

    index = 0
    side = "L"

    def select(name, selected_side):
        player = "1" if selected_side == "L" else "2"

        stats[player]["equipped_explosion"] = name

        with open("stats.json", "w") as file:
            json.dump({"players": stats}, file)

        preset("checkmark")

        oled.fill(0)
        oled.text("Explosion saved!", 0, 0)
        oled.text("Player: " + player, 0, 16)
        oled.text(name[:16], 0, 32)
        oled.show()

        utime.sleep(1)

    def show_menu(message=""):
        player = "1" if side == "L" else "2"

        oled.fill(0)
        oled.text("{}/{}".format(index + 1, len(names)), 0, 0)
        oled.text(names[index][:16], 0, 16)
        oled.text("Player: " + player, 0, 32)
        oled.text(message[:16], 0, 48)
        oled.show()

    show_menu("ACTION=preview")

    while True:
        key1 = read_keypad(keypad_1)
        key2 = read_keypad(keypad_2)

        # Player 2 can exit the Battlepass.
        if key2 == "ACTION":
            while read_keypad(keypad_2) == "ACTION":
                utime.sleep(0.05)
            return

        if key1 == "LEFT":
            index = (index - 1) % len(names)

        elif key1 == "RIGHT":
            index = (index + 1) % len(names)

        elif key1 in ("UP", "DOWN"):
            side = "R" if side == "L" else "L"

        elif key1 == "ACTION":
            hold_time = 0

            # Measure how long ACTION is held.
            while read_keypad(keypad_1) == "ACTION":
                utime.sleep(0.1)
                hold_time += 1

                # Allow Player 2 to exit during the hold.
                if read_keypad(keypad_2) == "ACTION":
                    return

            if hold_time >= 10:
                # Long press: equip explosion.
                select(names[index], side)
            else:
                # Short press: preview explosion.
                show_menu("Playing...")
                goal_explosions.goal_explosion(
                    names[index],
                    side,
                    3
                )

        else:
            utime.sleep(0.05)
            continue

        # Wait for navigation buttons to be released.
        while read_keypad(keypad_1) == key1:
            if read_keypad(keypad_2) == "ACTION":
                return
            utime.sleep(0.05)

        show_menu("ACTION=preview")

def show_stats():
    pass

def main():
    oled.fill(0)
    oled.text("Welcome!", 0, 0)
    oled.show()
    screen_text(intro_message)
    screen_rotation()
    utime.sleep(1)
    display.fill(0)
    display.show()
    menu()
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
