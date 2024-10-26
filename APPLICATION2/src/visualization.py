import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Path to CSV file (assuming it's being updated every 5 minutes)
data_file = 'data/daily_summary.csv'

# Function to load and process weather data
def load_weather_data():
    df = pd.read_csv(data_file)
    df['date'] = pd.to_datetime(df['date'])

    # Filter data to only include today's data
    today = pd.Timestamp(datetime.now().date())
    df = df[df['date'] == today]
    
    return df

# Function to calculate differences from previous averages
def calculate_differences(df):
    df['temp_diff'] = df['avg_temp'].diff().fillna(0)
    df['humidity_diff'] = df['avg_humidity'].diff().fillna(0)
    df['wind_diff'] = df['avg_wind_speed'].diff().fillna(0)
    return df

# Function to update the plot dynamically
def update_plot(i):
    df = load_weather_data()
    if df.empty:
        print("No data for today.")
        return

    df = calculate_differences(df)

    # Clear the previous plot
    for ax in axs:
        ax.clear()

    # Plot Temperature
    axs[0].plot(df['date'], df['avg_temp'], marker='o', label='Avg Temp (°C)', color='blue')
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].set_title('Temperature Overview')
    axs[0].legend(loc='upper right')

    # Annotate with changes in temperature
    for j in range(len(df)):
        axs[0].annotate(f"{df['temp_diff'].iloc[j]:+.2f}°C", (df['date'].iloc[j], df['avg_temp'].iloc[j]), textcoords="offset points", xytext=(0,5), ha='center')

    # Plot Humidity
    axs[1].plot(df['date'], df['avg_humidity'], marker='o', label='Avg Humidity (%)', color='blue')
    axs[1].set_ylabel('Humidity (%)')
    axs[1].set_title('Humidity Overview')
    axs[1].legend(loc='upper right')

    # Annotate with changes in humidity
    for j in range(len(df)):
        axs[1].annotate(f"{df['humidity_diff'].iloc[j]:+.2f}%", (df['date'].iloc[j], df['avg_humidity'].iloc[j]), textcoords="offset points", xytext=(0,5), ha='center')

    # Plot Wind Speed
    axs[2].plot(df['date'], df['avg_wind_speed'], marker='o', label='Avg Wind Speed (m/s)', color='blue')
    axs[2].set_ylabel('Wind Speed (m/s)')
    axs[2].set_title('Wind Speed Overview')
    axs[2].legend(loc='upper right')

    # Annotate with changes in wind speed
    for j in range(len(df)):
        axs[2].annotate(f"{df['wind_diff'].iloc[j]:+.2f} m/s", (df['date'].iloc[j], df['avg_wind_speed'].iloc[j]), textcoords="offset points", xytext=(0,5), ha='center')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Adjust layout for better spacing
    plt.tight_layout()

# Set up the plot
fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Create an animation that updates every 5 minutes (300 seconds)
ani = FuncAnimation(fig, update_plot, interval=300000)  # 300000 ms = 5 minutes

# Display the plot
plt.show()
