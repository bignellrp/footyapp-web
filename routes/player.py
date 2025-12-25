from flask import render_template, request, Blueprint, redirect, url_for
from services.post_player_data import *
from services.get_player_data import *
from urllib.parse import urlencode
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

    if request.method == 'POST':
        if request.form['submit_button'] == 'Post':
            ##Get player from form user input
            player_input = request.form.get('player_input')

            ##Using re.match to check name is in correct format
            match = re.match("(^[A-Z][a-zA-Z]*$)",player_input)
            if player_input in names:
                print("Player exists already")
                params = urlencode({'error': 'Player exists already'})
                return redirect(url_for('player.player') + '?' + params)
            elif match == None:
                '''If regex is wrong then error'''
                print("Player name input is invalid")
                params = urlencode({'error': 'Player name is not a valid input'})
                return redirect(url_for('player.player') + '?' + params)
            else:
                print("Adding new player with a generic score of 77")
                add_player(player_input)
                params = urlencode({'success': 'Updated successfully'})
                return redirect(url_for('player.player') + '?' + params)
        elif request.form['submit_button'] == 'Delete':
            ##Get player from form user input
            player_delete = request.form.get('player_delete')

            ##Using re.match to check name is in correct format
            match = re.match("(^[A-Z][a-zA-Z]*$)",player_delete)
            if player_delete not in names:
                print("Player doesnt exist")
                params = urlencode({'error': 'Player doesnt exist'})
                return redirect(url_for('player.player') + '?' + params)
            elif match == None:
                '''If regex is wrong then error'''
                print("Player name input is invalid")
                params = urlencode({'error': 'Player name is not a valid input'})
                return redirect(url_for('player.player') + '?' + params)
            else:
                print(f"Deleting player:{player_delete}")
                delete_player(player_delete)
                params = urlencode({'success': 'Updated successfully'})
                return redirect(url_for('player.player') + '?' + params)
        else:
            print("No button pressed")
            return redirect(url_for('player.player'))
    elif request.method == 'GET':
        ##If request method is not POST then it must be GET
        changed_rows = {}
        error = None
        success = None
        has_row_updates = False
        ##Need to change the validation to be done before values come back to python
        
        for key, value in request.args.items():
            if key.startswith('row_'):
                has_row_updates = True
                name = key.replace('row_', '')
                changed_rows[name] = value
                match = re.match("(^(?:100|[1-9]?[0-9])$)", value)
                if match == None:
                    print(name, "has an invalid total")
                    error = f"{name}'s total is not a valid input"
                    break  # Stop processing on first error
                else:
                    json_value = {"total": int(value)}
                    print(name, json_value)
                    update_player(name, json_value)
                    success = "Updated successfully"
    
        # If we had row updates, redirect to show message
        if has_row_updates:
            if error:
                params = urlencode({'error': error})
                return redirect(url_for('player.player') + '?' + params)
            elif success:
                params = urlencode({'success': success})
                return redirect(url_for('player.player') + '?' + params)
            
        # Changes needed to the JS to send updated name
        # for key, value in request.args.items():
        #     if key.startswith('row_'):
                
        #         old_name = key.replace('row_', '')
        #         new_name, new_total = value.split(':')  # Assuming you pass new name and total separated by ':' 
                
        #         changed_rows[old_name] = {'name': new_name, 'total': new_total}
                
        #         match = re.match("(^(?:100|[1-9]?[0-9])$)", new_total)
                
        #         if match == None:
        #             print(new_name, "has an invalid total")
        #             error = f"{new_name}'s total is not a valid input"
        #         else:
        #             json_value = {"name": new_name, "total": int(new_total)}
        #             print(new_name, json_value)
        #             update_player(old_name, json_value)
        #             tooltip = "Updated successfully"
        
        # Refresh the players
        get_all_players = all_players()
        get_all_player_totals = [{"name": player["name"], "total": player["total"]} for player in get_all_players]
                    
        return render_template('player.html', all_players = get_all_player_totals)