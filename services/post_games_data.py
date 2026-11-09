import requests
from dotenv import load_dotenv
import os
from services.post_player_data import *

##Load the .env file
load_dotenv()

####### JWT AUTH #######
# # Login to the API to get JWT token
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
games_api_url = f"{api_url}/games"

def update_result(game_data):
    '''Update the result of a game that already exists in the database'''
    # Send a PUT request to update all records
    # Example json game_data =
    # {
    # "date": "2023-08-15",
    # "teamA": [
    #     "Player 1",
    #     "Player 2",
    #     "Player 3",
    #     "Player 4",
    #     "Player 5"
    # ],
    # "teamB": [
    #     "Player 6",
    #     "Player 7",
    #     "Player 8",
    #     "Player 9",
    #     "Player 10"
    # ],
    # "scoreTeamA": 3,
    # "scoreTeamB": 2,
    # "totalTeamA": 100,
    # "totalTeamB": 100,
    # "colourTeamA": "red",
    # "colourTeamB": "blue"
    # }
    response = requests.put(games_api_url + "/" + game_data["date"], json=game_data, headers=access_headers)

    if response.status_code == 200:
        print("Game updated successfully")
        wipe_tally(keep_reserves=True)
    else:
        print(f"Failed to update record. Status code: {response.status_code}")


def update_result_keep_tally(game_data):
    '''Update an existing game without wiping player tally.'''
    response = requests.put(games_api_url + "/" + game_data["date"], json=game_data, headers=access_headers)

    if response.status_code == 200:
        print("Game updated successfully")
        # A result has been entered, so the game is played and reserves are no longer needed
        clear_reserves()
    else:
        print(f"Failed to update record. Status code: {response.status_code}")

def append_result(game_data):
    '''Add a new game to the database'''
    # Send a POST request to update all records
    # Example json game_data =
    # {
    # "date": "2023-08-15",
    # "teamA": [
    #     "Player 1",
    #     "Player 2",
    #     "Player 3",
    #     "Player 4",
    #     "Player 5"
    # ],
    # "teamB": [
    #     "Player 6",
    #     "Player 7",
    #     "Player 8",
    #     "Player 9",
    #     "Player 10"
    # ],
    # "scoreTeamA": 3,
    # "scoreTeamB": 2,
    # "totalTeamA": 100,
    # "totalTeamB": 100,
    # "colourTeamA": "red",
    # "colourTeamB": "blue"
    # }
    response = requests.post(games_api_url, json=game_data, headers=access_headers)

    if response.status_code == 200:
        print("Game added successfully")
        wipe_tally(keep_reserves=True)
    else:
        print(f"Failed to add record. Status code: {response.status_code}")

def update_score_result(date, score, wipe=True):
    '''Update the result of a game that already exists in the database
    based on the score the stats are also updated by the API.
    wipe=False leaves this week's Auto selections alone (used when
    re-entering the score of an older game).'''
    # Send a PUT request to update all records
    # Example json score =
    # {
    # "scoreTeamA": 5,
    # "scoreTeamB": 4
    # }
    response = requests.put(games_api_url + "/updatescore/" + date, json=score, headers=access_headers)

    if response.status_code == 200:
        print("Game updated successfully")
        if wipe:
            wipe_tally(keep_reserves=True)
    else:
        print(f"Failed to update record. Status code: {response.status_code}")


def void_score_result(date):
    '''Void a game's stored result. The API takes the points/wins/draws/losses/played
    back off the players and clears the score. Goals are left alone.
    Returns the API's JSON on success, otherwise None.'''
    response = requests.put(games_api_url + "/voidscore/" + date, headers=access_headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to void score. Status code: {response.status_code} {response.text}")
    return None

def swap_players(current_player, new_player):
    '''Swap players in the most recent game and update totals'''
    # Example usage
    # current_player = "PlayerA"
    # new_player = "PlayerB"
    # swap_players(current_player, new_player)
    payload = {
        "current_player": current_player,
        "new_player": new_player
    }
    
    response = requests.put(games_api_url + "/swap_player", json=payload, headers=access_headers)

    if response.status_code == 200:
        print("Players swapped and totals updated successfully")
    else:
        print(f"Failed to swap players. Status code: {response.status_code}")

##### TESTS #####

# current_player = "Cla"
# new_player = "Emily"
# swap_players(current_player, new_player)