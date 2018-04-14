#!/usr/bin/python

# TCSS499 Research Group
# University of Washington, Tacoma
# Enabling learning through hands on experience with Raspberri Pi
# Contributors: Michael Quandt, 
# See references in parent project 'Define and Populate' lab


# Program Spec
# soundmonitor.py opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected sound monitor
# every second and commits that data to the specified database
# with an abrieviated timestamp.

# Program setup requirements
# - Connect the sound monitor to port A2

# Program UI
# - A time accompanied by its corresponding reading will print to
#   console every second.
# - Observe the raw reading produce from the sound monitor (not DBs)
# - End program using the ctrl+c



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime

#connect to MySQLdb
#                    <host>       <MySQL user>     <pwrd>    <db_name>
db=MySQLdb.connect("localhost", "soundmonitor", "tcss499", "soundlevels")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the sound monitor to analog port A2
soundmonitor = 2

# stall the first data-read
time.sleep(1)

# the operational loop
while True:
	try:
        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current soundmonitor reading
		currentRead = grovepi.analogRead(soundmonitor)
		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), currentRead))

        	
        	# create the MySQL INSERT INTO statement
		insert_stmt = (
            		"INSERT INTO soundleveltime (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	data = (localtime.strftime('%H:%M:%S'), currentRead)
		
		# save the current readings to the database
        	try:
            		cursor.execute(insert_stmt, data)
            		db.commit()
        	except:
            		db.rollback()
		
		# stall to limit one reading each second
		time.sleep(1)
	
	# error logging
	except IOError:
		print("Error")
