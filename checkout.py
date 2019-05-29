#!/usr/bin/env python

import signal
import time
import sys
import gi
import sqlite3

from pirc522 import RFID
from datetime import datetime
from RPLCD.i2c import CharLCD

rdr = RFID()
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, cols=8, rows=2)
util = rdr.util()
util.debug = False

userCards = []
def end_read(signal,frame):

    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    lcd.clear()
    lcd.write_string('Not Running')
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
def write_stats(c):
	global lcd
	c.execute("select * from comteks where out='Y'",[])
	rows = c.fetchall()
	count = str(len(rows))
	drawer = str(20 - len(rows))
	lcd.clear()
	lcd.cursor_pos = (0,0)
	lcd.write_string("Out:" + count)
	lcd.cursor_pos = (1,0)
	lcd.write_string("In:" + drawer)
	#time.sleep(.5)
	#lcd.cursor_pos = (1,0)
	#lcd.write_string("")

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
db = sqlite3.connect("/home/pi/comteks/comteks.db")
c = db.cursor()
run = True
print("Starting")
lcd.clear()
while run:
	write_stats(c)
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
		if row[3] == 'Y':
			print"comtek #",row[2]," is beimg returned"
			c.execute("update comteks set out='N' where uid=?",[uid])
			lcd.cursor_pos = (0,0)
			lcd.write_string("Return#: " + str(row[2] + "     "))
			time.sleep(.5)
			write_stats(c)
			db.commit()
		else:
			print"Checkout comtek #:",row[2]
			c.execute("update comteks set out='Y' where uid=?", [uid])
			lcd.clear()
			lcd.cursor_pos = (0,0)
			lcd.write_string("Checkout: " + str(row[2]))
			time.sleep(.5)
			write_stats(c)
			db.commit()
		card_type = 2
	c.execute("select * from comteks where out='Y'")
	print("Done, the following comteks are out..")
	for row in c.fetchall():
		print(row)
	time.sleep(1)
#restart
db.close()


rdr.cleanup()
sys.exit()
