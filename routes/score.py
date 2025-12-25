from flask import render_template, request, Blueprint, redirect, url_for
from services.post_games_data import *
from services.get_games_data import *
from urllib.parse import urlencode
import re
from flask_login import login_required

score_blueprint = Blueprint('score', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@score_blueprint.route('/score', methods=['GET', 'POST'])
@login_required
def score():
    '''A function for building the score page.
    Takes in this weeks score as form input from flask form
    and return update function to add score to databasew'''

    get_teama = teama()
    get_teamb = teamb()
    get_date = date()
    get_scorea = scorea()
    get_scoreb = scoreb()
    get_totala = totala()
    get_totalb = totalb()
    get_coloura = coloura()
    get_colourb = colourb()
    
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
                               error = 'No games found in the database. Please create a game first.')
    
    get_coloura = str(get_coloura)
    get_colourb = str(get_colourb)

    if request.method == 'POST':

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
            params = urlencode({'error': 'Score exists already'})
            return redirect(url_for('score.score') + '?' + params)
        elif match_a == None or match_b == None:
            '''If score is not numeric then error'''
            print("Score is not a valid input")
            params = urlencode({'error': 'Score is not a valid input'})
            return redirect(url_for('score.score') + '?' + params)
        else:
            print("Updating score")
            update_score_result(get_date,score_output)
            params = urlencode({'success': 'Updated successfully'})
            return redirect(url_for('score.score') + '?' + params)
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
                           colourb = get_colourb)