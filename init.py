#!/usr/bin/env python

def binary(num, pre='0b', length=8, spacer=0):
    return '{0}{{:{1}>{2}}}'.format(pre, spacer, length).format(bin(num)[2:])

from smbus import SMBus
b = SMBus(1)

addr = 0x66


ret = b.read_i2c_block_data(addr, 0x81)
for i in range(0, 8):
	print (binary(ret[i]))

#b.write_i2c_block_data(addr,0x88,[0xFF, 0xFF, 0x33, 0x00, 0x00, 0x00, 0x0F])
