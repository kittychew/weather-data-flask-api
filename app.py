# Import the dependencies.
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
# Create engine using the `hawaii.sqlite` database file
database_path = "/Applications/Data Analysis Bootcamp/UofM-VIRT-DATA-PT-06-2024-U-LOLC/02_Challenges/10_SQL_Advanced/weather-data-flask-api/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement`
# and the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        "Welcome to the Hawaii Weather API!<br/><br/>"
        "Available Routes:<br/>"
        "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        "<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        "<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        "<a href='/api/v1.0/2017-01-01'>/api/v1.0/&lt;start&gt;</a><br/>"
        "<a href='/api/v1.0/2017-01-01/2017-08-01'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Find the most recent date in the data
    most_recent_date = db.session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

    # Go 12 months back from the most recent date
    twelve_months_ago = most_recent_date - timedelta(days=365)

    # Query data
    results = db.session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= twelve_months_ago).all()

    # Format as dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    results = db.session.query(Station.station, Station.name).all()
    stations_data = [{station: name} for station, name in results]
    return jsonify(stations_data)

@app.route('/api/v1.0/tobs')
def tobs():
    # Query the most-active station
    most_active_station = db.session.query(Measurement.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Get the latest date in the data
    most_recent_date = db.session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    twelve_months_ago = most_recent_date - timedelta(days=365)

    results = db.session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= twelve_months_ago).all()

    # Format results
    tobs_data = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end=None):
    start_date = datetime.strptime(start, '%Y-%m-%d')

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d')
        results = db.session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        results = db.session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date).all()

    stats_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(stats_data)

@app.teardown_appcontext
def close_session(exception):
    db.session.remove()

if __name__ == '__main__':
    app.run(debug=True)
