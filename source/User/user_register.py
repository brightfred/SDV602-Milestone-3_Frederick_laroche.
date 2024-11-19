"""
user register window class

This is my register window class. It creates and manages the registration screen.
It works with these controllers:
register_button.py to handle registration process
exit_button.py to handle closing events

Used by:
main.py when Register button is clicked


References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for Window: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#window-element
Reference for Button: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#button-element
Reference for InputText: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#input-element
Reference for Theme: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#theme
Reference for Object oriented: https://docs.python.org/3/tutorial/classes.html
Reference for Event Loop: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-1-one-window-runs-start-to-finish
"""

import PySimpleGUI as sg
import controller.DES.exit_button as exit_button
import controller.User.register_button as register_button

class RegisterView(object):
    def __init__(self):
        """
        This sets up my register window with empty values
        Everything gets created when set_up_layout() is called
        """
        self.window = None
        self.layout = []
        self.components = {"has_components": False}
        self.controls = []
        self.result = None

    def set_up_layout(self, **kwargs):
        """
        This creates my register window layout
        It has:
        Username input box
        Password input box (shows * for typing)
        Register button (tries to create account)
        Exit button
        
        Each button gets a controller from my imported modules
        """
        # Use light green color theme to match login window
        sg.theme("LightGreen")

        # Create input boxes
        self.components["User"] = sg.InputText(
            "",  # Empty at start
            key="User",  # Key for getting values
            size=(20, 30)  # Width=20, Height=30
        )
        self.components["Password"] = sg.InputText(
            "",
            key="Password",
            password_char="*",  # Show * when typing
            size=(20, 30)
        )

        # Create buttons and add their controllers
        # Register button
        self.components["Register"] = sg.Button(
            button_text="Register",
            size=(10, 2)  # Width=10, Height=2
        )
        self.controls.append(register_button.accept)

        # Exit button
        self.components["exit_button"] = sg.Exit(size=(5, 2))
        self.controls.append(exit_button.accept)

        # Put buttons in one row
        row_buttons = [
            self.components["Register"],
            self.components["exit_button"]
        ]

        # Add header text
        self.components["header"] = sg.Text(
            "Weather App Registration",
            font=("current 18")
        )

        # Create the whole layout
        self.layout = [
            [self.components["header"]],
            [sg.Text("User Name:", size=(10, 1)),
            self.components["User"]],
            [sg.Text("Password:", size=(10, 1)),
            self.components["Password"]],
            row_buttons,
        ]

    def render(self):
        """
        This creates and shows my register window
        Only works if layout is already set up
        """
        if self.layout != []:
            self.window = sg.Window(
                "Register",  # Window title
                self.layout,
                grab_anywhere=True,
                finalize=True
            )

    def accept_input(self):
        """
        This handles all the window events (button clicks etc)
        It runs until user registers or exits
        Returns the result (like username/password if registration works)
        
        Used by LoginView when Register button clicked
        """
        if self.window is not None:
            keep_going = True
            while keep_going:
                event, values = self.window.read()
                # Let each controller handle the event using a loop
                for accept_control in self.controls:
                    keep_going = accept_control(event, values, {"view": self})
            self.window.close()
            return self.result

    def set_result(self, result):
        """
        This saves the registration result (like username/password)
        """
        self.result = result