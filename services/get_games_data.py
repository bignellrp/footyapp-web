import requests
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

# Login to the API to get JWT token
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

# Url used for login
login_api_url = "http://localhost:8080/login"

response = requests.post(login_api_url, json={"username": API_USERNAME, "password": API_PASSWORD})
access_token = response.json()["access_token"]
access_headers = {
    "Authorization": f"Bearer {access_token}"
}

# Url used for games data
games_api_url = "http://localhost:8080/games"

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

# def most_recent_game():
#     response = requests.get(games_api_url, headers=access_headers)
#     if response.status_code == 200:
#         games = response.json()

#         # Sort games by date in descending order
#         # This might not work until date is converted in the api
#         sorted_games = sorted(games, key=lambda game: game["date"], reverse=True)

#         if sorted_games:
#             most_recent_game = sorted_games[0]
#             game_data = {
#                 "date": most_recent_game["date"],
#                 "teamA": most_recent_game["teamA"],
#                 "teamB": most_recent_game["teamB"],
#                 "scoreTeamA": most_recent_game["scoreTeamA"],
#                 "scoreTeamB": most_recent_game["scoreTeamB"],
#                 "totalTeamA": most_recent_game["totalTeamA"],
#                 "totalTeamB": most_recent_game["totalTeamB"],
#                 "colourTeamA": most_recent_game["colourTeamA"],
#                 "colourTeamB": most_recent_game["colourTeamB"]
#             }
#             return [game_data]
#         else:
#             print("No games found.")
#             return []
#     else:
#         print(f"Failed to fetch data. Status code: {response.status_code}")
#         return []

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
        return data[0] #Output only 1 game
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []


def date():
    list = most_recent_game()["date"]
    return list

def teama():
    list = most_recent_game()["teamA"]
    #list = ', '.join(map(str, list))
    return list

def teamb():
    list = most_recent_game()["teamB"]
    #list = ', '.join(map(str, list))
    return list

def scorea():
    list = most_recent_game()["scoreTeamA"]
    return list

def scoreb():
    list = most_recent_game()["scoreTeamB"]
    return list

def totala():
    list = most_recent_game()["totalTeamA"]
    return list

def totalb():
    list = most_recent_game()["totalTeamB"]
    return list

def coloura():
    list = most_recent_game()["colourTeamA"]
    return list

def colourb():
    list = most_recent_game()["colourTeamB"]
    return list


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