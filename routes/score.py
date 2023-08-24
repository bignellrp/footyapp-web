from flask import render_template, request, Blueprint
from services.post_games_data import *
from services.get_games_data import *
import re

score_blueprint = Blueprint('score', 
                            __name__, 
                            template_folder='templates', 
                            static_folder='static')

@score_blueprint.route('/score', methods=['GET', 'POST'])
def score():
    '''A function for building the score page.
    Takes in this weeks score as form input from flask form
    and return update function to add score to databasew'''

    teama = teama()
    teamb = teamb()
    date = game_data()
    date = date[0]["date"]
    scorea = scorea()
    scoreb = scoreb()
    coloura = coloura()
    colourb = colourb()
    coloura = "/static/"+str(coloura)+".png"
    colourb = "/static/"+str(colourb)+".png"

    if request.method == 'POST':

        ##Get score from form user input
        score_input_a = request.form.get('score_input_a')
        score_input_b = request.form.get('score_input_b')
        score_output = [
            {
            "scoreTeamA": score_input_a,
            "scoreTeamB": score_input_b
            }
        ]

        ##Print the result to database with update enabled
        error = None
        ##Using re.match to check if score input is 2 digits
        match_a = re.match("(^[0-9]{1,2}$)",score_input_a)
        match_b = re.match("(^[0-9]{1,2}$)",score_input_b)
        if scorea != "-":
            '''If there is a score then there 
            isn't a dash in scorea so don't 
            update score and display error'''
            print("Score exists already")
            error = "Score exists already"
        elif match_a == None or match_b == None:
            '''If score is not numeric then error'''
            print("Score is not a valid input")
            error = "Score is not a valid input"
        else:
            print("Updating score")
            update_score_result(score_output)
            
            ##If there is a dash then post is returned after running update
            return render_template('post.html')
        ##If there was an error return the score page with error
        return render_template('score.html', 
                               teama = teama, 
                               teamb = teamb, 
                               date = date, 
                               error = error,
                               coloura = coloura,
                               colourb = colourb)
    ##If request method is not POST then it must be GET
    return render_template('score.html', 
                           teama = teama, 
                           teamb = teamb, 
                           date = date,
                           coloura = coloura,
                           colourb = colourb)