import sqlite3
import random
import string
import time

def insert_plate(db, cursor, plate_number):
    cursor.execute(
    """INSERT INTO PLATE(PLATE_NO) VALUES (?)""",
    (plate_number))
    db.commit()

def insert_related_plate_data(db, cursor, plate_informations):
    cursor.execute(
    """INSERT INTO PLATE_INFO(TIME,LATITUDE,LONGTITUDE) VALUES (?,?,?)""", plate_informations)
    db.commit()

def generate_plate_information():
    plate_number = random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits) + random.choice(string.digits)
    recorded_time = time.time()
    longtitude = random.uniform(22,23)
    latitude = random.uniform(120,121)
    return [plate_number, recorded_time, longtitude, latitude]
def main():
    db = sqlite3.connect("alpr_jetson.db")
    cursor = db.cursor()
    plate_information = generate_plate_information()
    cursor.execute("SELECT * FROM PLATE")
    user_all = cursor.fetchall()
    print('')

main()


