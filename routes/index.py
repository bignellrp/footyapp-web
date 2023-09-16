from flask import render_template, request, Blueprint, session, redirect, url_for
from flask_login import login_required
from services.get_player_data import *
from services.post_player_data import *
from services.get_games_data import *
from services.get_even_teams import get_even_teams
from services.get_oscommand import GITBRANCH, IFBRANCH
import discord
from dotenv import load_dotenv
import os
#from flask_discord import requires_authorization

##Load the .env file
load_dotenv()

index_blueprint = Blueprint('index', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@index_blueprint.route('/auto', methods=['GET', 'POST'])
#@requires_authorization
@login_required
def index():
    '''A function for building the index page.
    Takes in available players from a flask form 
    and returns an even set of two 5 a side teams'''

    # get_all_players = all_players_by_channel()
    # get_player_names = player_names_by_channel()
    get_all_players = all_players()
    get_player_names = player_names()
    get_player_count = player_count()
    get_date = date()
    try:
        get_player_count = 10 - int(get_player_count)
    except:
        print("Cannot get player count from database!")
        pass

    if request.method == 'POST':
        if request.form['submit_button'] == 'Post':
            ##Use GetList to put the data 
            ##from the index template into the array
            available_players = request.form.getlist('available_players')
            error = None
            if len(available_players) < 10:
                '''If available players less than 10'''
                print("Not enough players!")
                error = "*ERROR*: Please select 10 players!"
                return render_template('index.html', 
                                        player_names = get_player_names, 
                                        player_count = get_player_count, 
                                        date = get_date,
                                        error = error)
            else:
                ##Build list of game_players if 
                ##name exists in available_players
                ##Also build a tally of available players 
                ##to use as a running session

                ##Example input:
                # get_all_players = [
                #     {'name': 'Amy', 'total': 77},
                #     {'name': 'Cal', 'total': 77},
                #     {'name': 'Joe', 'total': 77},
                #     {'name': 'Rik', 'total': 77}
                # ]
                # available_players = ["Amy", "Joe"]

                ##Example ouptput:
                #[('Amy', 77), ('Joe', 77)]

                game_players = []
                for player in get_all_players:
                    if player['name'] in available_players:
                        game_players.append((player['name'], player['total']))

                ##Save the tally of available players
                update_tally(available_players)
                print("Running tally function")   

                ##Takes in game_players and returns teams and totals
                team_a,team_b,team_a_total,team_b_total = get_even_teams(game_players)

                ##Add vars to a session to carry into results page
                session['team_a'] = team_a
                session['team_b'] = team_b
                session['team_a_total'] = team_a_total
                session['team_b_total'] = team_b_total
                print("Posting to results page")

                ##Send the teams to discord presave (only for main)
                try:
                    file = discord.File("static/football.png")
                    if IFBRANCH in GITBRANCH:
                        url = os.getenv("DISCORD_WEBHOOK")
                        teama_json = "\n".join(item for item in team_a)
                        teamb_json = "\n".join(item for item in team_b)
                        webhook = discord.Webhook.from_url(url, 
                                                        adapter=discord.RequestsWebhookAdapter())
                        ##Embed Message
                        embed=discord.Embed(title="PRE-SAVE:",
                                            color=discord.Color.dark_green())
                        embed.set_author(name="footyapp")
                        embed.add_field(name="TeamA (" 
                                        + str(team_a_total) 
                                        + "):", value=teama_json, 
                                        inline=True)
                        embed.add_field(name="TeamB (" 
                                        + str(team_b_total) 
                                        + "):", value=teamb_json, 
                                        inline=True)
                        embed.set_thumbnail(url="attachment://football.png")
                        webhook.send(file = file, embed = embed)
                except discord.DiscordException as e:
                   print("Discord Webhook Error!", e)
                   print("Check .env DISCORD_WEBHOOK is set correctly!")
                   pass
                    
                # Return Team A and Team B to the results template
                return render_template('result.html', 
                                        teama = team_a, 
                                        teamb = team_b, 
                                        scorea = team_a_total, 
                                        scoreb = team_b_total)
        elif request.form['submit_button'] == 'Save':
            ##Use GetList to put the data 
            ##from the index template into the array
            available_players = request.form.getlist('available_players')
            # Update the tally of available players
            update_tally(available_players)
            print("Running tally function")    
            return redirect(url_for('index.index'))
        elif request.form['submit_button'] == 'Wipe':
            wipe_tally()
            print("Running clear function")    
            return redirect(url_for('index.index'))
        else:
            available_players = request.form.getlist('available_players')
            print("No button pressed")
            return redirect(url_for('index.index'))
    elif request.method == 'GET':
        return render_template('index.html', 
                                date = get_date,
                                player_names = get_player_names, 
                                player_count = get_player_count)