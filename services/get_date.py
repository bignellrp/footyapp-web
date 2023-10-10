import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

def gameday():

    weekday_mapping = {
        'MONDAY': 0,
        'TUESDAY': 1,
        'WEDNESDAY': 2,
        'THURSDAY': 3,
        'FRIDAY': 4,
        'SATURDAY': 5,
        'SUNDAY': 6,
    }

    INPUT_GAMEDAY = os.getenv("GAMEDAY").strip().upper()
    weekday_number = weekday_mapping.get(INPUT_GAMEDAY)

    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days_ahead)

    d = datetime.today().date()  # Get today's date (ignoring time)
    # Games are played on {INPUT_GAMEDAY}, so return next {INPUT_GAMEDAY} date
    weekday = next_weekday(d, weekday_number)
    gameday = weekday.strftime('%Y-%m-%d')
    
    return gameday