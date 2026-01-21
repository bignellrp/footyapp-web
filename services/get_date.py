import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pytz

# Load the .env file
load_dotenv()

# Cutoff time (hour in GMT) after which games are scheduled for next week
GAME_CUTOFF_HOUR_GMT = 20  # 8pm GMT

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

    def next_weekday(d, weekday, current_time_gmt):
        days_ahead = weekday - d.weekday()
        
        # If it's the same day as the game day
        if days_ahead == 0:
            # Check if current time is before the cutoff hour
            if current_time_gmt.hour < GAME_CUTOFF_HOUR_GMT:
                # Return today's date
                return d
            else:
                # After cutoff hour, return next week's game day
                days_ahead = 7
        elif days_ahead < 0:
            # If the game day has passed this week, get next week's game day
            days_ahead += 7
        
        return d + timedelta(days_ahead)

    # Get current time in GMT
    gmt = pytz.timezone('GMT')
    current_time_gmt = datetime.now(gmt)
    
    d = current_time_gmt.date()  # Get today's date in GMT
    # Games are played on {INPUT_GAMEDAY}, so return appropriate date
    weekday = next_weekday(d, weekday_number, current_time_gmt)
    gameday = weekday.strftime('%Y-%m-%d')
    
    return gameday