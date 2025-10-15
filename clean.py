import csv
import sqlite3
import datetime
import math


with sqlite3.connect("train_data.db") as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id TEXT UNIQUE NOT NULL,
        vendor_id INTEGER NOT NULL,
        pickup_datetime TEXT NOT NULL,
        dropoff_datetime TEXT NOT NULL,
        passenger_count INTEGER NOT NULL,
        pickup_longitude REAL NOT NULL,
        pickup_latitude REAL NOT NULL,
        dropoff_longitude REAL NOT NULL,
        dropoff_latitude REAL NOT NULL,
        store_and_fwd_flag TEXT NOT NULL,
        trip_duration INTEGER NOT NULL,
        trip_speed REAL NOT NULL,
        distance REAL NOT NULL,
        pickup_hour INTEGER NOT NULL,
        day_of_week TEXT NOT NULL
    );
""")


try:
    with open('excluded_records.csv', mode='r', newline='', encoding='utf-8') as logger:
        pass
except FileNotFoundError:
    with open('excluded_records.csv', mode='w', newline='', encoding='utf-8') as log_w:
        logger = csv.writer(log_w)
        logger.writerow(['row_num', 'trip_id', 'reason', 'raw_row'])


go_to_next_row = False
with open('train.csv', mode='r', newline='') as file, \
        open('excluded_records.csv', mode='a', newline='', encoding='utf-8') as log_w:
    csv_reader = csv.reader(file, delimiter=',')
    logger = csv.writer(log_w)
    header = next(csv_reader)
    row_num = 1
    csv_reader = csv.reader(file, delimiter=',')
    for row in csv_reader:
        if len(row) != 11:
            logger.writerow([row_num, '', 'wrong field count', '|'.join(row)])
            row_num += 1
            continue

        trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, store_and_fwd_flag, trip_duration = row

        with sqlite3.connect("train_data.db") as conn:
            row_id = conn.execute("""
                SELECT id FROM trips WHERE trip_id = ?;
            """, (trip_id,)).fetchone()

            if row_id is not None:
                logger.writerow(
                    [row_num, trip_id, 'duplicate', '|'.join(row)])
                row_num += 1
                continue

        try:
            vendor_id = int(vendor_id)
            pickup_datetime = datetime.datetime.strptime(
                pickup_datetime, "%Y-%m-%d %H:%M:%S")
            dropoff_datetime = datetime.datetime.strptime(
                dropoff_datetime, "%Y-%m-%d %H:%M:%S")
            passenger_count = int(passenger_count)
            pickup_longitude = float(pickup_longitude)
            pickup_latitude = float(pickup_latitude)
            dropoff_longitude = float(dropoff_longitude)
            dropoff_latitude = float(dropoff_latitude)
            trip_duration = int(trip_duration)
        except ValueError:
            logger.writerow([row_num, trip_id, 'invalid data', '|'.join(row)])
            row_num += 1
            continue

        if passenger_count < 1:
            logger.writerow(
                [row_num, trip_id, 'anomalous data', '|'.join(row)])
            row_num += 1
            continue

        if trip_duration > 43200:
            logger.writerow(
                [row_num, trip_id, 'anomalous data', '|'.join(row)])
            row_num += 1
            continue

        pickup_hour = pickup_datetime.hour
        days_of_the_week = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
                            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        day_of_week = days_of_the_week[pickup_datetime.isoweekday()]

        R = 6371.0

        pickup_latitude = math.radians(pickup_latitude)
        pickup_longitude = math.radians(pickup_longitude)
        dropoff_latitude = math.radians(dropoff_latitude)
        dropoff_longitude = math.radians(dropoff_longitude)

        diff_latitude = dropoff_latitude - pickup_latitude
        diff_longitude = dropoff_longitude - pickup_longitude

        a = math.sin(diff_latitude / 2)**2 + math.cos(pickup_latitude) * \
            math.cos(dropoff_latitude) * math.sin(diff_longitude / 2)**2
        central_angle = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = R * central_angle

        trip_speed = distance_km / (trip_duration / 3600)

        with sqlite3.connect("train_data.db") as conn:

            conn.execute("""
                INSERT INTO trips (trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, store_and_fwd_flag, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration, trip_speed, distance, pickup_hour, day_of_week)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, store_and_fwd_flag, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration, trip_speed, distance_km, pickup_hour, day_of_week))
        row_num += 1
