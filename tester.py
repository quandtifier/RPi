#!/usr/bin/python


# IoT Education in Research
# TCSS499 Research Group
# University of Washington, Tacoma






# Get the necessary libraries for interfacing
import MySQLdb
import grovepi
import time
import datetime




btn = 6


	
# the operational loop
while True:
	try:

	
	# stop the program
	except KeyboardInterrupt:
		db.close()
		break

	# error logging
	except IOError:
		print("Error")



