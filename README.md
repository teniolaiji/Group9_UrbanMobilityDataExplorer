# How to Set Up Our Project
0. Download train.csv dataset from https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data?select=train.zip and place in root directory
1. Create a virtual environment using the command python -m venv .venv (for Windows) or python3 -m venv .venv (for Linux and Mac).
2. Activate the virtual environment using the command .venv\Scripts\activate (for windows) or source .venv/bin/activate (for Linux and Mac)
3. Install the dependencies using the command pip install -r requirements.txt
4. Run python clean.py (python3 clean.py) to parse and clean the data and stores the cleaned data in the db
5. Run python app.py to start the Flask server
6. Go to 127.0.0.1:5000

# About the Project
This project provides insights into urban mobility by analyzing the New York city taxi trip duration dataset.

# Project Structure
```
urban_mobility_project/
├── app.py                 # Flask web application server
├── clean.py              # Data cleaning and processing script
├── train.csv             # NYC taxi trip dataset
├── requirements.txt      # Python dependencies
├── static/              # CSS styling files
│   ├── analytics.css    # Styling for analytics page
│   └── home.css         # Styling for home page
└── templates/           # HTML template files
    ├── analytics.html   # Analytics dashboard page
    └── home.html        # Home page template
```

# Features
- Data cleaning and preprocessing of NYC taxi trip data
- SQLite database storage for efficient data queries
- Web-based dashboard for exploring urban mobility patterns
- Interactive analytics and visualizations
- Trip filtering and analysis capabilities

