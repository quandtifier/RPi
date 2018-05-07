#!/usr/bin/python

#################################### NOTES AND BUGS ######################################
# BUG 1: Program does not exit properly using 'except KeyboardInterrupt'
# BUG 2: Program struggles with datatypes for comparisons when using the average wind reading



# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


# Program Spec
# sc1.py opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected sound sensor
# and potentiometer every second and commits that data to the 
# specified database with an abrieviated timestamp.
# The database is queried based on several criteria 
# then an LED simulating noise cancellation is adjusted accordingly

# Program setup requirements
# - Connect the sound sensor to port A1
# - Connect the potentiometer to port A2
# - Connect the LED to port D4

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - Observe the raw readings produce from the sound monitor (not DBs)
# - End program using the ctrl+c

from decimal import Decimal

# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime

##################################### MANAGE CONNECTIONS #######################################

#connect to MySQLdb
#                    <host>        <MySQL user>         <pwrd>        <db_name>
db=MySQLdb.connect("localhost", "noiseadmin", "tcss499", "noise_station_db")

# enable traversal of the relation db
cursor=db.cursor(); 

# Connect the sound sensor to analog port A1
soundsensor = 1
# Connect the potentiometer to analog port A2
potentiometer = 2

# Connect the LED to analog port A3
led = 3
grovepi.pinMode(led,"OUTPUT")


# the operational loop
while True:
	# stall to limit one reading each second
	time.sleep(1)

	try:

#############################GET DATA AND PRINT IT TO CONSOLE#################################
        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current sound sensor reading
		current_noise = grovepi.analogRead(soundsensor)
		# store the current 'wind speed'
		current_wind = grovepi.analogRead(potentiometer) / 10

		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Noise -> Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), current_noise))
		print('Wind  -> Time {}  ::  Reading {}'.format(localtime.strftime('%H:%M:%S'), current_wind))

############################# BUILD INSERT STATEMENTS #########################################	

        	# create the MySQL INSERT INTO statement
		insert_noise = (
            		"INSERT INTO mic_readings (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		data_noise = (localtime.strftime('%H:%M:%S'), current_noise)
		
		# create the MySQL INSERT INTO statement
		insert_wind = (
            		"INSERT INTO windspeeds (rtime, reading) "
            		"VALUES (%s, %s)"
        	)
		data_wind = (localtime.strftime('%H:%M:%S'), current_wind)
        	
############################### SAVING CHANGES ###########################################
		
		# save the current readings to the database
        	try:
            		cursor.execute(insert_noise, data_noise)
			cursor.execute(insert_wind, data_wind)
            		db.commit()
			
        	except:
            		db.rollback()
		

##################################### find average over last 5 seconds ###################

#### BUG 2
		# get read to query the database for the last 5 second windspeed average
		tminusfive = localtime - datetime.timedelta(seconds=5)
		tminusfive = tminusfive.strftime('%H:%M:%S')
		average_wind_query = (
			"SELECT AVG(windspeeds.reading) as avgs "
			"FROM windspeeds "
			"WHERE windspeeds.rtime > %s"
		)
		global avg_wind_delta_5
		cursor.execute(average_wind_query, tminusfive)
		for (avgs) in cursor:
			avg_wind_delta_5 = float(avgs[0]) #### Bug 2 This is type(decimal.Decimal)

		global output_intensity
		if current_wind < 75: #if the wind > 75 we will not do any noise cancellation
			# Make the noise cancellation a function of 3/4(avg_wind)
			output_intensity = current_noise + (avg_wind_delta_5 * .75)
		else:
			output_intensity = 0

		
		# Send PWM signal to LED
		grovepi.analogWrite(led,int(output_intensity)//4)

	# stop the program
	except KeyboardInterrupt:###### BUG 1
		grovepi.analogWrite(led,0)

	# error logging
	except IOError:
		print("Error")

db.close()
grovepi.analogWrite(led,0)
