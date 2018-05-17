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
# and humidity management and also logs notifications data for site admins

# Program setup requirements
# - Connect the Grove Temperature and Humidity Sensor to Port D4
# - Connect the Grove button Port D5
# - Connect the Grove LCD RGB Backlight to any I2C Port

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every 2 seconds.
# - As the program executes, cup the sensor in you hands to observe changes in
#   in the readings.  After temperature/humidity increase, re-expose the sensor
#   to open air and observe.  After 20 seconds press the button for 5 seconds
#   to simulate an error in the fan system. This should populate the database
#   with aggregate data and the appropriate site administrators working that day.
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

##################################### MANAGE CONNECTIONS ###########################
#connect to MySQLdb
#                    <host>      <MySQL user>      <pwrd>      <db_name>
db=MySQLdb.connect("localhost", "station_admin", "tcss499", "noise_canceller")

# populate sample data
station_admin_staffer.build_schedules(db)
station_admin_staffer.staff_admins(db)

# Physical connections
btn = 6
grovepi.pinMode(btn,"INPUT")
ths = 4

# day_of_week used to correlate with admin_schedules
# Use lowercase first 3 letters of the day_of_week being tested
# 'fri'day should be the only day with all 5 notifications added
global day_of_week 
day_of_week = "fri" 
iteration = 0




################################## functions for db interaction ###############
# executes the insert.  No changes here but uncommenting the print()s
# may help with debugging
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

# populate the temp and humidity data into the database
def insert_ths(time, temp, humid):
	dml_string = (
		"INSERT INTO ths_readings (rtime, temperature, humidity) "
		"VALUES (%s,%s,%s)"
	)
	data = (time, temp, humid)
	do_insert(dml_string, data)

# adds new notifications to the database
def insert_notification(time, email, temp, humid, fan):
	dml_string = (
		"INSERT INTO notifications (ntime, admin_email, temperature, humidity, fan_level) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (time, email, temp, humid, fan)
	do_insert(dml_string, data)

# adds new administrators to the database
def insert_admin(email, fname, lname, schedule, manager):
	dml_string = (
		"INSERT INTO administrator (email, fname, lname, schedule_id, mgr_email) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (email, fname, lname, schedule, manager)
	do_insert(dml_string, data)


# adds new admin_schedules. id numbers 1, 2, and 3 are taken by sample data
def insert_schedule(schedule_id, day1, day2):
	dml_string = (
		"INSERT INTO admin_schedules (id, off_day_1, off_day_2) "
		"VALUES (%s,%s,%s)"
	)
	data = (schedule_id, day1, day2)
	do_insert(dml_string, data)


# find the average temp from a given start time 
# until the current time
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

# find the average humidity from a given start time 
# until the current time
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

# finds who is working today
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
	cursor.close()
	return emails


# finds who is working today then inserts a notification for 
# every available administrator
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

######################## program logic functions ###################
# Control the Grove LCD
def signal_lcd(fan):


	setRGB(0,128,64)
	if fan >= 0:
		setText("Fan Level = " + str(int(fan)) +"%")
	elif fan == -1:
		setText("Acquiring data\nPlease wait...")
	else:
		setText("Fan Malfunction\nNotified admins")

# get the simulated fan level
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




signal_lcd(-1) #acquire data message
################# Operational Loop ################
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
