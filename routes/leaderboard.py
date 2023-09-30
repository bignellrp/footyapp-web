from flask import render_template, Blueprint
from services.get_player_data import get_leaderboard
from flask_login import login_required

leaderboard_blueprint = Blueprint('leaderboard', 
                                  __name__, 
                                  template_folder='templates', 
                                  static_folder='static')

@leaderboard_blueprint.route('/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    '''A function for building the leaderboard page.
    Takes in leaderboard from players table 
    and returns top10 player names and scores'''

    #Example output:

    leaderboard = get_leaderboard()
    
    # Sorting the leaderboard by score (in descending order) and name (in ascending order)
    sorted_leaderboard = sorted(leaderboard, key=lambda x: (-x[1], x[0]))
    
    return render_template('leaderboard.html', 
                            game_stats = sorted_leaderboard)