import requests
from dotenv import load_dotenv
import os

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

def game_stats():
    response = requests.get(games_api_url + "/" + "game_stats", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #[('2023-08-30', 30, 20), ('2023-08-16', 3, 2), ('2023-08-15', 3, 2)]
        data = response.json()
        data = [(game["date"], game["scoreTeamA"], game["scoreTeamB"]) for game in data]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def game_wins(player):
    response = requests.get(games_api_url + "/wins/" + player, headers=access_headers)
    if response.status_code == 200:
        #Count games where the player is in teamA and scoreTeamA is greater than scoreTeamB
        data = response.json()
        data = data["wins"]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def most_recent_game():
    response = requests.get(games_api_url + "/" + "most_recent_game", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        # [{'date': '2023-08-30', 
        # 'teamA': [['Player 1', 
        # 'Player 2', 'Player 3', 
        # 'Player 4', 'Player 5']], 
        # 'teamB': [['Player 6', 
        # 'Player 7', 'Player 8', 
        # 'Player 9', 'Player 10']], 
        # 'scoreTeamA': 30, 
        # 'scoreTeamB': 20, 
        # 'totalTeamA': 100, 
        # 'totalTeamB': 100, 
        # 'colourTeamA': 'red', 
        # 'colourTeamB': 'blue'}]
        data = response.json()
        if data:
            return data[0] #Output only 1 game
        else:
            return None #No games in DB
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


def date():
    game = most_recent_game()
    if game is None:
        return None
    return game["date"]

def teama():
    game = most_recent_game()
    if game is None:
        return []
    return game["teamA"]

def teamb():
    game = most_recent_game()
    if game is None:
        return []
    return game["teamB"]

def scorea():
    game = most_recent_game()
    if game is None:
        return None
    return game["scoreTeamA"]

def scoreb():
    game = most_recent_game()
    if game is None:
        return None
    return game["scoreTeamB"]

def totala():
    game = most_recent_game()
    if game is None:
        return None
    return game["totalTeamA"]

def totalb():
    game = most_recent_game()
    if game is None:
        return None
    return game["totalTeamB"]

def coloura():
    game = most_recent_game()
    if game is None:
        return None
    return game["colourTeamA"]

def colourb():
    game = most_recent_game()
    if game is None:
        return None
    return game["colourTeamB"]


#### TESTS #####
# get_game_stats = game_stats()
# print("Game Stats:", get_game_stats)

# get_date = date()
# print("Date:", get_date)

# get_teama = teama()
# print("TeamA:", get_teama)

# get_teamb = teamb()
# print("TeamB:", get_teamb)

# get_scorea = scorea()
# print("Score Team A:", int(get_scorea))

# get_scoreb = scoreb()
# print("Score Team B:", int(get_scoreb))

# get_totala = totala()
# print("Total Team A:", int(get_totala))

# get_totalb = totalb()
# print("Total Team B:", int(get_totalb))

# get_coloura = coloura()
# print("Colour Team A:", get_coloura)

# get_colourb = colourb()
# print("Colour Team B:", get_colourb)

# get_most_recent_game = most_recent_game()
# print("Most Recent Game:", get_most_recent_game)