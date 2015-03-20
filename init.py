#!/usr/bin/env python
 
###
# CONFIGURATION
###

I2CDEV = 1 		# /dev/i2c-1
I2CADDR = 0x62 	# i2cdetect


# SET MOTOR PARAM
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
INIT_DRIVE = False

# CONFIGURATION END #

from smbus import SMBus
from time import sleep
from os import system
import RPi.GPIO as GPIO
import threading


b = SMBus(I2CDEV)
#flash light
pin = 13

button = 31

green = 33
red = 35
yellow = 37

#returns string, not integer
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
def capture(a,i):
	system("uvccapture -v -S45 -B80 -C42 -G5 -x640 -y480 -ocaptures/cap{:02}.jpg".format(i))

def mountUSB():
	system("mount -t vfat -o utf8,uid=pi,gid=pi,noatime /dev/sda1 /media/usbstick")

def umountUSB():
	system("umount /media/usbstick")

def copyToUSB():
	mountUSB()
	system("mkdir /media/usbstick/captures")
	system("cp captures/*.jpg /media/usbstick/captures/")
	system("rm captures/*.jpg")
	#system("cp merge.jpg /media/usbstick/")
	umountUSB()

def mergeImages():
	GPIO.output(green, GPIO.HIGH)
	print("Merging")
	system("convert +append captures/cap*.jpg merge.jpg")
    
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
       

def photoLogic():
	# First Error Check
	if checkErrors():
		GPIO.output(red, GPIO.HIGH)
		GPIO.output(yellow, GPIO.LOW)
		GPIO.output(green, GPIO.LOW)
		while True:
			if GPIO.input(button) == 1:
				return
			
	GPIO.output(yellow, GPIO.LOW)
	GPIO.output(red, GPIO.LOW)
	GPIO.output(green, GPIO.HIGH)
	
	while True:
		if GPIO.input(button) == 1:
			GPIO.output(green, GPIO.LOW)
			break
			
	# Second Error Check after initial waiting phase
	if checkErrors():
		GPIO.output(red, GPIO.HIGH)
		GPIO.output(yellow, GPIO.LOW)
		GPIO.output(green, GPIO.LOW)
		while True:
			if GPIO.input(button) == 1:
				return
			
	GPIO.output(yellow, GPIO.HIGH)
		
	system("v4l2-ctl --set-ctrl exposure_auto=1")
	system("v4l2-ctl --set-ctrl exposure_auto_priority=0")
	system("v4l2-ctl --set-ctrl exposure_absolute=300")

	sleep(.3)
	
	# setting motor parameter to configured values
	setMotorParam()

	# sets the internal position counter to 0
	resetPosition()

	# curPos should be 0
	curPos = 0
	sleep(2)
	# rotate and take pictures
	capture(1,0)
	for i in range (0,90):
	
		print (i)  
		while True:
			if GPIO.input(button) == 1:
				copyToUSB()
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
			
				print(tmcPos)
				sleep(.8)
				#system("gphoto2 --capture-image")
				#sleep(.7)
				#system("mv capt0000.jpg captures/c{:02}.jpg".format(i))
				# CAPTURE
				#t = threading.Thread(target=capture, args = (1,i))
				#t.daemon = True
				#t.start()
				GPIO.output(pin,GPIO.HIGH)
				# FLASH
				capture(1,i)

			
				GPIO.output(pin,GPIO.LOW)
				curPos = curPos + 35
				setPosition(curPos)
				break
	#mergeImages()
	copyToUSB()
	print ('#################################################################\n')           
	print("Done")                
	print ('#################################################################\n')

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
