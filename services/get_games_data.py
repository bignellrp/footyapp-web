import requests
from services.get_date import next_wednesday
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
    response = requests.get(games_api_url, headers=access_headers)
    if response.status_code == 200:

        games = response.json()

        # Sort players by name in alphabetical order
        # This might not work until date is converted in the api
        sorted_games = sorted(games, key=lambda game: game["date"])

        # Create the player_totals list with name and total
        game_stats = [
            {
                "date" : game["date"],
                "scoreTeamA" : game["scoreTeamA"],
                "scoreTeamB" : game["scoreTeamB"]
            } 
            for game in sorted_games
        ]
        return game_stats
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []
    
def most_recent_game():
    response = requests.get(games_api_url, headers=access_headers)
    if response.status_code == 200:
        games = response.json()

        # Sort games by date in descending order
        # This might not work until date is converted in the api
        sorted_games = sorted(games, key=lambda game: game["date"], reverse=True)

        if sorted_games:
            most_recent_game = sorted_games[0]
            game_data = {
                "date": most_recent_game["date"],
                "teamA": most_recent_game["teamA"],
                "teamB": most_recent_game["teamB"],
                "scoreTeamA": most_recent_game["scoreTeamA"],
                "scoreTeamB": most_recent_game["scoreTeamB"],
                "totalTeamA": most_recent_game["totalTeamA"],
                "totalTeamB": most_recent_game["totalTeamB"],
                "colourTeamA": most_recent_game["colourTeamA"],
                "colourTeamB": most_recent_game["colourTeamB"]
            }
            return [game_data]
        else:
            print("No games found.")
            return []
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def date():
    list = most_recent_game()[0]["date"]
    return list

def teama():
    list = most_recent_game()[0]["teamA"]
    list = ', '.join(map(str, list))
    return list

def teamb():
    list = most_recent_game()[0]["teamB"]
    list = ', '.join(map(str, list))
    return list

def scorea():
    list = most_recent_game()[0]["scoreTeamA"]
    return list

def scoreb():
    list = most_recent_game()[0]["scoreTeamB"]
    return list

def totala():
    list = most_recent_game()[0]["totalTeamA"]
    return list

def totalb():
    list = most_recent_game()[0]["totalTeamB"]
    return list

def coloura():
    list = most_recent_game()[0]["colourTeamA"]
    return list

def colourb():
    list = most_recent_game()[0]["colourTeamB"]
    return list

game_stats = game_stats()
print("Game Stats:", game_stats)

date = date()
print("Date:", date)

teama = teama()
print("TeamA:", teama)

teamb = teamb()
print("TeamB:", teamb)

scorea = scorea()
print("Score Team A:", int(scorea))

scoreb = scoreb()
print("Score Team B:", int(scoreb))

totala = totala()
print("Total Team A:", int(totala))

totalb = totalb()
print("Total Team B:", int(totalb))

coloura = coloura()
print("Colour Team A:", coloura)

colourb = colourb()
print("Colour Team B:", colourb)

most_recent_game = most_recent_game()
print("Most Recent Game:", most_recent_game)