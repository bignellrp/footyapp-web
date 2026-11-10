from flask import render_template, request, Blueprint, redirect, url_for
from services.post_games_data import *
from services.get_games_data import *
from services.get_date import can_change_colours
from urllib.parse import urlencode
import re
# from flask_login import login_required

score_blueprint = Blueprint('score', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@score_blueprint.route('/score', methods=['GET', 'POST'])
# @login_required  # Disabled: authentication is handled by NPM/Authentik.
def score():
    '''A function for building the score page.
    Takes in this weeks score as form input from flask form
    and return update function to add score to database'''

    try:
        # Work on the selected game (?game=YYYY-MM-DD / hidden form field),
        # falling back to the most recent game
        games = all_games()
        latest_date = games[0]['date'] if games else None
        selected_date = request.values.get('game')
        game = next((g for g in games if g['date'] == selected_date), None) or (games[0] if games else None)
        is_latest = game is not None and game['date'] == latest_date

        def back(params):
            '''Redirect to the score page, staying on the selected game.'''
            if not is_latest:
                params = {'game': game['date'], **params}
            return redirect(url_for('score.score') + '?' + urlencode(params))

        get_teama = game['teamA'] if game else []
        get_teamb = game['teamB'] if game else []
        get_date = game['date'] if game else None
        get_scorea = game['scoreTeamA'] if game else None
        get_scoreb = game['scoreTeamB'] if game else None
        get_totala = game['totalTeamA'] if game else None
        get_totalb = game['totalTeamB'] if game else None
        get_coloura = game['colourTeamA'] if game else None
        get_colourb = game['colourTeamB'] if game else None
        allow_colour_change = can_change_colours(get_date)
        
        # Handle empty games DB
        if get_date is None:
            return render_template('score.html', 
                                   teama = None, 
                                   teamb = None, 
                                   scorea = None,
                                   scoreb = None,
                                   totala = None,
                                   totalb = None,
                                   date = None,
                                   coloura = None,
                                   colourb = None,
                                   allow_colour_change = False,
                                   games = [],
                                   latest_date = None,
                                   database_error = False,
                                   error = 'No games found in the database. Please create a game first.')
        
        get_coloura = str(get_coloura)
        get_colourb = str(get_colourb)

        if request.method == 'POST':
            submit_button = request.form.get('submit_button', 'Save Scores')

            if submit_button == 'Reset Match':
                if get_scorea is None:
                    return back({'error': 'This game has no score to reset'})
                if void_score_result(get_date) is None:
                    return back({'error': 'Could not reset the match. Nothing was changed.'})
                return back({'success': 'Match reset: points removed. Enter the corrected score.'})

            if submit_button == 'Change Colours':
                new_coloura = request.form.get('ImageA')
                new_colourb = request.form.get('ImageB')

                invalid_colour_values = {None, '', 'None', 'teama', 'teamb'}
                if new_coloura in invalid_colour_values or new_colourb in invalid_colour_values:
                    return back({'error': 'Please select a valid colour for both teams'})

                if not allow_colour_change:
                    return back({'error': 'Colour changes are locked after 8pm on game day'})

                game_json = {
                    'date': get_date,
                    'teamA': get_teama,
                    'teamB': get_teamb,
                    'scoreTeamA': get_scorea,
                    'scoreTeamB': get_scoreb,
                    'totalTeamA': get_totala,
                    'totalTeamB': get_totalb,
                    'colourTeamA': new_coloura,
                    'colourTeamB': new_colourb,
                }

                update_result_keep_tally(game_json)
                return back({'success': 'Team colours updated successfully'})

            ##Get score from form user input
            score_input_a = request.form.get('score_input_a')
            score_input_b = request.form.get('score_input_b')
            score_output = {
                "scoreTeamA": score_input_a,
                "scoreTeamB": score_input_b
            }

            ##Print the result to database with update enabled
            ##Using re.match to check if score input is 2 digits
            match_a = re.match("(^[0-9]{1,2}$)",score_input_a)
            match_b = re.match("(^[0-9]{1,2}$)",score_input_b)
            if get_scorea != None:
                '''If there is a score then there 
                isn't a dash in scorea so don't 
                update score and display error'''
                print("Score exists already")
                return back({'error': 'Score exists already'})
            elif match_a == None or match_b == None:
                '''If score is not numeric then error'''
                print("Score is not a valid input")
                return back({'error': 'Score is not a valid input'})
            else:
                print("Updating score")
                # Only the latest game clears this week's Auto selections
                update_score_result(get_date, score_output, wipe=is_latest)
                return back({'success': 'Updated successfully'})
        ##If request method is not POST then it must be GET
        return render_template('score.html', 
                               teama = get_teama, 
                               teamb = get_teamb, 
                               scorea = get_scorea,
                               scoreb = get_scoreb,
                               totala = get_totala,
                               totalb = get_totalb,
                               date = get_date,
                               coloura = get_coloura,
                               colourb = get_colourb,
                               allow_colour_change = allow_colour_change,
                               games = games,
                               latest_date = latest_date,
                               is_latest = is_latest,
                               database_error = False)
    except Exception as e:
        # Database is unreachable
        print(f"Database error in score route: {str(e)}")
        return render_template('score.html', 
                               teama = None, 
                               teamb = None, 
                               scorea = None,
                               scoreb = None,
                               totala = None,
                               totalb = None,
                               date = None,
                               coloura = None,
                               colourb = None,
                               allow_colour_change = False,
                               games = [],
                               latest_date = None,
                               database_error = True,
                               error_message = "Unable to connect to database. Please try again later.")