"""
current_condition.py

This is my module for the Current Condition screen.
It shows current weather for NZ cities and lets users compare with Canadian cities.
The data comes from OpenWeather API for NZ cities and my CSV file for Canadian cities.

Used by main.py to create and manage the current condition screen.
Works with these controllers:
- fetch_weather_button.py for getting NZ weather
- current_weather_merge.py for comparing cities
- chat_button.py for the chat functionality

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for matplotlib: https://matplotlib.org/
Reference for datetime: https://docs.python.org/3/library/datetime.html
Reference for lists: https://docs.python.org/3/tutorial/introduction.html#lists
Reference for dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
Reference for plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
Reference for subplots: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
Reference for grid: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
Reference for legend: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import datetime
import matplotlib

"""
These are my lists of cities that have weather data available
Used in:
- City dropdown menus in this screen
- Get_local_data.py for data lookup
- current_weather_merge.py for city validation
"""
NZ_CITIES = [
    "Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga",
    "Napier-Hastings", "Dunedin", "Palmerston North", "Nelson", "Rotorua",
    "New Plymouth", "Whangarei", "Invercargill", "Whanganui", "Gisborne",
]

CANADIAN_CITIES = [
    "Vancouver", "Toronto", "Montreal", 
    "Winnipeg", "Calgary", "Edmonton",
]

def draw_figure_with_toolbar(canvas, fig):
    """
    This function puts a matplotlib chart in my PySimpleGUI window
    It adds zoom and pan tools to the chart
    
    Parameters:
    canvas: where to draw the chart (from PySimpleGUI)
    fig: the chart to draw (from matplotlib)
    
    Used by:
    - create_currentCondition_chart() below
    - historical_data.py for its charts
    - yearly_comparison.py for its charts
    """
    matplotlib.use("TkAgg")  # Need this to show charts in PySimpleGUI

    # Clear old chart if any
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    # Draw new chart
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    # Add toolbar with zoom and pan tools
    toolbar_frame = sg.tk.Frame(canvas)
    toolbar_frame.pack(side="bottom", fill="x")
    toolbar = NavigationToolbar2Tk(figure_canvas_agg, toolbar_frame)
    toolbar.update()

    return figure_canvas_agg, toolbar

def currentCondition_des_layout():
    """
    This function creates the layout for my Current Condition screen
    It has:
    - Navigation buttons (Prev/Next)
    - City selection dropdowns
    - Weather chart
    - Get Weather and Compare buttons
    - Chat section at bottom
    
    Used by:
    - main.py to create the screen
    - All the buttons reference the keys defined here
    """
    figure_w, figure_h = 700, 450  # Size of chart area

    layout = [
        # Top navigation
        [
            sg.Button("Prev"),
            sg.Text("Current Condition", font=("Arial", 22), 
                   justification="center", expand_x=True),
            sg.Button("Next"),
        ],
        
        # Data type selector (only Temperature for now)
        [
            sg.Text("Data type:"),
            sg.Combo(["Temperature"], default_value="Temperature",
                    readonly=True, key="-DATATYPE-"),
        ],
        
        # City selection dropdowns
        [sg.Text("Select Cities to Compare:", font=("Arial", 11, "bold"))],
        [
            sg.Frame("New Zealand City", [
                [sg.Combo(NZ_CITIES, default_value="Nelson",
                         key="-NZ-CITY-", readonly=True, size=(20, 1))]
            ]),
            sg.Frame("Canadian City", [
                [sg.Combo(CANADIAN_CITIES, default_value="Toronto",
                         key="-CANADIAN-CITY-", readonly=True, size=(20, 1))]
            ]),
        ],
        
        # Chart area
        [sg.Canvas(size=(figure_w, figure_h), key="canvas-chart",
                  pad=(0, (10, 20)))],
        
        # Action buttons
        [
            sg.Push(),
            sg.Button("Get Current Weather", key="-FETCH-WEATHER-", size=(15, 2)),
            sg.Button("Compare Cities", key="-MERGE-CURRENT-", size=(15, 2)),
            sg.Push(),
        ],
        
        # Chat section
        [sg.Multiline(size=(60, 5), expand_x=True,
                     key="-CHATBOX-CURRENT-CONDITION-",
                     disabled=True, autoscroll=True)],
        [sg.Input(size=(60, 3), expand_x=True, key="Message")],
        [sg.Push(), sg.Button("Send"), sg.Push()],
        
        # Exit button
        [sg.Push(), sg.Button("Exit")],
    ]
    return layout

def create_currentCondition_chart(weather_data):
    """
    This function creates the weather chart for the Current Condition screen
    It can show:
    - Just NZ city data (from OpenWeather API)
    - Both NZ and Canadian data for comparison
    
    Parameters:
    weather_data: dictionary with:
        time_labels: list of times for x-axis
        temp_history: NZ temperatures
        canadian_temps: Canadian temperatures (optional)
        city: NZ city name
        canadian_city: Canadian city name (optional)
    
    Used by:
    - fetch_weather_button.py when getting new weather
    - handle_compare_cities() when comparing cities
    """
    print("making new chart...")
    plt.clf()  # Clear any old chart
    fig, ax = plt.subplots(figsize=(10, 4))

    # Get data from the dictionary
    times = weather_data.get("time_labels", [])
    nz_temps = weather_data.get("temp_history", [])
    canadian_temps = weather_data.get("canadian_temps", [])
    nz_city = weather_data.get("city", "")
    canadian_city = weather_data.get("canadian_city", "")

    # Plot NZ data in blue with circles
    if nz_temps:
        ax.plot(times, nz_temps, label=f"{nz_city}",
                color="#2196F3", marker="o", linestyle="-")

    # Plot Canadian data in green with squares (if we have it)
    if canadian_temps:
        ax.plot(times, canadian_temps, label=f"{canadian_city}",
                color="#4CAF50", marker="s", linestyle="-")

    # Choose title based on what data we're showing
    title = "24-Hour Temperature Forecast"
    if canadian_city and nz_city:
        title = f"Temperature Comparison: {nz_city} vs {canadian_city}"
    elif nz_city:
        title = f"Temperature Forecast for {nz_city}"

    # Set up the chart
    ax.set_title(title)
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Time")
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)  # Angle the times so they fit better

    # Add legend if we have data
    if nz_temps or canadian_temps:
        ax.legend()

    plt.tight_layout()  # Make everything fit nicely
    print("chart is ready")
    return fig

def handle_compare_cities(window, values):
    """
    This function handles the Compare Cities button click
    It uses current_weather_merge.py to:
    1. Get NZ data from OpenWeather API table
    2. Get Canadian data from CSV
    3. Combine them into one dataset
    4. Show both on the same chart
    
    Used when someone clicks the Compare Cities button
    The button event is handled in main.py
    """
    try:
        print("\n=== starting to compare cities ===")
        
        # Get the comparison data from my merge controller
        from controller.DES import current_weather_merge
        state = {"view": window}
        merged_data = current_weather_merge.accept("-MERGE-CURRENT-", values, state)
        
        # Make new chart with the merged data
        if merged_data:
            print("making comparison chart...")
            fig = create_currentCondition_chart(merged_data)
            canvas_elem = window["canvas-chart"]
            canvas = canvas_elem.TKCanvas
            if canvas:
                draw_figure_with_toolbar(canvas, fig)
            print("compared cities ok")
        else:
            print("couldnt get the comparison data")

        print("=== done comparing cities ===\n")

    except Exception as e:
        print(f"got error when comparing cities: {str(e)}")