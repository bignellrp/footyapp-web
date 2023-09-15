from flask import render_template, request, Blueprint, session
from services.get_player_data import *
from flask_login import login_required

compare_blueprint = Blueprint('compare', 
                              __name__, 
                              template_folder='templates', 
                              static_folder='static')

@compare_blueprint.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    '''A function for building the compare page.
    Takes in available players from a flask form 
    and returns player names and total score for each team'''

    get_all_players = all_players()
    get_player_names = player_names()
    
    if request.method == 'POST':

        ##Use GetList to put the data 
        ##from the index template into the array
        available_players_a = request.form.getlist('available_players_a')
        available_players_b = request.form.getlist('available_players_b')
        check = any(player in available_players_a for player 
                                            in available_players_b)

        if len(available_players_a) < 5 or len(available_players_b) < 5:
            '''If available players less than 10'''
            print("Not enough players!")
            error = "*ERROR*: Please select 10 players!"
            return render_template('compare.html', 
                                   player_names = get_player_names, 
                                   error = error)
        elif check is True:
            '''If Player from ListA is in ListB'''
            print("You cannot have a player in both teams!")
            error = "*ERROR*: You cannot have a player in both teams!" 
            return render_template('compare.html', 
                                   player_names = get_player_names, 
                                   error = error)
        else:
            ##Build teams out of available players 
            ##from all_players using an if statement

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

            team_a = []
            team_b = []
            for player in get_all_players:
                if player['name'] in available_players_a:
                    team_a.append((player['name'], player['total']))
                elif player['name'] in available_players_b:
                    team_b.append((player['name'], player['total']))

            ##Take the first column and put names into team_a and team_b
            team_a_names = sorted([row[0] for row in team_a])
            team_b_names = sorted([row[0] for row in team_b])

            ##Take the second element of the tuple and sum
            team_a_total = sum([row[1] for row in team_a])
            team_b_total = sum([row[1] for row in team_b])
            
            ##Add vars to a session to carry into results page
            session['team_a'] = team_a_names
            session['team_b'] = team_b_names
            session['team_a_total'] = team_a_total
            session['team_b_total'] = team_b_total

            ##Return Team A and Team B to the results template
            return render_template('result.html', 
                                   teama = team_a_names, 
                                   teamb = team_b_names, 
                                   scorea = team_a_total, 
                                   scoreb = team_b_total)
    ##If request method is not POST then it must be GET 
    ##so render compare.html including player_names
    return render_template('compare.html', 
                            player_names = get_player_names)