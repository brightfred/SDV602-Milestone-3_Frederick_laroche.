"""
current_weather_merge.py

This is my controller for merging current weather data.

It works with two types of data:
NZ data that comes from OpenWeather API and is stored in the openweather table on jsndrop 
and then stored in the mergedcurrentdata table on jsndrop
Canadian data that comes from my currentCanadianweather.csv file and then stored in the mergedcurrentdata table on jsndrop

This file is used by current_condition.py when someone clicks the Compare Cities button.
The accept function at the bottom gets called from my main.py to handle the button click.

Reference for JSNDrop: Comes from Todd examples files in Moodle
Reference for pandas: https://pandas.pydata.org/docs/user_guide/index.html
Reference for json: https://docs.python.org/3/library/json.html
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
Reference for dictionary: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
Reference for len: https://docs.python.org/3/library/functions.html#len
Reference for print: https://docs.python.org/3/library/functions.html#print
Reference for if statement: https://docs.python.org/3/tutorial/controlflow.html#if-statements
Reference for for loop: https://docs.python.org/3/tutorial/controlflow.html#for-statements
Reference for str: https://docs.python.org/3/library/stdtypes.html#str
"""

import sys
sys.dont_write_bytecode = True
import requests
import json
import pandas as pd

"""
My CurrentWeatherMergeService class for working with the JSNDrop
This class:
Create and manage the merged data table
Get NZ weather data from the openweather table in JSNDrop
Store the combined NZ and Canadian data in the merged table

The tables it uses are:
openweather: where the OpenWeather API data goes (this is created by fetch_weather_button.py)
mergedcurrentdata: where i put both NZ and Canadian data together
"""
class CurrentWeatherMergeService:
    def __init__(self):
        # Setup my JSNDrop connection info
        self.base_url = "https://newsimland.com/~todd/JSON/"
        self.token = "96d5a614-3acb-41b4-b7f6-b298368bf871"
        # Names for my tables
        self.openweather_table = "openweather"   
        self.merged_table = "mergedcurrentdata"

    def drop_merged_table(self):
        """
        This function removes my merged data table from JSNDrop
        I do this before making a new one to make sure the data is fresh each time
        someone compares cities
        """
        print("now dropping the merged current table from jsondrop...")
        cmd = {
            "tok": self.token,
            "cmd": {"DROP": self.merged_table}
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("done dropping merged table")
        return response.json()

    def create_merged_table(self):
        """
        This function makes a new merged data table in JSNDrop
        The table can store:
        city: up to 50 characters for city name
        country: up to 20 characters for country name (needed to tell NZ and Canadian data apart more easily)
        temperature: numbers 
        timestamp: date and time like "2024-01-01 00:00:00"
        """
        print("making new merged current table...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "CREATE": self.merged_table,
                "EXAMPLE": {
                    "city": "A" * 50,
                    "country": "A" * 20,
                    "temperature": 22.5,
                    "timestamp": "2024-11-10 00:00:00",
                }
            }
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("new merged table is created")
        return response.json()

    def get_nz_data(self, city):
        """
        This function gets the NZ city data from the openweather table
        I use the city name to find the right data
        The data comes from fetch_weather_button.py and puts it in the openweather table
        """
        print(f"getting data for {city} from openweather table...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "SELECT": self.openweather_table,
                "WHERE": f"city = '{city}'" # Find the right city's data using the city name i got from the dropdown
            }
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got the nz data")
        return response.json()

    def store_merged_data(self, data):
        """
        This function saves the combined weather data to my merged table
        The data should have both NZ and Canadian temperatures with timestamps
        I need both in one table so i can compare them in the chart according to the assessment requirements
        Uses data as a parameter to store the data in the table
        """
        print("putting current weather data in merged table...")
        cmd = {
            "tok": self.token,
            "cmd": {"STORE": self.merged_table, "VALUE": data} 
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("merged data stored")
        return response.json()

def get_canadian_data(city):
    """
    This function gets data for a Canadian city from my CSV file
    The data needs to match the same format as the NZ data so it can be merged
    It returns None if it can't find the city data or if there is an error
    Use city as the parameter to get the right city's data
    """
    try:
        print(f"getting data for {city} from current canadian weather file...")
        # Read my CSV file that has the canadian weather data
        df = pd.read_csv("Dataset/currentCanadianweather.csv")
        # Find data just for the city we want using pandas filtering using the city column and the city name we got from the dropdown
        city_data = df[df["city"] == city]
        

        if not city_data.empty:
            # Make the data match the NZ format
            # I need records to look the same as what comes from OpenWeather API
            records = []
            # Go through each row in the city's data
            # index is the row number, row has the actual data
            # Im using a for loop and iterrows. It is a pandas function that gives me both 
            for index, row in city_data.iterrows():
                records.append({
                    "city": city,
                    "country": "Canada",  # Added country here so charts know it's Canadian data
                    "temperature": row["temperature"],
                    "timestamp": row["timestamp"]  # Same format as OpenWeather API uses to make it easy to merge
                })
            print(f"found data for {city}")
            return records
            
        print(f"no data found for {city}")
        return None
        
    except Exception as e:
        print(f"got error reading canadian data: {str(e)}")
        return None

def create_current_merged_dataset(nz_city, canadian_city):
    """
    This function combines current weather data from NZ and Canada
    I use it to get both cities' data ready for the chart
    
    It returns three things that my chart needs:
    nz_temps: list of temperatures for NZ city
    canadian_temps: list of temperatures for Canadian city
    time_labels: list of times to show on chart
    
    If anything goes wrong, it returns None, None, None to tell the chart
    there's no data to show
    """
    try:
        print("\n=== starting to make the current merged dataset ===")
        jsn_service = CurrentWeatherMergeService()

        # Start fresh with a new merged table
        jsn_service.drop_merged_table()
        jsn_service.create_merged_table()

        # Get NZ data and add country name  
        # I need to add 'New Zealand' as country because OpenWeather API
        # doesn't include it, but i need it to tell data apart in the chart
        print("getting nz current data...")
        nz_response = jsn_service.get_nz_data(nz_city)
        if nz_response.get("JsnMsg") == "SUCCESS.SELECT":
            nz_records = nz_response.get("Msg", [])
            for record in nz_records:
                record["country"] = "New Zealand" 
            # len() tells me how many records i got (good for debugging)
            print(f"got {len(nz_records)} nz records")
        else:
            print("couldnt get nz data")
            return None, None, None  # Return 3 None because chart expect 3 values

        # Get Canadian data from my CSV
        print("getting canadian current data...")
        canadian_records = get_canadian_data(canadian_city)
        if not canadian_records: # If i got no data back
            print("couldnt get canadian data")
            return None, None, None  # Return 3 None because chart needs 3 values
        print(f"got {len(canadian_records)} canadian records")

        # Put all the data together in JSNDrop
        print("combining current weather data...")
        nzca_records = nz_records + canadian_records  # Join the two lists of records using +
        jsn_service.store_merged_data(nzca_records) # Store the combined data in the merged table

        # Get just the temps and times for the chart
        # list comprehension makes new lists with just what the chart needs
        nz_temps = [record["temperature"] for record in nz_records]
        canadian_temps = [record["temperature"] for record in canadian_records]
        time_labels = [record["timestamp"] for record in nz_records]

        print("=== done making current merged dataset ===\n")
        return nz_temps, canadian_temps, time_labels

    except Exception as e:
        print(f"got error making current merged dataset: {str(e)}")
        return None, None, None  # Return 3 None because chart expects 3 values (temps, temps, times)

def accept(event, values, state):
    """
    This is my function that runs when someone clicks the Compare Cities button
    It gets called by main.py when handling button events
    It works with current_condition.py to update the chart
    
    It does this:
    Gets the cities they picked from the dropdowns
    Makes a merged dataset with both cities' data
    Returns the data in the right format for the chart
    
    If anything goes wrong, it returns None and prints error messages
    """
    if event == "-MERGE-CURRENT-":  # This is the button id from my current_condition.py
        try:
            print("\n=== starting to merge current city data ===")
            window = state["view"] 
            nz_city = values["-NZ-CITY-"]  # Get NZ city they picked
            canadian_city = values["-CANADIAN-CITY-"]  # Get Canadian city they picked

            print(f"trying to merge data for {nz_city} and {canadian_city}...")
            nz_temps, canadian_temps, time_labels = create_current_merged_dataset( # Call my function to get the data 
                nz_city, canadian_city
            )

            if nz_temps and canadian_temps and time_labels:
                print("got both cities data ok")
                # Send back data in the format my chart needs
                # This dictionary matches what current_condition.py expects(temps, temps, times)
                return {
                    "city": nz_city,
                    "canadian_city": canadian_city,
                    "temp_history": nz_temps,
                    "canadian_temps": canadian_temps,
                    "time_labels": time_labels
                }
            else:
                print(f"couldnt get data for {nz_city} and/or {canadian_city}")

            print("=== done merging current city data ===\n")

        except Exception as e:
            print(f"got an error in merge: {str(e)}")

    return None