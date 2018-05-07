#!/usr/bin/python

#################################### NOTES AND BUGS ######################################
# BUG 1: Program waits for 2 seconds between readings although it appears that the code specs otherwise


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


# Program Spec
# temp_humid_reader.py opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected Grove Temperature and 
# Humidity sensor every second and commits the readings to the specified database
# with an abrieviated timestamp.

# Program setup requirements
# - Connect the Grove Temperature and Humidity Sensor to Port A1

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - As the program executes, cup the sensor in you hands to observe changes in
#   in the readings.  After temperature/humidity increase, re-expose the sensor
#   to open air and observe the changes
# - End program using KeyboardInterrupt (Ctrl+c)



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime
import math

##################################### MANAGE CONNECTIONS #######################################

#connect to MySQLdb
#                    <host>     <MySQL user>  <pwrd>   <db_name>
db=MySQLdb.connect("localhost", "lab3admin", "tcss499", "lab3")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the Grove Temperature and Humidity Sensor to Port A1
ths = 4


# Operational Loop
while True:
	# limit one reading each second

	try:
		time.sleep(1) ### BUG 1
#############################GET DATA AND PRINT IT TO CONSOLE#################################

        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current temperature and humidity reading
		[temperature,humidity] = grovepi.dht(ths,0) # 0 indicates the sensor type
		#if math.isnan(temperature) == False and math.isnan(humidity) == False:
			# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {} :: Temperature = {}, Humidity = {}'.format(localtime.strftime('%H:%M:%S'), temperature, humidity))
        	

############################# BUILD INSERT STATEMENTS #########################################


        	# create the MySQL INSERT INTO statement
		insert_stmt = (
            		"INSERT INTO temperature_readings (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	temp_data = (localtime.strftime('%H:%M:%S'), temperature)
		
		insert_stmt2 = (
            		"INSERT INTO humidity_readings (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	humid_data = (localtime.strftime('%H:%M:%S'), humidity)

############################### SAVING CHANGES ###########################################
		# save the current readings to the database
        	try:
            		cursor.execute(insert_stmt, temp_data)
			cursor.execute(insert_stmt2, humid_data)
            		db.commit()
        	except:
            		db.rollback()

	# stop the program
	except KeyboardInterrupt as k:
		print('Keyboard interruption... Now exiting: %s'%k)
		break

	# error logging
	except IOError:
		print("Error")

cursor.close()
db.close()
