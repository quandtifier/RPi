#!/usr/bin/python

def do_insert(db,sql):
	# save the current readings to the database
        cursor = db.cursor()
	try:
		#print(sql)
            	cursor.execute(sql)
            	db.commit()
        except:
            	db.rollback()
	finally:
		cursor.close()

def build_schedules(db):
	dml_string = (
		"INSERT INTO admin_schedules (id, off_day_1, off_day_2) "
		"VALUES (1, 'sat', 'sun'), "
		"(2, 'mon', 'tue'), "
		"(3, 'wed', 'thu') "
	)
	do_insert(db,dml_string)

def staff_admins(db):
	dml_string = (
		"INSERT INTO administrators (email, fname, lname, schedule_id, mgr_email) "
		"VALUES ('boss@ncs.com','Alice','Harper',1,NULL), "
		"('bob@ncs.com','Bob','Newton',2,'boss@ncs.com'), "
		"('Charlie@ncs.com','Charlie','Euclid',3,'boss@ncs.com'), "
		"('Eve@ncs.com','Eve','Dykstra',1,'boss@ncs.com'), "
		"('Oscar@ncs.com','Oscar','Turing',2,'boss@ncs.com') "
	)
	do_insert(db,dml_string)