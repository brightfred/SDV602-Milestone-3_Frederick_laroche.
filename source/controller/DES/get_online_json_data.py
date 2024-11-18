"""
get online json data controller

This is my controller for working with my historical weather data in JSNDrop.
It takes data from my local WeatherData.csv file and puts it in JSNDrop.
Then other parts of my app can get the data from JSNDrop when they need it.

This controller:
Uploads data from WeatherData.csv to JSNDrop table weatherData
Gets data for specific cities and years from the table
Makes sure the data is sorted by months for the charts

This is used by:
historical_data.py and yearly_comparison.py when clicking Get JSON Data button

References:
Reference for JSNDrop: Comes from Todd examples files in Moodle
Reference for pandas: https://pandas.pydata.org/docs/user_guide/index.html
Reference for json: https://docs.python.org/3/library/json.html
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for lambda: https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
Reference for instance: https://docs.python.org/3/library/functions.html#isinstance
Reference for list: https://docs.python.org/3/library/stdtypes.html#list
Reference for DataFrame: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
import requests
import json
import pandas as pd

"""
My JSNDropService class for working with the weatherData table
This class:
Create and manage the weatherData table
Store data from my CSV file
Get data for specific cities and years
"""
class JSNDropService:
    def __init__(self):
        # Setup my JSNDrop connection info
        self.base_url = "https://newsimland.com/~todd/JSON/"
        self.token = "96d5a614-3acb-41b4-b7f6-b298368bf871"
        # Name for my weather data table
        self.table_name = "weatherData"

    def drop_table(self):
        """
        This function removes my weather table from JSNDrop
        I do this before uploading fresh data from my CSV
        """
        print("now dropping weather table from jsondrop...")
        cmd = {"tok": self.token, "cmd": {"DROP": self.table_name}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("done dropping the table")
        return response.json()

    def create_table(self):
        """
        This function makes a new weather table in JSNDrop
        The table can store:
        city: up to 50 characters for city name
        month: up to 50 characters for month name
        temperature: number
        year: number
        """
        print("making new weather table...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "CREATE": self.table_name,
                "EXAMPLE": {
                    "city": "A" * 50,  # This makes space for 50 characters
                    "month": "A" * 50, 
                    "temperature": 22.2,
                    "year": 2024,
                },
            },
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("new table is made")
        return response.json()

    def store_data(self, data):
        """
        This function saves weather data from my CSV into JSNDrop
        The data should have temperature for each month of each year
        """
        print("putting the data in jsondrop table...")
        cmd = {"tok": self.token, "cmd": {"STORE": self.table_name, "VALUE": data}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("done putting data in table")
        return response.json()

    def get_city_data(self, city, year):
        """
        This function gets data for one city and year from JSNDrop
        """
        print(f"getting data for {city} from jsondrop...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "SELECT": self.table_name,
                "WHERE": f"city = '{city}' AND year = {year}",
            },
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got the data from jsondrop")
        return response.json()

def upload_csv_to_jsondrop():
    """
    This function reads my WeatherData.csv file and puts it in JSNDrop
    I do this before getting any data so JSNDrop has the latest info every time user click the button
    """
    try:
        print("\n=== starting to put csv data in jsondrop ===")

        # Read my CSV file
        print("trying to read weather data file...")
        df = pd.read_csv("DataSet/WeatherData.csv")
        if df is None:
            print("couldnt read the weather file")
            return False

        # Setup my JSNDrop service
        jsn_service = JSNDropService()

        # Start fresh with new table by dropping and creating it
        jsn_service.drop_table()
        jsn_service.create_table()

        # Convert my data to format JSNDrop accepts
        data_to_upload = df.to_dict("records")
        result = jsn_service.store_data(data_to_upload)

        print("=== done putting csv data in jsondrop ===\n")
        return True

    except Exception as e:
        print(f"got error uploading to jsondrop: {str(e)}")
        return False

def get_city_year_data(city, year):
    """
    This function gets data for one city and year from JSNDrop
    It makes sure the data is sorted by months (Jan to Dec)
    Returns just the temperatures in the right order
    """
    try:
        jsn_service = JSNDropService()
        response = jsn_service.get_city_data(city, year)

        # Check if i got data back
        if response.get("JsnMsg") == "SUCCESS.SELECT" and isinstance(
            response.get("Msg"), list
        ):
            data = response["Msg"]
            df = pd.DataFrame(data)

            # This is the order i want my months in
            month_order = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            # Add a column that helps sort the months right
            df["month_order"] = df["month"].apply(lambda x: month_order.index(x))
            df = df.sort_values("month_order")

            # Get just the temperatures in the right order
            temps = df["temperature"].tolist()
            return temps

    except Exception as e:
        print(f"got error getting data: {str(e)}")
    return None

def accept(event, values, state):
    """
    This is my function that runs when someone clicks Get JSON Data
    It gets called from main.py when handling button events
    
    It does this:
    Uploads fresh data from CSV to JSNDrop
    Gets data for the city and year they picked
    Returns the temperatures if found
    """
    if event == "-FETCH-JSON-":
        try:
            print("\n=== starting to get jsondrop data ===")
            city = values["-NZ-CITY-"]  # Get city users picked
            year = values["-YEAR-"]  

            print("uploading fresh data...")
            if not upload_csv_to_jsondrop():
                print("couldnt upload the data")
                return None

            # Get the data for the city and year
            print(f"trying to get data for {city}...")
            json_data = get_city_year_data(city, year)

            if json_data:
                print(f"got {city}'s data")
                return json_data
            else:
                print(f"couldnt get data for {city}")

            print("=== done getting jsondrop data ===\n")

        except Exception as e:
            print(f"got error in json fetch: {str(e)}")

    return None