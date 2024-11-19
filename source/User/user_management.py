"""
user_management.py

This is my class for managing users and chat in my weather app.
It handles:
User registration and login
Chat messages for each screen
Keeping track of which screen users are on

Uses JSNDrop to store:
User info in tblUser table
Chat messages in tblChatV2 table

References:
Reference for datetime: https://docs.python.org/3/library/datetime.html
Reference for timestamp: https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
Reference for JSNDrop: Comes from Todd examples files in Moodle
"""

from model.network.jsn_drop_service import jsnDrop
from datetime import datetime

class UserManager(object):
    # These variables keep track of the current user state
    current_user = None  # Username of logged in user
    current_pass = None  # Password of logged in user
    current_status = None  # Login status (Logged In/Out)
    current_screen = None  # Which screen they're looking at
    jsn_tok = "96d5a614-3acb-41b4-b7f6-b298368bf871"

    def __init__(self):
        """
        This sets up my UserManager and creates needed tables
        I create:
        tblUser for storing user accounts
        tblChatV2 for storing chat messages
        """
        super().__init__()
        # Connect to JSNDrop service
        self.jsnDrop = jsnDrop(UserManager.jsn_tok, "https://newsimland.com/~todd/JSON")
        result = self.jsnDrop.create(
            "tblUser",
            {
                "PersonID PK": "A_LOOONG_NAME" + ("X" * 50),
                "Password": "A_LOOONG_PASSWORD" + ("X" * 50),
                "Status": "STATUS_STRING",  # Logged In/Out/Registered
            },
        )

        # Create chat table
        self.init_chat()

    def register(self, user_id, password):
        """
        This registers a new user if the username isn't taken
        
        """
        api_result = self.jsnDrop.select("tblUser", f"PersonID = '{user_id}'")
        if "DATA_ERROR" in self.jsnDrop.jsnStatus:  # Username not found
            result = self.jsnDrop.store(
                "tblUser",
                [{"PersonID": user_id, "Password": password, "Status": "Registered"}],
            )
            return "Registration Success"
        else:
            return "User Already Exists"

    def login(self, user_id, password):
        """
        This checks login info and logs user in if correct
        
        Parameters:
        user_id
        password
        """
        api_result = self.jsnDrop.select(
            "tblUser", f"PersonID = '{user_id}' AND Password = '{password}'"
        )
        if "DATA_ERROR" in self.jsnDrop.jsnStatus:
            UserManager.current_status = "Logged Out"
            UserManager.current_user = None
            return "Login Failed"
        else:
            UserManager.current_status = "Logged In"
            UserManager.current_user = user_id
            UserManager.current_pass = password
            self.jsnDrop.store(
                "tblUser",
                [{"PersonID": user_id, "Password": password, "Status": "Logged In"}],
            )
            return "Login Success"

    def logout(self):
        """
        This logs out the current user
        
        Returns:
        Logged Out if worked
        Error message if something went wrong
        "Must be Logged In to LogOut
        """
        if UserManager.current_status == "Logged In":
            api_result = self.jsnDrop.store(
                "tblUser",
                [{
                    "PersonID": UserManager.current_user,
                    "Password": UserManager.current_pass,
                    "Status": "Logged Out",
                }],
            )
            if not "ERROR" in api_result:
                UserManager.current_status = "Logged Out"
                return "Logged Out"
            return self.jsnDrop.jsnStatus
        return "Must be 'Logged In' to 'LogOut'"

    def get_current_user(self):
        """Gets username of logged in user"""
        return UserManager.current_user

    def is_logged_in(self):
        """Checks if someone is logged in"""
        return UserManager.current_status == "Logged In"

    def set_current_DES(self, DESScreen):
        """
        This saves which screen the user is looking at
        
        Parameters:
        DESScreen: which screen they're on (DES1/DES2/DES3)
        
        Returns:
        "Set Screen" if worked
        "Log in to set the current screen" if not logged in
        """
        result = None
        if UserManager.current_status == "Logged In":
            UserManager.current_screen = DESScreen
            result = "Set Screen"
        else:
            result = "Log in"
        return result

    def get_current_screen(self):
        """Gets which screen user is looking at"""
        return UserManager.current_screen

    def init_chat(self):
        """
        This creates the chat table if it doesn't exist
        The table stores:
        PersonID: who sent the message
        DESNumber: which screen it's for
        Chat: the message text
        Time: when it was sent
        """
        result = self.jsnDrop.create(
            "tblChatV2",
            {
                "PersonID": "A_LOOONG_NAME" + ("X" * 50),
                "DESNumber": "A_LOOONG_DES_ID" + ("X" * 50),
                "Chat": "A_LOONG____CHAT_ENTRY" + ("X" * 255),
                "Time": datetime.now().timestamp(),
            },
        )
        return result

    def chat(self, message):
        """
        This saves a new chat message
        
        Parameters:
        message
        
        Returns:
        Chat sent if worked
        Error message if something went wrong
        """
        result = None
        if UserManager.current_status != "Logged In":
            result = "You must be logged in to chat"
        elif UserManager.current_screen == None:
            result = "Chat not sent. A current screen must be set before sending chat - just testing"
        else:
            # Save message with current time and screen
            user_id = UserManager.current_user
            des_screen = UserManager.current_screen
            current_time = datetime.now().timestamp()
            api_result = self.jsnDrop.store(
                "tblChatV2",
                [{
                    "PersonID": user_id,
                    "DESNumber": f"{des_screen}",
                    "Chat": message,
                    "Time": current_time,
                }],
            )
            print(f"Storing chat message: {message}")  # Help me debug
            if "ERROR" in api_result:
                result = self.jsnDrop.jsnStatus
            else:
                result = "Chat sent"
        return result

    def get_chat(self):
        """
        This gets all chat messages for thre current screen
        Messages are sorted by time so they show in order
        I use lambda to sort by time with float conversion
        """
        result = None
        if UserManager.current_status == "Logged In":
            des_screen = UserManager.current_screen
            if not (des_screen is None):
                api_result = self.jsnDrop.select(
                    "tblChatV2", f"DESNumber = '{des_screen}'"
                )
                if not ("DATA_ERROR" in api_result):
                    result = self.jsnDrop.jsnResult
                    # Sort messages by time
                    if result:
                        print(f"Got chat messages: {len(result)}")  # Help me debug
                        try:
                            result = sorted(result, key=lambda x: float(x["Time"]))
                        except Exception as e:
                            print(f"Error sorting messages: {str(e)}")
        return result