from turtle import color
import gpxpy
import pandas as pd
import numpy as np
import geopy.distance
from numpy_ext import rolling_apply
import matplotlib.pyplot as plt
import requests

API_KEY = 'ak_7EcvB1jS_s1dFWhyfDgVU2ntd'
BATCH_SIZE = 50  # 512 for paid customers.

def rolling_metric_pace(duration, distance):
    return (duration.sum() / 60) / (distance.sum() / 1000)

def get_uthr_df(gpx_obj):
    # Convert to a dataframe one point at a time.
    points = []
    for segment in gpx.tracks[0].segments:
        for p in segment.points:
            points.append({
                'time': p.time,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'elevation': p.elevation,
            })
    df = pd.DataFrame.from_records(points)

    # Cumulative distance.
    coords = [(p.latitude, p.longitude) for p in df.itertuples()]
    df['distance'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
    df['cumulative_distance'] = df.distance.cumsum()


    # Timing.
    df['duration'] = df.time.diff().dt.total_seconds().fillna(0)
    df['cumulative_duration'] = df.duration.cumsum()
    df['pace_metric'] = pd.Series((df.duration / 60) / (df.distance / 1000)).bfill()

    #Convert elevation from meters to feet
    df['elevation'] = df['elevation'] * 3.28084
    return df


if __name__ == '__main__':
    gpx_path = 'uhtr_2019.gpx'
    with open(gpx_path) as f:
        gpx = gpxpy.parse(f)
    df_2019 = get_uthr_df(gpx)

    gpx_path = 'uhtr_2022.gpx'
    with open(gpx_path) as f:
        gpx = gpxpy.parse(f)
    df_2022 = get_uthr_df(gpx)

    ax1 = df_2019.plot(x='cumulative_distance',y='elevation',color='Red',label='2019 Elevation')
    ax1 = df_2022.plot(x='cumulative_distance',y='elevation',color='Blue',label='2022 Elevation',ax=ax1)

    #plt.plot(df['cumulative_duration'],df['elevation'])
    plt.show()

