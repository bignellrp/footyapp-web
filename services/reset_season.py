import requests
import json
import os
import tempfile
import zipfile
from dotenv import load_dotenv

##Load the .env file
load_dotenv()

# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         } 
api_url = os.getenv("API_URL")

def download_season_data():
    '''Download all season data (games and players) as JSON files in a ZIP'''
    
    # URLs for fetching data
    games_api_url = f"{api_url}/games"
    players_api_url = f"{api_url}/players"
    
    # Create a temporary directory to store files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Fetch games data
        games_response = requests.get(games_api_url, headers=access_headers)
        if games_response.status_code == 200:
            games_data = games_response.json()
            games_file_path = os.path.join(temp_dir, 'games.json')
            with open(games_file_path, 'w') as f:
                json.dump(games_data, f, indent=2)
        else:
            print(f"Failed to fetch games data. Status code: {games_response.status_code}")
            raise Exception(f"Failed to fetch games data. Status code: {games_response.status_code}")
        
        # Fetch players data
        players_response = requests.get(players_api_url, headers=access_headers)
        if players_response.status_code == 200:
            players_data = players_response.json()
            players_file_path = os.path.join(temp_dir, 'players.json')
            with open(players_file_path, 'w') as f:
                json.dump(players_data, f, indent=2)
        else:
            print(f"Failed to fetch players data. Status code: {players_response.status_code}")
            raise Exception(f"Failed to fetch players data. Status code: {players_response.status_code}")
        
        # Create ZIP file
        zip_path = os.path.join(temp_dir, 'season_data.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(games_file_path, 'games.json')
            zipf.write(players_file_path, 'players.json')
        
        return zip_path
    
    except Exception as e:
        print(f"Error creating season data ZIP: {e}")
        raise

def reset_season():
    '''Reset the season data by calling the backend API
    
    This function tries to reset the season by deleting all games data.
    The API endpoint pattern follows the RESTful convention where DELETE /games
    would delete all games (reset the season).
    '''
    
    # URL for resetting season - using DELETE on /games collection to reset
    games_api_url = f"{api_url}/games"
    
    try:
        # First try DELETE on the games collection (RESTful pattern for deleting all)
        response = requests.delete(games_api_url, headers=access_headers)
        
        if response.status_code == 200 or response.status_code == 204:
            print("Season reset successfully")
            return {"message": "Season reset successfully", "status_code": 200}
        elif response.status_code == 404:
            # If DELETE returns 404, try alternative endpoint patterns
            print(f"DELETE /games returned 404, trying alternative endpoints")
            
            # Try POST to a dedicated reset endpoint
            alternative_urls = [
                f"{api_url}/reset_season",
                f"{api_url}/games/reset",
                f"{api_url}/games/reset_season"
            ]
            
            for alt_url in alternative_urls:
                try:
                    alt_response = requests.post(alt_url, headers=access_headers)
                    if alt_response.status_code == 200 or alt_response.status_code == 204:
                        print(f"Season reset successfully using {alt_url}")
                        return {"message": "Season reset successfully", "status_code": 200}
                except:
                    continue
            
            # If none worked, return the error
            error_msg = f"Failed to reset season data. All endpoints returned 404. Please check the backend API."
            print(error_msg)
            return {"error": error_msg, "status_code": 404}
        else:
            error_msg = f"Failed to reset season data. Status code: {response.status_code}"
            print(error_msg)
            try:
                error_detail = response.json()
                error_msg += f" Error: {error_detail}"
            except:
                error_msg += f" Error: {response.text}"
            
            return {"error": error_msg, "status_code": response.status_code}
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error occurred while resetting season: {str(e)}"
        print(error_msg)
        return {"error": error_msg, "status_code": 500}
    except Exception as e:
        error_msg = f"Exception occurred while resetting season: {str(e)}"
        print(error_msg)
        return {"error": error_msg, "status_code": 500}

