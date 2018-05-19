#!/usr/bin/python

#################
#SOLUTION SCRIPT
#################

# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma
# Lab 6 Full Noise Cancellation Station


# Program Spec
# station_main.py is the driver program for the
# Noise Cancellation Station Lab Series Package. The Noise
# Station simulates a solution for noise polution as a varied 
# output to an LED and has simulated hardware protection system.

# Program setup requirements
# - Connect the sound sensor to Port A1
# - Connect the potentiometer to Port A2
# - Connect the LED to Port D3
# - Connect the Grove Temperature and Humidity Sensor to Port D4
# - Connect the Grove button Port D6
# - Connect the Grove LCD RGB Backlight to any I2C Port

# Program UI
# - A time accompanied by its corresponding readings will print to
#   console every two seconds.
# - Observe the raw readings produced from the system while manipulating
#   the sensors to facilitate the desired test environment
# - End program using KeyboardInterrupt (Ctrl+c)


#####################################################
#################### I/0 Legend #####################
## Sound Sensor  -> noise collection               ##
## Potentiometer -> simulated wind                 ##
## LED(hold 5s)  -> simulated noise cancellation   ##
## Temp&Humid    -> internal system monitoring     ##
## Button        -> simulate 'fan' malfunction     ##
## LCD           -> display system activity        ##
#####################################################
#####################################################

import MySQLdb
import grovepi
import datetime
import string
import station_admin_staffer
import case_monitor
import noise_canceller
from grove_rgb_lcd import *

global soundsensor
global potentiometer
global led
global ths
global btn
global db


# Connect the sound sensor to Port A1
soundsensor = 1
grovepi.pinMode(soundsensor,"INPUT")

# Connect the potentiometer to Port A2
potentiometer = 2
grovepi.pinMode(potentiometer,"INPUT")

# Connect the LED to Port D3
led = 3
grovepi.pinMode(led,"OUTPUT")

# Connect the temp&humid sensor to analog port A4
ths = 4
grovepi.pinMode(ths,"INPUT")

# Connect the button to Port D6
btn = 6
grovepi.pinMode(btn,"INPUT")

# Connect to MySQLdb
#                    <host>      <MySQL user>      <pwrd>      <db_name>
db=MySQLdb.connect("localhost", "station_admin", "tcss499", "noise_canceller")


# Assign business logic global variables
# day_of_week used to correlate with admin_schedules
# Use lowercase first 3 letters of the day_of_week being tested
# 'fri'day should be the only day with all 5 notifications added
global day_of_week
global period_for_average
period_for_average = 5 #           # 10sec=5cyc * 2sec/cyc
global fan_level


# Control the Grove LCD
def signal_lcd(fan, noise, wind):
	setRGB(0,128,64)
	
	if wind > 75:
		setText("High Winds\nSys Halt...")
	elif fan == -2:
		setText("Fan Malfunction\nNotified admins")
	elif fan >= 0:
		setText("Fan: " + str(int(fan)) +"%\nnoise: " + str(noise))
	elif fan == -1:
		setText("Acquiring data\nPlease wait...")

# Signal the LED to simulate noise cancellation
def signal_noise_cancel(level):
	if int(level) > 1023:
		level = 1023
	grovepi.analogWrite(led,int(level)//4)

# Close the recources and turn off displays
def closeStation():
	db.close()
	grovepi.analogWrite(led,0)
	setRGB(0,0,0)
	setText("")

# Runs the Noise Cancellation Station
def main():
	# get day of week from console
	day_of_week = raw_input("Enter 3 letter day of week ex: mon\n")
	# populate sample data
	station_admin_staffer.build_schedules(db)
	station_admin_staffer.staff_admins(db)

	iteration = 0

	fan_level = -1
	signal_lcd(fan_level,0,0) #acquire data message
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
				
				fan_level=case_monitor.average_data(localtime,period_for_average,day_of_week,is_malf)
				#if the wind > 75 we will not do any noise cancellation
			global output_intensity
			if current_wind < 75:
				output_intensity = current_noise * 3
			else:
				output_intensity = 0
			signal_noise_cancel(output_intensity)
			signal_lcd(fan_level,current_noise,current_wind)
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
