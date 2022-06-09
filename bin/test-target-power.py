#!/usr/bin/env python3

import sys
import time
from tools.client import Client

ldo_addr = 0x30
adc_addr = 0x48

c = Client()

adc_conf = {
    'vtref_v': '01d303',
    'vtref_i': '018b03',
    'vtpwr_v': '01f103',
    'vtpwr_i': '01bb03',
}

adc_scale = {
    'vtref_v': 2**15 / 4.096,
    'vtref_i': 2**15 / 0.256,
    'vtpwr_v': 2**15 / 6.144,
    'vtpwr_i': 2**15 / 0.256,
}

vtref_v_map = [0, 3.3, 1.8]
vtpwr_v_map = [0, 3.3, 5]

def ldo_set(vtref = 0, vtpwr = 0, enable = True):
    b = 0
    if enable:
        b |= (1 << 0) | (1 << 3)
        b |= [0, 1, 3][vtref] << 1
        b |= [0, 1, 3][vtpwr] << 4
    c.i2c_transfer(ldo_addr, bytes([0xf4, b]))
    time.sleep(0.05)

def adc_read(ch):
    c.i2c_transfer(adc_addr, bytes.fromhex(adc_conf[ch]))
    time.sleep(0.01)
    return int.from_bytes(c.i2c_transfer(adc_addr, b'\x00', 2), 'big') / adc_scale[ch]

def read_all():
    return (
        adc_read('vtref_v'),
        adc_read('vtref_i') * 1000,
        adc_read('vtpwr_v'),
        adc_read('vtpwr_i') * 1000,
    )

def close_enough(measured, expected):
    return abs(expected - measured) <= max(expected * .05, 0.05)

def test(vtref = 0, vtpwr = 0, enable = True):
    ldo_set(vtref, vtpwr, enable)

    print('Setting VTREF: {:.1f} V, VTPWR: {:.1f} V'.format(vtref_v_map[vtref], vtpwr_v_map[vtpwr]))

    vtref_v, vtref_i, vtpwr_v, vtpwr_i = read_all()

    print('Measuring VTREF: {:.2f} V, {:.2f} mA, VTPWR: {:.2f} V, {:.2f} mA'.format(vtref_v, vtref_i, vtpwr_v, vtpwr_i))

    if not all([
        close_enough(vtref_v, vtref_v_map[vtref]),
        close_enough(vtref_i, vtref_v * 4),
        close_enough(vtpwr_v, vtpwr_v_map[vtpwr]),
        close_enough(vtpwr_i, vtpwr_v * 2),
    ]):
        print('Error: Measured value doesn\'t match expected value.', file = sys.stderr)
        return False
    
    return True

if not all([
    test(0, 0),
    test(1, 0),
    test(2, 0),
    test(0, 1),
    test(0, 2),
    test(enable = 0),
]):
    sys.exit(1)
