import os
import pandas as pd
from datetime import datetime
from threading import Timer
import requests
from config import API_KEY, CITIES, INTERVAL, TEMP_THRESHOLD

processed_files = set()  # To track which files have been processed

# Function to fetch data from the OpenWeatherMap API
def fetch_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url)
    data = response.json()
    weather_info = {
        'city': city,
        'main': data['weather'][0]['main'],
        'temp': data['main']['temp'] - 273.15,  # Kelvin to Celsius
        'feels_like': data['main']['feels_like'] - 273.15,
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'dt': data['dt']
    }
    return weather_info

# Function to fetch and store weather data for all cities
def fetch_and_store_data():
    all_weather_data = []
    for city in CITIES:
        data = fetch_weather_data(city)
        all_weather_data.append(data)
    df = pd.DataFrame(all_weather_data)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'data/weather_data_{timestamp}.csv'
    df.to_csv(file_name, index=False)
    print(f"Data fetched and stored at {timestamp}")
    return file_name

# Function to calculate daily summary from the weather data
def calculate_daily_summary(df):
    df['date'] = pd.to_datetime(df['dt'], unit='s').dt.date
    summary = df.groupby('date').agg(
        avg_temp=('temp', 'mean'),
        max_temp=('temp', 'max'),
        min_temp=('temp', 'min'),
        avg_humidity=('humidity', 'mean'),
        max_humidity=('humidity', 'max'),
        min_humidity=('humidity', 'min'),
        avg_wind_speed=('wind_speed', 'mean'),
        max_wind_speed=('wind_speed', 'max'),
        min_wind_speed=('wind_speed', 'min'),
        dominant_condition=('main', lambda x: x.mode()[0])
    ).reset_index()
    summary.to_csv('data/daily_summary.csv', index=False)
    return summary

# Function to check for alerts based on temperature threshold
def check_alerts(df):
    for index, row in df.iterrows():
        if row['temp'] > TEMP_THRESHOLD:
            print(f"Alert! Temperature in {row['city']} exceeded {TEMP_THRESHOLD}°C")

# Function to process new weather data files
def process_weather_data():
    files = [f for f in os.listdir('data') if f.startswith('weather_data') and f not in processed_files]
    
    if not files:
        print("No new files to process.")
        return
    
    all_data = pd.concat([pd.read_csv(f'data/{file}') for file in files])
    daily_summary = calculate_daily_summary(all_data)
    check_alerts(all_data)
    
    # Mark files as processed
    processed_files.update(files)
    
    return daily_summary

# Scheduler for fetching new data every interval
def schedule_data_retrieval():
    # Fetch and store new data
    new_file = fetch_and_store_data()
    
    # Process the new data
    process_weather_data()
    
    # Schedule the next fetch and processing after INTERVAL seconds
    Timer(INTERVAL, schedule_data_retrieval).start()

if __name__ == '__main__':
    # Start the process of data retrieval and processing
    schedule_data_retrieval()
