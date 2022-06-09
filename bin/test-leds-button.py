#!/usr/bin/env python3

import sys
import time
from tools.client import Client

c = Client()

def button_pressed():
    return False if c.regs.test_io_in.read() & (1 << 16) else True

def set_leds(leds):
    c.regs.led_ctrl_set.write(leds)

print('Setting all leds to white.')

try:
    set_leds(0xfffff)

    print('Manually check and confirm five white leds by pressing and releasing the button.')
    print('Waiting...')

    while True:
        if button_pressed():
            break
        
        time.sleep(0.1)

    print('Button press detected.')

    while True:
        if not button_pressed():
            break
        
        time.sleep(0.1)

    print('Button release detected.')

finally:
    set_leds(0xe)
