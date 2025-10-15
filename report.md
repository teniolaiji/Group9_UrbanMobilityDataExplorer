Overview of your system
This project provides insights into urban mobility by analyzing the New York city taxi trip duration dataset.
It performs data cleaning and preprocessing of the NYC taxi trip data
Has an SQLite database storage for efficient data queries
Provides a web-based dashboard for exploring urban mobility patterns
Has interactive analytics and visualizations
Does trip filtering and analysis


Technical descriptions (architecture designs)
Flask is used for the backend while HTML, CSS and JS are used for the frontend.
There are two main scripts the project uses in the backend: clean.py and app.py. 
clean.py parses and cleans the data and stores the cleaned data in the SQLITE db
app.py contains the Flask code that runs the server to fetch from the db and display on the frontend.
The backend renders 2 frontend templates, home.html (for displaying the taxi duration data and for performing filtering operations such as getting all trips between a time range, or trips that lasted for a duration range, etc) while analytics.html tackles grouping the data by certain criteria such as number of trips per day of week. This analytics.html visualizes the data using chart.js in the form of pie charts and bar graphs.



1. Problem Framing and Dataset Analysis
Describe the dataset and its context
The dataset is raw data from the New York City Taxi Trip dataset, which contains trip records including timestamps, distances, durations, pickup/dropoff locations, and other metadata.
It includes the following columns: id, vendor_id, pickup_datetime, dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, store_and_fwd_flag, trip_duration.
The context of the dataset is it shows the durations it took different taxis to pick up and drop off passengers at specific dates and locations.


Identify data challenges (e.g., missing fields, outliers, anomalies)
There were no missing fields we identified in the dataset. However, we identified some anomalies such as trips with passenger_count of 0. We also noticed some trips with durations that lasted longer than 12 hours which is not reasonable for NYC. We filtered out all these rows during the data cleaning step and logged them in the excluded_records.csv file.

Explain assumptions made during data cleaning
1. We assumed that a reasonable trip should not last longer than 12 hours
2. We assumed that a trip should not have zero passengers
3. We assumed that all trips would have data in the required fields.


Highlight one unexpected observation that influenced your design



2. System Architecture and Design Decisions
![System Architecture and Design Decisions](<Team 9 System Architecture Diagram.png>)

Justify your stack choices and schema structure
We chose Flask because it is very lightweight and easy to write since it is written in Python and we are very familiar with Python. We decided to use HTML, CSS and JS for the frontend and have that rendered by the Flask app. 
When we examined the raw dataset, we decided we only needed on table called trips in the database. We went with SQLite because it does not require any complex setup and it is very straightforward to use. All the columns in the raw dataset are in our DB, and in addition, we added some derived fields such as trip_speed, distance, pickup_hour and day_of_week to make analytics easier when we were grouping by no_of_trips_per_day_of_week or no_of_trips_per_time_of_day.


Discuss trade-offs you made during the design process
Some trade-offs we made during the design process were:
For logging, we wrote excluded rows to a CSV excluded_records.csv for simplicity.
To be more robust, we could have used concurrent writers/structured analysis. So we lack log levels and auto-rotation which are provided by the Python logging module.
We also used SQLite which may block under concurrent requests, Postgres is more robust and handles this better.


3. Algorithmic Logic and Data Structures
The algorithm works by first of all fetching all the day_of_week from the db. Then it calls the group_trips_by_key function and passes in the records (which is a list of tuples, where each tuple contains one item which is the day of the week, records looks like [('Saturday',), ('Friday',), ('Monday',), ('Friday',), ('Thursday',), ('Thursday',), ('Thursday',), ('Friday',), ('Friday',), ('Friday',), ('Monday',), ('Saturday',), ('Wednesday',), ('Saturday',)]). The group_trips_by_key function works like this:
It goes through each record (i.e. a tuple like ("Monday",) extracts the day of week i.e. Monday, and checks whether we have come across this key before). If we have not, it adds it as a new entry in the result list like ["Monday", 1]. But if we have come across it before, we increase the count instead like ["Monday", 2]. At the end, when we have gone through all the records, we return a list of lists like [['Monday', 7185], ['Sunday', 7390], ['Tuesday', 7737], ['Wednesday', 7919], ['Saturday', 8269], ['Friday', 8378], ['Thursday', 8274]].

Its time complexity is O(nxk) where n is the number of trips and k is the number of unique groups. SQLite's built-in GROUP BY runs in O(n log n) or O(n) and is far faster because it uses efficient indexing and memory handling. So SQLite performs the same task more efficiently, especially as the dataset grows.

4. Insights and Interpretation
Present three meaningful insights derived from the data. For each:
Key insights:
- Most trips have a single passenger.


- 


Show how you derived it (via query, algorithm, or visualization)

Include a visual (e.g., chart or screenshot)

Interpret what it means in the context of urban mobility

5. Reflection and Future Work
Reflect on technical and team challenges


Suggest improvements and next steps if this were a real-world product

- We would use PostgreSQL and not SQLite in production.
- We would use the Python logging module for logging the excluded records because it provides us with autorotation of logs and logging levels.
- We would deploy the site on a platform like Render so that users can access it from anywhere in the world.
- We would use React for the frontend so that the users have a better experience using the app as a Single Page Application.
