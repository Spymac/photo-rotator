#!/usr/bin/env python
 
###
# CONFIGURATION
###

I2CDEV = 1 		# /dev/i2c-1
I2CADDR = 0x66 	# i2cdetect


# SET MOTOR PARAM
lRun  	= 0xA 	# run current
lHold 	= 0xA 	# hold current

vMax 	= 0xF   # velocity Max (0-F)
vMin 	= 0xA 	# velocity Min (0-F)

secPos 	= 0x000 # 11 Bit
shaft 	= False # Motor turn direction (Boolean)
accel 	= 0x4   # Acceleration (3 Bit)


accelShape = True # Acceleration Shape (Boolean)
stepMode   = 0x0  # half stepping, etc (0-3)

# Initialization Drive
targetPos1 = 0x8FFF
targetPos2 = 0x000F


def binary(num, pre='0b', length=8, spacer=0):
    return '{0}{{:{1}>{2}}}'.format(pre, spacer, length).format(bin(num)[2:])
 

from smbus import SMBus
b = SMBus(I2CDEV)
 

 
 
# GETFULLSTATUS 1
print ("GETFULLSTATUS 1:\n")
ret = b.read_i2c_block_data(I2CADDR, 0x81)
for i in range(1, 8):
	print (binary(ret[i]))
 
# GETFULLSTATUS 2
print ("\nACTUAL POS:\n")
 
ret = b.read_i2c_block_data(I2CADDR, 0xFC)
for i in range(1, 3):
	print (binary(ret[i]))
 
# SETMOTORPARAM
'''
b.write_i2c_block_data(I2CADDR,0x89,[
	0xFF, 0xFF, 
	(lRun << 4) + lHold,
	(vMax << 4) + vMin,
	(((((secPos >> 8) & 0b0111) << 1) + shaft) << 4) + accel,
	secPos & 0b000011111111,
	(accelShape << 4) + (stepMode << 2)])
'''
 
'''
# Position Init
b.write_i2c_block_data(I2CADDR,0x88,[
		0xFF, 0xFF, 
		(vMax << 4) + vMin,
		targetPos1 >> 8, targetPos1 & 0x00FF, targetPos2 >> 8, targetPos2 & 0x00FF])
'''
# SETPOSITION: 0x0000
b.write_i2c_block_data(I2CADDR,0x8B,[
		0xFF, 0xFF, 
		0x00, 
		0x00])