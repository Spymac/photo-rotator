#!/usr/bin/env python
 
###
# CONFIGURATION
###

I2CDEV = 1 		# /dev/i2c-1
I2CADDR = 0x66 	# i2cdetect


# SET MOTOR PARAM
lRun  	= 0xF 	# run current
lHold 	= 0xF 	# hold current

vMax 	= 0xF   # velocity Max (0-F)
vMin 	= 0x3 	# velocity Min (0-F)

secPos 	= 0x000 # 11 Bit 0-4FF (0x400 = -1024; 0x3ff = 1023)
shaft 	= False # Motor turn direction (Boolean)
accel 	= 0x4   # Acceleration (3 Bit)


accelShape = False # Acceleration Shape (Boolean)
stepMode   = 0x0  # half stepping, etc 2 Bit (0-3)

# Initialization drive
targetPos1 = 0x8FFF
targetPos2 = 0x000F

WRITE_RAM_ON_STARTUP = True
INIT_DRIVE = False

# CONFIGURATION END #

from smbus import SMBus
from time import sleep
from os import system

b = SMBus(I2CDEV)

def binary(num, pre='0b', length=8, spacer=0):
    return '{0}{{:{1}>{2}}}'.format(pre, spacer, length).format(bin(num)[2:])
 
def isNegative(v):
    return bool(v >> 15 == 1)

def setBit(int_type, offset):
    return(int_type | (1 << offset))

def getPositionBytes(newPosition):
    if newPosition < 0:
        print("Negative position values not supported.")
    else:
        if newPosition >= 32767:
            newPosition = 32767
			
    return [newPosition >> 8, newPosition & 0x00ff]

def setPosition(newPosition):
    positionByte = getPositionBytes(newPosition)
    b.write_i2c_block_data(I2CADDR,0x8B,[0xFF, 0xFF, positionByte[0], positionByte[1]])

def getPosition():
    ret = b.read_i2c_block_data(I2CADDR, 0xFC)
    return (ret[1] << 8) + ret[2]

def resetPosition():
    b.write_byte(I2CADDR, 0x86)
	
def hardStop():
    b.write_byte(I2CADDR, 0x85)

def gotoSecurePosition():
    b.write_byte(I2CADDR, 0x84)

def getFullStatus1():
    ret = b.read_i2c_block_data(I2CADDR, 0x81)
    return ret    

def getFullStatus2():
    ret = b.read_i2c_block_data(I2CADDR, 0xFC)
    return ret
    
def setMotorParam():
    if WRITE_RAM_ON_STARTUP:
        b.write_i2c_block_data(I2CADDR,0x89,[0xFF, 0xFF, (lRun << 4) + lHold, (vMax << 4) + vMin, (((((secPos >> 8) & 0b0111) << 1) + shaft) << 4) + accel, secPos & 0b000011111111, (accelShape << 4) + (stepMode << 2)])

def positionInit():
    if INIT_DRIVE:
        b.write_i2c_block_data(I2CADDR,0x88,[0xFF, 0xFF,  (vMax << 4) + vMin, targetPos1 >> 8, targetPos1 & 0x00FF, targetPos2 >> 8, targetPos2 & 0x00FF])
  
# not done      
def checkError():
    pass
    #ret1 = getFullStatus1()
    #ret2 = getFullStatus2()
    

#MAIN 
if __name__ == "__main__":
    
    # GETFULLSTATUS 1
    print ("GETFULLSTATUS 1:\n")
    ret = getFullStatus1()    
    for i in range(1, 8):
        print (binary(ret[i]))
        
    # setting motor parameter to configured values
    setMotorParam()
    
    # sets the internal position counter to 0
    resetPosition()
    sleep(2)
    
    # curPos should be 0
    curPos = getPosition()
    
    # rotate and take pictures
    for i in range (0,90):
        curPos = curPos + 35
        setPosition(curPos)
        print (i)
        while True:
             tmcPos = getPosition()
             print(tmcPos)
             if abs(tmcPos-curPos) < 2:
                 system("uvccapture -v -S45 -B190 -C35 -G50 -x640 -y480 -otest/test{:02}.jpg".format(i))
                 break
	
