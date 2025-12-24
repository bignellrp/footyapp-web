import requests
import json
import zipfile
import io
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
    "Authorization": f"Bearer {access_token}"
}
api_url = os.getenv("API_URL")

def fetch_all_game_stats():
    """Fetch all game statistics from the API"""
    games_api_url = f"{api_url}/games"
    
    try:
        response = requests.get(games_api_url, headers=access_headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch game stats. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching game stats: {e}")
        return None

def fetch_all_player_stats():
    """Fetch all player statistics from the API"""
    player_api_url = f"{api_url}/players"
    
    try:
        response = requests.get(player_api_url, headers=access_headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch player stats. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return None

def create_backup_zip():
    """
    Create a ZIP file containing game_stats.json and player_stats.json
    Returns a BytesIO object containing the ZIP file or None if error occurs
    """
    # Fetch stats from API
    game_stats = fetch_all_game_stats()
    player_stats = fetch_all_player_stats()
    
    # Check if we successfully fetched both stats
    if game_stats is None:
        print("Failed to fetch game stats for backup")
        return None
    if player_stats is None:
        print("Failed to fetch player stats for backup")
        return None
    
    # Create a BytesIO object to store the ZIP file in memory
    zip_buffer = io.BytesIO()
    
    try:
        # Create ZIP file in memory
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add game_stats.json to ZIP
            game_stats_json = json.dumps(game_stats, indent=2)
            zip_file.writestr('game_stats.json', game_stats_json)
            
            # Add player_stats.json to ZIP
            player_stats_json = json.dumps(player_stats, indent=2)
            zip_file.writestr('player_stats.json', player_stats_json)
        
        # Reset buffer position to the beginning
        zip_buffer.seek(0)
        return zip_buffer
        
    except Exception as e:
        print(f"Error creating backup ZIP: {e}")
        return None

def reset_season_data():
    """
    Call the API endpoint to reset all season data
    Returns True if successful, False otherwise
    """
    reset_api_url = f"{api_url}/reset_season"
    
    try:
        response = requests.post(reset_api_url, headers=access_headers)
        if response.status_code == 200:
            print("Season data reset successfully")
            return True
        else:
            print(f"Failed to reset season data. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error resetting season data: {e}")
        return False
