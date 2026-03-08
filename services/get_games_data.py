import requests
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException, ConnectionError, Timeout
from services.database_error_handler import DatabaseError
from services.cache_service import get_cached, set_cached, CACHE_KEY_GAME_STATS

##Load the .env file
load_dotenv()

# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         } 
api_url = os.getenv("API_URL")
# Url used for games data
games_api_url = f"{api_url}/games"

def game_stats():
    cached = get_cached(CACHE_KEY_GAME_STATS)
    if cached is not None:
        return cached
    try:
        response = requests.get(games_api_url + "/" + "game_stats", headers=access_headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            data = [(game["date"], game["scoreTeamA"], game["scoreTeamB"]) for game in data]
            set_cached(CACHE_KEY_GAME_STATS, data)
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
    except (ConnectionError, Timeout, RequestException) as e:
        print(f"Database connection error in game_stats: {str(e)}")
        raise DatabaseError(f"Database unreachable: {str(e)}")

def all_games():
    '''Fetch all game data including team player lists for stats calculation.
    Returns the full game records needed to compute per-player statistics.'''
    try:
        response = requests.get(games_api_url, headers=access_headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
    except (ConnectionError, Timeout, RequestException) as e:
        print(f"Database connection error in all_games: {str(e)}")
        raise DatabaseError(f"Database unreachable: {str(e)}")

def most_recent_game():
    try:
        response = requests.get(games_api_url + "/" + "most_recent_game", headers=access_headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0] #Output only 1 game
            else:
                return None #No games in DB
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except (ConnectionError, Timeout, RequestException) as e:
        print(f"Database connection error in most_recent_game: {str(e)}")
        raise DatabaseError(f"Database unreachable: {str(e)}")


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