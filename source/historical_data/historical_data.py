"""
historical data screen

This is my module for the historical data screen.
It shows yearly weather data for cities and lets users compare NZ and Canadian cities.
The data comes from different sources:
NZ data from WeatherData.csv via get_online_json_data.py
Canadian data from CanadianWeatherData.csv via merged_data.py

Used by main.py to create and manage the historical data screen.
Works with these controllers:
get_local_data.py for the city lists and CSV operations
get_online_json_data.py for getting NZ data from JSNDrop
merged_data.py for comparing cities
chat_button.py for the chat functionality

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for matplotlib: https://matplotlib.org/
Reference for subplot: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot.html
Reference for plot: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
Reference for grid: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
Reference for TkAgg: https://matplotlib.org/stable/users/explain/backends.html
Reference for Toolbar: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
Reference for Multiline: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#multiline-element
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
    
    """
    import matplotlib
    matplotlib.use("TkAgg") 

    # Clear old chart if any ( i was getting an error without it)
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    # Draw new chart
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    # Add toolbar with zoom and pan tools , it is a built in feature of matplotlib

    toolbar_frame = sg.tk.Frame(canvas)
    toolbar_frame.pack(side="bottom", fill="x") 
    toolbar = NavigationToolbar2Tk(figure_canvas_agg, toolbar_frame)
    toolbar.update()

    return figure_canvas_agg, toolbar

def historical_des_layout():
    """
    This function creates the layout for my Historical Data screen
    It has:
    navigation buttons (Prev/Next)
    City selection dropdowns
    Year selector
    Chart area
    Get JSON and Create Merged Data buttons
    Chat section at bottom
    
    Used by:
    main.py to create the screen
    """
    figure_w, figure_h = 700, 450

    layout = [
        # Top navigation
        [
            sg.Button("Prev"),
            sg.Text("Historical Data", font=("Arial", 22),
                justification="center", expand_x=True),
            sg.Button("Next"),
        ],
        
        # Data type (only Temperature for now)
        [
            sg.Text("Data type:"),
            sg.Combo(["Temperature"], default_value="Temperature",
                    key="-DATATYPE-", readonly=True),
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
            sg.Button("Get JSON Data", key="-FETCH-JSON-", size=(15, 2)),
            sg.Button("Create Merged Data", key="-MERGE-DATA-", size=(15, 2)),
            sg.Push(),
        ],
        
        # Chat section
        [sg.Multiline(size=(60, 5), expand_x=True,
                    key="-CHATBOX-HISTORICAL-DATA-",
                    disabled=True, autoscroll=True)],
        [sg.Input(size=(60, 3), expand_x=True, key="Message")],
        [sg.Push(), sg.Button("Send"), sg.Push()],
        
        # Exit button
        [sg.Push(), sg.Button("Exit")],
    ]
    return layout

def create_historical_chart(nz_data=None, canadian_data=None,
                        nz_city=None, canadian_city=None):
    """
    This function creates the historical weather chart
    It can show:
    Just NZ city data
    Both NZ and Canadian data for comparison
    Example data if no real data yet (for testing)
    """
    print("making new historical chart...")
    plt.clf() 
    fig, ax = plt.subplots(figsize=(10, 4))

    # List of months for my x-axis
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    # Plot NZ data
    if nz_data:
        ax.plot(months[:len(nz_data)], nz_data, label=f"{nz_city}",
            color="#2196F3", marker="o", linestyle="-")

    # Plot Canadian data
    if canadian_data:
        ax.plot(months[:len(canadian_data)], canadian_data,
            label=f"{canadian_city}", color="#4CAF50",
            marker="s", linestyle="-")

    # Show example data if no real data yet
    if not (nz_data or canadian_data):
        values = [15, 17, 14, 12, 10, 8, 7, 9, 11, 13, 14, 15]
        ax.plot(months, values, label="Example Data")

    # Choose title based on what data i'm showing on the chart
    title = "Temperature History"
    if nz_city and canadian_city:
        title = f"Temperature Comparison: {nz_city} vs {canadian_city}"
    elif nz_city:
        title = f"Temperature History for {nz_city}"

    # Set up the chart
    ax.set_title(title)
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Months")
    ax.grid(True, linestyle="--", alpha=0.7)

    # Add legend if have data
    if nz_data or canadian_data:
        ax.legend()

    plt.tight_layout() 
    print("historical chart is ready")
    return fig

def handle_json_fetch(window, values):
    """
    This function handles the Get JSON Data button click
    It gets NZ data from JSNDrop using get_online_json_data.py
    Shows the data for one NZ city on the chart
    
    Called when someone clicks Get JSON Data button
    Button event is handled in my main.py
    """
    try:
        result = get_online_json_data.accept("-FETCH-JSON-", values,
                                        {"view": window})
        if result:
            fig = create_historical_chart(nz_data=result,
                                        nz_city=values["-NZ-CITY-"])
            canvas_elem = window["canvas-chart"]
            canvas = canvas_elem.TKCanvas
            if canvas:
                draw_figure_with_toolbar(canvas, fig)
            return result
    except Exception as e:
        print(f"got error in historical json fetch: {str(e)}")
        return None

def handle_merge_event(window, values, json_data):
    """
    This function handles the Create Merged Data button click
    It uses merged_data.py controller to:
    Get NZ data from JSNDrop
    Get Canadian data from CSV
    Combine them into one dataset
    Show both on the same chart
    
    Called when someone clicks Create Merged Data button
    Button event is handled in my main.py
    """
    try:
        result = merged_data.accept("-MERGE-DATA-", values, {"view": window})
        if result:
            fig = create_historical_chart(
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
        print(f"got error in historical merge: {str(e)}")