"""
Register Window controller

This is my register window button controller. 
This one just handles the Register button click in the login window to open the register window.
When clicked, it sets the state result to Register .it tells the login window to open the register window.
It's like a bridge between the login window and register window.

Reference for state: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2b-one-window-at-a-time
Reference for boolean: https://docs.python.org/3/library/stdtypes.html#boolean-values
Reference for return: https://docs.python.org/3/reference/simple_stmts.html#return
Reference for if statement: https://docs.python.org/3/tutorial/controlflow.html#if-statements
"""

import sys
sys.dont_write_bytecode = True

def accept(event, values, state):
    """
    This is my function that runs when someone clicks the Register button in the login window
    It does this:

    Checks if Register button was clicked
    If clicked:
        Tells state to open register window
        Returns False to close login window

    If not clicked:
        Returns True to keep login window open
    """
    if event == "Register":
        # Tell the login window to open register window
        # I set the result to Register 
        state["view"].set_result("Register")
        # Return False to close login window
        return False
        
    # Return True to keep login window open if Register button wasn't clicked
    return True