from flask import render_template, request, Blueprint, session, redirect, url_for
# from flask_login import login_required
from services.get_player_data import *
from services.post_player_data import *
from services.get_games_data import *
from services.get_post_tenant_data import *
from services.get_date import gameday
from services.get_even_teams import get_even_teams
from urllib.parse import urlencode
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

import json

def parse_squad(raw, fallback_playing=None):
    '''Return (playing, reserves) name lists from the Auto screen.
    raw is JSON from the hidden squad input / autosave: {"playing": [...], "reserves": [...]}.
    Falls back to a plain list of ticked names, where the first ones play.'''
    playing, reserves = None, []
    if isinstance(raw, str) and raw:
        try:
            raw = json.loads(raw)
        except ValueError:
            raw = None
    if isinstance(raw, dict):
        playing = raw.get('playing', [])
        reserves = raw.get('reserves', [])
    elif isinstance(raw, list):
        fallback_playing = raw
    if playing is None:
        playing = fallback_playing or []
    def clean(names, seen):
        out = []
        for name in names:
            if isinstance(name, str) and name not in seen and name not in out:
                out.append(name)
        return out
    playing = clean(playing, [])
    reserves = clean(reserves, playing)
    return playing, reserves

def split_squad(playing, reserves, playing_count):
    '''Cap playing at playing_count (overflow joins the front of the reserves) and reserves at MAX_RESERVES.'''
    overflow = playing[playing_count:]
    return playing[:playing_count], (overflow + reserves)[:MAX_RESERVES]

@index_blueprint.route('/', methods=['GET', 'POST'])
#@requires_authorization
# @login_required  # Disabled: authentication is handled by NPM/Authentik.
def index():
    '''A function for building the index page.
    Takes in available players from a flask form 
    and returns an even set of two teams'''

    try:
        # get_all_players = all_players_by_channel()
        # get_player_names = player_names_by_channel()
        get_date = gameday()
        get_all_players = all_players()
        get_player_names = squad_names()
        get_player_count = player_count()

        try:
            if 'playernum' in session:
                players = session['playernum']
            else:
                players = playernum
                session['playernum'] = players
            get_player_count = players - int(get_player_count)
        except Exception as err:
            print(f"Cannot get player count from database due to: {err}")
            get_player_count = 0

        if request.method == 'POST':
            # ... existing POST logic remains the same ...
            if request.form['submit_button'] == 'Post':
                ##Use GetList to put the data 
                ##from the index template into the array
                ordered_playing, ordered_reserves = parse_squad(request.form.get('squad_order'),
                                                                request.form.getlist('available_players'))
                available_players, reserve_players = split_squad(ordered_playing, ordered_reserves, players)
                if len(available_players) < players:
                    '''If playing players less than total (reserves are optional)'''
                    print("Not enough players!")
                    params = urlencode({'error': f'Please select {players} players!'})
                    return redirect(url_for('index.index') + '?' + params)
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

                    ##Save the tally of playing players and the ordered reserves
                    save_squad(available_players, reserve_players)
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
                    if os.getenv('DISCORD_ENABLED', 'false').lower() == 'true':
                        try:
                            file = discord.File("static/football.png")
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
                        
                    # Return Team A and Team B to the results template
                    get_gameday = gameday()
                    return render_template('result.html', 
                                            teama = team_a, 
                                            teamb = team_b, 
                                            scorea = team_a_total, 
                                            scoreb = team_b_total,
                                            date = get_gameday)
            elif request.form['submit_button'] == 'Save':
                ##Use GetList to put the data 
                ##from the index template into the array
                ordered_playing, ordered_reserves = parse_squad(request.form.get('squad_order'),
                                                                request.form.getlist('available_players'))
                available_players, reserve_players = split_squad(ordered_playing, ordered_reserves, players)
                save_squad(available_players, reserve_players)
                print("Running tally function")    
                return redirect(url_for('index.index'))
            elif request.form['submit_button'] == 'Wipe':
                wipe_tally()
                print("Running clear function")    
                return redirect(url_for('index.index'))
            elif request.form['submit_button'] == 'Total':
                try:
                    if request.form.get('players_checkbox') == "True":
                        # checkbox was ticked, the user wants 12 players
                        players_twelve()
                        session['playernum'] = 12
                        print("Changing to 12 players")
                    else: 
                        # checkbox was not ticked, assume user wants 10 players
                        players_ten()
                        session['playernum'] = 10
                        print("Changing to 10 players")
                except Exception as err:
                    print(f"Error changing player number: {err}")

                return redirect(url_for('index.index'))
            else:
                available_players = request.form.getlist('available_players')
                print("No button pressed")
                return redirect(url_for('index.index'))
        elif request.method == 'GET':
            squad_order = json.dumps({
                'playing': [name for name, is_playing, reserve in get_player_names if is_playing],
                'reserves': [name for name, is_playing, reserve in
                             sorted(get_player_names, key=lambda p: p[2]) if reserve and not is_playing],
            })
            return render_template('index.html', 
                                    date = get_date,
                                    player_names = get_player_names, 
                                    player_count = get_player_count,
                                    players = players,
                                    max_reserves = MAX_RESERVES,
                                    squad_order = squad_order,
                                    database_error = False)
    except Exception as e:
        # Database is unreachable
        print(f"Database error in index route: {str(e)}")
        return render_template('index.html', 
                                date = None,
                                player_names = None, 
                                player_count = 0,
                                players = 10,
                                max_reserves = MAX_RESERVES,
                                squad_order = '{"playing": [], "reserves": []}',
                                database_error = True,
                                error_message = "Unable to connect to database. Please check your connection and try again.")

@index_blueprint.route('/autosave', methods=['POST'])
# @login_required  # Disabled: authentication is handled by NPM/Authentik.
def autosave():
    """A route to auto-save checked players as they change."""
    try:
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        playernum_value = int(session.get('playernum', playernum))
        ordered_playing, ordered_reserves = parse_squad(data.get('squad'), data.get('available_players', []))
        if len(ordered_playing) > playernum_value or len(ordered_reserves) > MAX_RESERVES:
            return {'status': 'error',
                    'message': f'Squad is full ({playernum_value} playing + {MAX_RESERVES} reserves)'}, 400

        # Save the playing tally and the ordered reserves
        available_players, reserve_players = split_squad(ordered_playing, ordered_reserves, playernum_value)
        save_squad(available_players, reserve_players)
        print("Autosaved playing tally via API route")
        return {'status': 'success', 'message': 'Tally autosaved successfully'}
    except Exception as e:
        print(f"Error in autosave: {e}")
        return {'status': 'error', 'message': str(e)}, 500