from machine import Pin, ADC
from utime import sleep_ms

KEYPAD_1_PIN = 26  # ADC0
KEYPAD_2_PIN = 27  # ADC1

keypad_1 = ADC(Pin(KEYPAD_1_PIN))
keypad_2 = ADC(Pin(KEYPAD_2_PIN))

def read_keypads():
    value_1 = keypad_1.read_u16()
    value_2 = keypad_2.read_u16()

    print(f"Keypad 1: {value_1} | Keypad 2: {value_2}")

def main():
    while True:
        read_keypads()
        sleep_ms(1000)

if __name__ == "__main__":
    main()