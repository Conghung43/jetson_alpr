import sqlite3
import random
import string
from datetime import datetime
import os.path
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def insert_plate(db, cursor, plate_number):
    cursor.execute(
    """INSERT INTO PLATE(PLATE_NO) VALUES (?)""",
    [plate_number],)
    db.commit()

def insert_related_plate_data(db, cursor, plate_informations):
    cursor.execute(
    """INSERT INTO PLATE_INFORMATION(RECORDED_TIME,LATITUDE,LONGTITUDE, PLATE_ID) VALUES (?,?,?,?)""", (plate_informations))
    db.commit()

def generate_plate_information():
    plate_number = random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits)
    recorded_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    longtitude =  round(random.uniform(22,23),5)
    latitude = round(random.uniform(120,121),5)
    return [plate_number, recorded_time, longtitude, latitude]
def main():
    # db_path = os.path.join(BASE_DIR, "alpr_jetson.db")
    # with sqlite3.connect(db_path) as db:
    db = sqlite3.connect("main.db")
    cursor = db.cursor()
    
    # cursor.execute("CREATE TABLE PLATE (ID INTEGER PRIMARY KEY AUTOINCREMENT,  PLATE_NO VARCHAR(10))")
    # cursor.execute("""CREATE TABLE PLATE_INFORMATION (ID INTEGER PRIMARY KEY AUTOINCREMENT,  
    #                                         RECORDED_TIME VARCHAR(255),
    #                                         LATITUDE VARCHAR(255),
    #                                         LONGTITUDE VARCHAR(255),
    #                                         PLATE_ID INTEGER,
    #                                         FOREIGN KEY(PLATE_ID) REFERENCES PLATE(ID))""")
    # cursor.execute("ALTER TABLE PLATE_INFORMATION ADD TIME DATETIME")
    # insert_plate(db, cursor, plate_information[0])
    # insert_plate(db, cursor, plate_information[1:].append(0))
    # cursor.execute("DROP TABLE PLATE_INFORMATION")
    # cursor.execute("DELETE FROM PLATE WHERE id=?", (4,))
    # cursor.execute("SELECT PLATE_NO, RECORDED_TIME,LATITUDE,LONGTITUDE FROM PLATE JOIN PLATE_INFORMATION ON PLATE_INFORMATION.PLATE_ID = PLATE.ID ")

    for i in range(10):
        plate_information = generate_plate_information()
        plate_information.append(1)
        insert_related_plate_data(db, cursor, plate_information[1:])
    cursor.execute("SELECT * FROM PLATE_INFORMATION")
    user_all = cursor.fetchall()
    print(user_all)
    # db.commit()

main()


