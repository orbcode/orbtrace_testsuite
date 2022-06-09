#!/usr/bin/env python3

import sys
from tools.client import Client

read_addr = 0x30
read_reg = 0xe9
expected_data = b'\x06'

c = Client()

print(f'Reading register {read_reg:#x}.')
data = c.i2c_transfer(read_addr, read_reg.to_bytes(1, 'big'), len(expected_data))

if not data == expected_data:
    print(f'Error: Read value {data.hex()} doesn\'t match expected value {expected_data.hex()}.', file = sys.stderr)
    sys.exit(1)

print('OK')
