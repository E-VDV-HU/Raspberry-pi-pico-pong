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

Connections: Analog Keypad 2 (currently disconnected)
 * Signal -> GP27 (ADC1, physical pin 32)
"""

from machine import Pin, SPI, ADC, SoftI2C
import utime

#vars
brightness = 5
WIDTH = 128
HEIGHT = 64

# Known I2C pin pairs: (SCL, SDA, name)
i2c_pin_pairs = [
    (14, 15, "GP14/GP15"),
    (7, 6, "GP7/GP6")
]

detected_i2c = []
oled = None
display = None

#report
def report(status, name, details=""):
    print(f"[{status}] {name}: {details}")

#test 1: I2C device detection
print("\n--- I2C DEVICE SCAN ---")

for scl_pin, sda_pin, name in i2c_pin_pairs:
    print(f"\nScanning {name}: SCL=GP{scl_pin}, SDA=GP{sda_pin}")

    try:
        i2c = SoftI2C(
            scl=Pin(scl_pin),
            sda=Pin(sda_pin),
            freq=100000
        )
        utime.sleep_ms(100)
        devices = i2c.scan()

        if devices:
            addresses = [hex(device) for device in devices]
            print("Detected addresses:", addresses)

            for address in devices:
                detected_i2c.append(
                    (name, address, i2c)
                )
        else:
            print("No I2C devices detected.")

    except Exception as e:
        print("I2C scan error:", repr(e))

#summary of I2C detection
print("\n--- I2C DETECTION RESULTS ---")

if detected_i2c:
    for name, address, bus in detected_i2c:
        report("DETECTED", f"I2C device {hex(address)}", name)
else:
    report("NONE FOUND", "I2C", "No responding devices on tested pins")

#test 2: OLED
print("\n--- SSD1306 OLED TEST ---")

oled_target = None

for name, address, bus in detected_i2c:
    if address in (0x3C, 0x3D):
        oled_target = (name, address, bus)
        break

if oled_target:
    name, address, bus = oled_target

    try:
        from ssd1306 import SSD1306_I2C

        oled = SSD1306_I2C(
            WIDTH,
            HEIGHT,
            bus,
            addr=address
        )

        oled.fill(0)
        oled.text("CONNECTION TEST", 0, 0)
        oled.text("OLED FOUND", 0, 18)
        oled.text(name, 0, 36)
        oled.text(hex(address), 0, 52)
        oled.show()

        report("PASS", "SSD1306 OLED", f"Initialized at {hex(address)} on {name}")

    except Exception as e:
        report("FAIL", "SSD1306 OLED", repr(e))
else:
    report("NOT DETECTED", "SSD1306 OLED", "No response at 0x3C or 0x3D")

#test 3: MAX7219
print("\n--- MAX7219 MATRIX TEST ---")

try:
    import max7219

    spi = SPI(
        0,
        baudrate=10000000,
        polarity=1,
        phase=0,
        sck=Pin(2),
        mosi=Pin(3)
    )

    ss = Pin(5, Pin.OUT)
    display = max7219.Matrix8x8(spi, ss, 1)
    display.brightness(brightness)
    display.set_rotation(270)

    # Show a short visual test pattern
    display.fill(1)
    display.show()
    utime.sleep_ms(400)

    display.fill(0)

    # Draw a border
    for x in range(8):
        display.pixel(x, 0, 1)
        display.pixel(x, 7, 1)

    for y in range(8):
        display.pixel(0, y, 1)
        display.pixel(7, y, 1)

    display.show()

    report(
        "VISUAL CHECK",
        "MAX7219",
        "Test pattern sent. Confirm that it appears on the matrix."
    )

except Exception as e:
    report("ERROR", "MAX7219", repr(e))

#test 4: Player 1 ADC input
print("\n--- PLAYER 1 ADC: GP26 ---")

try:
    keypad_1 = ADC(Pin(26))
    values = []

    for i in range(20):
        values.append(keypad_1.read_u16())
        utime.sleep_ms(25)

    average = sum(values) // len(values)
    minimum = min(values)
    maximum = max(values)

    print("Readings:", values)
    print("Minimum:", minimum)
    print("Maximum:", maximum)
    print("Average:", average)
    print("Variation:", maximum - minimum)

    report(
        "DIAGNOSTIC ONLY",
        "Player 1 ADC",
        "Readings do not prove a keypad is connected."
    )

except Exception as e:
    report("ERROR", "Player 1 ADC", repr(e))

#test 5: Player 2 ADC input
print("\n--- PLAYER 2 ADC: GP27 ---")

try:
    keypad_2 = ADC(Pin(27))
    values = []

    for i in range(20):
        values.append(keypad_2.read_u16())
        utime.sleep_ms(25)

    average = sum(values) // len(values)
    minimum = min(values)
    maximum = max(values)

    print("Readings:", values)
    print("Minimum:", minimum)
    print("Maximum:", maximum)
    print("Average:", average)
    print("Variation:", maximum - minimum)

    report(
        "DIAGNOSTIC ONLY",
        "Player 2 ADC",
        "Currently disconnected; readings may be floating."
    )

except Exception as e:
    report("ERROR", "Player 2 ADC", repr(e))

#test 6: onboard LED
print("\n--- ONBOARD LED TEST ---")

try:
    led = Pin("LED", Pin.OUT)

    for i in range(4):
        led.toggle()
        utime.sleep_ms(250)

    led.on()

    report("COMMAND SENT", "Onboard LED", "It should have blinked four times.")

except Exception as e:
    report("ERROR", "Onboard LED", repr(e))

#summary
print("\n--- FINAL SUMMARY ---")

if detected_i2c:
    print("Devices responding over I2C:")
    for name, address, bus in detected_i2c:
        print(f" - {hex(address)} on {name}")
else:
    print("No I2C devices were detected.")

if oled is not None:
    print("OLED initialized successfully.")
else:
    print("OLED was not initialized.")

print("MAX7219: visual confirmation required.")
print("ADC inputs: physical device presence cannot be confirmed automatically.")
print("Onboard LED: blink commands sent.")
print("\nTest complete.")