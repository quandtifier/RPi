#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma
# Lab 4 Noise Cancellation Station


# Program Spec
# noise_canceller.py does not run as-downloaded.  After building 
# a database with the necessary schema, complete the script below
# where indicated by 'TODO:' opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected sound sensor
# and potentiometer every two seconds and commits that data to the 
# specified database with a timestamp.
# The database is queried based on several criteria 
# then an LED simulating noise cancellation is adjusted accordingly
# output is also generated for the Grove LCD

# Program setup requirements
# - Connect the sound sensor to port A1
# - Connect the potentiometer to port A2
# - Connect the LED to port D4
# - Connect the Grove LCD to any I2C port

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - Observe the raw readings produced from the sound monitor (not DBs)
# - Information about noise cancellation emmitance is given via the LCD
# - End program using the ctrl+c


import MySQLdb
import grovepi
import time
import datetime
from grove_rgb_lcd import *
from decimal import Decimal

global localtime
global current_noise
global current_wind
global period_for_average
period_for_average = 5  #           # 10sec=5cyc * 2sec/cyc
global iteration
iteration = 0

#connect to MySQLdb
#ex:         MySQLdb.connect("<host>","<MySQL user>","<pwrd>","<db_name>")
#TODO: db=MySQLdb.connect()



# Connect the sound sensor to analog port A1
soundsensor = 1
# Connect the potentiometer to analog port A2
potentiometer = 2

# Connect the LED to analog port A3
led = 3
grovepi.pinMode(led,"OUTPUT")


# try to execute the sql insert statement
# for help with debugging uncomment the print statements below
def do_insert(sql,data):
        cursor = db.cursor()
	try:
		#print(sql)
		#print(data)
            	cursor.execute(sql, data)
            	db.commit()
        except:
            	db.rollback()
	finally:
		cursor.close()


####################### insert noise ################

def insert_noise_data(start, end, avg, max, min):
	dml_string = (
		#TODO:
		#TODO:
        )
	data = ()#TODO:
	do_insert(dml_string,data)


def insert_noise_reading():
	dml_string = (
		#TODO:
		#TODO:
        )
	data = ()#TODO:Hint: these variables are global delcared above
	do_insert(dml_string,data)


####################### insert wind ################

def insert_wind_data(start, end, avg, max, min):
	dml_string = (
		#TODO:
		#TODO:
	)
	data = ()#TODO:
	do_insert(dml_string, data)


def insert_wind_speed():
	dml_string = (
		#TODO:
		#TODO:
	)
	data = ()#TODO:
	do_insert(dml_string, data)


####################### aggregate wind data retrievals ################

def query_avg_wind(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global avgval
	for (avg) in cursor:
		avgval = float(avg[0])
	cursor.close()
	return avgval

def query_max_wind(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global maxval
	for (max) in cursor:
		maxval = float(max[0])
	cursor.close()
	return maxval

def query_min_wind(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global minval
	for (min) in cursor:
		minval = float(min[0])
	cursor.close()
	return minval

####################### aggregate noise data retrievals ################

def query_avg_noise(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global avgval
	for (avg) in cursor:
		avgval = float(avg[0])
	cursor.close()
	return avgval

def query_max_noise(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global maxval
	for (max) in cursor:
		maxval = float(max[0])
	cursor.close()
	return maxval

def query_min_noise(start):
	cursor = db.cursor()
	query = (
		#TODO:
		#TODO:
		#TODO:
	)
	cursor.execute(query, start)
	global minval
	for (min) in cursor:
		minval = float(min[0])
	cursor.close()
	return minval


################### NO MODIFICATIONS REQUIRED BELOW THIS LINE #########################
def signal_outputs(level,avg_wind):
	if int(level) > 1023:
		level = 1023
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
		iteration = iteration + 1

        	# get the system time and store a formatted copy
		localtime = datetime.datetime.now()
		formated_time = localtime.strftime('%H:%M:%S')

		# store the current sound and wind sensor readings
		current_noise = grovepi.analogRead(soundsensor)
		current_wind = grovepi.analogRead(potentiometer) / 10

		# print data, localtime is parsed to have form: <'HH:MM:SS'>
		print('Time {}  ::  Noise ->  {} units'.format(formated_time, current_noise))
		print('               ::  Wind  ->  {} mph'.format(current_wind))

		# insert the sensor readings into the database
		insert_noise_reading()
		insert_wind_speed()

		# query the database for the last 5 second windspeed average
		last_n_seconds = localtime - datetime.timedelta(seconds=5)
		last_n_seconds = last_n_seconds.strftime('%H:%M:%S')
		avg_wind_last_n = query_avg_wind(last_n_seconds)

		# every 'period_for_average' number of seconds insert a tuple of aggregate data
		if iteration % period_for_average == 0:
			# factor out
			start_time = localtime - datetime.timedelta(seconds=period_for_average)
			#start_time = start_time.strftime('%H:%M:%S')
			avg_wind_delta_n = query_avg_wind(start_time)
			max_wind_delta_n = query_max_wind(start_time)
			min_wind_delta_n = query_min_wind(start_time)
			insert_wind_data(
			start_time,
			localtime,
			int(avg_wind_delta_n),
			int(max_wind_delta_n),
			int(min_wind_delta_n)
			)
			avg_noise_delta_n = query_avg_noise(start_time)
			max_noise_delta_n = query_max_noise(start_time)
			min_noise_delta_n = query_min_noise(start_time)
			insert_noise_data(
			start_time,
			localtime,
			int(avg_noise_delta_n),
			int(max_noise_delta_n),
			int(min_noise_delta_n)
			)

		#if the wind > 75 we will not do any noise cancellation
		global output_intensity
		if current_wind < 75: 
			output_intensity = current_noise * 3
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
