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
import string
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
btn = 6
grovepi.pinMode(btn,"INPUT")
ths = 4

# Program execution variable for weekdays to correlate with admin_schedules
# Use lowercase first 3 letters day of week being tested
# 'fri'day should be the only day with all 5 notifications added
global day_of_week 
day_of_week = "fri" 
iteration = 0


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


def query_admin_schedule():
	cursor = db.cursor()
	query = (
		"SELECT email as avail_admins "
		"FROM administrators, admin_schedules "
		"WHERE id=schedule_id AND %s <> off_day_1 AND %s <> off_day_2"
	)
	data = (day_of_week, day_of_week)
	cursor.execute(query, data)
	emails = list(cursor.fetchall())
	print("emails: " + str(emails[0]))
	do_insert(query,data)
	cursor.close()
	return emails


def signal_lcd(fan):

	# Control the Grove LCD
	setRGB(0,128,64)
	if fan >= 0:
		setText("Fan Level = " + str(int(fan)) +"%")
	elif fan == -1:
		setText("Acquiring data\nPlease wait...")
	else:
		setText("Fan Malfunction\nNotified admins")

# 
def manipulate_fan(avg_temp, avg_humid):
	over_temp = avg_temp - 22 
	fan_op_level = 0
	if over_temp > 2 or avg_humid > 80:
		fan_op_level = 100
	elif over_temp > 1 or avg_humid > 50:
		fan_op_level = 50
	else:
		fan_op_level = avg_humid
	return fan_op_level

def build_notification(fan):
	available_admins = query_admin_schedule()
	for email in available_admins:
		form_email = string.replace(str(email),"(","")  #format the email for re-insertion
		form_email = string.replace(form_email,")","")
		form_email = string.replace(form_email," ","")
		form_email = string.replace(form_email,",","")
		form_email = string.replace(form_email,"\"","")
		form_email = string.replace(form_email,"\'","")
		insert_notification(localtime,form_email,avg_temp_delta_n,avg_humid_delta_n,fan)

signal_lcd(-1) #acquire data message
# Operational Loop
while True:
	try:
		iteration += 1
		time.sleep(2)
		# get the system time
		localtime = datetime.datetime.now()
		
		# read and store the current temperature and humidity 
		[temperature,humidity] = grovepi.dht(ths,0) # 0 indicates the sensor type
		if math.isnan(temperature) == False and math.isnan(humidity) == False:
			# print data, localtime is parsed to have form: <'HH:MM:SS'>
			print('Time {} :: Temperature = {}, Humidity = {}'.format(localtime.strftime('%H:%M:%S'), temperature, humidity))
        	insert_ths(localtime,temperature,humidity)
		
		if iteration % 5 == 0:
			start_time = localtime - datetime.timedelta(seconds=10)
			avg_temp_delta_n = query_avg_temp(start_time)
			avg_humid_delta_n = query_avg_humid(start_time)
			fan = 0
			if int(grovepi.digitalRead(btn)) == 1:
				build_notification(fan)
				fan = -2
			else:
				fan = manipulate_fan(avg_temp_delta_n, avg_humid_delta_n)
			signal_lcd(fan)
			
	# stop the program
	except KeyboardInterrupt as k:
		print('Keyboard interruption... Now exiting: %s'%k)
		break

	# error logging
	except IOError:
		print("Error")


db.close()
setRGB(0,0,0)
setText("")
