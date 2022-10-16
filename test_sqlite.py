import sqlite3
import random
import string
from datetime import datetime
import os.path
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_plate(cursor, plate_number):
    id_plate = cursor.execute(f"SELECT * FROM PLATE WHERE PLATE_NO = ?",(plate_number,)).fetchone()
    return id_plate
def insert_plate(db, cursor, plate_number):
    id_plate = read_plate(cursor, plate_number)
    if id_plate is None:
        cursor.execute("""INSERT INTO PLATE(PLATE_NO) VALUES (?)""",[plate_number],)
        db.commit()
        id_plate = read_plate(cursor, plate_number)
    return id_plate

def insert_related_plate_data(db, cursor, plate_informations):
    cursor.execute(
    """INSERT INTO PLATE_INFORMATION(RECORDED_TIME,LATITUDE,LONGTITUDE, PLATE_ID) VALUES (?,?,?,?)""", (plate_informations))
    db.commit()

def write_db(db, cursor, plate_information):
    # input: plate_information will have (plate_number, captured_time, latitude, longtitude)
    id_plate = insert_plate(db, cursor, plate_information[0])
    plate_information.append(id_plate[0])
    insert_related_plate_data(db, cursor, plate_information[1:])

def test():
    # db_path = os.path.join(BASE_DIR, "alpr_jetson.db")
    # with sqlite3.connect(db_path) as db:
    db = sqlite3.connect("main.db")
    cursor = db.cursor()
    
    # cursor.execute("DROP TABLE PLATE_INFORMATION")
    # cursor.execute("DROP TABLE PLATE")
    # cursor.execute("CREATE TABLE PLATE (ID INTEGER PRIMARY KEY AUTOINCREMENT,  PLATE_NO VARCHAR(20) UNIQUE)")
    # cursor.execute("""CREATE TABLE PLATE_INFORMATION (ID INTEGER PRIMARY KEY AUTOINCREMENT,  
    #                                         RECORDED_TIME VARCHAR(255),
    #                                         LATITUDE VARCHAR(20),
    #                                         LONGTITUDE VARCHAR(20),
    #                                         PLATE_ID INTEGER,
    #                                         FOREIGN KEY(PLATE_ID) REFERENCES PLATE(ID))""")
    # cursor.execute("ALTER TABLE PLATE_INFORMATION ADD TIME DATETIME")
    # insert_plate(db, cursor, plate_information[0])
    # insert_plate(db, cursor, plate_information[1:].append(0))
    # cursor.execute("DELETE FROM PLATE WHERE id=?", (4,))
    # cursor.execute("SELECT PLATE_NO, RECORDED_TIME,LATITUDE,LONGTITUDE FROM PLATE JOIN PLATE_INFORMATION ON PLATE_INFORMATION.PLATE_ID = PLATE.ID ")

    for i in range(5):
        plate_information = generate_plate_information()
        id_plate = insert_plate(db, cursor, plate_information[0])
        plate_information.append(id_plate[0])
        for i in range(30):
            # plate_information = generate_plate_information()
            
            insert_related_plate_data(db, cursor, plate_information[1:])

    # id_plate = insert_plate(db, cursor, 'HIL8963')

    cursor.execute("SELECT ID, PLATE_NO FROM PLATE")
    user_all = cursor.fetchall()
    print(user_all)
    # db.commit()
def generate_plate_information():
    plate_number = random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits)
    recorded_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    longtitude =  round(random.uniform(22,23),5)
    latitude = round(random.uniform(120,121),5)
    return [plate_number, recorded_time, longtitude, latitude]

# unit test
# db = sqlite3.connect("main.db")
# cursor = db.cursor()
# plate_information = generate_plate_information()


