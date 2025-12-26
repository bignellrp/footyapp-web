from flask import render_template, request, Blueprint, redirect, url_for
from services.post_games_data import *
from services.get_games_data import *
from services.get_player_data import *
from services.get_even_teams import get_even_teams
from services.get_date import gameday
from urllib.parse import urlencode
import services.post_games_data as post
import discord
from dotenv import load_dotenv
import os
import re
from flask_login import login_required

##Load the .env file
load_dotenv()

swap_blueprint = Blueprint('swap', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@swap_blueprint.route('/swap', methods=['GET', 'POST'])
@login_required
def swap():
    '''A function for adding a new player'''
    try:
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

        if request.method == 'POST':
            # ... existing POST logic remains the same ...
            if request.form['submit_button'] == 'Swap':
                # Check if there are games in the database
                if get_date is None:
                    params = urlencode({'error': 'No games found in the database. Please create a game first.'})
                    return redirect(url_for('swap.swap') + '?' + params)
                
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
                    params = urlencode({'error': 'Game has already been played this week!'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif match_a == None or match_b == None:
                    '''If regex is wrong then error'''
                    print("Player name input is invalid")
                    params = urlencode({'error': 'Player name is not a valid input'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif current_player not in teams:
                    print(f'{current_player} is not in the teams list!')
                    params = urlencode({'error': f'{current_player} is not in the teams list!'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif new_player not in use_player_names:
                    print(f'{new_player} is not in the player list!')
                    params = urlencode({'error': f'{new_player} is not in the player list!'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif all([current_player in get_teama, new_player in get_teama]):
                    print(f'{current_player} and {new_player} are in Team A: {teama}')
                    params = urlencode({'error': f'{current_player} and {new_player} are in Team A: {teama}'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif all([current_player in get_teamb, new_player in get_teamb]):
                    print(f'{current_player} and {new_player} are in Team B: {teamb}')
                    params = urlencode({'error': f'{current_player} and {new_player} are in Team B: {teamb}'})
                    return redirect(url_for('swap.swap') + '?' + params)
                else:
                    swap_players(current_player, new_player)
                    params = urlencode({'success': 'Updated successfully'})
                    return redirect(url_for('swap.swap') + '?' + params)
            # ... rest of POST logic for Shuffle remains the same ...
        
        ##If request method is not POST then it must be GET
        return render_template('swap.html', 
                               teama = get_teama, 
                               teamb = get_teamb,
                               scorea = get_scorea,
                               scoreb = get_scoreb,
                               totala = get_totala,
                               totalb = get_totalb,
                               date = get_date,
                               coloura = get_coloura,
                               colourb = get_colourb,
                               database_error = False)
    except Exception as e:
        # Database is unreachable
        print(f"Database error in swap route: {str(e)}")
        return render_template('swap.html', 
                               teama = None, 
                               teamb = None,
                               scorea = None,
                               scoreb = None,
                               totala = None,
                               totalb = None,
                               date = None,
                               coloura = None,
                               colourb = None,
                               database_error = True,
                               error_message = "Unable to connect to database. Please try again later.")