# Import my dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta

# Create our engine, connecting it to the assigned sqlite database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setup Flask
app = Flask(__name__)

# Establish routes
# Provide in-line HTML formatting to make the page look prettier
@app.route("/")
def welcome():

    return (
        # Assignment and creator info
        f"<h4>Hawaii Climate Info <br>"
        f"By: Ryan Zimmerlee<br>"
        f"Date: 04/02/2019<br><br><br>"
        f"Below are the available routes and Hawaii climate information: </h4> <br>"

        # Precipitation page
        f"<b>Precipitation by day for the last year:</b><br>"
        f"/api/v1.0/precipitation<br><br>"

        # Weather station page
        f"<b>All Hawaii weather stations:</b><br>"
        f"/api/v1.0/stations<br><br>"

        # Temperature page
        f"<b>Temperature by day for the last year:</b><br>"
        f"/api/v1.0/tobs<br><br>"

        # Min, max, avg temp page - by start date
        f"<b>The below route will give you the min, max and average temperature values for all dates greater than the date provided: </b><br>"
        f"<b>Please provide a start date after the backslash using the following format: .../api/v1.0/YYYY-MM-DD/ </b><br>"
        f"/api/v1.0/<start_date><br><br>"

        # Min, max, avg temp page - by start and end date
        f"<b>The below route will give you the min, max and average temperature values for the provided date range. </b><br>"
        f"<b>Please provide a start date and an end date after the backslash using the following format: .../api/v1.0/YYYY-MM-DD/YYYY-MM-DD </b><br>"
        f"/api/v1.0/<start_date>/<end_date>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precips():
    # Start the session for the page
    session = Session(engine)

    # Find one year time delta from the last date in the SQL Measurement table
    meas_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = datetime.strptime(meas_dates[0], "%Y-%m-%d")
    oneYear = max_date - timedelta(days=365)

    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > oneYear).all()

    # Convert list of tuples into normal list
    precip_lastyear = list(np.ravel(precip))

    # JSONIFY the object
    return jsonify(precip_lastyear)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Start the session for the page
    session = Session(engine)

    # Query Station sqlite and get all station names 
    station_names = session.query(Station.name).all()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_names))

    # JSONIFY the list of tuples
    return jsonify(all_stations)

# Temperature route
@app.route("/api/v1.0/tobs")
def temps():
    # Start the session for the page
    session = Session(engine)

    # Find one year time delta from the last date in the SQL Measurement table
    meas_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = datetime.strptime(meas_dates[0], "%Y-%m-%d")
    oneYear = max_date - timedelta(days=365)

    # Query Measurement sqlite to get the date and temperature
    temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > oneYear).order_by(Measurement.date).all()

    # Create a list of a collection of dictionaries that extracts the data we want from the object
    temps_lastyear = []
    for date, tobs in temps:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temps_lastyear.append(temp_dict)

    # JSONIFY the list
    return jsonify(temps_lastyear)

# Start date only route
@app.route("/api/v1.0/<start_date>")
def startDate(start_date):
    # Start the session for the page
    session = Session(engine)

    # Query Measurement sqlite to get the min, max and avg result for the selected date ranges 
    start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # JSONIFY the object
    return jsonify(start_date)

# Start and end date route
@app.route("/api/v1.0/<start_date>/<end_date>")
def startAndEndDate(start_date, end_date):
    # Start the session for the page
    session = Session(engine)

    # Query Measurement sqlite to get the min, max and avg result for the selected date ranges    
    start_and_end_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # JSONIFY the object
    return jsonify(start_and_end_date)

# Allow for page debugging / log
if __name__ == '__main__':
    app.run(debug=True)