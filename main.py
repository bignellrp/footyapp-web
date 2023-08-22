import requests

player_api_url = "http://localhost:8080/players"

def get_playing_players(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()
        # Create the playing_players list with name
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

        # Sort players by name in alphabetical order
        sorted_players = sorted(players, key=lambda player: player["name"])

        # Create the player_totals list with name and total
        player_totals = [
            {"name": player["name"], "total": player["total"]} for player in sorted_players
        ]
        return list(player_totals)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def get_winpercentage(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()

        # Sort players by name in alphabetical order
        sorted_players = sorted(players, key=lambda player: player["winpercent"])

        # Create the player_totals list with name and total
        player_winpercentages = [
            {"name": player["name"], "winpercentage": player["winpercent"]} for player in sorted_players
        ]
        return list(player_winpercentages)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def get_stats(player_api_url):
    response = requests.get(player_api_url)

    if response.status_code == 200:
        players = response.json()

        # Sort players by name in alphabetical order
        sorted_players = sorted(players, key=lambda player: player["name"])

        # Create the player_stats list with name, wins, draws, losses, score and winpercent
        player_stats = [{
            player["name"], 
            player["wins"],
            player["draws"],
            player["losses"],
            player["score"],
            player["winpercent"]
            } for player in sorted_players
        ]
        return list(player_stats)
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
        return list(player_names)
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

stats = get_stats(player_api_url)
print("Stats:", stats)

winpercentages = get_winpercentage(player_api_url)
print("Winpercentages:", winpercentages)