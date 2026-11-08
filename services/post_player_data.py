import requests
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

####### JWT AUTH #######
# Login to the API to get JWT token
# API_USERNAME = os.getenv("API_USERNAME")
# API_PASSWORD = os.getenv("API_PASSWORD")

# # Url used for login
# login_api_url = "http://localhost:8080/login"

# response = requests.post(login_api_url, json={"username": API_USERNAME, "password": API_PASSWORD})
# access_token = response.json()["access_token"]
# access_headers = {
#     "Authorization": f"Bearer {access_token}"
# }

#########################
#########################


# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         } 
api_url = os.getenv("API_URL")
# Url used for games data
player_api_url = f"{api_url}/players"

MAX_RESERVES = 5

def wipe_tally(keep_reserves=False):
    # Prepare the updated data. Reserves are kept after a game is saved so the
    # first reserve can still be offered on the Swap page.
    updated_data = {"playing": False}
    if not keep_reserves:
        updated_data["reserve"] = 0

    # Send a PUT request to update all records
    response = requests.put(player_api_url, json=updated_data, headers=access_headers)

    if response.status_code == 200:
        print("All records updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

def update_tally(available_players):

    # Send a PUT request to update all records
    response = requests.put(player_api_url + '/update_playing', json=available_players, headers=access_headers)

    if response.status_code == 200:
        print("Tally updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

def update_reserves(reserve_players):
    """Save an ordered list of reserves (first item is reserve 1)."""
    response = requests.put(player_api_url + '/update_reserves', json=reserve_players, headers=access_headers)

    if response.status_code == 200:
        print("Reserves updated successfully")
    else:
        print(f"Failed to update reserves. Status code: {response.status_code}")

def clear_reserves():
    """Clear every player's reserve place."""
    response = requests.put(player_api_url, json={"reserve": 0}, headers=access_headers)
    if response.status_code != 200:
        print(f"Failed to clear reserves. Status code: {response.status_code}")

def save_squad(playing_players, reserve_players):
    """Replace the saved squad: playing players plus ordered reserves."""
    wipe_tally()
    update_tally(playing_players)
    update_reserves(reserve_players)

def modify_tally(available_players):

    # Send a PUT request to update all records
    response = requests.put(player_api_url + '/update_notplaying', json=available_players, headers=access_headers)

    if response.status_code == 200:
        print("Tally updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

def update_player(player,data):

    # Send a PUT request to update all records
    response = requests.put(player_api_url + '/' + player, json=data, headers=access_headers)

    if response.status_code == 200:
        print("Player updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

def add_player(name):
    
    new_player = {
        "name": name,
        "total": 77,
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

    response = requests.post(player_api_url, json=new_player, headers=access_headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Player added successfully")
        print("Player ID:", response_data["_id"])
    else:
        print(f"Failed to add player. Status code: {response.status_code}")

def delete_player(player):

    # Send a DELETE request to delete the player
    response = requests.delete(player_api_url + '/' + player, headers=access_headers)

    if response.status_code == 200:
        print("Player deleted successfully")
    else:
        print(f"Failed to modify db. Status code: {response.status_code}")