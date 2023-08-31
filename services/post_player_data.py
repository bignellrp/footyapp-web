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

def wipe_tally():
    # Prepare the updated data
    updated_data = {"playing": False}

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