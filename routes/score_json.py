from flask import Blueprint, jsonify
from services.get_games_data import most_recent_game

score_json_blueprint = Blueprint('score_json', __name__)


@score_json_blueprint.route('/score-json', methods=['GET'])
def score_json():
    '''JSON view of the most recent game.

    Exposes only the game date, team A player names, team B player names
    and each team's shirt colour. Access is controlled upstream by NPM/Authentik; Flask password
    authentication is currently disabled for all pages.
    '''
    try:
        game = most_recent_game()
    except Exception as e:
        print(f"Database error in score-json route: {str(e)}")
        return jsonify({'error': 'Unable to connect to database. Please try again later.'}), 503

    if game is None:
        return jsonify({'error': 'No games found.'}), 404

    return jsonify({
        'date': game.get('date'),
        'teamA': game.get('teamA', []),
        'teamB': game.get('teamB', []),
        'colourTeamA': game.get('colourTeamA'),
        'colourTeamB': game.get('colourTeamB'),
    })
