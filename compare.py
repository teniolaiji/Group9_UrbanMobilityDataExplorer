import sqlite3
import time

def sqlite_compare():
    with sqlite3.connect("train_data.db") as conn:
        no_of_trips_per_day_of_week = conn.execute("""
            SELECT day_of_week, COUNT(*) AS no_of_trips
            FROM trips
            GROUP BY day_of_week;
        """).fetchall()
        return no_of_trips_per_day_of_week
    

def group_trips_by_key_compare(records):
    grouped = []
    for record in records:
        key = record[0]
        found = False
        for group in grouped:
            if group[0] == key:
                group[1] += 1
                found = True
                break
        if not found:
            grouped.append([key, 1])
    return grouped


start_time1 = time.time()
sqlite_compare()
end_time1 = time.time()

dureation_sqlite_compare = end_time1 - start_time1
print(f"It took {dureation_sqlite_compare} seconds for sqlite_compare() to complete.")



start_time2 = time.time()
with sqlite3.connect("train_data.db") as conn:
    records = conn.execute("SELECT day_of_week FROM trips;").fetchall()
    group_trips_by_key_compare(records)
end_time2 = time.time()

duration_group_trips_by_key_compare = end_time2 - start_time2
print(f"It took {duration_group_trips_by_key_compare} seconds for group_trips_by_key_compare() to complete.")