#!/usr/bin/env python

import signal
import time
import sys
import gi
from pirc522 import RFID


rdr = RFID()
util = rdr.util()
util.debug = False

userCards = []
def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()
def shortuid(uid):
	strUid = ""
	for i in uid:
		strUid += str(i)
	return strUid

def tochar (bytes):
	newString = ''
	for b in bytes:
		c = chr(b)
		newString+= c
	return newString

signal.signal(signal.SIGINT, end_read)

print("Starting")
print("Scan card...")
def card_data():
	run=True
	while run:
    		rdr.set_antenna_gain(7)
		rdr.wait_for_tag()

    		(error, data) = rdr.request()
    		if error:
			continue
        	#print("\nDetected: " + format(data, "02x"))

	    	(error, uid) = rdr.anticoll()
    		if not error:
        		print("Card read UID: " + shortuid(uid))

        		#print("Setting tag")
        		util.set_tag(uid)
        		#print("\nAuthorizing")
        		#util.auth(rdr.auth_a, [0x12, 0x34, 0x56, 0x78, 0x96, 0x92])
        		util.auth(rdr.auth_a, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        		#print("\nReading")
			util.do_auth(1)
        		(rerror, data1) = rdr.read(1)
			if rerror:
				continue	
			print(tochar(data1))
			util.do_auth(2)
			(rerror,data2) = rdr.read(2)
			if rerror:
				continue
			print(tochar(data2))

        		#print("\nDeauthorizing")
			util.deauth()

			return(shortuid(uid),data1,data2)
        		#time.sleep(1)
# get user card
card = card_data()
time.sleep(1)
print("Scan comtek...")
comtek = card_data()
time.sleep(1)
while 1:
	input = raw_input("More?..y/n")
	if input == 'y':
		print("Scan comtek..")
		comtek = card_data()
		time.sleep(1)
		continue
	if input == 'n':
		break
rdr.cleanup()
sys.exit()
