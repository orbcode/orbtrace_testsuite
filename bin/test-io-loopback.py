#!/usr/bin/env python3

import sys
import time
from tools.client import Client

c = Client()

outputs = {
    0: 0x2529,
    1: 0x4a52,
    3: 0x2529,
    4: 0x4a52,
    10: 0x2529,
    11: 0x4a52,
    12: 0x9084,
    13: 0x2529,
    14: 0x4a52,
    15: 0x9084,
}

def check(expected):
    value = c.regs.test_io_in.read() & 0xffff
    if value == expected:
        return True

    out = c.regs.test_io_out.read()
    oe = c.regs.test_io_oe.read()

    print(f'Error: Read value {value:#06x} doesn\'t match expected value {expected:#06x}. OUT={out:#06x}, OE={oe:#06x}', file = sys.stderr)

    return False

def set(pin, level = 0):
    if pin is None:
        mask = 0
    else:
        mask = 1 << pin
    
    c.regs.test_io_out.write(mask if level else 0)
    c.regs.test_io_oe.write(mask)

def test(pin):
    set(pin, 0)
    low = check(0xffff & ~outputs[pin])
    set(pin, 1)
    high = check(0xffff)

    return low and high

set(None)

print('Enabling VTREF=3.3V')
c.ldo_set(vtref = 1)

if not check(0xffff):
    c.ldo_set(enable = False)
    sys.exit(1)

print('Pullups OK')

if not all(test(pin) for pin in outputs):
    c.ldo_set(enable = False)
    sys.exit(1)

print('All outputs OK')

c.ldo_set(enable = False)
