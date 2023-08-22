import requests

# Replace with the actual URL of your API endpoint
player_api_url = "http://localhost:8080/players"

def get_playing_players(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()
        playing_players = [{  
                player["name"]
                } for player in players if player.get("playing")
        ]
        return playing_players
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def get_totals(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()
        player_totals = [{  
                player["name"], 
                player["total"]
                } for player in players
        ]
        return player_totals
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def get_all_player_names(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()
        player_names = [{  
                player["name"]
                } for player in players
        ]
        return player_names
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []
    
def get_leaderboard(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()

        # Sort players by score in descending order
        sorted_players = sorted(players, key=lambda player: player["score"], reverse=True)
        
        # Select the top 10 players
        top_players = sorted_players[:10]

        # Create the leaderboard list with name and score
        leaderboard = [
            {"name": player["name"], "score": player["score"]} for player in top_players
        ]
        return leaderboard
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

playing_players = get_playing_players(player_api_url)
print("Playing Players:", playing_players)

totals = get_totals(player_api_url)
print("Totals:", totals)

names = get_all_player_names(player_api_url)
print("Names:", names)

leaderboard = get_leaderboard(player_api_url)
print("Leaderboard:", leaderboard)