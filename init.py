#!/usr/bin/env python
 
###
# CONFIGURATION
###
# I2C address and device
I2CDEV = 1 	# /dev/i2c-1
I2CADDR = 0x62 	# i2cdetect

# MOTOR PARAMETERS
lRun  	= 0xF 	# run current
lHold 	= 0xF 	# hold current

vMax 	= 0x1   # velocity Max (0-F)
vMin 	= 0x1 	# velocity Min (0-F)

secPos = 0x000 # 11 Bit 0-4FF (0x400 = -1024; 0x3ff = 1023)
shaft 	= False # Motor turn direction (Boolean)
accel 	= 0x9   # Acceleration (3 Bit)


accelShape = True # Acceleration Shape (Boolean)
stepMode   = 0x0  # half stepping, etc 2 Bit (0-3)

# Initialization drive
targetPos1 = 0x8FFF
targetPos2 = 0x000F

WRITE_RAM_ON_STARTUP = True
# No init drive, position will be reset to 0 on start
INIT_DRIVE = False

# CONFIGURATION END #

from smbus import SMBus
from time import sleep
from os import system
from os import path
import RPi.GPIO as GPIO


b = SMBus(I2CDEV)

# GPIO pin layout
pin = 13
button = 31
green = 33
red = 35
yellow = 37

# debug and convenience function, format to binary string
def binary(num, pre='0b', length=8, spacer=0):
    return '{0}{{:{1}>{2}}}'.format(pre, spacer, length).format(bin(num)[2:])
# check for negative: most significant bit == 1
def isNegative(v):
    return bool(v >> 15 == 1)
# set Bit at offset
def setBit(int_type, offset):
    return(int_type | (1 << offset))
# splits one 2 byte number in two 1 Byte numbers
def getPositionBytes(newPosition):
    if newPosition < 0:
        print("Negative position values not supported.")
    else:
        if newPosition >= 32767:
            newPosition = 32767
			
    return [newPosition >> 8, newPosition & 0x00ff]
# sets motor position at newPosition
def setPosition(newPosition):
    positionByte = getPositionBytes(newPosition)
    b.write_i2c_block_data(I2CADDR,0x8B,[0xFF, 0xFF, positionByte[0], positionByte[1]])
# returns current motor position
def getPosition():
    ret = b.read_i2c_block_data(I2CADDR, 0xFC)
    return (ret[1] << 8) + ret[2]
# resets current position to 0, no motor movement
def resetPosition():
    b.write_byte(I2CADDR, 0x86)
# not used here, implemented for completion	
def hardStop():
    b.write_byte(I2CADDR, 0x85)
# not used here, implemented for completion
def gotoSecurePosition():
    b.write_byte(I2CADDR, 0x84)
# initializes board and returns complete status of chip
def getFullStatus1():
    ret = b.read_i2c_block_data(I2CADDR, 0x81)
    return ret    
# return actual, target and secure position
def getFullStatus2():
    ret = b.read_i2c_block_data(I2CADDR, 0xFC)
    return ret
# set motor parameters defined in configuration on top of this file
def setMotorParam():
    if WRITE_RAM_ON_STARTUP:
        b.write_i2c_block_data(I2CADDR,0x89,[0xFF, 0xFF, (lRun << 4) + lHold, (vMax << 4) + vMin, (((((secPos >> 8) & 0b0111) << 1) + shaft) << 4) + accel, secPos & 0b000011111111, (accelShape << 4) + (stepMode << 2)])
# initialization drive, not used here because position is reset at start
def positionInit():
    if INIT_DRIVE:
        b.write_i2c_block_data(I2CADDR,0x88,[0xFF, 0xFF,  (vMax << 4) + vMin, targetPos1 >> 8, targetPos1 & 0x00FF, targetPos2 >> 8, targetPos2 & 0x00FF])
# captures one image
def capture(a,i):
	system("uvccapture -v -S45 -B80 -C42 -G5 -x640 -y480 -ocaptures/cap{:02}.jpg".format(i))
# mounts USB device
def mountUSB():
	system("mount -t vfat -o utf8,uid=pi,gid=pi,noatime /dev/sda1 /media/usbstick 2> /dev/null")
# unmounts USB device
def umountUSB():
	system("umount /media/usbstick")
# checks if USB device is mounted
def checkUSB():
	if path.ismount("/media/usbstick"):
		return True
	else:
		GPIO.output(red, GPIO.HIGH) 
		return False	
# copies all images to USB device and deletes images on internal storage
def copyToUSB():
	mountUSB()
	if checkUSB():
		system("mkdir /media/usbstick/captures")
		system("mkdir /media/usbstick/web")
		system("cp captures/*.jpg /media/usbstick/captures/")
		system("cp html/* /media/usbstick/web/")
		system("rm captures/*.jpg")
		umountUSB()
		return True
	else:
		return False
# not used anymore, merges images horizontaly
def mergeImages():
	GPIO.output(green, GPIO.HIGH)
	print("Merging")
	system("convert +append captures/cap*.jpg merge.jpg")
# checks for errors from the stepper driver
def checkErrors():
	try:
		ret = getFullStatus1()
		errorlist1 = ['VddReset', 'StepLoss', 'ElDef' , 'UV2', 'TSD', 'TW', 'Tinfo: Warning Very High Temperature', 'Tinfo: Warning High Temperature']
		errorlist2 = ['OVC1', 'OVC2' , 'unknown' , 'CPFAIL']
		errors = []
		for i in range(4,6):
			errors.append(binary(ret[i]))   
		for i in range(2,10):
			if errors[0][i] == str(1) and errors[0][i+1] == str(1) and i == 6:
				print ('Error: Motor Shutdown, High Temperature')
				return True
			elif errors[0][i] == str(1):
				print ('Error'), errorlist1[i-2]    
				return True   
		for l in range(6,10):
			if errors[1][l] == str(1) and l-6 != 2:
				print ('Error'), errorlist2[l-6]
				return True
    		return False     
	except:
		return True
       
# main program logic
def photoLogic():
	# First Error Check
	if checkErrors():
		GPIO.output(red, GPIO.HIGH)
		GPIO.output(yellow, GPIO.LOW)
		GPIO.output(green, GPIO.LOW)
		while True:
			if GPIO.input(button) == 1:
				return
	# Check if USB is mounted if not return wait for Button press
	mountUSB()
	if not checkUSB():
		return

	umountUSB()
		
	# ALL IS READY, SET LED GREEN
	GPIO.output(yellow, GPIO.LOW)
	GPIO.output(red, GPIO.LOW)
	GPIO.output(green, GPIO.HIGH)
	

	# Waiting for button start press
	while True:
		if GPIO.input(button) == 1:
			GPIO.output(green, GPIO.LOW)
			break
			
	# Second error check after initial waiting phase
	if checkErrors():
		GPIO.output(red, GPIO.HIGH)
		GPIO.output(yellow, GPIO.LOW)
		GPIO.output(green, GPIO.LOW)
		while True:
			if GPIO.input(button) == 1:
				return
	
	# Second error check, if USB is mounted
	mountUSB()
	if not checkUSB():
		return
	umountUSB()
		
	GPIO.output(yellow, GPIO.HIGH)
	
	# Setting camera exposure
	system("v4l2-ctl --set-ctrl exposure_auto=1")
	system("v4l2-ctl --set-ctrl exposure_auto_priority=0")
	system("v4l2-ctl --set-ctrl exposure_absolute=300")

	sleep(.3)
	
	# Setting motor parameter to configured values
	setMotorParam()

	# Sets the internal position counter to 0
	resetPosition()

	# curPos should be 0
	curPos = 0
	sleep(2)
	# rotate and take pictures
	# one initial capture to activate exposure settings
	capture(1,0)
	for i in range (0,90):
	
		print (i)  
		while True:
			# check for abort button
			if GPIO.input(button) == 1:
				if not copyToUSB():
					GPIO.output(red,GPIO.HIGH)
					return 
				GPIO.output(yellow, GPIO.LOW)
				GPIO.output(red, GPIO.HIGH)
				sleep(.4)
				GPIO.output(yellow, GPIO.LOW)
				GPIO.output(green, GPIO.HIGH)
				sleep(2.5)
				GPIO.output(red, GPIO.LOW)
				return 
			
			tmcPos = getPosition()
			if checkErrors():
				GPIO.output(red, GPIO.HIGH)
				GPIO.output(yellow, GPIO.LOW)
				while True:
					if GPIO.input(button) == 1:
						return
			if abs(tmcPos-curPos) < 1:
				# desired position is reached
				print(tmcPos)
				sleep(.8)
				
				# TURN FLASH ON
				GPIO.output(pin,GPIO.HIGH)
				# Capture image i
				capture(1,i)
				# TURN FLASH OFF
				GPIO.output(pin,GPIO.LOW)
				
				# Seek next position
				curPos = curPos + 36
				setPosition(curPos)
				break
	# copy images after all shots
	copyToUSB()
	print ('#################################################################\n')           
	print("Done")                
	print ('#################################################################\n')
	return

#MAIN 
if __name__ == "__main__":
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.setup(button,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(green, GPIO.OUT)
	GPIO.setup(red, GPIO.OUT)
	GPIO.setup(yellow, GPIO.OUT)
	while True:
		photoLogic()	
