from flask import render_template, Blueprint, jsonify, request
from services.get_games_data import game_stats
from services.get_player_data import player_stats
from services.reset_season import reset_season
from flask_login import login_required

stats_blueprint = Blueprint('stats', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@stats_blueprint.route('/stats', methods=['GET'])
@login_required
def stats():
    '''A function for building the stats page.
    Takes in game stats from google sheets 
    and return them to stats page'''

    get_game_stats = game_stats()
    get_player_stats = player_stats()
    
    return render_template('stats.html', 
                           game_stats = get_game_stats, 
                           player_game_stats = get_player_stats)

@stats_blueprint.route('/stats/reset_season', methods=['POST'])
@login_required
def reset_season_endpoint():
    '''Reset the season by deleting all games and resetting player stats.
    Only accessible to authenticated users.'''
    
    result = reset_season()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500