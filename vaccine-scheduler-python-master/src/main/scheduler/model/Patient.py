import sys
import random
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql

class Patient:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    return self
        except pymssql.Error:
            print("Error occurred when getting Patients")
            cm.close_connection()

        cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_patients = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_patients, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Patients")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    # Insert availability with parameter date d
    def reserve(self, d, v, c):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        taken_id = self.get_id()
        id = random.choice([x for x in range(1000000, 9999999) if x not in taken_id])

        add_availability = "INSERT INTO Reservations VALUES (%s , %s, %s , %s, %s)"
        try:
            cursor.execute(add_availability, (id, v, self.username, c, d))
            conn.commit()
            print("Appointment id: ", id)
        except pymssql.Error:
            print("Error occurred when updating reservations")
            cm.close_connection()
        cm.close_connection()


    def get_id(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        result = []
        select_reservations = "SELECT * FROM Reservations"
        try:
            cursor.execute(select_reservations)
            conn.commit()
            for row in cursor:
                result.append(row['AppointmentID'])
        except pymssql.Error:
            print("Error occurred when getting reservations")
            cm.close_connection()
        cm.close_connection()
        return result
