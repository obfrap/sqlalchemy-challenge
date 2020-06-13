#matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc


##############################################################
# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()

# reflect the tables|
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station







##############################################################
# Flask Setup
# Import Flask
from flask import Flask
from flask import jsonify

# Create app
app = Flask(__name__)

# Home route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"This is the homepage for SQLAlchemy Challenge Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Enter start date or end date at end of url below to search for Min, Average and Max temperatures over time range <br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Format Examples:<br/>"
        f"/api/v1.0/2010-01-18<br/>"
        f"/api/v1.0/2010-01-18/2017-08-17"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create session
    session = Session(engine)

    # Run query
    results=session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #Create Dictionary of results
    date_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_precip.append(prcp_dict)

    return jsonify(date_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    # Run query
    results=session.query(Station.station, Station.name).all()

    session.close()

    #Create Dictionary of results
    station_name = []
    for station, name in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_name.append(station_dict)

    return jsonify(station_name)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Run query
    station_inf = session.query(Measurement.station,  
                    func.count(Measurement.station).label("total_count"),
                    )
    session.close()
    station_inf = station_inf.group_by(Measurement.station).order_by(desc("total_count"))
    var = station_inf[0][0]
    
    #Create new session and query to pull all results for var my variable
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    lastrow_convert = dt.datetime.strptime(last_row.date, '%Y-%m-%d')
    end_date=lastrow_convert
    # Subtract 365 days
    start_date = lastrow_convert - pd.Timedelta('365 days')
    #Convert back to format that data table is using for query purposes
    start_date_conv=dt.datetime.strftime(start_date, '%Y-%m-%d')
    start_date_conv
    session.close()

    session = Session(engine)

    station_temp=session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == var).filter(Measurement.date >= start_date_conv).filter(Measurement.date <= end_date).order_by(Measurement.date).all()
    session.close()
    return jsonify(station_temp)

@app.route("/api/v1.0/<start>")
def start(start=None):
    # Start new session
    session = Session(engine)
    
    #Query to pull in dates and temps for <start> range to end of dataset.
    from_start = session.query(Measurement.date, func.min(Measurement.tobs).label("Min"), func.avg(Measurement.tobs).label("Avg"),
                            func.max(Measurement.tobs).label("Max")).filter(Measurement.date >= start).group_by(
                            Measurement.date).all()
    
    session.close()
    # Return results
    return jsonify(from_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    #Start new session
    session = Session(engine)
    #Query to pull in dates and temps for <start> range to <end> range given
    start_to_end = session.query(Measurement.date, func.min(Measurement.tobs).label("Min"), func.avg(Measurement.tobs).label("Avg"),
                                func.max(Measurement.tobs).label("Max")).filter(Measurement.date >= start).filter(
                                Measurement.date <= end).group_by(Measurement.date).all()
   
    session.close()
    # Return results 
    return jsonify(start_to_end)   


if __name__ == "__main__":
    app.run(debug=True)