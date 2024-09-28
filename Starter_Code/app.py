# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime


#################################################
# Database Setup
#################################################
# Create engine using the `hawaii.sqlite` database file
database_path = "/Applications/Data Analysis Bootcamp/UofM-VIRT-DATA-PT-06-2024-U-LOLC/02_Challenges/10_SQL_Advanced/sql-alchemy-challenge/Starter_Code/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement`
# and the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return "Welcome to the Hawaii Weather API!"

@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    precipitation_data = [{date: prcp} for date, prcp in results]
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station, Station.name).all()
    stations_data = [{station: name} for station, name in results]
    return jsonify(stations_data)

@app.teardown_appcontext
def close_session(exception):
    session.remove()

if __name__ == '__main__':
    app.run(debug=True)