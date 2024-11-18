"""
Get local data controller
This is my controller for getting data from local CSV files.
It is used by historical_data.py and yearly_comparison.py when reading local weather data.
The historical weather data is stored in CSV files in my Dataset folder.

References:
Reference for os.path: https://docs.python.org/3/library/os.path.html
Reference for pandas: https://pandas.pydata.org/docs/user_guide/index.html
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for lists: https://docs.python.org/3/tutorial/introduction.html#lists
Reference for lambda: https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
Reference for tolist: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.tolist.html
Reference for sort_values: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
"""

import sys
sys.dont_write_bytecode = True
import os
import pandas as pd

# These are my CSV files that have the weather data
# I use these files because i don't have an API for historical data, it cost money
NZ_DATA_FILE = "DataSet/WeatherData.csv"
CANADIAN_DATA_FILE = "DataSet/CanadianWeatherData.csv"

"""
These are the cities i have data for in my CSV files

"""

NZ_CITIES = [
    "Auckland",
    "Wellington",
    "Christchurch",
    "Hamilton",
    "Tauranga",
    "Napier-Hastings",
    "Dunedin",
    "Palmerston North",
    "Nelson",
    "Rotorua",
    "New Plymouth",
    "Whangarei",
    "Invercargill",
    "Whanganui",
    "Gisborne",
]

# List of all Canadian cities i have data for
CANADIAN_CITIES = [
    "Vancouver",
    "Toronto",
    "Montreal",
    "Winnipeg",
    "Calgary",
    "Edmonton",
]

# Years i have data for in my CSV files
AVAILABLE_YEARS = ["2023", "2024"]

def get_city_data(city, year):
    """
    This function gets data for one city and year from my NZ weather CSV
    It returns just the temperatures in the right order by month
    
    Parameters:
    city: which city to get data for (must be in NZ_CITIES list)
    year: which year to get data for (must be in AVAILABLE_YEARS list)
    
    Returns:
    list of temperatures ,if it found data for this city and year
    None if no data found or there's an error
    
    """
    try:
        print(f"\n=== getting data for {city} year {year} ===")

        print("trying to read weather file...")
        # First check if my CSV file exists
        if os.path.exists(NZ_DATA_FILE):
            # Read the CSV file with pandas (df is short for Data frame)
            df = pd.read_csv(NZ_DATA_FILE)
            # Find rows for just this city and year
            filtered_data = df[(df["city"] == city) & (df["year"] == int(year))]

            # If data was found for this city and year
            if not filtered_data.empty:
                # This is the order i want my months in
                month_order = [
                    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                ]
                # Add a column that helps sort the months right
                # For each month name, find its position in month_order
                # It takes the month name, finds its index in month_order
                filtered_data["month_order"] = filtered_data["month"].apply(
                    lambda x: month_order.index(x)
                )
                # Sort the data by this new column
                filtered_data = filtered_data.sort_values("month_order")

                # Get just the temperatures in the right order
                temps = filtered_data["temperature"].tolist()
                print(f"found data for {city}")
                return temps
            else:
                print(f"no data found for {city} in {year}")
        else:
            print("cant find the weather file")
        return None
    except Exception as e:
        print(f"got error getting city data: {str(e)}")
        return None

def accept(event, values, state):
    """
    This is my function that runs when someone clicks Get Local Data
    It gets called from my main.py when dealing with button events
    
    It does this:
    Gets the city and year user picked
    Tries to get data from the CSV file
    Returns the temperatures if found
    
    Used by:
    - historical_data.py for the Get Local Data button
    - yearly_comparison.py for the Get Local Data button
    """
    if event == "-LOCAL-DATA-":
        try:
            window = state["view"]  # The window showing right now
            city = values["-NZ-CITY-"]  # Get city they picked
            year = values["-YEAR-"]  # Get year they picked

            data = get_city_data(city, year)
            if data:
                print("got the data ok")
                return data
            print("couldn't get the data")

        except Exception as e:
            print(f"got error in local data: {str(e)}")

    return None