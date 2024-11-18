"""
Login controller

This is my login controller. It handles the login event and calls the login method from the UserManager class.
The login method returns a string that is displayed in a popup window.
Then, if the login is successful, the current screen is set to DES1 and the credentials are stored in the state.
If the login is unsuccessful, a popup window is displayed with the error message.

Reference for state: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2b-one-window-at-a-time
Reference for popup: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-popup-windows
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for if statement: https://docs.python.org/3/tutorial/controlflow.html#if-statements
Reference for print: https://docs.python.org/3/tutorial/inputoutput.html#output-formatting
Reference for boolean: https://docs.python.org/3/library/stdtypes.html#boolean-values
Reference for string: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
from User.user_management import UserManager

def accept(event, values, state):
    """
    This is my main login function that runs when someone clicks Login
    It does this:
    Gets the username and password they typed
    Checks if they are in the database using my UserManager class
    If login works:
        Sets their screen to DES1
        Saves their login info in the state
        Closes login window
    If login fails:
        Shows error message in popup
    
    The state dictionary has:
    view: the current window being shown
    result: tuple of (username, password) if login works
    """
    # I use keep_going to control if the login window stays open
    # True means keep showing login window
    # False means close it and go to main app
    keep_going = True

    if event == "Login":
        # I print messages to help me debug
        print("Got login - just testing")
        
        try:
            a_user_manager = UserManager()

            # Get what they typed in the login boxes
            # It has all the info from the window
            user_name = values["User"]  
            password = values["Password"]  
            print(f"Got User = {user_name} , Password = {password} - just testing")

            # Try to log them in
            login_result = a_user_manager.login(user_name, password)
            print(f"Got login result: {login_result}")

            # Check if login worked
            if login_result == "Login Success":
                # Set their starting screen to DES1
                UserManager.current_screen = "DES1"
                # Save their login info in the state
                # The view.set_result puts it in a tuple (username, password)
                state["view"].set_result((user_name, password))
                
                # Close login window
                keep_going = False
            else:
                sg.popup(login_result, title="Login Result")

        except Exception as e:
            # If anything goes wrong, show the error in the console and as a popup
            # This helps me find and fix problems quickly
            print(f"got error in login: {str(e)}")
            sg.popup(f"Login error: {str(e)}", title="Login Error")

    return keep_going