"""
Register controller

This is my register controller. It handles the register event and calls the register method from the UserManager class.
The register method returns a string that is displayed in a popup window.
If registration is successful, the credentials are stored in the state and the register window closes.
If registration fails, a popup window is displayed with the error message.

Reference for state: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2b-one-window-at-a-time
Reference for popup: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-popup-windows
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for if statement: https://docs.python.org/3/tutorial/controlflow.html#if-statements
Reference for print: https://docs.python.org/3/tutorial/inputoutput.html#output-formatting
Reference for boolean: https://docs.python.org/3/library/stdtypes.html#boolean-values
Reference for string: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
Reference for popup: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-popup-windows
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
from User.user_management import UserManager

def accept(event, values, state):
    """
    This is my main register function that runs when someone clicks Register
    It does this:
    Gets the username and password the users typed
    Tries to register them in the database using the UserManager
    If registration works:
        Saves their info in the state 
        Closes register window
    If registration fails:
        Shows error message in popup
    
    The state dictionary holds:
    view: the current window being shown
    result: tuple of (username, password) if registration works
    """
    # I use keep_going to control if the register window stays open
    # True means keep show the register window
    # False means close it and go back to login
    keep_going = True

    if event == "Register":
        print("Got Register - just testing")
        try:
            a_user_manager = UserManager()
            # Get what they typed in the register boxes
            user_name = values["User"]  
            password = values["Password"]  
            print(f"Got User = {user_name} , Password = {password} - just testing")

            # Try to register them
            register_result = a_user_manager.register(user_name, password)
            print(f"REGISTER RESULT {register_result}")

            # Check if registration worked
            if register_result == "Registration Success":
                # Save their registration info in the state
                state["view"].set_result((user_name, password))
                # Close register window by returning False
                keep_going = False
            else:
                sg.popup(register_result, title="Registration Result")

        except Exception as e:
            # If anything goes wrong, show the error in a popup and print it
            # This helps me find and fix problems quickly
            print(f"got error in register: {str(e)}")
            sg.popup(f"Registration error: {str(e)}", title="Registration Error")

    return keep_going