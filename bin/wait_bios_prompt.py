#!/usr/bin/env python3

import sys
import time
import argparse
import serial

parser = argparse.ArgumentParser()
parser.add_argument('--port', help = 'BIOS serial port')

args = parser.parse_args()

while True:
    try:
        com = serial.Serial(args.port, timeout = 0.3)
    except serial.serialutil.SerialException:
        time.sleep(0.1)
    else:
        break

print('Waiting for BIOS prompt:')

while True:
    line = com.readline()

    if line == b'':
        print('Timeout', file = sys.stderr)
        sys.exit(1)

    print(line.decode('utf-8').strip())

    if line == b'\r\x1b[92;1mlitex\x1b[0m> ':
        print('OK')
        break
