#!/usr/bin/python

# TCSS499 Research Group
# University of Washington, Tacoma
# Enabling learning through hands on experience with Raspberri Pi
# Contributors: Michael Quandt, 
# See references in parent project 'Define and Populate' lab


# Program Spec
# sc1.py opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected sound monitor
# and potentiometer every second and commits that data to the 
# specified database with an abrieviated timestamp.

# Program setup requirements
# - Connect the sound monitor to port A1
# - Connect the potentiometer to port A2
# - Connect the LED to port D4

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - Observe the raw readings produce from the sound monitor (not DBs)
# - End program using the ctrl+c



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime

#connect to MySQLdb
#                    <host>      <MySQL user>   <pwrd>  <db_name>
db=MySQLdb.connect("localhost", "sc1program", "tcss499", "sc1")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the sound monitor to analog port A1
soundmonitor = 1
# Connect the potentiometer to analog port A2
potentiometer = 2

# Connect the LED to analog port A2
led = 5
grovepi.pinMode(led,"OUTPUT")

# stall the first data-read
time.sleep(1)

# the operational loop
while True:
	try:
        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current soundmonitor reading
		current_noise = grovepi.analogRead(soundmonitor)
		# store the current 'wind speed'
		current_wind = grovepi.analogRead(potentiometer)

		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), current_noise))
		print('Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), current_wind))
        	
        	# create the MySQL INSERT INTO statement
		insert_noise = (
            		"INSERT INTO micreads (rtime, reading) "
            		"VALUES (%s, %s)"
        	)

		# create the MySQL INSERT INTO statement
		insert_wind = (
            		"INSERT INTO windspeeds (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	data_noise = (localtime.strftime('%H:%M:%S'), current_noise)
		data_wind = (localtime.strftime('%H:%M:%S'), current_wind)
		
		# save the current readings to the database
        	try:
            		cursor.execute(insert_noise, data_noise)
			cursor.execute(insert_wind, data_wind)
            		db.commit()
        	except:
            		db.rollback()
		
		# stall to limit one reading each second
		time.sleep(1)
	
	# error logging
	except IOError:
		print("Error")
