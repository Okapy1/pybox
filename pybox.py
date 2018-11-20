#!/usr/bin/env python
# -*- coding: utf8 -*-

'''
PyBox plays video files from RFID card
using Raspberry Pi, MFRC522 module and OMXPlayer
'''

# Import libraries
import RPi.GPIO as GPIO
import MFRC522
import signal
import subprocess
from time import sleep

# RGB pin mapping
rgb_red = 16
rgb_green = 21
rgb_blue = 20
rgb = [rgb_red, rgb_green, rgb_blue]

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in rgb:
	GPIO.setup(pin, GPIO.OUT)

# RFID cards
cards = [[9, 213, 179, 14],
		[169, 147, 84, 60],
		[205, 213, 84, 60],
		[90, 8, 85, 60]]
parent_token = [[219, 58, 149, 133],]


# Clear all existing color values
def rgb_clear():
	for pin in rgb:
		GPIO.output(pin, 0)

# Control RGB
def switch_rgb(color = 'off'):
	if color == 'off':
		rgb_clear()
	elif color in rgb:
		rgb_clear()
		GPIO.output(color, 1)
	else:
		print("led error")
	print("led {}".format(color))


# Acces parental mode
parent_access = False

# Continue reading rfid
rfid_continue_reading = True


# Read rfid card
def read_rfid(card):
	global parent_access
	if card in parent_token:
		print("token recognized - parental access granted")
		parent_access = True
		switch_rgb(rgb_blue)
	elif card in cards:
		print("card recognized : {}".format(card))
		if parent_access:
			print("playback allowed")
			switch_rgb(rgb_green)
			# play_video('test.h264')
		else:
			print("playback not allowed")
			switch_rgb('off')
		# Reset parent access for playing only 1 video each time
		# parent_access = False
	else:
		print("card unrecognized")
		switch_rgb(rgb_red)
		parent_access = False
		
	sleep(3)
	switch_rgb('off')



# Video player
def play_video(filename):
	# /opt/vc/src/hello_pi/hello_video/test.h264
	# /home/pi/Videos/test.h264
	path = '/opt/vc/src/hello_pi/hello_video/' + filename
	command = ['omxplayer', path]
	print(command)
	print("Playing video") 
	subprocess.call(command)
	print("End of video")


# Stop reading properly
def rfid_end_read(signal,frame):
	print ("End of RFID reading")
	# stop the while loop and turn off the pins (led and rfid)
	rfid_continue_reading = False
	GPIO.cleanup()


# Initialize rfid reader
signal.signal(signal.SIGINT, rfid_end_read)
MIFAREReader = MFRC522.MFRC522()

print("Waiting for rfid card")
print("CTRL + C to stop")


while rfid_continue_reading:
	# Detecting rfid tag
	(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

	# A tag is detected
	if status == MIFAREReader.MI_OK:
		print("------------------------")
		print("A card has been detected")

	# Collect UID
	(status,uid) = MIFAREReader.MFRC522_Anticoll()

	# Read UID
	if len(uid[:4]) > 0:
		if parent_access:
			# print ("UID de la carte : "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3]))
			print("UID : {}".format(uid[:4]))
		read_rfid(uid[:4])

	# Set parental access OFF
	# parent_access = False
	

'''
	# Default authentification key
	key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
	
	# Select tag
	MIFAREReader.MFRC522_SelectTag(uid)

	# Authentification
	status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

	if status == MIFAREReader.MI_OK:
		MIFAREReader.MFRC522_Read(8)
		MIFAREReader.MFRC522_StopCrypto1()
	else:
		print ("Authentification error")
'''