from flask import render_template, request, Blueprint, session, redirect, url_for
from services.get_date import gameday
import services.post_games_data as post
from services.get_games_data import *
from services.get_oscommand import GITBRANCH, IFBRANCH
import discord
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

result_blueprint = Blueprint('result', 
                             __name__, 
                             template_folder='templates', 
                             static_folder='static')

@result_blueprint.route('/result', methods=['GET', 'POST'])
def result():
    '''A function for building the results page.
    Takes in teama and teamb from flask 
    session so result carries between pages
    and returns the body to the google sheet 
    in row format'''
    
    if request.method == 'POST':
        if request.form['submit_button'] == 'Store':

            ##Get Colour from form
            teama_colour = request.form.get('ImageA')
            teamb_colour = request.form.get('ImageB')
            ##Pull data from flask session
            ##Taken from reddit 
            ##https://www.reddit.com/r/flask/comments/nsghsf/hidden_list/
            teama_passback = session['team_a']
            teamb_passback = session['team_b']
            scorea_passback = session['team_a_total']
            scoreb_passback = session['team_b_total']

            game_json = {
                "date": gameday,
                "teamA": teama_passback,
                "teamB": teamb_passback,
                "scoreTeamA": None,
                "scoreTeamB": None,
                "totalTeamA": scorea_passback,
                "totalTeamB": scoreb_passback,
                "colourTeamA": teama_colour,
                "colourTeamB": teamb_colour
                }

            ##Now vars are safely in the game_json remove 
            ##them from the session so they are not carried 
            ##from page to page unnecessarily.
            session.pop('team_a', None)
            session.pop('team_b', None)
            session.pop('team_a_total', None)
            session.pop('team_b_total', None)


            ##Send Discord Message
            try:
                ##Send the teams to discord
                fileA = discord.File("static/"+teama_colour+".png")
                fileB = discord.File("static/"+teamb_colour+".png")
                if IFBRANCH in GITBRANCH:
                    url = os.getenv("DISCORD_WEBHOOK")
                else:
                    url = os.getenv("DISCORD_WEBHOOK_DEV")
                teama_json = "\n".join(item for item in teama_passback)
                teamb_json = "\n".join(item for item in teamb_passback)
                webhook = discord.Webhook.from_url(url, 
                                                adapter=discord.RequestsWebhookAdapter())
                ##Embed Message
                embed1=discord.Embed(title="TEAM A:",
                                    color=discord.Color.dark_green())
                embed1.set_author(name="footyapp")
                embed1.add_field(name="TeamA (" 
                                + str(scorea_passback) 
                                + "):", value=teama_json, 
                                inline=True)
                embed1.set_thumbnail(url="attachment://"+teama_colour+".png")
                webhook.send(file = fileA, embed = embed1)

                embed2=discord.Embed(title="TEAM B:",
                                    color=discord.Color.dark_green())
                embed2.set_author(name="footyapp")
                embed2.add_field(name="TeamB (" 
                                + str(scoreb_passback) 
                                + "):", value=teamb_json, 
                                inline=True)
                embed2.set_thumbnail(url="attachment://"+teamb_colour+".png")
                webhook.send(file = fileB, embed = embed2)
            except:
                print("Discord Webhook not set")
                pass

            ##Gets Result data for validation
            get_scorea = scorea()
            get_date = date()

            ##Run Update Functions, either update or append
            if get_date == gameday and get_scorea == None:
                '''If the last row has next wednesdays date 
                then replace the results.
                Else append results on a new line'''
                post.update_result(game_json)
                print("Running update function")
            else:
                post.append_result(game_json)
                print("Running append function")

            ##Return Team A and Team B to the results template
            return render_template('post.html')
        if request.form['submit_button'] == 'Rerun':
            print("Rerun button pressed!")
            try:
                ##Send Rerun message to discord
                if IFBRANCH in GITBRANCH:
                    url = os.getenv("DISCORD_WEBHOOK")
                else:
                    url = os.getenv("DISCORD_WEBHOOK_DEV")
                webhook = discord.Webhook.from_url(url, 
                                                adapter=discord.RequestsWebhookAdapter())
                ##Embed Message
                embed=discord.Embed(title="Rerun button pressed",
                                    color=discord.Color.dark_green())
                embed.set_author(name="footyapp")
                webhook.send(embed = embed)
            except:
                print("Discord Webhook not set")
                pass
            return redirect(url_for('index.index'))
    elif request.method == 'GET':
        ##If request method is not POST then it must be GET
        return render_template('result.html')