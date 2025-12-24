from flask import render_template, Blueprint, send_file, jsonify
from services.get_games_data import game_stats
from services.get_player_data import player_stats
from flask_login import login_required
import json
import zipfile
import io
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load the .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

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
def reset_season():
    '''Reset the season and return a ZIP file with current stats as backup'''
    try:
        # Get current stats before reset
        get_game_stats = game_stats()
        get_player_stats = player_stats()
        
        # Convert stats to JSON-serializable format
        game_stats_data = [
            {
                "date": date,
                "scoreTeamA": score_a,
                "scoreTeamB": score_b
            }
            for date, score_a, score_b in get_game_stats
        ]
        
        player_stats_data = [
            {
                "name": name,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "score": score,
                "winpercent": winpercent
            }
            for name, wins, draws, losses, score, winpercent in get_player_stats
        ]
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add game stats JSON
            game_stats_json = json.dumps(game_stats_data, indent=2)
            zip_file.writestr('game_stats.json', game_stats_json)
            
            # Add player stats JSON
            player_stats_json = json.dumps(player_stats_data, indent=2)
            zip_file.writestr('player_stats.json', player_stats_json)
        
        # Reset the season via API
        access_token = os.getenv("API_TOKEN")
        api_url = os.getenv("API_URL")
        
        # Validate environment variables
        if not access_token or not api_url:
            logger.error("Missing API_TOKEN or API_URL environment variables")
            return jsonify({"error": "Server configuration error: missing API credentials"}), 500
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Call the API to reset games
        games_reset_url = f"{api_url}/games/reset"
        games_response = requests.delete(games_reset_url, headers=headers)
        
        # Call the API to reset player stats
        players_reset_url = f"{api_url}/players/reset_stats"
        players_response = requests.put(players_reset_url, headers=headers)
        
        # Check if reset was successful
        if games_response.status_code not in [200, 204]:
            logger.error(f"Failed to reset games. Status: {games_response.status_code}")
            return jsonify({"error": "Failed to reset game statistics"}), 500
            
        if players_response.status_code not in [200, 204]:
            logger.error(f"Failed to reset player stats. Status: {players_response.status_code}")
            return jsonify({"error": "Failed to reset player statistics"}), 500
        
        # Prepare ZIP file for download
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stats_backup_{timestamp}.zip"
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"Error in reset_season: {str(e)}")
        return jsonify({"error": "Failed to reset season", "details": str(e)}), 500