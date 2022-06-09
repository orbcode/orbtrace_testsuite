#!/usr/bin/env python3

import treepoem
import time
import subprocess
import usb1

gtin = '07090058320000'
date = time.strftime('%Y-%m-%d')
git_rev = subprocess.check_output('git describe --always --long --dirty', shell = True).decode('utf-8').strip()

from PIL import Image, ImageDraw, ImageFont, ImageShow

import brother_ql.raster
import brother_ql.conversion
import brother_ql.backends.helpers

font = ImageFont.truetype('font/NotoSansMono-Regular.ttf', 36)

def create_label(serial):
    label = Image.new('1', (696, 271), 1)

    datamatrix = treepoem.generate_barcode(
        barcode_type = 'gs1datamatrix',
        data = f'(01){gtin}(21){serial}',
    )

    label.paste(datamatrix.convert('1').resize((246, 246)), (0, 12))

    text = [
        'https://orbcode.org/',
        'orbtrace-mini r1.0',
        serial,
        'All tests PASSED',
        date,
        git_rev,
    ]

    draw = ImageDraw.Draw(label)

    draw.multiline_text((260, 0), '\n'.join(text), font = font)

    return label

def print_label(label):
    qlr = brother_ql.raster.BrotherQLRaster('QL-1060N')
    qlr.exception_on_warning = True

    instructions = brother_ql.conversion.convert(qlr = qlr, label = '62x29', images = [label])
    brother_ql.backends.helpers.send(instructions = instructions, printer_identifier = 'usb://0x04f9:0x202a', backend_identifier = 'pyusb', blocking=True)

def find_serial():
    with usb1.USBContext() as context:
        serial, = (dev.getSerialNumber() for dev in context.getDeviceIterator() if dev.getVendorID() == 0x1209 and dev.getProductID() == 0x3443)
    
    return serial

label = create_label(find_serial())

#ImageShow.show(label)

print_label(label)
