#!/usr/bin/env python3

import sys
from tools.client import Client

read_addr = 0x48
read_reg = 0x01
read_len = 2

c = Client()

print(f'Reading register {read_reg:#x}.')
data = c.i2c_transfer(read_addr, read_reg.to_bytes(1, 'big'), read_len)

print('OK')
