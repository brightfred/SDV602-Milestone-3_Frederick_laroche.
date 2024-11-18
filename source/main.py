"""
main.py

This is my main application file that controls everything in my weather app.
It manages:
- User login and registration
- Three weather screens (Current, Historical, Yearly)
- All button clicks and screen changes
- Data flow between screens
- Charts updating

Used by:
- All other modules when they need to update charts or change screens
- Runs first when starting the app

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for matplotlib: https://matplotlib.org/
Reference for Window: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#window-element
Reference for Events: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#events
Reference for Button: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#button-element
Reference for popup: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#popup-element
Reference for Theme: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#theme
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for Object oriented: https://docs.python.org/3/tutorial/classes.html
Reference for Event Loop: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-1-one-window-runs-start-to-finish
"""

import sys
sys.dont_write_bytecode = True

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Import my screen modules
import current_condition.current_condition as current_condition
import historical_data.historical_data as historical_data
import yearly_comparison.yearly_comparison as yearly_comparison
import top_command_interface.top_command_interface as top_command_interface

# Import my user handling modules
from User.user_login import LoginView
from User.user_register import RegisterView
from User.user_management import UserManager

# Import my button controllers
from controller.User import chat_button
from controller.DES import fetch_weather_button
from controller.DES import get_online_json_data
from controller.DES import merged_data

# Import chart tools
from current_condition.current_condition import draw_figure_with_toolbar

class WeatherApp:
    """
    This is my main app class that controls everything
    It manages:
    - Login/register screens
    - Three weather screens
    - All button clicks
    - Charts and data
    """

    def __init__(self):
        """
        This sets up all the parts of my app
        
        I store:
        user_manager: handles login/register
        login_view: the login screen
        register_view: the register screen
        current_user: who's logged in
        top_interface: main menu
        windows: list of my three screens
        current_window_index: which screen showing (0,1,2)
        figure_agg_list: charts for each screen
        json_data: data from JSNDrop
        """
        self.user_manager = UserManager()
        self.login_view = LoginView()
        self.register_view = RegisterView()
        self.current_user = None
        self.top_interface = None
        self.windows = []
        self.current_window_index = None
        self.figure_agg_list = [None, None, None]
        self.json_data = None

    def handle_login(self):
        """
        This function controls my login screen
        It shows the login window and handles what happens when users try to:
        - Log in with username/password
        - Click Register to make new account
        - Exit the app
        
        Returns:
        username if login works
        None if they exit or something goes wrong
        
        Used by:
        - run() function when app starts
        - After logout to show login screen again
        """
        while True:
            # Show login window
            self.login_view.set_up_layout()
            self.login_view.render()
            result = self.login_view.accept_input()

            # Handle what they did in login window
            if result is None or result == "Exit":
                return None  # They closed window or clicked Exit
            elif result == "Register":
                self.handle_register()  # They clicked Register
            elif isinstance(result, tuple):
                # They tried to log in - check if it works
                username, password = result
                login_result = self.user_manager.login(username, password)
                if login_result == "Login Success":
                    self.current_user = username
                    return username
                else:
                    sg.popup(login_result, title="Login Failed")

    def handle_register(self):
        """
        This function controls my register screen
        It shows the register window and makes new accounts
        
        Called by handle_login() when Register clicked
        Gets called by main.py's handle_window_events()
        """
        self.register_view.set_up_layout()
        self.register_view.render()
        result = self.register_view.accept_input()

        # If they filled in the form, try to register them
        if isinstance(result, tuple):
            username, password = result
            register_result = self.user_manager.register(username, password)
            sg.popup(register_result, title="Registration Result")

    def create_chart(self, window_index, window):
        """
        This function makes empty charts when screens first open
        Each screen (Current/Historical/Yearly) gets its own chart
        
        Parameters:
        window_index: which screen (0,1,2)
        window: the window to put chart in
        
        Returns:
        fig: the matplotlib chart
        None: if something went wrong
        
        Called by initialize_windows() when making screens
        """
        fig = None
        if window_index == 0:  # Current Condition screen
            fig = current_condition.create_currentCondition_chart({})
        elif window_index == 1:  # Historical Data screen  
            fig = historical_data.create_historical_chart()
        elif window_index == 2:  # Yearly Comparison screen
            fig = yearly_comparison.create_yearly_chart()

        # Put the chart in the window if we made one
        if fig:
            canvas_elem = window["canvas-chart"]
            canvas = canvas_elem.TKCanvas
            if canvas:
                draw_figure_with_toolbar(canvas, fig)
            return fig
        return None

    def update_chart(self, data):
        """
        This function updates charts with new data
        It gets called when users:
        - Click Get Current Weather
        - Click Compare Cities
        - Change cities or years
        
        Parameters:
        data: dictionary with new data for chart
        
        Used by:
        - handle_window_events() when handling button clicks
        - fetch_weather_button.py after getting new data
        """
        try:
            if self.current_window_index == 0:  # Current condition screen
                fig = current_condition.create_currentCondition_chart(data)
                if fig:
                    # Update the chart
                    window = self.windows[self.current_window_index]
                    canvas_elem = window["canvas-chart"]
                    canvas = canvas_elem.TKCanvas
                    if canvas:
                        # Clear old chart and draw new one
                        for child in canvas.winfo_children():
                            child.destroy()
                        draw_figure_with_toolbar(canvas, fig)
                    return True
            elif self.current_window_index == 1:  # Historical data screen
                pass  # Uses its own update function
            elif self.current_window_index == 2:  # Yearly comparison screen
                pass  # Uses its own update function
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
            return False
        
    def initialize_windows(self):
        """
        This function creates all my app windows at startup
        It makes:
        - Top menu (main navigation)
        - Current Condition screen
        - Historical Data screen
        - Yearly Comparison screen
        
        All screens start hidden except top menu
        Each screen gets an empty chart ready
        
        Returns:
        True: if all windows created ok
        False: if something went wrong
        
        Called by:
        - run() after successful login
        """
        try:
            # Make the top menu window first
            print("making top menu window...")
            self.top_interface = top_command_interface.create_top_interface()
            self.top_interface.finalize()
            self.top_interface.CurrentLocation()

            # Get layouts for my three screens
            print("getting screen layouts...")
            window_layouts = [
                current_condition.currentCondition_des_layout(),
                historical_data.historical_des_layout(),
                yearly_comparison.yearly_des_layout(),
            ]

            # Make a window for each layout
            print("making screen windows...")
            self.windows = []
            for i, layout in enumerate(window_layouts):
                window = sg.Window(
                    "Weather App",
                    layout,
                    finalize=True,  # Create window right away
                    location=(500, 100),  # Where to put window
                    resizable=True,  # Let users resize window
                )
                self.windows.append(window)

            # Hide all screens at start
            print("hiding screens...")
            for window in self.windows:
                window.Hide()

            # Make empty charts for each screen
            print("making empty charts...")
            for i in range(len(self.windows)):
                self.figure_agg_list[i] = self.create_chart(i, self.windows[i])

            print("all windows ready")
            return True

        except Exception as e:
            sg.popup_error(f"Error initializing windows: {str(e)}")
            return False

    def handle_window_events(self, window, event, values):
        """
        This function handles all button clicks and events
        It controls:
        - Switching between screens
        - Button clicks on all screens
        - Chart updates
        - Chat messages
        
        Parameters:
        window: which window the event came from
        event: what happened (button click etc)
        values: any values from form inputs
        
        Returns:
        "Logout": if they clicked logout
        "Exit": if they're closing app
        None: for normal events
        
        Called by:
        - run() in main event loop
        This is the heart of my app - handles everything users do!
        """
        try:
            # Handle top menu events
            if window == self.top_interface:
                
                # They clicked Current Condition
                if event == "Current Condition":
                    if self.current_window_index is not None:
                        self.windows[self.current_window_index].Hide()
                    self.current_window_index = 0  # Current Condition is screen 0
                    self.windows[self.current_window_index].UnHide()
                    # Tell UserManager which screen we're on
                    result = self.user_manager.set_current_DES("DES1")
                    if result != "Set Screen":
                        sg.popup(result, title="Screen Change Error")

                # They clicked Historical Data
                elif event == "Historical Data":
                    if self.current_window_index is not None:
                        self.windows[self.current_window_index].Hide()
                    self.current_window_index = 1  # Historical Data is screen 1
                    self.windows[self.current_window_index].UnHide()
                    result = self.user_manager.set_current_DES("DES2")
                    if result != "Set Screen":
                        sg.popup(result, title="Screen Change Error")

                # They clicked Yearly Comparison
                elif event == "Yearly Comparison":
                    if self.current_window_index is not None:
                        self.windows[self.current_window_index].Hide()
                    self.current_window_index = 2  # Yearly Comparison is screen 2
                    self.windows[self.current_window_index].UnHide()
                    result = self.user_manager.set_current_DES("DES3")
                    if result != "Set Screen":
                        sg.popup(result, title="Screen Change Error")

                # They clicked Logout
                elif event == "Logout":
                    self.user_manager.logout()
                    # Close all windows to go back to login
                    for window in self.windows:
                        window.close()
                    self.top_interface.close()
                    return "Logout"

                # They clicked Exit or closed window
                elif event in (sg.WIN_CLOSED, "Exit"):
                    for window in self.windows:
                        window.close()
                    self.top_interface.close()
                    return "Exit"

            # Handle events from the three main screens
            elif window in self.windows:
                
                # They clicked Prev button
                if event == "Prev":
                    # Hide current screen
                    self.windows[self.current_window_index].Hide()
                    # Go to previous screen (wrap around to end if at start)
                    self.current_window_index = (self.current_window_index - 1) % len(
                        self.windows
                    )
                    # Show new screen
                    self.windows[self.current_window_index].UnHide()
                    # Tell UserManager which screen we're on
                    result = self.user_manager.set_current_DES(
                        f"DES{self.current_window_index + 1}"
                    )
                    if result != "Set Screen":
                        sg.popup(result, title="Screen Change Error")

                # They clicked Next button
                elif event == "Next":
                    self.windows[self.current_window_index].Hide()
                    # Go to next screen (wrap around to start if at end)
                    self.current_window_index = (self.current_window_index + 1) % len(
                        self.windows
                    )
                    self.windows[self.current_window_index].UnHide()
                    result = self.user_manager.set_current_DES(
                        f"DES{self.current_window_index + 1}"
                    )
                    if result != "Set Screen":
                        sg.popup(result, title="Screen Change Error")

                # They clicked Send in chat
                elif event == "Send":
                    chat_button.accept(event, values, {"view": window})

                # They clicked Get Current Weather
                elif event == "-FETCH-WEATHER-":
                    if self.current_window_index == 0:  # Only on Current Condition screen
                        state = {
                            "view": window,
                            "update_chart": self.update_chart,
                        }
                        fetch_weather_button.accept(event, values, state)

                # They clicked Compare Cities
                elif event == "-MERGE-CURRENT-":
                    if self.current_window_index == 0:  # Only on Current Condition screen
                        current_condition.handle_compare_cities(window, values)

                # They clicked Get JSON Data
                elif event == "-FETCH-JSON-":
                    if self.current_window_index == 1:  # On Historical Data screen
                        self.json_data = historical_data.handle_json_fetch(
                            window, values
                        )
                    elif self.current_window_index == 2:  # On Yearly Comparison screen
                        self.json_data = yearly_comparison.handle_json_fetch(
                            window, values
                        )

                # They clicked Create Merged Data or Get (NZ+CAN) Merged Data
                elif event == "-MERGE-DATA-":
                    if self.current_window_index == 1:  # On Historical Data screen
                        historical_data.handle_merge_event(
                            window, values, self.json_data
                        )
                    elif self.current_window_index == 2:  # On Yearly Comparison screen
                        yearly_comparison.handle_merge_event(
                            window, values, self.json_data
                        )

                # They closed a screen
                elif event in (sg.WIN_CLOSED, "Exit"):
                    window.close()
                    if window == self.windows[self.current_window_index]:
                        self.current_window_index = None
                    # If all windows closed, exit app
                    if all(not win.TKroot.winfo_exists() for win in self.windows):
                        return "Exit"

        except Exception as e:
            sg.popup_error(f"Error handling event: {str(e)}")
        return None
    

    def run(self):
            """
            This is my main app function that runs everything
            It handles:
            1. Login/register flow
            2. Creating all windows
            3. Main event loop for button clicks
            
            The flow is:
            - Show login until successful
            - Create all windows
            - Handle events until logout/exit
            - Go back to login if they logged out
            
            Called by:
            - main() when app starts
            This is where everything starts!
            """
            while True:
                # First show login window
                print("showing login window...")
                self.current_user = self.handle_login()
                if not self.current_user:
                    break  # They exited instead of logging in

                # After login, create all windows
                print("creating app windows...")
                if not self.initialize_windows():
                    break  # Something went wrong making windows

                # Main event loop - handle all button clicks
                print("starting main event loop...")
                while True:
                    try:
                        # Wait for something to happen
                        window, event, values = sg.read_all_windows()

                        # Check if they're closing app
                        if event in (sg.WIN_CLOSED, "Exit"):
                            # Close everything properly
                            for win in self.windows:
                                win.close()
                            if self.top_interface:
                                self.top_interface.close()
                            return

                        # Handle whatever they did
                        result = self.handle_window_events(window, event, values)
                        if result == "Logout":
                            print("user logged out - going back to login...")
                            break  # Go back to login
                        elif result == "Exit":
                            print("user exited app...")
                            return  # Close program

                    except Exception as e:
                        sg.popup_error(f"Error in main loop: {str(e)}")
                        break


def main():
    """
    This is where my app starts
    It:
    1. Sets the color theme
    2. Creates the app
    3. Runs it
    
    This is the entry point when running main.py
    """
    # Use light green theme for all windows
    sg.theme("LightGreen")
    
    # Create and run the app
    print("starting weather app...")
    app = WeatherApp()
    app.run()


# Only run if this file is run directly
if __name__ == "__main__":
    main()