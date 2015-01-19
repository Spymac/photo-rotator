#!/usr/bin/env python

from smbus import SMBus
b = SMBus(1)

addr = 0x62


ret = b.read_i2c_block_data(addr, 0x81)

print [map(hex, l) for l in ret]
