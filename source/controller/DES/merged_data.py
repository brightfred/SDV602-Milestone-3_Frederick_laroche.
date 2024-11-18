"""
merged data controller

This is my controller for merging historical weather data from NZ and Canada.
It takes NZ data from weatherData table and Canadian data from CanadianWeatherData.csv,
combines them in a new mergedWeatherData table in JSNDrop.

This controller is used by:
historical_data.py when Create Merged Data button is clicked
yearly_comparison.py when Get (NZ+CAN) Merged Data button is clicked

References:
Reference for JSNDrop: Comes from Todd examples files in Moodle
Reference for pandas: https://pandas.pydata.org/docs/user_guide/index.html
Reference for json: https://docs.python.org/3/library/json.html
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for lambda: https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
Reference for list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
Reference for len: https://docs.python.org/3/library/functions.html#len
Reference for string formatting: https://docs.python.org/3/library/string.html#formatstrings
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
import requests
import json
import pandas as pd

"""
My JSNDropMergeService class for working with the merged data table
This class helps me:
Make and manage the mergedWeatherData table
Get NZ data from weatherData table
Store combined NZ and Canadian data

The tables it uses are:
weatherData: has the NZ data (managed by get_online_json_data.py)
mergedWeatherData: where i put both NZ and Canadian data together
"""
class JSNDropMergeService:
    def __init__(self):
        # Setup my JSNDrop connection
        self.base_url = "https://newsimland.com/~todd/JSON/"
        self.token = "96d5a614-3acb-41b4-b7f6-b298368bf871"
        # Names for my tables
        self.weather_table = "weatherData"  # This has NZ data
        self.merged_table = "mergedWeatherData"  # This will have both datasets

    def drop_merged_table(self):
        """
        This function removes my merged data table from JSNDrop by dropping it
        I do this before making a new one so i get fresh combined data
        """
        print("removing old merged table...")
        cmd = {"tok": self.token, "cmd": {"DROP": self.merged_table}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("old merged table is gone")
        return response.json()

    def create_merged_table(self):
        """
        This function makes a new merged data table in JSNDrop
        The table can store:
        city: up to 50 characters for city name
        country: 
        month: up to 50 characters for month nam
        temperature: number 
        year: number
        """
        print("making new merged table...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "CREATE": self.merged_table,
                "EXAMPLE": {
                    "city": "A" * 50,
                    "country": "New Zealand",
                    "month": "A" * 50,
                    "temperature": 22.2,
                    "year": 2024,
                },
            },
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("new merged table is ready")
        return response.json()

    def get_nz_data(self):
        """
        This function gets all NZ data from weatherData table
        I use ALL command to get everything because i want all cities and years
        """
        print("getting nz data from weather table...")
        cmd = {"tok": self.token, "cmd": {"ALL": self.weather_table}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got nz data ok")
        return response.json()

    def store_merged_data(self, data):
        """
        This function saves the combined NZ and Canadian data in my merged table
        The data should have both countries records with country names added to tell them apart
        """
        print("putting all data in merged table...")
        cmd = {"tok": self.token, "cmd": {"STORE": self.merged_table, "VALUE": data}}
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("data is in merged table")
        return response.json()

    def get_comparison_data(self, nz_city, canadian_city, year):
        """
        This function gets data for two specific cities and a year
        I use OR in the WHERE to get both cities at once.I Had error with AND but Or was working as expected
        """
        print(f"getting data for {nz_city} and {canadian_city}...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "SELECT": self.merged_table,
                "WHERE": f"(city = '{nz_city}' OR city = '{canadian_city}') AND year = {year}",
            },
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got both cities data")
        return response.json()

def create_merged_dataset():
    """
    This function combines NZ and Canadian weather data into one dataset
    It does this:
    Makes a fresh merged table
    Gets NZ data from weatherData table
    Gets Canadian data from CSV file
    Adds country names to tell them apart
    Combines them into one dataset
    Stores the combined data in mergedWeatherData table
    
    Returns True if everything worked, False if something went wrong
    """
    try:
        print("\n=== starting to make merged dataset ===")
        jsn_service = JSNDropMergeService()

        # Start fresh with new table by dropping and creating it
        jsn_service.drop_merged_table()
        jsn_service.create_merged_table()

        # Get NZ data and add country name 
        print("getting nz data...")
        nz_data = jsn_service.get_nz_data()
        if nz_data.get("JsnMsg") == "SUCCESS.ALL":
            nz_records = nz_data.get("Msg", [])
            # Add New Zealand as country to each record
            for record in nz_records:
                record["country"] = "New Zealand"
            print(f"got {len(nz_records)} nz records")
        else:
            print("couldnt get nz data")
            return False

        # Get Canadian data from CSV file
        print("getting canadian data from file...")
        canadian_df = pd.read_csv("DataSet/CanadianWeatherData.csv")
        if not canadian_df.empty:
            canadian_records = canadian_df.to_dict("records")
            # Add Canada as country to each record
            for record in canadian_records:
                record["country"] = "Canada"
            print(f"got {len(canadian_records)} canadian records")
        else:
            print("couldnt get canadian data")
            return False

        # Put both datasets in the merged table
        print("putting both datasets together...")
        all_records = nz_records + canadian_records
        jsn_service.store_merged_data(all_records)

        print("=== done making merged dataset ===\n")
        return True

    except Exception as e:
        print(f"got error making merged dataset: {str(e)}")
        return False

def get_comparison_data(nz_city, canadian_city, year):
    """
    This function gets comparison data for two cities in a specific year
    It gets the data from mergedWeatherData table and sorts it by months
    Returns two lists of temperatures: one for each city
    
    Used by:
    historical_data.py and yearly_comparison.py for showing city comparisons data in charts
    """
    try:
        jsn_service = JSNDropMergeService()
        response = jsn_service.get_comparison_data(nz_city, canadian_city, year)

        if response.get("JsnMsg") == "SUCCESS.SELECT" and isinstance(
            response.get("Msg"), list
        ):
            data = response["Msg"]
            df = pd.DataFrame(data)

            # Sort the data by months (Jan to Dec)
            month_order = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            df["month_order"] = df["month"].apply(lambda x: month_order.index(x))
            df = df.sort_values("month_order")

            # Get temperatures for each city separately
            nz_temps = df[df["city"] == nz_city]["temperature"].tolist()
            canadian_temps = df[df["city"] == canadian_city]["temperature"].tolist()

            return nz_temps, canadian_temps

    except Exception as e:
        print(f"got error getting comparison: {str(e)}")
    return None, None

def accept(event, values, state):
    """
    This is my function that runs when someone clicks Create Merged Data
    It gets called from main.py when handling button events
    
    It does this:
    Gets the cities and year they picked
    Creates fresh merged dataset with both countries' data
    Gets comparison data for their chosen cities
    Returns the data in a format my charts can use
    
    Used by:
    historical_data.py for the Create Merged Data button and
    yearly_comparison.py for the Get (NZ+CAN) Merged Data button
    """
    if event == "-MERGE-DATA-":
        try:
            print("\n=== starting to merge city data ===")
            nz_city = values["-NZ-CITY-"]  # Get NZ city users picked
            canadian_city = values["-CANADIAN-CITY-"] # Get Canadian city
            year = values["-YEAR-"]  # Get year 

            print("making fresh merged dataset...")
            if not create_merged_dataset():
                print("couldnt make merged dataset")
                return None

            # Get the comparison data for their cities
            print(f"getting data for {nz_city} and {canadian_city}...")
            nz_data, canadian_data = get_comparison_data(nz_city, canadian_city, year)

            if nz_data and canadian_data:
                print("got both cities data ok")
                return {"nz_data": nz_data, "canadian_data": canadian_data}
            else:
                print(f"couldnt get data for {nz_city} and {canadian_city}")

            print("=== done merging city data ===\n")

        except Exception as e:
            print(f"got error in merge: {str(e)}")

    return None