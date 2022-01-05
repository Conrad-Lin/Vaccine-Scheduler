import random
import sys
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    global current_patient
    global current_caregiver
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    # check if passwords are safe
    letters = 0
    numbers = 0
    for i in password:
        if i.isalpha():
            letters += 1
        elif i.isnumeric():
            numbers += 1

    if len(password) < 8:
        print("Password too short")
        return
    elif password.islower() or password.isupper():
        print("Password needs upper and lowercase letters")
        return
    elif numbers <= 0 or letters <= 0:
        print("Password needs a combination of letters and numbers")
        return
    elif password.count('!') == 0 and password.count('@') == 0 and password.count('#') == 0 and password.count('?') == 0:
        print("Password needs one special character of !, @, #, ?")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        current_patient = Patient(username, salt=salt, hash=hash)
        current_caregiver = None
        # save to caregiver information to our database
        try:
            current_patient.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def create_caregiver(tokens):
    global current_patient
    global current_caregiver
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check if passwords are safe
    letters = 0
    numbers = 0
    for i in password:
        if i.isalpha():
            letters += 1
        elif i.isnumeric():
            numbers += 1

    if len(password) < 8:
        print("Password too short")
        return
    elif password.islower() or password.isupper():
        print("Password needs upper and lowercase letters")
        return
    elif numbers <= 0 or letters <= 0:
        print("Password needs a combination of letters and numbers")
        return
    elif password.count('!') == 0 and password.count('@') == 0 and password.count('#') == 0 and password.count(
            '?') == 0:
        print("Password needs one special character of !, @, #, ?")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        current_caregiver = Caregiver(username, salt=salt, hash=hash)
        current_patient = None
        # save to caregiver information to our database
        try:
            current_caregiver.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        try:
            patient = Patient(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if patient is None:
        print("Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient
    pass


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_availabilities = "SELECT * FROM Availabilities WHERE Time = %s"
    select_vaccines = "SELECT * FROM Vaccines"

    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # Get the caregivers available on that day
    try:
        d = datetime.datetime(year, month, day)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availabilities, d)

        if cursor.rowcount == 0:
            print("Sorry, there are no appointments available at that time")
            return
        else:
            print("Caregivers Available: ")
            for row in cursor:
                print(row['Username'])
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error retrieving schedules")

    # Get vaccine availabilities
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_vaccines)
        print('\nVaccine Availabilities:')
        for row in cursor:
            print(row['Name'], ": ", row['Doses'])
    except pymssql.Error:
        print("Error retrieving vaccines")


def reserve(tokens):
    global current_patient

    if current_patient is None:
        print("Please login as a patient first!")
        return
    if len(tokens) != 3:
        print("Please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    select_availabilities = "SELECT * FROM Availabilities WHERE Time = %s"

    date = tokens[1]
    vaccine_name = str(tokens[2])
    vaccine = None
    cname = None
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # See if the vaccine selected is available
    try:
        doses = 0
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
        if vaccine is None or vaccine.get_available_doses() <= 0:
            print("There is no available vaccine of name: ", vaccine_name)
            return
    except pymssql.Error:
        print("Error retrieving vaccine")

    # Get a random available caregiver
    try:
        d = datetime.datetime(year, month, day)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availabilities, d)

        if cursor.rowcount == 0:
            print("Sorry, there are no appointments available at that time")
            return
        else:
            usernames = [];
            for row in cursor:
                usernames.append(row['Username'])
            cname = usernames[random.randint(0, len(usernames)) - 1]
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error retrieving schedules")

    # Delete the availability, remove a vaccine dose, and upload the reservation
    try:
        d = datetime.datetime(year, month, day)

        try:
            delete_availability(d, cname)
        except:
            print('Error deleting availability')
            return

        try:
            current_patient.reserve(d, vaccine_name, cname)
        except:
            print('Error uploading reservation')
            return

        try:
            vaccine.decrease_available_doses(1)
        except:
            print('Error decreasing doses')
            return

        print("Caregiver Username: ", cname)
        print("Successfully made reservation!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error making reservation")


def delete_availability(d, cname):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    delete = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"

    try:
        cursor.execute(delete, (d, cname))
        conn.commit()
    except pymssql.Error:
        print("Error occurred when updating availability")
        cm.close_connection()
    cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        d = datetime.datetime(year, month, day)
        try:
            current_caregiver.upload_availability(d)
        except:
            print("Upload Availability Failed")
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = str(tokens[1])
    doses = int(tokens[2])
    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    global current_caregiver
    global current_patient

    cm = ConnectionManager()
    conn = cm.create_connection()

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    if current_caregiver is None:
        select_appointments = "SELECT * FROM Reservations WHERE pUsername = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, current_patient.get_username())

            if cursor.rowcount == 0:
                print("You have no appointments")
            else:
                print('Appointments: ')
                for row in cursor:
                    print("ID: ", row['AppointmentID'], ", Vaccine: ", row['Dose'],
                          ", Caregiver: ", row["cUsername"], ", Date: ", row['Time'])
        except pymssql.Error:
            print("Error retrieving appointments")
    else:
        select_appointments = "SELECT * FROM Reservations WHERE cUsername = %s"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(select_appointments, current_caregiver.get_username())

            if cursor.rowcount == 0:
                print("You have no appointments")
            else:
                print('Appointments: ')
                for row in cursor:
                    print("ID: ", row['AppointmentID'], ", Vaccine: ", row['Dose'],
                          ", Patient: ", row["pUsername"], ", Date: ", row['Time'])
        except pymssql.Error:
            print("Error retrieving appointments")


def logout(tokens):
    global current_caregiver
    global current_patient

    # first check if you need to log anyone out, then check which user type to log out
    if current_caregiver is None and current_patient is None:
        print("Please login first")
    elif current_caregiver is None:
        print("Successfully logged out " + current_patient.get_username())
        current_patient = None
    else:
        print("Successfully logged out " + current_caregiver.get_username())
        current_caregiver = None


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
