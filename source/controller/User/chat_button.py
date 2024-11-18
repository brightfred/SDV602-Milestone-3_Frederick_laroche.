"""
Chat Controller

This module contains the controller for my chat functionality.
The accept function is called when the Send button is clicked.
I use JSNDrop to store and get chat messages for each screen separately.

Reference for multiline: https://docs.pysimplegui.com/en/latest/documentation/module/elements/multiline/
Reference for datetime: https://docs.python.org/3/library/datetime.html#module-datetime
Reference for push: https://docs.pysimplegui.com/en/latest/documentation/module/layouts/#push
Reference for append: https://docs.pysimplegui.com/en/latest/cookbook/#recipe-recipe-multiline-update
Reference for update: https://docs.pysimplegui.com/en/latest/cookbook/#recipe-recipe-multiline-update
Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
Reference for State: https://docs.pysimplegui.com/en/latest/cookbook/#recipe-recipe-state-management
Reference for lambda: https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
Reference for float: https://docs.python.org/3/library/functions.html#float
Reference for strftime: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
Reference for str: https://docs.python.org/3/library/stdtypes.html#str
"""

import sys
sys.dont_write_bytecode = True
import PySimpleGUI as sg
from datetime import datetime
from User.user_management import UserManager
import requests
import json
import time

""" 
My Chat class for interacting with the JSNDrop service
This class is used to create chat tables, store messages, and get the chat history
Each DES screen has its own chat table in JSNDrop:
Current Condition uses tblChat_DES1
Historical Data uses tblChat_DES2
Yearly Comparison uses tblChat_DES3

Each table has these columns:
PersonID: who sent the message
Message: what they wrote
Time: when they sent it (using timestamp)
"""
class ChatJSNDropService:
    def __init__(self):
        # Setup my connection to JSNDrop
        self.base_url = "https://newsimland.com/~todd/JSON/"
        self.token = "96d5a614-3acb-41b4-b7f6-b298368bf871"
        
        # Make table names for each screen's chat
        self.des1_table = "tblChat_DES1"
        self.des2_table = "tblChat_DES2"
        self.des3_table = "tblChat_DES3"
    
    def create_chat_table(self, table_name):
        """
        This function makes a new chat table in JSNDrop if it doesn't exist
        I use this to make sure each screen has its own chat table
        
        The table has:
        PersonID: up to 50 characters for username
        Message: up to 500 characters for the chat message
        Time: timestamp when message was sent
        Reference for JSNDrop: Comes from Todd examples files in Moodle
        """
        print(f"making chat table {table_name}...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "CREATE": table_name,
                "EXAMPLE": {
                    "PersonID": "A" * 50,
                    "Message": "A" * 500,
                    "Time": time.time()
                }
            }
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print(f"{table_name} is ready")
        return response.json()
    
    def store_message(self, table_name, person_id, message):
        """
        This function saves a new chat message to the table
        It stores:
        who sent it (person_id)
        what they wrote (message)
        when they sent it (current time)
        """
        print(f"saving message to {table_name}...")
        cmd = {
            "tok": self.token,
            "cmd": {
                "STORE": table_name,
                "VALUE": {
                    "PersonID": person_id,
                    "Message": message,
                    "Time": time.time()
                }
            }
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("message is saved")
        return response.json()

    def get_chat_history(self, table_name):
        """
        This function gets all messages from a chat table
        I use this to show the chat history when someone 
        opens a screen or sends a new message
        """
        print(f"getting messages from {table_name}...")
        cmd = {
            "tok": self.token,
            "cmd": {"ALL": table_name}
        }
        response = requests.get(f"{self.base_url}?tok={json.dumps(cmd)}")
        print("got the messages history")
        return response.json()


def accept(event, values, state):
    """
    This is my main chat function that runs when someone clicks Send
    It does these things:
    Gets the message they typed
    Figures out which screen they're on
    Saves their message to the right chat table
    Updates the chat display with all messages
    
    The messages show up like this:
    [TIME] USERNAME: their message
    """
    keep_going = True

    if event == "Send":
        print("Got Chat - just testing")
        
        try:
            # Get the message they typed and clean it up by removing extra spaces
            message = values.get("Message", "").strip()
            if not message:
                return keep_going

            # Setup my chat service and user manager
            a_user_manager = UserManager()
            screen = UserManager.current_screen
            chat_service = ChatJSNDropService()

            # Figure out which chat table to use
            # based on which screen they're on
            if screen == "DES1":
                table_name = chat_service.des1_table
                output_key = "-CHATBOX-CURRENT-CONDITION-"
            elif screen == "DES2":
                table_name = chat_service.des2_table
                output_key = "-CHATBOX-HISTORICAL-DATA-"
            else:
                table_name = chat_service.des3_table
                output_key = "-CHATBOX-YEARLY-COMPARISON-"

            # Make sure the chat table exists and save their message
            chat_service.create_chat_table(table_name)
            result = chat_service.store_message(table_name, a_user_manager.current_user, message)

            if result:
                # Clear the message box after sending it so they can type a new one
                state["view"]["Message"].update("")

                # Get all messages and show them
                response = chat_service.get_chat_history(table_name)
                
                if response.get("JsnMsg") == "SUCCESS.ALL":
                    messages = response.get("Msg", [])
                    
                    # Make the chat text look nice with timestamps
                    # This one was a bit tricky to get right
                    # It gets all messages, sorts them by time, and makes a string
                    # I used a lambda function to sort by the Time key
                    # Then i used float to convert the timestamp to a number
                    # Then i used datetime to convert the number to a date object
                    # Then i used strftime to format the date object as a string
                    # The += operator is to add the new message to the chat text
                    chat_text = ""
                    for msg in sorted(messages, key=lambda x: x.get("Time", 0)):
                        date_obj = datetime.fromtimestamp(float(msg["Time"]))
                        time_str = date_obj.strftime("%H:%M:%S")
                        chat_text += f"[{time_str}] {msg['PersonID']}: {msg['Message']}\n"

                    try:
                        # I used try/except here to catch any errors
                        # If there's an error, it prints the error message
                        # I used update to change the chat display with the new messages
                        # State is a dictionary that holds the current view and data of the app
                        # I used the output_key to find the right chat to update
                        # In my error message, I used str(e) to convert the error to a string to be able to find the error and fix it when it is necessary
                        # Reference for update: https://docs.pysimplegui.com/en/latest/cookbook/#recipe-recipe-multiline-update
                        # Reference for Try/Except: https://docs.python.org/3/tutorial/errors.html
                        # Reference for State: https://docs.pysimplegui.com/en/latest/cookbook/#recipe-recipe-state-management
                        state["view"][output_key].update(chat_text)
                        print(f"Updated chat history for {screen}")
                    except Exception as e:
                        print(f"Error updating chat: {str(e)}")

        except Exception as e:
            print(f"got error in chat: {str(e)}")

    return keep_going