#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


# Program Spec
# knob_reader.py opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected potentiometer
# every second and commits the reading to the specified database
# with an abrieviated timestamp.

# Program setup requirements
# - Connect the rotary angular sensor (potentiometer) to port A2

# Program UI
# - A time accompanied by its corresponding reading will print to
#   console every second.
# - Twist the potentiometer and observe the real-time data
# - End program using the ctrl+c



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime

#connect to MySQLdb
#                    <host>       <MySQL user>     <pwrd>    <db_name>
db=MySQLdb.connect("localhost", "potentiometer", "tcss499", "lab2")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the Rotary Angle Sensor to analog port A2
potentiometer = 2

# stall the first data-read
time.sleep(1)

# the operational loop
while True:
	try:
        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current potentiometer reading
		currentRead = grovepi.analogRead(potentiometer)
		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), currentRead))

        	
        	# create the MySQL INSERT INTO statement
		insert_stmt = (
            		"INSERT INTO knob_readings (rtime, reading) "
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
	
	# stop the program
	except KeyboardInterrupt:
		db.close()
		break

	# error logging
	except IOError:
		print("Error")
