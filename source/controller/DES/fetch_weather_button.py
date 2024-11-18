"""
Fetch Weather button controller

This is my controller for getting weather data from OpenWeather API.
It gets called when someone clicks the Get Current Weather button in current_condition.py.
It gets the forecast data for a NZ city and stores it in JSNDrop for later use.

This controller:
Gets weather data from OpenWeather API
Stores it in my openweather table in JSNDrop
Updates the chart with the new data

References:
Reference for JSNDrop: Comes from Todd examples files in Moodle
Reference for OpenWeatherAPI: https://openweathermap.org/forecast5
Reference for requests: https://docs.python-requests.org/en/latest/
Reference for json: https://docs.python.org/3/library/json.html
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for list slicing: https://docs.python.org/3/tutorial/introduction.html#lists
Reference for string formatting: https://docs.python.org/3/library/string.html#formatstrings
Reference for list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
import requests
import json

# My API key for OpenWeather
OPEN_WEATHER_API_KEY = "b7eda5f8420789bab44ef47a8d11f1ae"

"""
My WeatherJSNDropService class for working with JSNDrop
This class helps me:
Make and manage the openweather table
Store weather data from the API
Get stored weather data for specific cities

This gets used by:
current_weather_merge.py to get NZ data for comparison
current_condition.py to show weather for one city
"""
class WeatherJSNDropService:
    def __init__(self):
        # Setup my JSNDrop connection info
        self.base_url = "https://newsimland.com/~todd/JSON/"
        self.token = "96d5a614-3acb-41b4-b7f6-b298368bf871"
        # Name of the table where i store OpenWeather API data
        self.table_name = "openweather"

    def drop_table(self):
        """
        This function removes my openweather table from JSNDrop
        I do this before adding new data to make sure it's fresh
        """
        print("now dropping the openweather table from jsondrop...")
        cmd = {"tok": self.token, "cmd": {"DROP": self.table_name}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("done dropping the table")
        return response.json()

    def create_table(self):
        """
        This function makes a new openweather table in JSNDrop
        The table can store:
        city: up to 50 characters for city name
        temperature: number (float) 
        timestamp: date and time like 2024-01-01 00:00:00
        """
        print("making new openweather table...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "CREATE": self.table_name,
                "EXAMPLE": {
                    "city": "A" * 50,  # This makes space for 50 characters
                    "temperature": 22.2,
                    "timestamp": "2024-11-10 00:00:00",
                },
            },
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("new table is created")
        return response.json()

    def store_data(self, data):
        """
        This function saves the weather data in my JSNDrop table
        The data comes from OpenWeather API and has temperature for next 24 hours
        """
        print("putting the weather data into jsondrop table...")
        cmd = {"tok": self.token, "cmd": {"STORE": self.table_name, "VALUE": data}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("done putting data in the table")
        return response.json()

    def get_city_data(self, city):
        """
        This function gets data for one city from my JSNDrop table
        Used by current_weather_merge.py when comparing cities
        """
        print(f"getting data for {city} from jsondrop...")
        cmd = {
            "tok": self.token,
            "cmd": {"SELECT": self.table_name, "WHERE": f"city = '{city}'"},
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got the data from jsondrop")
        return response.json()

def get_current_weather(city):
    """
    This function gets weather data from OpenWeather API
    It gets 24 hours of forecast in 3-hour section (8 section for 24 hours)
    Returns 3 things:
    forecast_data: ready to store in JSNDrop
    temps: just the temperatures for the chart
    times: the timestamps for the chart
    """
    try:
        print(f"getting weather data for {city} from openweather api...")
        # Make the API URL with my key and city name
        url = (
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}"
            f"&units=metric&appid={OPEN_WEATHER_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        # Check if API request worked
        if data.get("cod") != "200":
            print(f"cannot get data for {city} from api")
            return None, None, None

        # Get next 24 hours of forecast
        print("got the weather data from api, now making it ready for jsondrop...")
        forecast_data = []
        # Get first 8 entries (24 hours) from API data
        for entry in data["list"][:8]:  # Each entry is 3 hours, so 8 entries = 24 hours
            # Example taken from : https://openweathermap.org/forecast5 and https://max-coding.medium.com/create-a-weather-map-using-openweather-api-in-python-f048473ca6ae
            forecast_data.append(
                {
                    "city": city,
                    "temperature": entry["main"]["temp"],
                    "timestamp": entry["dt_txt"],
                }
            )

        # Make lists of just temps and times for the chart
        temps = [entry["main"]["temp"] for entry in data["list"][:8]]
        times = [entry["dt_txt"] for entry in data["list"][:8]]

        print("weather data is ready for jsondrop")
        return forecast_data, temps, times
    except Exception as e:
        print(f"got error when getting weather: {str(e)}")
        return None, None, None

def accept(event, values, state):
    """
    This is my function that runs when someone clicks Get Current Weather
    It gets called from my main.py when dealing with button events
    It works with current_condition.py to update the chart

    It does these things:
    Gets weather data for the NZ city they picked
    Stores it in JSNDrop
    Updates the chart with new data
    """
    keep_going = True

    if event == "-FETCH-WEATHER-":
        try:
            window = state["view"]  # The window showing right now
            nz_city = values["-NZ-CITY-"]  # Get city user picked

            print("\n=== starting weather fetch process ===")

            # Setup my JSNDrop service
            jsn_service = WeatherJSNDropService()

            # Get fresh data from OpenWeather API
            forecast_data, nz_temps, times = get_current_weather(nz_city)
            if forecast_data and nz_temps and times:
                # Drop old table to start fresh
                jsn_service.drop_table()

                # Make new table
                jsn_service.create_table()

                # Store the new data
                jsn_service.store_data(forecast_data)

                print("now making the chart with the data from jsondrop...")

                # Make the data dictionary that my chart needs
                weather_data = {
                    "city": nz_city,
                    "temp_history": nz_temps,
                    "time_labels": times,
                    "unit": "°C",
                    "data_type": values.get("-DATATYPE-", "Temperature"),
                }

                # Update the chart when we have new data
                if "update_chart" in state:
                    state["update_chart"](weather_data)
                    print("chart is updated with new data")
                else:
                    print("cannot update the chart")
            else:
                print(f"could not get weather data for {nz_city}")

            print("=== weather fetch process finished ===\n")

        except Exception as e:
            print(f"got error in fetch weather: {str(e)}")

    return keep_going