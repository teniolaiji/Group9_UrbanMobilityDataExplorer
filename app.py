import sqlite3

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    print(request.args)

    query = "SELECT * FROM trips"
    query_second_part = []
    parameters = []
    start_pickup_time = request.args.get('start_pickup_time')
    end_pickup_time = request.args.get('end_pickup_time')

    if start_pickup_time and end_pickup_time:
        query_second_part.append("pickup_datetime BETWEEN ? AND ?")
        parameters += [start_pickup_time, end_pickup_time]

    min_distance = request.args.get('min_distance')
    max_distance = request.args.get('max_distance')

    if min_distance and max_distance:
        query_second_part.append("distance BETWEEN ? AND ?")
        parameters += [min_distance, max_distance]

    min_trip_duration = request.args.get('min_trip_duration')
    max_trip_duration = request.args.get('max_trip_duration')

    if min_trip_duration and max_trip_duration:
        query_second_part.append("trip_duration BETWEEN ? AND ?")
        parameters += [min_trip_duration, max_trip_duration]

    with sqlite3.connect("train_data.db") as conn:
        if query_second_part:
            query_second_part = " AND ".join(query_second_part)
            query += f" WHERE {query_second_part};"
        trips = conn.execute(f"{query}", parameters).fetchall()

    return render_template("home.html", trips=trips)


def group_trips_by_key(records):
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


@app.route('/analytics')
def analytics():
    with sqlite3.connect("train_data.db") as conn:
        day_of_weeks = conn.execute("SELECT day_of_week FROM trips;").fetchall()
        no_of_trips_per_day_of_week = group_trips_by_key(day_of_weeks)
        print(no_of_trips_per_day_of_week)

        no_of_passengers_per_day_of_week = conn.execute("""
            SELECT day_of_week, SUM(passenger_count) AS no_of_passengers
            FROM trips
            GROUP BY day_of_week
            ORDER BY no_of_passengers DESC;
        """).fetchall()

        no_of_trips_per_time_of_day = conn.execute("""
            SELECT pickup_hour, COUNT(*) AS no_of_trips
            FROM trips
            GROUP BY pickup_hour
            ORDER BY pickup_hour;
        """).fetchall()
        
        passenger_distribution = conn.execute("""
            SELECT passenger_count, COUNT(*) AS no_of_trips
            FROM trips
            GROUP BY passenger_count
            ORDER BY no_of_trips DESC;
        """).fetchall()

        no_of_passengers_per_time_of_day = conn.execute("""
            SELECT pickup_hour, SUM(passenger_count) AS total_no_of_passengers
            FROM trips
            GROUP BY pickup_hour
            ORDER BY pickup_hour ASC;
        """).fetchall()


    context = {
        'no_of_trips_per_day_of_week': no_of_trips_per_day_of_week,
        'no_of_passengers_per_day_of_week': no_of_passengers_per_day_of_week,
        'no_of_trips_per_time_of_day': no_of_trips_per_time_of_day,
        'passenger_distribution': passenger_distribution,
        'no_of_passengers_per_time_of_day': no_of_passengers_per_time_of_day,
    }
    return render_template("analytics.html", **context)

if __name__ == '__main__':
    app.run(debug=True)