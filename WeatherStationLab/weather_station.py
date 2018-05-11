#!/usr/bin/python

#################
#SOLUTION SCRIPT
#################

# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


# Program Spec
# As written, weather_station.py does not run. Please modify to enable
# weather_station.py to open a connection to MySQLdb using a existing
# user and database.  It should then read the connected Grove Temperature and 
# Humidity sensor every 2 seconds and commit the readings to the a database
# with an abrieviated timestamp.  The Grove LED is incorporated to signal
# high humidity levels. We will work more with outputs in future labs.

# Program setup requirements
# - Connect the Grove Temperature and Humidity Sensor to Port D4
# - Connect the Grove LED to Port D3

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - As the program executes, cup the sensor in you hands to observe changes in
#   in the readings.  After temperature/humidity increase, re-expose the sensor
#   to open air and observe the changes and the LED. 
# - End program using KeyboardInterrupt (Ctrl+c)



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime
import math

##################################### MANAGE CONNECTIONS #######################################

# **Problem 1** connect to MySQLdb
#                 ("<host>", "<MySQLuser>", "<pwrd>", "<db_name>")
db=MySQLdb.connect("", "", "", "")

# Physical connecections
ths = 4
led = 3


# Operational Variables
global localtime
global insert_into_temp
global temp_date
global insert_into_humidity
global humid_data


# Operational Loop
while True:
	# enable traversal of the db tables
	cursor=db.cursor(); 
	try:
		time.sleep(2) # ths has a 2 second signal collection period

#############################GET DATA AND PRINT IT TO CONSOLE#################################

        	# get the system time
		localtime = datetime.datetime.now()
		
		# store the current temperature and humidity reading
		[temperature,humidity] = grovepi.dht(ths,0) # 0 indicates the sensor type
		if math.isnan(temperature) == False and math.isnan(humidity) == False:
			# print data, localtime is parsed to have form: <'HH:MM:SS'>
			print('Time {} :: Temperature = {}, Humidity = {}'.format(localtime.strftime('%H:%M:%S'), temperature, humidity))
        	

############################# BUILD INSERT STATEMENTS #########################################


        	# create the MySQL INSERT INTO statement
		insert_into_temp = (
			# **Problem 2** Write mysql to insert the new tuple 
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	temp_data = (localtime.strftime('%H:%M:%S'), temperature)
		
		insert_into_humidity = (
			# **Problem 3**Write mysql to insert the new tuple 
        	)
		
		# store the data which corresponds to the '%s' in VALUES clause
        	humid_data = (localtime.strftime('%H:%M:%S'), humidity)

############################### SAVING CHANGES ###########################################
		# save the current readings to the database
        	try:
            		cursor.execute(insert_into_temp, temp_data)
			cursor.execute(insert_into_humidity, humid_data)
            		db.commit()
        	except:
            		db.rollback()
		finally:
			cursor.close()

		# see if humidity is above threshold and signal if so
		if math.isnan(humidity) == False and int(humidity) > 91:
			grovepi.digitalWrite(led, 1)
		else:
			grovepi.digitalWrite(led, 0)

	# stop the program
	except KeyboardInterrupt as k:
		print('Keyboard interruption... Now exiting: %s'%k)
		grovepi.digitalWrite(led, 0)
		break

	# error logging
	except IOError:
		print("Error")

cursor.close()
db.close()
