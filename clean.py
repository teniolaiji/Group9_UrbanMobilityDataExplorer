import csv
import sqlite3
import datetime
import math

# Read raw trip records from `train.csv`, validate and clean them,
# compute derived fields (distance, speed, pickup hour, day of week),
# insert valid records into the `trips` table in `train_data.db`, and
# log invalid/excluded rows into `excluded_records.csv`.


with sqlite3.connect("train_data.db") as conn:
    # Ensure the `trips` table exists. Columns include raw fields and
    # computed/derived fields used for analysis (distance, trip_speed, hour, day).
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


# Prepare the excluded records log. If it doesn't exist, create it.
try:
    with open('excluded_records.csv', mode='r', newline='', encoding='utf-8') as logger:
        pass
except FileNotFoundError:
    with open('excluded_records.csv', mode='w', newline='', encoding='utf-8') as log_w:
        logger = csv.writer(log_w)
        # Columns: original row number, trip id (if any), reason for exclusion, raw row
        logger.writerow(['row_num', 'trip_id', 'reason', 'raw_row'])


go_to_next_row = False
# Open the input CSV and append to the excluded-records log.
with open('train.csv', mode='r', newline='') as file, \
        open('excluded_records.csv', mode='a', newline='', encoding='utf-8') as log_w:
    csv_reader = csv.reader(file, delimiter=',')
    logger = csv.writer(log_w)
    # Consume header row from the input file
    header = next(csv_reader)
    # row_num is used for logging; it currently starts at 1 (note: header consumed)
    row_num = 1
    # Recreate reader starting at the current file position (after header)
    csv_reader = csv.reader(file, delimiter=',')
    for row in csv_reader:
        # Skip rows that do not have exactly 11 fields
        if len(row) != 11:
            logger.writerow([row_num, '', 'wrong field count', '|'.join(row)])
            row_num += 1
            continue

        # Unpack expected CSV fields in order
        trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, store_and_fwd_flag, trip_duration = row

        # Quick duplicate check by querying the DB for an existing trip_id
        with sqlite3.connect("train_data.db") as conn:
            row_id = conn.execute("""
                SELECT id FROM trips WHERE trip_id = ?;
            """, (trip_id,)).fetchone()

            if row_id is not None:
                # Duplicate detected — log and skip
                logger.writerow(
                    [row_num, trip_id, 'duplicate', '|'.join(row)])
                row_num += 1
                continue

        # Parse and coerce types; invalid conversions will be logged and skipped
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
            # Non-numeric or malformed data — log and continue
            logger.writerow([row_num, trip_id, 'invalid data', '|'.join(row)])
            row_num += 1
            continue

        # Additional anomaly detection
        if passenger_count < 1:
            logger.writerow(
                [row_num, trip_id, 'anomalous data', '|'.join(row)])
            row_num += 1
            continue

        if trip_duration > 43200:
            # Trip longer than 12 hours considered anomalous
            logger.writerow(
                [row_num, trip_id, 'anomalous data', '|'.join(row)])
            row_num += 1
            continue

        # Compute derived temporal fields: hour and weekday
        pickup_hour = pickup_datetime.hour
        days_of_the_week = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
                            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        day_of_week = days_of_the_week[pickup_datetime.isoweekday()]

        # Formula to compute great-circle distance between pickup and dropoff
        R = 6371.0

        # Convert degrees to radians for trigonometric functions
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

        # Compute trip speed in km/h (distance in km divided by duration in hours)
        trip_speed = distance_km / (trip_duration / 3600)

        # Insert cleaned and derived data into the DB
        with sqlite3.connect("train_data.db") as conn:

            conn.execute("""
                INSERT INTO trips (trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, store_and_fwd_flag, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration, trip_speed, distance, pickup_hour, day_of_week)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (trip_id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, store_and_fwd_flag, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_duration, trip_speed, distance_km, pickup_hour, day_of_week))
        row_num += 1
