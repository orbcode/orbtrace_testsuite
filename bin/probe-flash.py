#!/usr/bin/env python3

import sys
from tools.client import Client

expected_id = b'\x01\x60\x17'

c = Client()

id = c.flash_read_id()

print(f'ID: {id.hex().upper()}')

if not id.startswith(expected_id):
    print(f'Error: Expected {expected_id.hex().upper()}.', file = sys.stderr)
    sys.exit(1)

uid = c.flash_read_uid()

print(f'UID: {uid.hex().upper()}')
