import pandas as pd
from datetime import datetime, timedelta
import time

# Load hvfhv data
# hvfhs_cols = [
#     "pickup_datetime",
#     "dropoff_datetime",
#     "PULocationID",
#     "DOLocationID",
#     "trip_miles",
#     "trip_time",
#     "base_passenger_fare",
#     "tolls",
#     "tips",
#     "congestion_surcharge",
#     "airport_fee",
#     "shared_match_flag",
#     "wav_match_flag",
# ]
# hvfhv = pd.read_parquet("fhvhv_tripdata_2024-12.parquet", columns=hvfhs_cols)
# hvfhv = hvfhv.rename(
#     columns={
#         "trip_miles": "trip_distance",
#         "base_passenger_fare": "fare_amount",
#         "tolls": "tolls_amount",
#     }
# )
# # Load yellow taxi data

# yellow_taxi = pd.read_parquet(
#     "yellow_tripdata_2024-12.parquet",
#     columns=[
#         "tpep_pickup_datetime",
#         "tpep_dropoff_datetime",
#         "PULocationID",
#         "DOLocationID",
#         "trip_distance",
#         "fare_amount",
#         "tolls_amount",
#         "tip_amount",
#         "congestion_surcharge",
#         "Airport_fee",
#     ],
# )


# yellow_taxi = yellow_taxi.rename(
#     columns={
#         "tpep_pickup_datetime": "pickup_datetime",
#         "tpep_dropoff_datetime": "dropoff_datetime",
#         "tip_amount": "tips",
#     }
# )

yellow_taxi = pd.read_csv("/Users/linxinyu/Documents/umich/courses/640/yellow_taxi_clean1.csv",low_memory=False)
hvfhv = pd.read_csv("/Users/linxinyu/Documents/umich/courses/640/hvfhv_clean1.csv")

rate = pd.read_csv('/Users/linxinyu/Documents/umich/courses/640/Estimated_RatePerDistance.csv')
speed_to_rate = dict(zip(rate['Speed'], rate['RatePerDistance']))
yellow_taxi['pickup_datetime'] = pd.to_datetime(yellow_taxi['pickup_datetime'], errors='coerce')
yellow_taxi['dropoff_datetime'] = pd.to_datetime(yellow_taxi['dropoff_datetime'], errors='coerce')
yellow_taxi['trip_time'] = (yellow_taxi['dropoff_datetime'] - yellow_taxi['pickup_datetime']).dt.total_seconds()

def map_speed_to_rate(speed):
    if pd.isna(speed) or speed <= 0:
        return pd.NA
    if speed > 100:
        speed = 100
    speed = int(speed)
    return speed_to_rate.get(speed, pd.NA)

def add_carbon_emission(df, trip_miles_col, trip_time_col):
    df = df.copy()
    df = df[df[trip_time_col] > 0]
    df['avg_speed_mph'] = df[trip_miles_col] / (df[trip_time_col] / 3600)
    df['RatePerDistance'] = df['avg_speed_mph'].apply(map_speed_to_rate)
    df['CarbonEmission_g'] = df['RatePerDistance'] * df[trip_miles_col]
    return df

hvfhv_processed = add_carbon_emission(hvfhv, trip_miles_col='trip_miles', trip_time_col='trip_time')
yellow_processed = add_carbon_emission(yellow_taxi, trip_miles_col='trip_distance', trip_time_col='trip_time')
hvfhv_processed.to_csv('hvfhv_processed.csv', index=False)
yellow_processed.to_csv('yellow_processed.csv', index=False)


# air = pd.read_csv('/Users/linxinyu/Documents/umich/courses/640/air_quality_grouped.csv')

# air['local_hour'] = air['local_hour'].str.slice(0, 19)

# df_grouped = air.groupby(['local_hour', 'region'], as_index=False).agg({
#     'NO2': 'mean',
#     'OZONE': 'mean',
#     'PM2.5': 'mean'
# })

# df_grouped.to_csv('air_quality_grouped.csv', index=False)

def enrich_with_air_quality(df_trip, df_air, pickup_datetime_col='pickup_datetime', pickup_borough_col='pickup_borough'):


    df_trip = df_trip.copy()
    df_trip[pickup_datetime_col] = pd.to_datetime(df_trip[pickup_datetime_col])
    df_trip['local_hour'] = df_trip[pickup_datetime_col].dt.floor('H').astype(str)
    df_trip['region'] = df_trip[pickup_borough_col].str.lower()

    df_air = df_air.copy()
    df_air['local_hour'] = df_air['local_hour'].str.slice(0, 19)
    df_air['region'] = df_air['region'].str.lower()

    df_enriched = df_trip.merge(df_air, on=['local_hour', 'region'], how='left')

    return df_enriched

# hvfhv_enriched = enrich_with_air_quality(hvfhv, air)

# yellow_enriched = enrich_with_air_quality(yellow_taxi, air,pickup_datetime_col='tpep_pickup_datetime')

# hvfhv_enriched.to_csv('hvfhv_enriched.csv', index=False)
# yellow_enriched.to_csv('yellow_enriched.csv', index=False)


# def process_weather_file(file_path, region_name):

#     df = pd.read_excel(file_path)
#     df = df[['Date', 'Maximum', 'Minimum']]
#     df['avg_temp'] = (df['Maximum'] + df['Minimum']) / 2
#     df['region'] = region_name
#     df = df.rename(columns={'Date': 'pickup_date'})
#     df = df[['pickup_date', 'region', 'avg_temp']]
#     return df


# bronx_weather = process_weather_file('/Users/linxinyu/Documents/umich/courses/640/bronk.xlsx', 'bronx')
# brooklyn_weather = process_weather_file('/Users/linxinyu/Documents/umich/courses/640/brooklyn.xlsx', 'brooklyn')
# manhattan_weather = process_weather_file('/Users/linxinyu/Documents/umich/courses/640/manhattan.xlsx', 'manhattan')
# queens_weather = process_weather_file('/Users/linxinyu/Documents/umich/courses/640/queens.xlsx', 'queens')
# staten_weather = process_weather_file('/Users/linxinyu/Documents/umich/courses/640/staten_island.xlsx', 'staten_island')



# bronx_weather['region'] = 'bronx'
# brooklyn_weather['region'] = 'brooklyn'
# manhattan_weather['region'] = 'manhattan'
# queens_weather['region'] = 'queens'
# staten_weather['region'] = 'staten_island'

# weather_all = pd.concat([
#     bronx_weather,
#     brooklyn_weather,
#     manhattan_weather,
#     queens_weather,
#     staten_weather
# ], axis=0)

# weather_all.rename(columns={'date': 'pickup_date'}, inplace=True)

# def enrich_with_weather(df_trip, weather_all_df, pickup_datetime_col='pickup_datetime', pickup_borough_col='pickup_borough'):

#     df_trip = df_trip.copy()

#     df_trip[pickup_datetime_col] = pd.to_datetime(df_trip[pickup_datetime_col])
#     df_trip['pickup_date'] = df_trip[pickup_datetime_col].dt.date.astype(str)
#     df_trip['region'] = df_trip[pickup_borough_col].str.lower()

#     weather_all_df = weather_all_df.copy()
#     weather_all_df['pickup_date'] = weather_all_df['pickup_date'].astype(str)
#     weather_all_df['region'] = weather_all_df['region'].str.lower()

#     df_enriched = df_trip.merge(weather_all_df, on=['pickup_date', 'region'], how='left')

#     return df_enriched

# hvfhv_enriched = enrich_with_weather(hvfhv, weather_all)
# yellow_enriched = enrich_with_weather(yellow_taxi, weather_all, pickup_datetime_col='tpep_pickup_datetime')

# hvfhv_enriched.to_csv('hvfhv.csv', index=False)
# yellow_enriched.to_csv('yellow.csv', index=False)
# weather_all.to_csv('weather_all.csv', index=False)

# zone_lookup = pd.read_csv('/Users/linxinyu/Documents/umich/courses/640/taxi_zone_lookup.csv')

# taxi_to_borough = dict(zip(zone_lookup['LocationID'], zone_lookup['Borough']))
# yellow_taxi['pickup_borough'] = yellow_taxi['PULocationID'].map(taxi_to_borough)
# yellow_taxi['dropoff_borough'] = yellow_taxi['DOLocationID'].map(taxi_to_borough)
# target_boroughs = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
# taxi_filtered = yellow_taxi[
#     (yellow_taxi['pickup_borough'].isin(target_boroughs)) |
#     (yellow_taxi['dropoff_borough'].isin(target_boroughs))
# ]
# taxi_filtered.to_csv('yellow_taxi_filtered.csv', index=False)

# hvfhv_to_borough = dict(zip(zone_lookup['LocationID'], zone_lookup['Borough']))
# hvfhv['pickup_borough'] = hvfhv['PULocationID'].map(hvfhv_to_borough)
# hvfhv['dropoff_borough'] = hvfhv['DOLocationID'].map(hvfhv_to_borough)
# hvfhv_filtered = hvfhv[
#     (hvfhv['pickup_borough'].isin(target_boroughs)) |
#     (hvfhv['dropoff_borough'].isin(target_boroughs))
# ]
# hvfhv_filtered.to_csv('hvfhv_filtered.csv', index=False)


# citi_df1 = pd.read_csv(
#     "202412-citibike-tripdata/202412-citibike-tripdata_1.csv",
#     parse_dates=["started_at", "ended_at"],
# )
# citi_df2 = pd.read_csv(
#     "202412-citibike-tripdata/202412-citibike-tripdata_2.csv",
#     parse_dates=["started_at", "ended_at"],
# )
# citi_df3 = pd.read_csv(
#     "202412-citibike-tripdata/202412-citibike-tripdata_3.csv",
#     parse_dates=["started_at", "ended_at"],
# )

# citi_bike = pd.concat([citi_df1, citi_df2, citi_df3], ignore_index=True)
