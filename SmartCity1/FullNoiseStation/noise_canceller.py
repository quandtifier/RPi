#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma


import MySQLdb
import grovepi
import time
import datetime
import station_main
from grove_rgb_lcd import *
from decimal import Decimal








def insert_noise_data(start, end, avg, max, min):
	dml_string = (
            	"INSERT INTO noise_data (start_of_delta, end_of_delta, avg_noise, max_noise, min_noise) "
            	"VALUES (%s,%s,%s,%s,%s)"
        )
	data = (start, end, avg, max, min)
	do_insert(dml_string,data)

####################### insert noise ################

def insert_noise_reading(time, current_noise):
	dml_string = (
            	"INSERT INTO noise_readings (rtime, noise_level) "
            	"VALUES (%s, %s)"
        )
	data = (time, current_noise)
	do_insert(dml_string,data)

####################### insert wind ################

def insert_wind_data(start, end, avg, max, min):
	dml_string = (
		"INSERT INTO wind_data (start_of_delta, end_of_delta, avg_noise, max_noise, min_noise) "
            	"VALUES (%s,%s,%s,%s,%s)"
	)
	data = (start, end, avg, max, min)
	do_insert(dml_string,data)


def insert_wind_speed(time, current_wind):
	dml_string = (
		"INSERT INTO wind_speeds (rtime, wind_speed) "
		"VALUES (%s, %s)"
	)
	data = (time, current_wind)
	do_insert(dml_string,data)
####################### aggregate wind data retrievals ################

def query_avg_wind(start):
	query = (
		"SELECT AVG(wind_speeds.wind_speed) as avg "
		"FROM wind_speeds "
		"WHERE wind_speeds.rtime > %s"
	)
	result = list(execute_query(query,start))
	return result[0][0]

def query_max_wind(start):
	query = (
		"SELECT MAX(wind_speeds.wind_speed) as max "
		"FROM wind_speeds "
		"WHERE wind_speeds.rtime > %s"
	)
	result = list(execute_query(query,start))
	return result[0][0]

def query_min_wind(start):
	query = (
		"SELECT MIN(wind_speeds.wind_speed) as min "
		"FROM wind_speeds "
		"WHERE wind_speeds.rtime > %s"
	)
	result = list(execute_query(query,start))
	return result[0][0]


####################### aggregate noise data retrievals ################

def query_avg_noise(start):
	query = (
		"SELECT AVG(noise_readings.noise_level) as avg "
		"FROM noise_readings "
		"WHERE noise_readings.rtime > %s"
	)
	result = list(execute_query(query,start))
	return result[0][0]

def query_max_noise(start):
	query = (
		"SELECT MAX(noise_readings.noise_level) as max "
		"FROM noise_readings "
		"WHERE noise_readings.rtime > %s"
	)
	result = list(execute_query(query,start))
	return result[0][0]

def query_min_noise(start):
	query = (
		"SELECT MIN(noise_readings.noise_level) as min "
		"FROM noise_readings "
		"WHERE noise_readings.rtime > %s"
	)
	result = list(execute_query(query,start))

	return result[0][0]

######## NO MODIFICATIONS REQUIRED BELOW THIS LINE (in student copy)########




def average_data(time,delta):
	start_time = time - datetime.timedelta(seconds=delta*2)
	avg_wind_delta_n = query_avg_wind(start_time)
	max_wind_delta_n = query_max_wind(start_time)
	min_wind_delta_n = query_min_wind(start_time)
	insert_wind_data(
	start_time,
	time,
	int(avg_wind_delta_n),
	int(max_wind_delta_n),
	int(min_wind_delta_n)
	)
	avg_noise_delta_n = query_avg_noise(start_time)
	max_noise_delta_n = query_max_noise(start_time)
	min_noise_delta_n = query_min_noise(start_time)
	insert_noise_data(
	start_time,
	time,
	int(avg_noise_delta_n),
	int(max_noise_delta_n),
	int(min_noise_delta_n)
	)
	return int(avg_noise_delta_n)


def execute_query(sql,data):
	db = station_main.db
	cursor = db.cursor()
	cursor.execute(sql,data)
	result = list(cursor.fetchall())
	cursor.close()
	return result

# try to execute the sql insert statement
def do_insert(sql,data):
	# save the current readings to the database\
	db = station_main.db
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
