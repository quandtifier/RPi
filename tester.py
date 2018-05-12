#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma






# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime

#connect to MySQLdb
#                    <host>       <MySQL user>     <pwrd>    <db_name>
db=MySQLdb.connect("localhost", "root", "tcss499", "tester")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the Rotary Angle Sensor to analog port A2
potentiometer = 2

# stall the first data-read
time.sleep(1)

def do_insert(sql,data):
	# save the current readings to the database
        try:
		print(sql)
		print(data)
            	cursor.execute(sql, data)
            	db.commit()
        except:
            	db.rollback()

def insert_into(table,values):
	# create the MySQL INSERT INTO statement
	insert_stmt = (
	"INSERT INTO sample (rtime, reading) "
	"VALUES (%s, %s)"
	)
	# store the data which corresponds to the '%s' in VALUES clause
        data = (values[0].strftime('%H:%M:%S'), values[1])
	do_insert(insert_stmt, data)
	
# the operational loop
while True:
	try:
        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current potentiometer reading
		currentRead = grovepi.analogRead(potentiometer)
		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), currentRead))

        	insert_into("sample",[localtime, currentRead])
  
		# stall to limit one reading each second
		time.sleep(1)
	
	# stop the program
	except KeyboardInterrupt:
		db.close()
		break

	# error logging
	except IOError:
		print("Error")



