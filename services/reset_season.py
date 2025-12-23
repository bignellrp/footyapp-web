import requests
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         } 
api_url = os.getenv("API_URL")

# URLs for reset operations
games_api_url = f"{api_url}/games"
players_api_url = f"{api_url}/players"

def reset_season():
    """
    Reset the season by:
    1. Deleting all games
    2. Resetting all player stats (except name and total)
    
    Returns:
        dict: Response with success status and message
    """
    try:
        # Step 1: Delete all games
        games_response = requests.delete(games_api_url, headers=access_headers)
        
        if games_response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to delete games. Status code: {games_response.status_code}"
            }
        
        # Step 2: Reset player stats (keeping name and total)
        reset_data = {
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "score": 0,
            "playing": False,
            "played": 0,
            "percent": 0,
            "winpercent": 0,
            "goals": 0
        }
        
        players_response = requests.put(
            f"{players_api_url}/reset_season", 
            json=reset_data, 
            headers=access_headers
        )
        
        if players_response.status_code != 200:
            return {
                "success": False,
                "message": f"Games deleted but failed to reset player stats. Status code: {players_response.status_code}"
            }
        
        return {
            "success": True,
            "message": "Season reset successfully. All games deleted and player stats reset."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error resetting season: {str(e)}"
        }
