#!/usr/bin/python


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
# - Connect the Grove LCD to any I2C port

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
from grove_rgb_lcd import *


global localtime
global current_noise
global current_wind
global period_for_average
period_for_average = 10
global iteration
iteration = 0

#connect to MySQLdb
#                    <host>      <MySQL user>    <pwrd>       <db_name>
db=MySQLdb.connect("localhost", "station_admin", "tcss499", "noise_canceller")



# Connect the sound sensor to analog port A1
soundsensor = 1
# Connect the potentiometer to analog port A2
potentiometer = 2

# Connect the LED to analog port A3
led = 3
grovepi.pinMode(led,"OUTPUT")

def do_insert(sql,data):
	# save the current readings to the database
        cursor = db.cursor()
	try:
		print(sql)
		print(data)
            	cursor.execute(sql, data)
            	db.commit()
        except:
            	db.rollback()
	finally:
		cursor.close()


def insert_noise_data():
	dml_string = (
            	"INSERT INTO noise_data (end_of_delta, avg_noise, max_noise, min_noise) "
            	"VALUES ()"
        )
	data = (localtime)
	do_insert(dml_string,data)


def insert_noise_reading():
	dml_string = (
            	"INSERT INTO noise_readings (rtime, noise_level) "
            	"VALUES (%s, %s)"
        )
	data = (localtime, current_noise)
	do_insert(dml_string,data)


def insert_wind_data():
	dml_string = (
		"INSERT INTO wind_data (end_of_delta, avg_noise, max_noise, min_noise) "
            	"VALUES ()"
	)
	data = (localtime)
	do_insert(dml_string, data)


def insert_wind_speed():
	dml_string = (
		"INSERT INTO wind_speeds (rtime, wind_speed) "
		"VALUES (%s, %s)"
	)
	data = (localtime, current_wind)
	do_insert(dml_string, data)

def query_avg_wind(delta):
	cursor = db.cursor()
	average_wind_query = (
		"SELECT AVG(wind_speeds.wind_speed) as avgs "
		"FROM wind_speeds "
		"WHERE wind_speeds.rtime > %s"
	)
	cursor.execute(average_wind_query, delta)
	for (avgs) in cursor:
		return float(avgs[0])
	cursor.close()

def signal_outputs(level,avg_wind):
	if int(level) > 1000:
		level = 1000
	grovepi.analogWrite(led,int(level)//4)
	
	cw = str(current_wind)
	aw = str(int(avg_wind))
	n = str(current_noise)

	# Control the Grove LCD
	setRGB(0,128,64)
	if current_wind >= 75:
		setText("Operation Halt:\n" + "Windspeed= " + cw +"mph")
	else:
		setText("avgwind=" + aw + "mph\n" + "noise=" + n + "units")


# the operational loop
while True:
	try:
		# one reading every two seconds
		time.sleep(2)

        	# get the system time and store a formatted copy
		localtime = datetime.datetime.now()
		formated_time = localtime.strftime('%H:%M:%S')

		# store the current sound and wind sensor readings
		current_noise = grovepi.analogRead(soundsensor)
		current_wind = grovepi.analogRead(potentiometer) / 10

		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Noise ->  {} units'.format(formated_time, current_noise))
		print('               ::  Wind  ->  {} mph'.format(current_wind))

		# insert the data into the database
		insert_noise_reading()
		insert_wind_speed()

		# query the database for the last 5 second windspeed average
		last_n_seconds = localtime - datetime.timedelta(seconds=5)
		last_n_seconds = last_n_seconds.strftime('%H:%M:%S')
		avg_wind_last_n = query_avg_wind(last_n_seconds)
		if int(iteration//2) % period_for_average == 0:
			delta_n = localtime - datetime.timedelta(seconds=period_for_average)
			delta_n = last_n_seconds.strftime('%H:%M:%S')
			avg_wind_delta_n = query_avg_wind(delta_n)

		#if the wind > 75 we will not do any noise cancellation
		global output_intensity
		if current_wind < 75: 
			# Make the noise cancellation [c = noise + 3/4(avg_wind)]
			output_intensity = current_noise + (avg_wind_last_n * .75)
		else:
			output_intensity = 0
	
		signal_outputs(output_intensity,avg_wind_last_n)


	# stop the program
	except KeyboardInterrupt as k:
		print('Keyboard interruption... Now exiting: %s'%k)
		break

	# error logging
	except IOError:
		print("Error")


# close resources and reset hardware
db.close()
grovepi.analogWrite(led,0)
setRGB(0,0,0)
setText("")
