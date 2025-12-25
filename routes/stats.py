from flask import render_template, Blueprint, send_file, jsonify
from services.get_games_data import game_stats
from services.get_player_data import player_stats
from services.reset_season import download_season_data, reset_season
from flask_login import login_required
import os

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

@stats_blueprint.route('/stats/download_season_data', methods=['GET'])
@login_required
def download_data():
    '''Download season data as a ZIP file'''
    try:
        zip_path = download_season_data()
        # Note: The temp directory is not cleaned up immediately as Flask needs
        # to serve the file. The OS will eventually clean up temp files.
        # Consider implementing a cleanup mechanism if this becomes an issue.
        return send_file(zip_path, 
                        as_attachment=True, 
                        download_name='season_data.zip',
                        mimetype='application/zip')
    except Exception as e:
        print(f"Error downloading season data: {e}")
        return jsonify({"error": str(e)}), 500

@stats_blueprint.route('/stats/reset_season', methods=['POST'])
@login_required
def reset():
    '''Reset the season data'''
    try:
        result = reset_season()
        return jsonify(result), result.get('status_code', 200)
    except Exception as e:
        print(f"Error resetting season: {e}")
        return jsonify({"error": str(e)}), 500