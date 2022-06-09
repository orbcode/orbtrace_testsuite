#!/usr/bin/env python3

import sys
import subprocess

proc = subprocess.Popen(sys.argv[1:], stdout = subprocess.PIPE)

while True:
    line = proc.stdout.readline().decode('utf-8')

    if not line:
        break

    if '\r' in line:
        line = line.split('\r')[-1]

    sys.stdout.write(line)

sys.exit(proc.wait())
