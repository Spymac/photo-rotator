#!/usr/bin/env python

from smbus import SMBus
b = SMBus(1)

addr = 0x62


#ret = b.read_i2c_block_data(addr, 0x81)
#print (ret)

b.write_i2c_block_data(addr,0x88,[0xFF, 0xFF, 0x33, 0x00, 0x00, 0x00, 0x0F])
