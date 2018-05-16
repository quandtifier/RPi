#!/usr/bin/python

#################
#SOLUTION SCRIPT
#################

# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


# Program Spec
# case_monitor.py opens a connection with MySQLdb then runs monitoring logic
# with the GrovePi+ sensors to obtain readings from inside of the noise
# cancellation station's hardware case. The program simulates temperature
# and humidity management and also sends communications to site admins via
# email.

# Program setup requirements
# - Connect the Grove Temperature and Humidity Sensor to Port D4
# - Connect the Grove button Port D5
# - Connect the Grove LCD RGB Backlight to any I2C Port

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - As the program executes, cup the sensor in you hands to observe changes in
#   in the readings.  After temperature/humidity increase, re-expose the sensor
#   to open air and observe the systems notification manager 
# - End program using KeyboardInterrupt (Ctrl+c)



# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime
import math
import station_admin_staffer
from grove_rgb_lcd import *
from decimal import Decimal

##################################### MANAGE CONNECTIONS #######################################

#connect to MySQLdb
#                    <host>      <MySQL user>      <pwrd>      <db_name>
db=MySQLdb.connect("localhost", "station_admin", "tcss499", "noise_canceller")
# populate sample data
station_admin_staffer.build_schedules(db)
station_admin_staffer.staff_admins(db)

# Physical connecections
btn = 5
ths = 4

iteration = 0


def insert_ths(time, temp, humid):
	dml_string = (
		"INSERT INTO ths_readings (rtime, temperature, humidity) "
		"VALUES (%s,%s,%s)"
	)
	data = (time, temp, humid)
	do_insert(dml_string, data)

def insert_notification(time, email, temp, humid, fan):
	dml_string = (
		"INSERT INTO notifications (ntime, admin_email, temperature, humidity, fan_level) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (time, email, temp, humid, fan)
	do_insert(dml_string, data)

def insert_admin(email, fname, lname, schedule, manager):
	dml_string = (
		"INSERT INTO administrator (email, fname, lname, schedule_id, mgr_email) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (email, fname, lname, schedule, manager)
	do_insert(dml_string, data)

def insert_schedule(schedule_id, day1, day2):
	dml_string = (
		"INSERT INTO ths_readings (id, off_day_1, off_day_2) "
		"VALUES (%s,%s,%s)"
	)
	data = (schedule_id, day1, day2)
	do_insert(dml_string, data)


def query_avg_temp(start):
	cursor = db.cursor()
	query = (
		"SELECT AVG(temperature) as avg "
		"FROM ths_readings "
		"WHERE rtime > %s"
	)
	cursor.execute(query, start)
	global avgval
	for (avg) in cursor:
		avgval = float(avg[0])
	cursor.close()
	return avgval

def query_avg_humid(start):
	cursor = db.cursor()
	query = (
		"SELECT AVG(humidity) as avg "
		"FROM ths_readings "
		"WHERE rtime > %s"
	)
	cursor.execute(query, start)
	global avgval
	for (avg) in cursor:
		avgval = float(avg[0])
	cursor.close()
	return avgval


def do_insert(sql,data):
	# save the current readings to the database
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


# Operational Loop
while True:
	try:
		iteration = iteration + 1
		time.sleep(2)
		# get the system time
		localtime = datetime.datetime.now()
		
		# store the current temperature and humidity reading
		[temperature,humidity] = grovepi.dht(ths,0) # 0 indicates the sensor type
		if math.isnan(temperature) == False and math.isnan(humidity) == False:
			# print data, localtime is parsed to have form: <'HH:MM:SS'>
			print('Time {} :: Temperature = {}, Humidity = {}'.format(localtime.strftime('%H:%M:%S'), temperature, humidity))
        	insert_ths(localtime,temperature,humidity)
		
		if iteration % 5 == 0:
			start_time = localtime - datetime.timedelta(seconds=10)
			avg_temp_delta_n = query_avg_temp(start_time)
			avg_humid_delta_n = query_avg_humid(start_time)
			fan_op_level = 0
			insert_notification(localtime,"boss@ncs.com",avg_temp_delta_n,avg_humid_delta_n,fan_op_level)

	# stop the program
	except KeyboardInterrupt as k:
		print('Keyboard interruption... Now exiting: %s'%k)
		grovepi.digitalWrite(led, 0)
		break

	# error logging
	except IOError:
		print("Error")


db.close()
