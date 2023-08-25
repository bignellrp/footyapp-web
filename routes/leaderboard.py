from flask import render_template, Blueprint
from services.get_player_data import get_leaderboard

leaderboard_blueprint = Blueprint('leaderboard', 
                                  __name__, 
                                  template_folder='templates', 
                                  static_folder='static')

@leaderboard_blueprint.route('/leaderboard', methods=['GET'])
def leaderboard():
    '''A function for building the leaderboard page.
    Takes in leaderboard from players table 
    and returns top10 player names and scores'''

    #Example output:

    leaderboard = get_leaderboard()
    
    return render_template('leaderboard.html', 
                            game_stats = leaderboard)