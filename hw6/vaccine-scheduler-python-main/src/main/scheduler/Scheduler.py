from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import sqlite3
import datetime
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password> 
    # check for length 

    if len(tokens) != 3:
        print("Create patient failed")
        return 
    
    username = tokens[1]
    password = tokens[2]

    # check unique username
    if username_exists_patient(username):
        print("Username taken, try again")
        return

    if not check_password("patient", password): # password needs to be valid
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    patient = Patient(username, salt = salt, hash = hash)

    try:
        patient.save_to_db()
    except sqlite3.Error as e:
        print("Create patient failed")
        return
    except Exception as e:
        print("Create patient failed")
        return
    
    # passed all checks, we're good!
    print("Created user", username)


def check_password(name, password):


    invalid_message = "Create " + name + " failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from \"!\", \"@\", \"#\", \"?\")"

    valid_password = False

    if (len(password) >= 8) and bool(re.search(r"[A-Z]+", password)) and bool(re.search(r"[a-z]+", password)) and bool(re.search(r'\d+', password)) and bool(re.search(r"[!@#?]+", password)):
        valid_password = True
    else:
        print(invalid_message)

    return valid_password


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again")
        return
    
    # bonus! 
    if not check_password("caregiver", password): # password needs to be valid
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except sqlite3.Error as e:
        print("Failed to create user.")
        return
    except Exception as e:
        print("Failed to create user.")
        return
    print("Created user", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Failed to create user")
        cm.close_connection()
        return True
    except Exception as e:
        print("Failed to create user")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return
    

    username = tokens[1]
    password = tokens[2]

    if not username_exists_patient(username):
        print("Login patient failed")
        return


    patient = None
    try:
        patient = Patient(username, password=password).get()
    except sqlite3.Error as e:
        print("Login patient failed")
        return
    except Exception as e:
        print("Login patient failed")
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except sqlite3.Error as e:
        print("Login failed.")
        return
    except Exception as e:
        print("Login failed.")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # first make sure we're logged in 

    if current_caregiver == current_patient:
        print("Please login first")
        return
    if len(tokens) != 2:
        print("Please try again")
        return

    # if we have good input and logged in, continue:
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:
        # need to parse date?
        date_whole = tokens[1].split("-")
        d = datetime.datetime(int(date_whole[0]), int(date_whole[1]), int(date_whole[2]))
        
        get_available_dates = "SELECT Username FROM Availabilities WHERE TIME = ? ORDER BY Username"
        get_vaccines = "SELECT Name, Doses FROM Vaccines"

        # get all availabilities and vaccines
        cursor.execute(get_available_dates, (str(d),))
        available_dates = cursor.fetchall()
        cursor.execute(get_vaccines,())
        available_vaccs = cursor.fetchall()

        # now set up our prints
        print("Caregivers:")

        if (len(available_dates) == 0):
            print("No caregivers available")
        else:
            # if we do have appointments to view:
            for row in available_dates:
                print(f"{row['Username']}")

        
        print("Vaccines:")

        if (len(available_vaccs) == 0):
            print("No vaccines available")
        else:
            # if we do have appointments to view:
            for row in available_vaccs:
                print(f"{row['Name']} {row['Doses']}")

        return

        
    except sqlite3.Error: 
        print("Please try again")
        cm.close_connection()
        return
    except Exception:
        print("Please try again")
        cm.close_connection()
        return


def reserve(tokens):
    # if no one is logged in
    if current_caregiver == current_patient:
        print("Please login first")
        return 
    if current_patient == None:
        print("Please login as a patient")
        return 
    
    # extra check to make sure input is valid
    if len(tokens) != 3: # three to include the command
        print("Please try again")
        return 
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:

        # need to parse date?
        date_whole = tokens[1].split("-")
        d = datetime.datetime(int(date_whole[0]), int(date_whole[1]), int(date_whole[2]))

        find_available_date = "SELECT Time, Username FROM Availabilities WHERE Time = ? ORDER BY Username LIMIT 1"

        cursor.execute(find_available_date, (str(d),))

        appt_date = cursor.fetchall()

        if len(appt_date) == 0:
            print("No caregiver is available")
            return
        
        # now that we know a caregiver is available:
        assigned_caregiver = appt_date[0]["Username"]
        assigned_date = appt_date[0]["Time"]

        vaccine_name = tokens[2]
        vaccine = Vaccine(vaccine_name, available_doses=None).get()

        # check that we have available vaccines
        if vaccine is not None:
            if vaccine.available_doses <= 0:
                print("Not enough available doses")
                return
            else:
                vaccine.decrease_available_doses(1)
        else:
            # which error class should this be?
            print("Not enough available doses")
            return 
        
        # now that we know we have a valid caregiver + vaccine, add to table!
        add_appointment = "INSERT INTO Reservations (cUsername, pUsername, Time, Name) VALUES (?, ?, ?, ?)"
        cursor.execute(add_appointment, (str(assigned_caregiver), str(current_patient.username),
                                         str(assigned_date), str(vaccine_name)))
        
        # update caregiver availabilities table
        drop_availability = "DELETE FROM Availabilities WHERE Time = ? AND Username = ?"
        cursor.execute(drop_availability, (str(assigned_date), str(assigned_caregiver)))

        conn.commit()

        # now that we've done all this successfully, print out:
        get_appt = "SELECT ApptID, Time, cUsername, pUsername FROM Reservations WHERE pUsername = ? AND cUsername = ? AND Time = ?"
        cursor.execute(get_appt, (str(current_patient.username), str(assigned_caregiver), str(assigned_date)))
        appt = cursor.fetchall()

        for row in appt:
            print(f"Appointment ID {row['ApptID']}, Caregiver username {row['cUsername']}")

        return 

    except sqlite3.Error as e: 
        print("Please try again")
        cm.close_connection()
        return 
    except Exception as e: 
        print("Please try again")
        cm.close_connection()
        return 


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again")
        return

    date = tokens[1]
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except sqlite3.Error as e:
        print("Upload Availability Failed")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        return
    print("Availability uploaded!")


def cancel(tokens):
    if current_caregiver == current_patient:
        print("Please login first")
        return 
    if len(tokens) != 2:
        print("Please try again")
        return 
    
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        cancel_id = tokens[1]

        get_appt = "SELECT ApptID, Time, pUsername, cUsername, Name FROM Reservations WHERE ApptID = ?"
        cursor.execute(get_appt, (str(cancel_id),))
        appt = cursor.fetchall()
        valid_appt = False

        # patient / caregiver can only cancel their own appointments
        if current_patient is not None:
            if appt[0][2] == current_patient.username: # hard code it in?
                valid_appt = True
            else:
                print(f"Appointment ID {cancel_id} does not exist")
        elif current_caregiver is not None:
            if appt[0][3] == current_caregiver.username:
                valid_appt = True
            else:
                print(f"Appointment ID {cancel_id} does not exist")

        # now we know the appointment id is valid, delete it and fix other tables
        if valid_appt:
            delete_appt = "DELETE FROM Reservations WHERE ApptID = ?"
            vaccine = Vaccine(appt[0][4], None).get()

            vaccine.increase_available_doses(1) # replenish

            cursor.execute(delete_appt, (cancel_id,))
            
            print(f"Appointment ID {cancel_id} has been successfully canceled")

            # then update availabilities, regardless of who canceled
            insert_avail = "INSERT INTO Availabilities VALUES (?,?)"
            cursor.execute(insert_avail, (str(appt[0][1]), str(appt[0][3])))

            conn.commit()
        else:
            print(f"Appointment ID {cancel_id} does not exist")

        return

    except sqlite3.Error as e: 
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again")
        cm.close_connection()
        return            
        


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except sqlite3.Error as e:
        print("Error occurred when adding doses")
        return
    except Exception as e:
        print("Error occurred when adding doses")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    print("Doses updated!")


def show_appointments(tokens):

    # if no user is logged in:
    if current_caregiver == current_patient:
        print("Please login first")
        return
    
    # if we have too many tokens
    if len(tokens) != 1:
        print("Please try again")
        return 
    
    # create our connection
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:
        # first display output for the caregiver 
        if current_caregiver is not None:
            get_caregiver_appointments = "SELECT ApptID, Name, Time, pUsername FROM Reservations WHERE cUsername = ? ORDER BY ApptID"
            
            cursor.execute(get_caregiver_appointments, (str(current_caregiver.username),))

            appointments = cursor.fetchall()

            if len(appointments) == 0:
                print("No appointments scheduled")
                return
            
            # if we do have appointments to view:
            for row in appointments:
                print(f"{row['ApptID']} {row['Name']} {row['Time'][0:10]} {row['pUsername']}")

        # and next for the patient  
        if current_patient is not None:
            get_patient_appointments = "SELECT ApptID, Name, Time, cUsername FROM Reservations WHERE pUsername = ? ORDER BY ApptID"
            cursor.execute(get_patient_appointments, (str(current_patient.username),))
            appointments = cursor.fetchall()

            if len(appointments) == 0:
                print("No appointments scheduled")
                return
            
            # if we do have appointments to view:
            for row in appointments:
                print(f"{row['ApptID']} {row['Name']} {row['Time'][0:10]} {row['cUsername']}")

            return 


    # all other errors
    except sqlite3.Error as e: 
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e: 
        print("Please try again")
        cm.close_connection()
        return
    


def logout(tokens):
    global current_patient
    global current_caregiver

    if len(tokens) != 1:
        print("Please try again")
        return

    try:
        if current_patient != current_caregiver: # one is not None
            current_caregiver = None
            current_patient = None
            print("Successfully logged out")
        else: 
            print("Please login first")
            return
    except Exception as e:
        print("Please try again")
        return

def start():
    stop = False
    print("*** Please enter one of the following commands ***")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        #response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
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
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()