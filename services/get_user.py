from dotenv import load_dotenv
import os
from flask_login import UserMixin

##Load the .env file
load_dotenv()

# Get the values of AUTH_USERNAME and AUTH_PASSWORD from the environment variables
auth_username = os.getenv("AUTH_USERNAME")
auth_password = os.getenv("AUTH_PASSWORD")

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = auth_username
        self.password = auth_password