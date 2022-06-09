#!/usr/bin/env python3

from tools.client import Client

c = Client()

print('Resetting...')
c.regs.reset_ctl.write(1)
