import requests
from dotenv import load_dotenv
import os
from services.get_post_tenant_data import get_channelid
from services.cache_service import (get_cached, set_cached,
                                     CACHE_KEY_PLAYER_STATS,
                                     CACHE_KEY_LEADERBOARD)
from services.get_games_data import all_games

##Load the .env file
load_dotenv()

####### JWT AUTH #######
# # Login to the API to get JWT token
# API_USERNAME = os.getenv("API_USERNAME")
# API_PASSWORD = os.getenv("API_PASSWORD")

# # Url used for login
# login_api_url = "http://localhost:8080/login"
# # Prepare the request data
# login_data = {"username": API_USERNAME, "password": API_PASSWORD}

# try:
#     response = requests.post(login_api_url, json=login_data)
#     if response.status_code == 200:
#         # Successful response
#         access_token = response.json()["access_token"]
#         access_headers = {
#             "Authorization": f"Bearer {access_token}"
#         }   
#     else:
#         print(f"Failed to log in. Status code: {response.status_code}")
    
# except requests.exceptions.RequestException as e:
#     print("An error occurred:", e)
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

def player_names():
    response = requests.get(player_api_url + "/" + "player_names", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        # {'name': 'Amy', 'playing': True}, 
        # {'name': 'Cal', 'playing': False}, 
        # {'name': 'Joe', 'playing': True}, 
        # {'name': 'Rik', 'playing': True}
        player_names = response.json()
        # Sort the player_names list first by playing status (True comes first),
        # and then alphabetically by name.
        sorted_players = sorted(player_names, key=lambda x: (not x["playing"], x["name"]))
        # Extract only the name and playing status from the sorted list.
        data = [(player["name"], player["playing"]) for player in sorted_players]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def all_players():
    response = requests.get(player_api_url + "/" + "all_players", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        # [{'name': 'Amy', 'total': 77}, 
        # {'name': 'Cal', 'total': 77}, 
        # {'name': 'Joe', 'total': 77}, 
        # {'name': 'Rik', 'total': 77}]
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def _compute_player_stats(games):
    '''Calculate per-player stats from all game history.

    Points system:
    - Win:  3 points for each player on the winning team
    - Draw: 1 point for each player who participated
    - Loss: 0 points

    Returns a dict mapping player name to {wins, draws, losses}.
    Only games with valid scores are counted.
    '''
    stats = {}
    for game in games:
        score_a = game.get('scoreTeamA')
        score_b = game.get('scoreTeamB')
        team_a = game.get('teamA', [])
        team_b = game.get('teamB', [])

        ## Skip games that haven't had a score entered yet
        if score_a is None or score_b is None:
            continue

        try:
            score_a = int(score_a)
            score_b = int(score_b)
        except (ValueError, TypeError):
            continue

        if score_a > score_b:
            winners, losers = team_a, team_b
        elif score_b > score_a:
            winners, losers = team_b, team_a
        else:
            ## Draw – all participants get 1 point
            for player in list(team_a) + list(team_b):
                stats.setdefault(player, {'wins': 0, 'draws': 0, 'losses': 0})
                stats[player]['draws'] += 1
            continue

        for player in winners:
            stats.setdefault(player, {'wins': 0, 'draws': 0, 'losses': 0})
            stats[player]['wins'] += 1
        for player in losers:
            stats.setdefault(player, {'wins': 0, 'draws': 0, 'losses': 0})
            stats[player]['losses'] += 1

    return stats


def player_stats():
    cached = get_cached(CACHE_KEY_PLAYER_STATS)
    if cached is not None:
        return cached

    ## Fetch all games and calculate stats from game history
    games = all_games()
    calculated = _compute_player_stats(games)

    ## Get all player names so players with zero games still appear
    players = all_players()

    data = []
    for player in players:
        name = player['name']
        pstats = calculated.get(name, {'wins': 0, 'draws': 0, 'losses': 0})
        wins = pstats['wins']
        draws = pstats['draws']
        losses = pstats['losses']
        played = wins + draws + losses
        score = wins * 3 + draws
        winpercent = round((wins / played) * 100, 1) if played > 0 else 0
        data.append((name, wins, draws, losses, score, winpercent))

    set_cached(CACHE_KEY_PLAYER_STATS, data)
    return data

def get_leaderboard():
    cached = get_cached(CACHE_KEY_LEADERBOARD)
    if cached is not None:
        return cached

    ## Derive leaderboard from locally calculated player stats.
    ## Goals are not individually tracked per player so default to 0.
    stats = player_stats()
    data = [(name, score, 0) for name, wins, draws, losses, score, winpercent in stats]

    set_cached(CACHE_KEY_LEADERBOARD, data)
    return data

def winpercentage():
    response = requests.get(player_api_url + "/" + "winpercentage", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #[('Rik', 0), ('Cal', 0), ('Amy', 0), ('Joe', 0)]
        data = response.json()
        data = [(player["name"], player["winpercent"]) for player in data]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def player_count():
    response = requests.get(player_api_url + "/" + "game_player_tally", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #['Rik', 'Amy', 'Joe', 'Cal']
        data = response.json()
        game_player_tally = [(player["name"]) for player in data]
        return len(game_player_tally) # Just return the length of the list
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f'')
        return []

def game_player_tally():
    response = requests.get(player_api_url + "/" + "game_player_tally", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #['Rik', 'Amy', 'Joe']
        data = response.json()
        game_player_tally = [(player["name"]) for player in data]
        return game_player_tally
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f'')
        return []

def game_player_tally_with_score():
    response = requests.get(player_api_url + "/" + "game_player_tally", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #[{'Rik',77},{'Amy',55}]
        data = response.json()
        game_player_tally = [(player["name"], player["total"]) for player in data]
        return game_player_tally
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f'')
        return []

def game_player_tally_with_score_and_index():
    '''A list of players where playing = True, their total and an added index'''
    response = requests.get(player_api_url + "/" + "game_player_tally", headers=access_headers)
    if response.status_code == 200:
        #Example output:
        #[(1, 'Cal', 77), (2, 'Cla', 77)]
        data = response.json()
        print(data)
        game_player_tally = [
            (index + 1, player["name"], player["total"])
            for index, player in enumerate(sorted(data, key=lambda x: x["name"]))
        ]
        return game_player_tally
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f'')
        return []

def all_players_by_channel():
    response = requests.get(player_api_url + "/" + "all_players_by_channel" + "/" + get_channelid, headers=access_headers)
    if response.status_code == 200:
        #Example output:
        # [{'name': 'Amy', 'total': 77}, 
        # {'name': 'Cal', 'total': 77}, 
        # {'name': 'Joe', 'total': 77}, 
        # {'name': 'Rik', 'total': 77}]
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def player_names_by_channel():
    response = requests.get(player_api_url + "/" + "player_names_by_channel" + "/" + get_channelid, headers=access_headers)
    if response.status_code == 200:
        #Example output:
        # {'name': 'Amy', 'playing': True}, 
        # {'name': 'Cal', 'playing': False}, 
        # {'name': 'Joe', 'playing': True}, 
        # {'name': 'Rik', 'playing': True}
        player_names = response.json()
        data = [(player["name"], player["playing"]) for player in player_names]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

##### TESTS #####

# player_names = player_names()
# print("Player Names:", player_names)

# totals = all_players()
# print("Totals:", totals)

# stats = player_stats()
# print("Stats:", stats)

# leaderboard = get_leaderboard()
# print("Leaderboard:", leaderboard)

# winpercentages = winpercentage()
# print("Winpercentages:", winpercentages)

# game_player_tally = game_player_tally()
# player_count = player_count()
# print("Player Count:", player_count)
# print("Game Player Tally:", game_player_tally)

# game_player_tally_with_score_and_index = game_player_tally_with_score_and_index()
# print("Game Player Tally:", game_player_tally_with_score_and_index)