#!/usr/bin/env python3

import sys
import argparse
import usb1

parser = argparse.ArgumentParser()
parser.add_argument('--vid', type = lambda x: int(x, 16), help = 'Match VID')
parser.add_argument('--pid', type = lambda x: int(x, 16), help = 'Match PID')
parser.add_argument('--port', help = 'Match port path')

args = parser.parse_args()

found = False

def hotplug_callback(context, device, event):
    if event != usb1.HOTPLUG_EVENT_DEVICE_ARRIVED:
        return

    if args.vid is not None and args.vid != device.getVendorID():
        return

    if args.pid is not None and args.pid != device.getProductID():
        return

    if args.port is not None and args.port != '.'.join(str(port) for port in device.getPortNumberList()):
        return

    print('Found device:', device)

    global found
    found = True

with usb1.USBContext() as context:
    if not context.hasCapability(usb1.CAP_HAS_HOTPLUG):
        print('Hotplug support is missing. Please upgrade libusb.')
        sys.exit(1)

    context.hotplugRegisterCallback(hotplug_callback)

    if not found:
        print('Waiting for device.')

    while not found:
        context.handleEvents()
