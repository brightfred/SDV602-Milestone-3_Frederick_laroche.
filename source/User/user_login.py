"""
user_login.py

This is my login window class. It creates and manages the login screen.
It works with these controllers:
- login_button.py to handle login attempts
- register_window_button.py to open register window
- exit_button.py to handle closing

Used by:
- main.py to show login screen at startup
- WeatherApp class to manage user login

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for Window: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#window-element
Reference for Button: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#button-element
Reference for InputText: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#input-element
Reference for Theme: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#theme
Reference for Object oriented: https://docs.python.org/3/tutorial/classes.html
Reference for Event Loop: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-1-one-window-runs-start-to-finish
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg

# Import my button controllers
import controller.DES.exit_button as exit_button
import controller.User.login_button as login_button
import controller.User.register_window_button as register_window_button

class LoginView(object):
    def __init__(self):
        """
        This sets up my login window with empty values
        Everything gets created when set_up_layout() is called
        
        I store:
        window: the PySimpleGUI window (None until created)
        layout: list for window layout (empty at start)
        components: dictionary of GUI elements
        controls: list of button handlers
        result: what to return from login attempt
        """
        self.window = None
        self.layout = []
        self.components = {"has_components": False}
        self.controls = []
        self.result = None

    def set_up_layout(self, **kwargs):
        """
        This creates my login window layout
        It has:
        - Username input box
        - Password input box (shows * for typing)
        - Login button
        - Register button (opens register window)
        - Exit button
        
        Each button gets a controller from my imported modules
        """
        # Use light green color theme
        sg.theme("LightGreen")

        # Create input boxes
        self.components["User"] = sg.InputText(
            "",  # Empty at start
            key="User",  # Key for getting values
            size=(20, 1)  # Width=20, Height=1
        )
        self.components["Password"] = sg.InputText(
            "",
            key="Password",
            password_char="*",  # Show * when typing
            size=(20, 1)
        )

        # Create buttons and add their controllers
        # Login button
        self.components["Login"] = sg.Button(
            button_text="Login",
            size=(10, 1)
        )
        self.controls.append(login_button.accept)

        # Register button
        self.components["RegisterWindow"] = sg.Button(
            button_text="Register",
            size=(10, 1)
        )
        self.controls.append(register_window_button.accept)

        # Exit button
        self.components["exit_button"] = sg.Exit(size=(5, 1))
        self.controls.append(exit_button.accept)

        # Put buttons in one row
        row_buttons = [
            self.components["Login"],
            self.components["RegisterWindow"],
            self.components["exit_button"],
        ]

        # Add header text
        self.components["header"] = sg.Text(
            "Weather App Login",
            font=("current 18")
        )

        # Create the whole layout
        self.layout = [
            [self.components["header"]],  # First row: header
            [sg.Text("User Name:", size=(10, 1)),
            self.components["User"]],  # Second row: username
            [sg.Text("Password:", size=(10, 1)),
            self.components["Password"]],  # Third row: password
            row_buttons,  # Fourth row: all buttons
        ]

    def render(self):
        """
        This creates and shows my login window
        Only works if layout is already set up
        """
        if self.layout != []:
            self.window = sg.Window(
                "Login",  # Window title
                self.layout,
                grab_anywhere=False,  # Don't let window be dragged
                finalize=True,  # Create window right away
                return_keyboard_events=True,  # Catch keyboard input
                location=(300, 200)  # Where to put window
            )

    def accept_input(self):
        """
        This handles all the window events (button clicks etc)
        It runs until user logs in, registers, or exits
        Returns the result (like username/password if login works)
        """
        if self.window is not None:
            keep_going = True
            while keep_going:
                # Wait for something to happen
                event, values = self.window.read()
                print(f"Login window event: {event}")  # Help me debug

                # Check if window was closed
                if event in (sg.WIN_CLOSED, "Exit"):
                    self.result = None
                    break

                # Handle button clicks using my controllers
                for accept_control in self.controls:
                    keep_going = accept_control(event, values, {"view": self})
                    if not keep_going:
                        break

            # Clean up and return result
            self.window.close()
            print(f"Login result: {self.result}")  # Help me debug
            return self.result

    def set_result(self, result):
        """
        This saves the login result (like username/password)
        Used by login_button.py when login works
        """
        print(f"Setting login result to: {result}")  # Help me debug
        self.result = result

    def get_size(self):
        """
        This gets the window size if it exists
        Used for positioning other windows
        """
        return self.window.size if self.window else None

    def get_location(self):
        """
        This gets where the window is on screen
        Used for positioning other windows
        """
        return self.window.current_location() if self.window else None

    def close(self):
        """
        This closes the window properly
        Makes sure window is set to None after closing
        """
        if self.window:
            self.window.close()
            self.window = None