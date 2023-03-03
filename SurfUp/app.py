# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

# Import SQLAlchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask dependencies
from flask import Flask, jsonify

# Set up the database

engine = create_engine("sqlite:///resources/hawaii.sqlite")

# Reflect the database into  classes
Base = automap_base()
Base.prepare(autoload_with=engine)


# Save  references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create  session (link) from Python to the DB
session = Session(engine)

# Set up Flask
app = Flask(__name__)



# Define the home page and list all available routes
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (enter date as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date/end_date (enter dates as YYYY-MM-DD/YYYY-MM-DD)"
    )

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a json list of stations from the dataset"""
    # Performing a query to list the stations names and codes
    stations = session.query(Station.name, Station.station).all()
    # Closing Session
    session.close()
    # Converting list of tuples into normal list
    station_list = list(np.ravel(stations))
    return jsonify(station_list)

# Convert the query results from your precipitation analysis
#  (i.e. retrieve only the last 12 months of data) to a dictionary
#  using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
       
    # Query the last 12 months of precipitation data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    query_date = last_date - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()


  # Close the session
    session.close()


    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_dict = {date: prcp for date, prcp in prcp_data}


    # Return the JSON representation of your dictionary
    return jsonify(prcp_dict)




@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
     
    # Query the dates and temperature observations of the most-active station for the previous year of data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    query_date = last_date - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == 'USC00519281').all()
    # Close the session
    session.close()
    # Convert the query results to a list of dictionaries
    tobs_list = list(np.ravel(tobs_data))

    # Return the JSON representation of the list
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date."""
    # Create a session with the database
    session = Session(engine)
    # Query the minimum, average, and maximum temperatures for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    # Close the session
    session.close()
    # Create a dictionary to store the results
    temp_dict = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    # Return the JSON representation of the dictionary
    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    # Create a session with the database
    session = Session(engine)
    # Query the minimum, average, and maximum temperatures for all dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    # Close the session
    session.close()
    # Create a dictionary to store the results
    temp_dict = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    # Return the JSON representation of the dictionary
    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)