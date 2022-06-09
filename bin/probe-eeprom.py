#!/usr/bin/env python3

import sys
import random
import time
from tools.client import Client

eeprom_addr = 0x50
test_addr = 0
test_len = 16

test_data = random.randbytes(test_len)

c = Client()

print(f'Writing {test_len} bytes.')
c.i2c_transfer(0x50, test_addr.to_bytes(2, 'big') + test_data, 0)

time.sleep(0.1)

print(f'Reading {test_len} bytes.')
data = c.i2c_transfer(0x50, test_addr.to_bytes(2, 'big'), test_len)

if not data == test_data:
    print(f'Error: Read data doesn\'t match written data.', file = sys.stderr)
    sys.exit(1)

print(f'Clearing {test_len} bytes.')
c.i2c_transfer(0x50, test_addr.to_bytes(2, 'big') + b'\xff' * test_len, 0)
