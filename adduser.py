#/usr/bin/python

import sys
import time
import signal
import pirc522
import sqlite3

from pirc522 import RFID

run = True
rdr = RFID()
util = rdr.util()
util.debug = False
rdr.set_antenna_gain(7)

def end_run(signal,frame):
	global run
	run = False
	rdr.cleanup
	sys.exit()
def toints(strdata):
	ints = []
	for c in strdata:
		cint =  ord(c)
		ints.append(cint)
	return ints
def insertRow(uid, name, phone):
	db = sqlite3.connect("comteks.db")
	c = db.cursor()
	c.execute("insert into users values (?, ?, ?, 'N')", (uid, name, phone))
	db.commit()
	db.close()
def shortuid(uid):
        strUid = ""
        for i in uid:
                strUid += str(i)
        return strUid
	
signal.signal(signal.SIGINT, end_run)

print("create new ID card")
def scanTag(name,phone):
	run = True
	while run:
		
		rdr.wait_for_tag()
		(error, data) = rdr.request()
		if not error:
			print("card detected: " + format(data, "02x"))
		else:
			print(error)
		(error, uid) = rdr.anticoll()
		if not error:
			print("using card: " + str(uid[1:3]))
			util.set_tag(uid)

			util.auth(rdr.auth_b, [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
			#util.read_out(1)
			#util.do_auth(1)
			if util.rewrite(1,toints(name)):
				continue
			#util.do_auth(2)
			#util.read_out(2)
			if util.rewrite(2,toints(phone)):
				continue
			run = False
			return uid
run = True
while run:
	print("create new ID card")  
	print("Enter Name")
	name = raw_input("Full Name:")

	print("Enter new phone number")
	phone = raw_input("Phone #")

	print("Hold new card to scanner")
	print("Adding to database..")
	uid = scanTag(name, phone)
	insertRow(shortuid(uid),name,phone)
	if raw_input("Add new ID card..? y/n:") == 'n':
		run = False
db = sqlite3.connect("comteks.db")
c = db.cursor()
c.execute("select * from comteks")
rows = c.fetchall()
print("DB now contains...")
print(rows)

db.close()

print("cleaning uup")
util.deauth()
rdr.cleanup()
sys.exit()
