#!/usr/bin/python
import MySQLdb
import time
import grovepi
#connect to MySQLdb
db=MySQLdb.connect("localhost", "potentiometer", "tcss499", "knobreadtime")
cursor=db.cursor();

# Connect the Rotary Angle Sensor to analog port A2
potentiometer = 2

time.sleep(1)
i = 0
localtime = time.ctime();
while True:
	try:
        t = time.ctime();
		# Read resistance from potentiometer
		i = grovepi.analogRead(potentiometer)
		print(i)

        # FROM https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
        insert_stmt = (
            "INSERT INTO employees (emp_no, first_name, last_name, hire_date) "
            "VALUES (%s, %s)"
        )
        data = (localtime, i)
        try:
            cursor.execute(insert_stmt, data)
            db.commit();
        except:
            db.rollback();
	except IOError:
		print("Error")

db.close();
