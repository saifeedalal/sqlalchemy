from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

# Reflect Tables into SQLAlchemy ORM
# Python SQL toolkit and Object Relational Mapper

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, bindparam

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Exploratory Climate Analysis
# Design a query to retrieve the last 12 months from 08-23-2017 of precipitation data and plot the results
# Calculate the date 1 year ago from today

query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
# print(query_date)
# Perform a query to retrieve the data and precipitation scores
yearly_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= query_date).\
                all()

#print(yearly_data)
#print(yearly_data)
# Save the query results as a Pandas DataFrame and set the index to the date column
yearly_prcp_df = pd.DataFrame(yearly_data)
yearly_prcp_df.set_index('date', inplace=True)
yearly_prcp_df.fillna(value=0, inplace=True)

# Sort the dataframe by date
yearly_prcp_df.sort_index(inplace=True)
# yearly_prcp_df.head(10)

# Use Pandas Plotting with Matplotlib to plot the data
multi_plot = yearly_prcp_df.plot(kind="bar", figsize=(15,3))
plt.title("Precipitation Analysis")
plt.show()
plt.tight_layout()

# Rotate the xticks for the dates
multi_plot.set_xticklabels(yearly_prcp_df.index, rotation=45)

# Use Pandas to calcualte the summary statistics for the precipitation data

yearly_prcp_df.describe()

# How many stations are available in this dataset?
stations_count = session.query(Measurement.station).distinct().count()
print(f'There are [{stations_count}] stations in the dataset')

# What are the most active stations?
# List the stations and the counts in descending order.

active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()

print(f'Active stations in descending order : {active_stations}')

# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?

temp_details = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).all()
#temp_details

# Choose the station with the highest number of temperature observations.
activemost_station = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).limit(1).all()

print(f'Most active station is : {activemost_station[0][0]}')


# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
activemost_station_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == activemost_station[0][0],Measurement.date >= query_date).\
                    order_by(Measurement.date).\
                    all()

activemost_station_df = pd.DataFrame(activemost_station_data,columns={'Date','Temp'})
#activemost_station_df

multi_plot = activemost_station_df.plot(kind="hist", bins=12, figsize=(10,3))

bins=100, 
plt.title(f'Temperature Analysis for station : {activemost_station[0][0]}')
plt.show()
plt.tight_layout()

# Rotate the xticks for the dates
multi_plot.set_xticklabels(activemost_station_df.Date, rotation=45)


# Write a function called `calc_temps` that will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.

calc_temps_result = calc_temps('2016-10-01', '2016-10-07')

print (calc_temps_result)

# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)

x = [1]
average = [calc_temps_result[0][1]]
variance = [calc_temps_result[0][2] - calc_temps_result[0][0]]

x_pos = [i for i, _ in enumerate(x)]

plt.bar(x_pos, average, color='green', yerr=variance)
plt.xlabel("Trip")
plt.ylabel("Temp")
plt.title("Trip Avg Temp")

plt.xticks(x_pos, x)

plt.show()


# Calculate the rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation

prcp_data = session.query( func.sum(Measurement.prcp),Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).\
                    filter(Measurement.station == Station.station,Measurement.date >= '2016-10-01',Measurement.date <= '2016-10-07').\
                    group_by(Measurement.station).\
                    order_by(func.sum(Measurement.prcp).desc()).\
                    all()
print(prcp_data)

## Optional Challenge Assignment

# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")

# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip

# Use the start and end date to create a range of dates
date_list  = ["10-01-2016","10-02-2016","10-03-2016","10-04-2016","10-05-2016","10-06-2016","10-07-2016"]
#date_list
# Stip off the year and save a list of %m-%d strings

formatted_date_list = ["10-01","10-02","10-03","10-04","10-05","10-06","10-07"]

# Loop through the list of %m-%d strings and calculate the normals for each date
normals_max_list = [daily_normals(date)[0][2] for date in formatted_date_list]
#print(normals_max_list)

normals_min_list = [daily_normals(date)[0][0] for date in formatted_date_list]
#print(normals_min_list)

normals_avg_list = [daily_normals(date)[0][1] for date in formatted_date_list]
#print(normals_avg_list)

# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index

normals_df = pd.DataFrame(normals_max_list,columns = {'Max'})
normals_df['Min'] = normals_min_list
normals_df['Avg'] = normals_avg_list
normals_df['Date'] = date_list
normals_df.set_index('Date',inplace=True)

# Plot the daily normals as an area plot with `stacked=False`
fig1 = normals_df.plot(kind='area',stacked=False)
plt.show()
plt.title("Normals Plot")
plt.xticks(np.arange(7), normals_df.index, rotation ='45')

#--------------------------------------------------
# Getting dates and temperature for last one year
yearly_temp_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= query_date).\
                all()

yearly_temp_dict = {}
yearly_temp_dict = yearly_temp_data

#------------------------------------------------------
# Getting list of unique stations
station_list = session.query(Station.station).\
                distinct().\
                all()

#------------------------------------------------------
# Getting temperature for last one year
temp_list = session.query(Measurement.tobs).\
                filter(Measurement.date >= query_date).\
                all()

#-------------------------------------------------------

#Create an app, being sure to pass __name__
app = Flask(__name__)
    
@app.route("/")
def home():
    
    return "<h3>Available Routes:</h3>\
            <h5>/api/v1.0/precipitation</h5>\
            <h5>/api/v1.0/stations</h5>\
            <h5>/api/v1.0/tobs</h5>\
            <h5>/api/v1.0/<start></h5>\
            <h5>/api/v1.0/<start>/<end></h5>"

@app.route("/api/v1.0/precipitation")
def precipitation():

    return (jsonify(yearly_temp_dict))

@app.route("/api/v1.0/stations")
def stations():

    return (jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():

    return (jsonify(temp_list))

@app.route('/api/v1.0/<start>')
def temp_range(start_date):
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    #create dictionary from result
    temps_dictionary = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dictionary)

@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_range1(start_date, end_date):
    #query
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    #create dictionary from result
    temps_dictionary1 = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dictionary1)

if __name__ == '__main__':
     app.run(debug=False)