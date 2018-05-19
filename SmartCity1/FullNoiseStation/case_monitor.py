#!/usr/bin/python

#################
#SOLUTION SCRIPT
#################

# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma

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
day_of_week = "mon"
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
    do_insert(dml_string,data)

# adds new notifications to the database
def insert_notification(time, email, temp, humid, fan):
	dml_string = (
		"INSERT INTO notifications (ntime, admin_email, temperature, humidity, fan_level) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (time, email, temp, humid, fan)
    do_insert(dml_string,data)

# adds new administrators to the database
def insert_admin(email, fname, lname, schedule, manager):
	dml_string = (
		"INSERT INTO administrator (email, fname, lname, schedule_id, mgr_email) "
		"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (email, fname, lname, schedule, manager)
    do_insert(dml_string,data)


# adds new admin_schedules. id numbers 1, 2, and 3 are taken by sample data
def insert_schedule(schedule_id, day1, day2):
	dml_string = (
		"INSERT INTO admin_schedules (id, off_day_1, off_day_2) "
		"VALUES (%s,%s,%s)"
	)
	data = (schedule_id, day1, day2)
    do_insert(dml_string,data)


# find the average temp from a given start time
# until the current time
def query_avg_temp(start):
	cursor = db.cursor()
	query = (
		"SELECT AVG(temperature) as avg "
		"FROM ths_readings "
		"WHERE rtime > %s"
	)
    result = list(execute_query(query,start)
	return result[0]

# find the average humidity from a given start time
# until the current time
def query_avg_humid(start):
	query = (
		"SELECT AVG(humidity) as avg "
		"FROM ths_readings "
		"WHERE rtime > %s"
	)
    result = list(execute_query(query,start)
	return result[0]

# finds who is working today
def query_admin_schedule(day):

	query = (
		"SELECT email as avail_admins "
		"FROM administrators, admin_schedules "
		"WHERE id=schedule_id AND %s <> off_day_1 AND %s <> off_day_2"
	)
	data = (day, day)
    result = list(execute_query(query,data)
	return result[0]


# finds who is working today then inserts a notification for
# every available administrator
def build_notification(fan,day):
	available_admins = query_admin_schedule(day)
	for email in available_admins:
		form_email = string.replace(str(email),"(","")  #format the email for re-insertion
		form_email = string.replace(form_email,")","")
		form_email = string.replace(form_email," ","")
		form_email = string.replace(form_email,",","")
		form_email = string.replace(form_email,"\"","")
		form_email = string.replace(form_email,"\'","")
		insert_notification(localtime,form_email,avg_temp_delta_n,avg_humid_delta_n,fan)

######################## program logic functions ###################


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

def close():
    setRGB(0,0,0)
    setText("")

def average_data(time,delta,day):
    start_time = time - datetime.timedelta(seconds=delta*2)
    avg_temp_delta_n = query_avg_temp(start_time)
    avg_humid_delta_n = query_avg_humid(start_time)
    fan = 0
    if int(grovepi.digitalRead(btn)) == 1:
    	build_notification(fan)
    	fan = -2
    else:
    	fan = manipulate_fan(avg_temp_delta_n, avg_humid_delta_n)
    return int(fan)



def execute_query(sql,data):
    cursor = db.cursor()
    cursor.execute(sql,data)
    result = list(cursor.fetchall())
    cursor.close()
    return result

# try to execute the sql insert statement
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
