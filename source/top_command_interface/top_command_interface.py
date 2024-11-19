"""
top command interface screen

This is my module for the main menu window of my weather app.
It creates a window with buttons to open each screen:
Current Condition screen
Historical Data screen
Yearly Comparison screen
Exit button to close the app

This module is used by:
my main.py to create the main menu window

References:
Reference for PySimpleGUI: https://www.pysimplegui.org/
Reference for Window: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#window-element
Reference for Button: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#button-element
Reference for Text: https://pysimplegui.readthedocs.io/en/latest/call%20reference/#text-element
Reference for Push: https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2a-extending-window-create-toolbars
Reference for expand_x: https://docs.pysimplegui.com/en/latest/documentation/module/common_element_parameters/#expand_x-expand_y
Reference for location: https://docs.pysimplegui.com/en/latest/call_reference/tkinter/window/
Reference for font: https://docs.pysimplegui.com/en/latest/documentation/module/common_element_parameters/#font
Reference for size: https://docs.pysimplegui.com/en/latest/documentation/module/common_element_parameters/#size
"""

import PySimpleGUI as sg

def create_top_interface():
    """
    This function creates my main menu window with navigation buttons
    
    I use sg.Push() to center everything
    
    The buttons are used by:
    Current Condition: Opens the current weather screen
    Historical Data: Opens the historical comparison screen
    Yearly Comparison: Opens the yearly comparison screen
    Exit: Closes the whole app
    
    Used by my main.py when starting the app
    """
    # Create the layout for my main menu
    layout = [
        [sg.Text('Weather Data App',
                font=('Arial', 20),  
                justification='center',  
                expand_x=True)],  # Make it use full width
        
        # Button for Current Condition screen
        [sg.Push(),
        sg.Button('Current Condition',
                size=(20, 2),  # Width=20, Height=2
                font=('Arial', 14)),  
        sg.Push()],
        
        # Button for Historical Data screen
        [sg.Push(),
        sg.Button('Historical Data',
                size=(20, 2),
                font=('Arial', 14)),
        sg.Push()],
        
        # Button for Yearly Comparison screen
        [sg.Push(),
        sg.Button('Yearly Comparison',
                size=(20, 2),
                font=('Arial', 14)),
        sg.Push()],
        
        # Exit button at bottom
        [sg.Push(),
        sg.Button('Exit',
                size=(10, 2),
                font=('Arial', 14)),
        sg.Push()]
    ]
    
    # Create the window using my layout
    top_command_interface_window = sg.Window(
        'Top Command Interface',  # Window title
        layout,  # The layout i made above
        size=(300, 400),  # width=300, height=400
        location=(None, None),  # Let Windows choose where to put it
    )
    
    return top_command_interface_window