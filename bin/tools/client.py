from .comm_usb import CommUSB

import time

class Client(CommUSB):
    def __init__(self, *, vid = 0x1209, pid = 0x0001, csr_csv = 'gateware/test/csr.csv'):
        CommUSB.__init__(self, vid = vid, pid = pid, csr_csv = csr_csv)

        self.open()

    def flash_transfer_byte(self, b):
        while not (self.regs.spiflash_mmap_master_status.read() & (1 << 0)):
            pass

        self.regs.spiflash_mmap_master_rxtx.write(b)

        while not (self.regs.spiflash_mmap_master_status.read() & (1 << 1)):
            pass

        return self.regs.spiflash_mmap_master_rxtx.read() & 0xff

    def flash_transfer_cmd(self, bs):
        self.regs.spiflash_mmap_master_phyconfig.write((1 << 16) | (1 << 8) | (8 << 0))

        self.regs.spiflash_mmap_master_cs.write(1)

        r = [self.flash_transfer_byte(b) for b in bs]

        self.regs.spiflash_mmap_master_cs.write(0)

        return bytes(r)

    def flash_write_enable(self):
        self.flash_transfer_cmd(b'\x06')

    def flash_read_id(self):
        return self.flash_transfer_cmd(b'\x9f' + b'\0' * 4)[1:]

    def flash_read_uid(self):
        return self.flash_transfer_cmd(b'\x4b' + b'\0' * (4 + 8))[5:]
    
    def flash_read_register(self, addr):
        return self.flash_transfer_cmd(b'\x65' + addr.to_bytes(3, 'big') + b'\0\0')[5]

    def flash_write_register(self, addr, value):
        self.flash_transfer_cmd(b'\x71' + addr.to_bytes(3, 'big') + value.to_bytes(1, 'big'))

    def i2c_bitbang(self, scl = 1, sda = 1, oe = 1):
        self.regs.i2c_w.write((scl << 0) | (oe << 1) | (sda << 2))
    
    def i2c_start(self):
        self.i2c_bitbang(1, 1)
        self.i2c_bitbang(1, 0)
        self.i2c_bitbang(0, 0)

    def i2c_stop(self):
        self.i2c_bitbang(0, 0)
        self.i2c_bitbang(1, 0)
        self.i2c_bitbang(1, 1)
        self.i2c_bitbang(oe = 0)

    def i2c_transmit_bit(self, b):
        self.i2c_bitbang(0, b)
        self.i2c_bitbang(1, b)
        self.i2c_bitbang(0, b)
        self.i2c_bitbang(0, 0, 0)

    def i2c_receive_bit(self):
        self.i2c_bitbang(0, 0, 0)
        self.i2c_bitbang(1, 0, 0)
        b = self.regs.i2c_r.read() & 1
        self.i2c_bitbang(0, 0, 0)
        return b
    
    def i2c_transmit_byte(self, b):
        for i in range(7, -1, -1):
            self.i2c_transmit_bit(1 if b & (1 << i) else 0)

        return self.i2c_receive_bit() == 0
    
    def i2c_receive_byte(self, ack):
        b = 0
        for i in range(7, -1, -1):
            b |= 1 << i if self.i2c_receive_bit() else 0
        self.i2c_transmit_bit(0 if ack else 1)

        return b
    
    def i2c_transfer(self, addr, write = '', read = 0):
        rdata = []

        try:
            if write:
                self.i2c_start()
                if not self.i2c_transmit_byte((addr << 1) | 0):
                    raise Exception('Write address NAK')
                
                for b in write:
                    if not self.i2c_transmit_byte(b):
                        raise Exception('Write NAK')

            if read:
                self.i2c_start()
                if not self.i2c_transmit_byte((addr << 1) | 1):
                    raise Exception('Read address NAK')
                
                while read:
                    rdata.append(self.i2c_receive_byte(read > 1))
                    read -= 1
                
        finally:
            self.i2c_stop()

        return bytes(rdata)

    def ldo_set(self, vtref = 0, vtpwr = 0, enable = True):
        b = 0
        if enable:
            b |= (1 << 0) | (1 << 3)
            b |= [0, 1, 3][vtref] << 1
            b |= [0, 1, 3][vtpwr] << 4
        self.i2c_transfer(0x30, bytes([0xf4, b]))
        time.sleep(0.05)

#PROGRAM_SIZE = 256
#ERASE_SIZE = 4096
#
#def read_status_register():
#    return transfer_cmd(b'\x05\x00')[1]
#
#def write_enable():
#    transfer_cmd(b'\x06')
#
#def page_program(addr, data):
#    transfer_cmd(b'\x02' + addr.to_bytes(3, 'big') + data)
#
#def sector_erase(addr):
#    transfer_cmd(b'\x20' + addr.to_bytes(3, 'big'))
#
#def write_stream(addr, stream):
#    assert addr & (ERASE_SIZE - 1) == 0
#
#    while True:
#        data = stream.read(PROGRAM_SIZE)
#
#        if not data:
#            break
#        
#        if addr & (ERASE_SIZE - 1) == 0:
#            write_enable()
#            sector_erase(addr)
#
#            while read_status_register() & 1:
#                pass
#
#            print(f'Erased addr {addr}.')
#
#        write_enable()
#        page_program(addr, data)
#
#        while read_status_register() & 1:
#            pass
#
#        print(f'Wrote {len(data)} bytes.')
#
#        addr += len(data)
#
#def main():
#    with open(sys.argv[1], 'rb') as f:
#        write_stream(0, f)
#
#if __name__ == '__main__':
#    main()
