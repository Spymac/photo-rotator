#!/usr/bin/env python
 
def binary(num, pre='0b', length=8, spacer=0):
    return '{0}{{:{1}>{2}}}'.format(pre, spacer, length).format(bin(num)[2:])
 
from smbus import SMBus
b = SMBus(1)
 
addr = 0x66
 
 
# GETFULLSTATUS 1
print ("GETFULLSTATUS 1:\n")
ret = b.read_i2c_block_data(addr, 0x81)
for i in range(1, 8):
	print (binary(ret[i]))
 
# GETFULLSTATUS 2
print ("\nACTUAL POS:\n")
 
ret = b.read_i2c_block_data(addr, 0xFC)
for i in range(1, 3):
	print (binary(ret[i]))
 
# SETMOTORPARAM
'''
b.write_i2c_block_data(addr,0x89,[
	0xFF, 0xFF, 
	0xAA, #lRun, lHold 
	0xFA, #VMAX VMIN
	0x04, #SECPOS, SHAFT, ACC
	0x00, #SECPOS 7:0
	0x10]) #ACCSHAPE, STEPPING MODE
'''
 
'''
b.write_i2c_block_data(addr,0x88,[
		0xFF, 0xFF, 
		0x4A, # VMAX, VMIN
		0x8F, 0xFF, 0x00, 0x0F])
'''
# SETPOSITION: 0x0000
b.write_i2c_block_data(addr,0x8B,[
		0xFF, 0xFF, 
		0x00, 
		0x00])