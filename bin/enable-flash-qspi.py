#!/usr/bin/env python3

import sys
from tools.client import Client

c = Client()

print('Reading CR1NV.')

cr1nv = c.flash_read_register(2)
quad_nv = 1 if cr1nv & (1 << 1) else 0

print(f'QUAD_NV={quad_nv}.')

if quad_nv:
    sys.exit(0)

print('Setting QUAD_NV=1.')

c.flash_write_enable()
c.flash_write_register(2, cr1nv | (1 << 1))

print('Re-reading CR1NV.')

cr1nv = c.flash_read_register(2)
quad_nv = 1 if cr1nv & (1 << 1) else 0

print(f'QUAD_NV={quad_nv}.')

if not quad_nv:
    print(f'Error: Write failed.', file = sys.stderr)
    sys.exit(1)
