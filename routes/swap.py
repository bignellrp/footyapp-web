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
                    print(f'{current_player} and {new_player} are in Team A: {get_teama}')
                    params = urlencode({'error': f'{current_player} and {new_player} are in Team A'})
                    return redirect(url_for('swap.swap') + '?' + params)
                elif all([current_player in get_teamb, new_player in get_teamb]):
                    print(f'{current_player} and {new_player} are in Team B: {get_teamb}')
                    params = urlencode({'error': f'{current_player} and {new_player} are in Team B'})
                    return redirect(url_for('swap.swap') + '?' + params)
                else:
                    swap_players(current_player, new_player)
                    params = urlencode({'success': 'Updated successfully'})
                    return redirect(url_for('swap.swap') + '?' + params)
            elif request.form['submit_button'] == 'Shuffle':
                # Check if there are games in the database
                if get_date is None:
                    params = urlencode({'error': 'No games found in the database. Please create a game first.'})
                    return redirect(url_for('swap.swap') + '?' + params)
                
                # Retrieve the value of the hidden input 'confirm_shuffle'
                confirm_shuffle_value = request.form.get('confirm_shuffle')
                if confirm_shuffle_value == 'on':
                    available_players = get_teama + get_teamb
                    game_players = []
                    for player in get_all_players:
                        if player['name'] in available_players:
                            game_players.append((player['name'], player['total']))
                    # Run the even teams command with the existing players        
                    get_newteama,get_newteamb,get_newtotala,get_newtotalb = get_even_teams(game_players)

                    get_gameday = gameday()

                    game_json = {
                        "date": get_gameday,
                        "teamA": get_newteama,
                        "teamB": get_newteamb,
                        "scoreTeamA": None,
                        "scoreTeamB": None,
                        "totalTeamA": get_newtotala,
                        "totalTeamB": get_newtotalb,
                        "colourTeamA": get_coloura,
                        "colourTeamB": get_colourb
                    }
                    ##Send Discord Message
                    try:
                        ##Send the teams to discord
                        fileA = discord.File("static/"+get_coloura+".png")
                        fileB = discord.File("static/"+get_colourb+".png")
                        url = os.getenv("DISCORD_WEBHOOK")
                        teama_json = "\n".join(item for item in get_newteama)
                        teamb_json = "\n".join(item for item in get_newteamb)
                        webhook = discord.Webhook.from_url(url, 
                                                        adapter=discord.RequestsWebhookAdapter())
                        ##Embed Message
                        embed1=discord.Embed(title="TEAM A:",
                                            color=discord.Color.dark_green())
                        embed1.set_author(name="footyapp")
                        embed1.add_field(name="TeamA (" 
                                        + str(get_newtotala) 
                                        + "):", value=teama_json, 
                                        inline=True)
                        embed1.set_thumbnail(url="attachment://"+get_coloura+".png")
                        webhook.send(file = fileA, embed = embed1)

                        embed2=discord.Embed(title="TEAM B:",
                                            color=discord.Color.dark_green())
                        embed2.set_author(name="footyapp")
                        embed2.add_field(name="TeamB (" 
                                        + str(get_newtotalb) 
                                        + "):", value=teamb_json, 
                                        inline=True)
                        embed2.set_thumbnail(url="attachment://"+get_colourb+".png")
                        webhook.send(file = fileB, embed = embed2)
                    except:
                        print("Discord Webhook not set")

                    ##Gets Result data for validation
                    get_scorea = scorea()
                    get_date = date()

                    ##Run Update Functions, either update or append
                    if get_date == get_gameday and get_scorea == None:
                        '''If the last row has next wednesdays date 
                        then replace the results.
                        Else append results on a new line'''
                        post.update_result(game_json)
                        print("Running update function")
                    else:
                        post.append_result(game_json)
                        print("Running append function")
                    
                    params = urlencode({'success': 'Teams Updated Successfully!'})
                    return redirect(url_for('swap.swap') + '?' + params)
                #If not confirmed just return the original
                params = urlencode({'error': 'Problem running shuffle!'})
                return redirect(url_for('swap.swap') + '?' + params)
        
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