from flask import render_template, request, Blueprint
from services.post_player_data import *
from services.get_player_data import *
import re
from flask_login import login_required

player_blueprint = Blueprint('player', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@player_blueprint.route('/player', methods=['GET', 'POST'])
@login_required
def player():
    '''A function for adding a new player'''

    get_all_players = all_players()
    names = [player["name"] for player in get_all_players]
    get_all_player_totals = [{"name": player["name"], "total": player["total"]} for player in get_all_players]
    error = None

    if request.method == 'POST':
            ##Get player from form user input
            player_input = request.form.get('player_input')

            ##Using re.match to check name is in correct format
            match = re.match("(^[A-Z][a-zA-Z]*$)",player_input)
            if player_input in names:
                print("Player exists already")
                error = "Player exists already"
            elif match == None:
                '''If regex is wrong then error'''
                print("Player name input is invalid")
                error = "Player name is not a valid input"
            else:
                print("Adding new player with a generic score of 77")
                add_player(player_input)
                
                ##If there is a dash then post is returned after running update
                return render_template('post.html')
    elif request.method == 'GET':
        ##If request method is not POST then it must be GET
        changed_rows = {}
        error = None
        ##Need to change the validation to be done before values come back to python
        
        for key, value in request.args.items():
            if key.startswith('row_'):
                name = key.replace('row_', '')
                changed_rows[name] = value
                match = re.match("(^(?:100|[1-9]?[0-9])$)", value)
                if match == None:
                    print(name, "has an invalid total")
                    error = f"{name}'s total is not a valid input"
                else:
                    json_value = {"total": value}
                    print(name, json_value)
                    update_player(name, json_value)
        # Refresh the players
        get_all_players = all_players()
        get_all_player_totals = [{"name": player["name"], "total": player["total"]} for player in get_all_players]
                    
        return render_template('player.html', all_players = get_all_player_totals, error=error)