import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

# Get gameday from .env file
INPUT_GAMEDAY = os.getenv("GAMEDAY")

# Convert weekday name to a number (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
weekday_number = datetime.strptime(INPUT_GAMEDAY, "%A").weekday()

def next_weekday(d, weekday):
    '''Takes in todays date and weekday 
    returns the required day in isoformat'''
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)
    
d = datetime.today()
##Games are played on wednesday 
##so returns next wednesday's date
weekday = next_weekday(d, 2).isoformat()
gameday_input = weekday.strftime('%Y-%m-%d')
gameday = datetime.strptime(gameday_input, '%Y-%m-%d')
print(gameday)