#!/usr/bin/env python

import signal
import time
import sys
import gi
import sqlite3

from pirc522 import RFID
from datetime import datetime

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
def checkout(card,comtek):
	#associate card and comtek with a date
	time = datetime.today()
db = sqlite3.connect("comteks.db")
c = db.cursor()

print("Starting...")
run = True
while run:
	print("Scan card...")
	card_type = 0
	card = card_data()
	uid = card[0]

	#find the uid in users or comtek table

	c.execute("select * from comteks where uid=?", [uid])
	row = c.fetchone()
	if row  == None:
		print("Looking for User ID")
		c.execute("select * from users where uid=?", [uid])
		row = c.fetchone()
		if row:
			print("you scanned a ID card")
			card_type = 1

	else:
		print("You scanned a comtek!")
		card_type = 2
	if row == None:
		print("Couldnt find card..")
	else:
		print(row)
	time.sleep(1)

	if card_type == 1: #scan comtek to checkout
		print "Finding records for: ",row[1]
		comtek = card_data()
		uid = comtek[0]
		c.execute("select * from comteks where uid=?", [uid])
		row = c.fetchone()
		print(row)
		c.execute("update comteks set out='Y' where uid=?",[uid])
	if card_type == 2:
		print "checking in comtek #: ",row[2]
		#user = card_data()
		c.execute("update comteks set out='N' where uid=?",[uid])
		#uid = user[0]
	db.commit()
	c.execute("select * from comteks where out='Y'")
	print("Done, the following comteks are out..")
	for row in c.fetchall():
		print(row)
	
	#restart
db.close()


rdr.cleanup()
sys.exit()
