#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma
# Lab 6 Full Noise Cancellation Station


# TODO: Program Spec
# noise_canceller_sol.py is a solution set for the like named Python
# scrypt. It opens a connection to MySQLdb using a existing
# user and database.  It then reads the connected sound sensor
# and potentiometer every two seconds and commits that data to the
# specified database with a timestamp.
# The database is queried based on several criteria
# then an LED simulating noise cancellation is adjusted accordingly
# output is also generated for the Grove LCD

# TODO: Program setup requirements
# - Connect the sound sensor to port A1
# - Connect the potentiometer to port A2
# - Connect the LED to port D4
# - Connect the Grove LCD to any I2C port
# - Connect the Grove Temperature and Humidity Sensor to Port D4
# - Connect the Grove button Port D5
# - Connect the Grove LCD RGB Backlight to any I2C Port

# TODO: Program UI
# - A time accompanied by its corresponding readings will print to
#   console every second.
# - Observe the raw readings produced from the sound monitor (not DBs)
# - Information about noise cancellation emmitance is given via the LCD
# - End program using the ctrl+c

# - A time accompanied by its corresponding readings will print to
#   console every 2 seconds.
# - As the program executes, cup the sensor in you hands to observe changes in
#   in the readings.  After temperature/humidity increase, re-expose the sensor
#   to open air and observe.  After 20 seconds press the button for 5 seconds
#   to simulate an error in the fan system. This should populate the database
#   with aggregate data and the appropriate site administrators working that day.
# - End program using KeyboardInterrupt (Ctrl+c)

import MySQLdb
import grovepi
import time
import datetime
import math
import string
import station_admin_staffer
import case_monitor
import noise_canceller
from grove_rgb_lcd import *
from decimal import Decimal

global soundsensor
global potentiometer
global led
global ths
global btn
global db

# Connect the sound sensor to analog port A1
soundsensor = 1
grovepi.pinMode(soundsensor,"INPUT")
# Connect the potentiometer to analog port A2
potentiometer = 2
grovepi.pinMode(potentiometer,"INPUT")
# Connect the LED to analog port A3

ths = 4
grovepi.pinMode(ths,"INPUT")
led = 3
grovepi.pinMode(led,"OUTPUT")
btn = 6
grovepi.pinMode(btn,"INPUT")
#connect to MySQLdb
#  <host>      <MySQL user>      <pwrd>      <db_name>
db=MySQLdb.connect("localhost", "station_admin", "tcss499", "noise_canceller")

# day_of_week used to correlate with admin_schedules
# Use lowercase first 3 letters of the day_of_week being tested
# 'fri'day should be the only day with all 5 notifications added
global day_of_week
day_of_week = 'mon'
global period_for_average
period_for_average = 5





# Control the Grove LCD
def signal_lcd(fan, noise):
	setRGB(0,128,64)
	if fan >= 0:
		setText("Fan: " + str(int(fan)) +"%\nnoise: " + str(noise))
	elif fan == -1:
		setText("Acquiring data\nPlease wait...")
	else:
		setText("Fan Malfunction\nNotified admins")

def signal_noise_cancel(level):
	if int(level) > 1023:
		level = 1023
	grovepi.analogWrite(led,int(level)//4)


def closeStation():
	db.close()
	grovepi.analogWrite(led,0)
	setRGB(0,0,0)
	setText("")


def main():
	#populate sample data
	station_admin_staffer.build_schedules(db)
	station_admin_staffer.staff_admins(db)

	day_of_week = "mon"
	period_for_average = 5  #           # 10sec=5cyc * 2sec/cyc
	iteration = 0
	signal_lcd(-1,0) #acquire data message
	################# Operational Loop ################
	while True:
		try:
			is_malf = int(grovepi.digitalRead(btn))
			iteration += 1
			
			#get the system time
			localtime = datetime.datetime.now()
			
			
			################NOISE_CANCELLER##################
			#store the current sound and wind sensor readings
			current_noise = grovepi.analogRead(soundsensor)
			current_wind = grovepi.analogRead(potentiometer) / 10

			#insert the data into the database
			noise_canceller.insert_noise_reading(localtime,current_noise)
			noise_canceller.insert_wind_speed(localtime,current_wind)
			
			################CASE_MONITOR##################
			#read and store the current temperature and humidity
			
			[temperature,humidity] = grovepi.dht(ths,0) # 0 indicates the sensor type
			time.sleep(2)			
			case_monitor.insert_ths(localtime,temperature,humidity)
			
			############POPULATE AVERAGES EVERY N SECONDS######
			#every 'period_for_average' number of seconds insert a tuple of aggregate data
			if iteration % period_for_average == 0:
				avg_noise=noise_canceller.average_data(localtime,period_for_average)
				
				fan=case_monitor.average_data(localtime,period_for_average,day_of_week,is_malf)
				signal_lcd(fan,avg_noise)
				#if the wind > 75 we will not do any noise cancellation
			global output_intensity
			if current_wind < 75:
				output_intensity = current_noise * 3
			else:
				output_intensity = 0
			signal_noise_cancel(output_intensity)
			print("")
			print('Time{}: '.format(localtime.strftime('%H:%M:%S')))
			print(':: Noise       = {} units'.format(current_noise))
			print(':: Wind        = {} mph'.format(current_wind))
			print(':: Temperature = {}\n:: Humidity    = {}'.format(temperature, humidity))
		#stop the program
		except KeyboardInterrupt as k:
			print('Keyboard interruption... Now exiting: %s'%k)
			break

		#error logging
		except IOError:
			print("Error")

	closeStation()


if __name__ == '__main__':
    main()
