"""
yearly_comparison.py

This is my module for the Yearly Comparison screen.
It shows yearly weather data and lets users compare NZ and Canadian cities.
The data comes from different sources:
- NZ data from WeatherData.csv via get_online_json_data.py
- Canadian data from CanadianWeatherData.csv via merged_data.py

Used by main.py to create and manage the yearly comparison screen.
Works with these controllers:
- get_local_data.py for the city lists
- get_online_json_data.py for getting NZ data from JSNDrop
- merged_data.py for comparing cities
- chat_button.py for the chat functionality

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for matplotlib: https://matplotlib.org/
Reference for subplot: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot.html
Reference for toolbar: https://matplotlib.org/stable/api/backend_tools_api.html
Reference for grid: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
Reference for plt.clf: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.clf.html
Reference for TkAgg: https://matplotlib.org/stable/users/explain/backends.html
Reference for tight_layout: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# Get my lists of cities and years from Get_local_data.py
from controller.DES.Get_local_data import NZ_CITIES, CANADIAN_CITIES, AVAILABLE_YEARS
# Import my data controllers
from controller.DES import get_online_json_data
from controller.DES import merged_data

def draw_figure_with_toolbar(canvas, fig):
    """
    This function puts a matplotlib chart in my PySimpleGUI window
    It adds zoom and pan tools to the chart
    
    Parameters:
    canvas: where to draw the chart (from PySimpleGUI)
    fig: the chart to draw (from matplotlib)
    
    Used by:
    - handle_json_fetch() when showing NZ data
    - handle_merge_event() when showing comparison
    - current_condition.py for its charts
    - historical_data.py for its charts
    """
    import matplotlib
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

def yearly_des_layout():
    """
    This function creates the layout for my Yearly Comparison screen
    It has:
    - Navigation buttons (Prev/Next)
    - City selection dropdowns
    - Year selector
    - Chart area
    - Get JSON Drop Data and Get (NZ+CAN) Merged Data buttons
    - Chat section at bottom
    
    Used by:
    - main.py to create the screen
    - All buttons reference the keys defined here
    """
    figure_w, figure_h = 700, 450  # Size of chart area

    layout = [
        # Top navigation
        [
            sg.Button("Prev"),
            sg.Text("Yearly Comparison", font=("Arial", 22),
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
        
        # Year selector
        [
            sg.Push(),
            sg.Text("Year:"),
            sg.Combo(AVAILABLE_YEARS, default_value="2023",
                    key="-YEAR-", readonly=True, size=(10, 1)),
            sg.Push(),
        ],
        
        # Chart area
        [sg.Canvas(size=(figure_w, figure_h), key="canvas-chart",
                pad=(0, (10, 20)))],
        
        # Action buttons
        [
            sg.Push(),
            sg.Button("Get JSON Drop Data", key="-FETCH-JSON-", size=(15, 2)),
            sg.Button("Get (NZ+CAN) Merged Data", key="-MERGE-DATA-", size=(15, 2)),
            sg.Push(),
        ],
        
        # Chat section
        [sg.Multiline(size=(60, 5), expand_x=True,
                    key="-CHATBOX-YEARLY-COMPARISON-",
                    disabled=True, autoscroll=True)],
        [sg.Input(size=(60, 3), expand_x=True, key="Message",
                do_not_clear=False)],
        [sg.Push(), sg.Button("Send"), sg.Push()],
        
        # Exit button
        [sg.Push(), sg.Button("Exit")],
    ]
    return layout

def create_yearly_chart(nz_data=None, canadian_data=None,
                    nz_city=None, canadian_city=None):
    """
    This function creates the yearly comparison chart
    It can show:
    - Just NZ city data
    - Both NZ and Canadian data for comparison
    - Example data if no real data yet
    
    Parameters:
    nz_data: list of temperatures for NZ city (optional)
    canadian_data: list of temperatures for Canadian city (optional)
    nz_city: name of NZ city (optional)
    canadian_city: name of Canadian city (optional)
    
    Used by:
    - handle_json_fetch() when showing NZ data
    - handle_merge_event() when showing comparison
    """
    print("making new yearly chart...")
    plt.clf()  # Clear any old chart
    fig, ax = plt.subplots(figsize=(10, 4))

    # List of months for x-axis
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    # Plot NZ data in blue with circles (if we have it)
    if nz_data:
        ax.plot(months[:len(nz_data)], nz_data,
            label=f"{nz_city}",
            color="#2196F3", marker="o", linestyle="-")

    # Plot Canadian data in green with squares (if we have it)
    if canadian_data:
        ax.plot(months[:len(canadian_data)], canadian_data,
            label=f"{canadian_city}",
            color="#4CAF50", marker="s", linestyle="-")

    # Show example data if no real data yet
    if not (nz_data or canadian_data):
        values = [15, 17, 14, 12, 10, 8, 7, 9, 11, 13, 14, 15]
        ax.plot(months, values, label="Example Data")

    # Set title based on what we're showing
    title = "Temperature Comparison"
    if nz_city and canadian_city:
        title = f"Temperature Comparison: {nz_city} vs {canadian_city}"

    # Set up the chart
    ax.set_title(title)
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Months")
    ax.grid(True, linestyle="--", alpha=0.7)

    # Add legend if we have data
    if nz_data or canadian_data:
        ax.legend()

    plt.tight_layout()  # Make everything fit nicely
    print("yearly chart is ready")
    return fig

def handle_json_fetch(window, values):
    """
    This function handles the Get JSON Drop Data button click
    It gets NZ data from JSNDrop using get_online_json_data.py
    Shows the data for one NZ city on the chart
    
    Called when someone clicks Get JSON Drop Data button
    Button event is handled in main.py
    """
    try:
        result = get_online_json_data.accept("-FETCH-JSON-", values,
                                        {"view": window})
        if result:
            fig = create_yearly_chart(nz_data=result,
                                    nz_city=values["-NZ-CITY-"])
            canvas_elem = window["canvas-chart"]
            canvas = canvas_elem.TKCanvas
            if canvas:
                draw_figure_with_toolbar(canvas, fig)
            return result
    except Exception as e:
        print(f"got error in yearly json fetch: {str(e)}")
        return None

def handle_merge_event(window, values, json_data):
    """
    This function handles the Get (NZ+CAN) Merged Data button click
    It uses merged_data.py to:
    1. Get NZ data from JSNDrop
    2. Get Canadian data from CSV
    3. Combine them into one dataset
    4. Show both on the same chart
    
    Called when someone clicks Get (NZ+CAN) Merged Data button
    Button event is handled in main.py
    """

    try:
        result = merged_data.accept("-MERGE-DATA-", values, {"view": window})
        if result:
            fig = create_yearly_chart(
                nz_data=result["nz_data"],
                canadian_data=result["canadian_data"],
                nz_city=values["-NZ-CITY-"],
                canadian_city=values["-CANADIAN-CITY-"]
            )
            canvas_elem = window["canvas-chart"]
            canvas = canvas_elem.TKCanvas
            if canvas:
                draw_figure_with_toolbar(canvas, fig)
    except Exception as e:
        print(f"got error in yearly merge: {str(e)}")