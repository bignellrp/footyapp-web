from flask import render_template, request, Blueprint
from services.post_games_data import *
from services.get_games_data import *
from services.get_player_data import *
from services.get_even_teams import get_even_teams
import re
from flask_login import login_required

swap_blueprint = Blueprint('swap', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@swap_blueprint.route('/swap', methods=['GET', 'POST'])
@login_required
def swap():
    '''A function for adding a new player'''
    error = None
    tooltip = None
    get_all_players = all_players()
    names = [player["name"] for player in get_all_players]

    get_teama = teama()
    get_teamb = teamb()
    get_date = date()
    get_scorea = scorea()
    get_scoreb = scoreb()
    get_totala = totala()
    get_totalb = totalb()
    get_coloura = coloura()
    get_colourb = colourb()
    get_coloura = "/static/"+str(get_coloura)+".png"
    get_colourb = "/static/"+str(get_colourb)+".png"

    if request.method == 'POST':
        if request.form['submit_button'] == 'Swap':
            ##Get vars
            use_player_names = names
            teams = get_teama + get_teamb
            current_player = request.form.get('cur_player_input')
            new_player = request.form.get('new_player_input')
            
            ##Using re.match to check if score input is 2 digits
            match_a = re.match("(^[A-Z][a-zA-Z]*$)",str(current_player))
            match_b = re.match("(^[A-Z][a-zA-Z]*$)",str(new_player))
            
            if get_scorea != None:
                print('Game has already been played this week!')
                error = 'Game has already been played this week!'
            elif match_a == None or match_b == None:
                '''If regex is wrong then error'''
                print("Player name input is invalid")
                error = "Player name is not a valid input"
            elif current_player not in teams:
                print(f'{current_player} is not in the teams list!')
                error = f'{current_player} is not in the teams list!'
            elif new_player not in use_player_names:
                print(f'{new_player} is not in the player list!')
                error = f'{new_player} is not in the player list!'
            elif all([current_player in get_teama, new_player in get_teama]):
                print(f'{current_player} and {new_player} are in Team A: {teama}')
                error = f'{current_player} and {new_player} are in Team A: {teama}'
            elif all([current_player in get_teamb, new_player in get_teamb]):
                print(f'{current_player} and {new_player} are in Team B: {teamb}')
                error = f'{current_player} and {new_player} are in Team B: {teamb}'
            else:
                swap_players(current_player, new_player)
                tooltip = "Updated successfully"
                ##Refresh the teams
                get_teama = teama()
                get_teamb = teamb()
                ##If there is a dash then post is returned after running update
                return render_template('swap.html', 
                                teama = get_teama, 
                                teamb = get_teamb,
                                scorea = get_scorea,
                                scoreb = get_scoreb,
                                totala = get_totala,
                                totalb = get_totalb,
                                date = get_date, 
                                error = error,
                                tooltip = tooltip,
                                coloura = get_coloura,
                                colourb = get_colourb)
            ##If there was an error return the score page with error
            return render_template('swap.html', 
                                teama = get_teama, 
                                teamb = get_teamb,
                                scorea = get_scorea,
                                scoreb = get_scoreb,
                                totala = get_totala,
                                totalb = get_totalb,
                                date = get_date, 
                                error = error,
                                tooltip = tooltip,
                                coloura = get_coloura,
                                colourb = get_colourb)
        if request.form['submit_button'] == 'Shuffle':
            if request.form.get('confirm_shuffle') == 'on':
                available_players = get_teama + get_teamb
                game_players = []
                for player in get_all_players:
                    if player['name'] in available_players:
                        game_players.append((player['name'], player['total']))
                get_teama,get_teamb,get_totala,get_totalb = get_even_teams(game_players)
            return render_template('swap.html', 
                                teama = get_teama, 
                                teamb = get_teamb,
                                scorea = get_scorea,
                                scoreb = get_scoreb,
                                totala = get_totala,
                                totalb = get_totalb,
                                date = get_date, 
                                error = error,
                                tooltip = tooltip,
                                coloura = get_coloura,
                                colourb = get_colourb)
    ##If request method is not POST then it must be GET
    elif request.method == 'GET':
        return render_template('swap.html', 
                               teama = get_teama, 
                               teamb = get_teamb,
                               scorea = get_scorea,
                               scoreb = get_scoreb,
                               totala = get_totala,
                               totalb = get_totalb,
                               date = get_date, 
                               error = error,
                               tooltip = tooltip,
                               coloura = get_coloura,
                               colourb = get_colourb)