from flask import Flask
from routes import *
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from services.get_user import User
#from flask_discord import DiscordOAuth2Session, Unauthorized

##Load the .env file
load_dotenv()

##Create the Flask App
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Get the values of AUTH_USERNAME and AUTH_PASSWORD from the environment variables
auth_username = os.getenv("AUTH_USERNAME")
auth_password = os.getenv("AUTH_PASSWORD")

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

##Import Secret Key for Session Pop
app.secret_key = os.getenv("SESSION")
##Get the Discord OAuth2 Client ID and Secret
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
#app.config["DISCORD_BOT_TOKEN"] = ""

##Set the Discord OAuth2 Client ID and Secret
#discord = DiscordOAuth2Session(app)

##Register the blueprint for each route
# app.register_blueprint(index_blueprint)
# app.register_blueprint(compare_blueprint)
# app.register_blueprint(leaderboard_blueprint)
# app.register_blueprint(stats_blueprint)
# app.register_blueprint(result_blueprint)
# app.register_blueprint(score_blueprint)
# app.register_blueprint(login_blueprint)
# app.register_blueprint(logout_blueprint)
# app.register_blueprint(player_blueprint)
# app.register_blueprint(swap_blueprint)

# Define the folder containing your route blueprints
blueprint_folder = "routes"

# Loop through the files in the folder
for filename in os.listdir(blueprint_folder):
    if filename.endswith(".py"):
        # Import the blueprint module
        module_name = filename[:-3]  # Remove the .py extension
        module = __import__(f"{blueprint_folder}.{module_name}", fromlist=["*"])
        
        # Access the blueprint attribute within the module
        blueprint = getattr(module, f"{module_name}_blueprint", None)
        
        # Register the blueprint with the Flask app if it exists
        if blueprint:
            app.register_blueprint(blueprint)

#Login to Discord
#https://github.com/weibeu/Flask-Discord
# @app.route('/login')
# def login():
#     return discord.create_session()

# @app.route("/callback/")
# def callback():
#     discord.callback()
#     return redirect(url_for("index.index"))

# @app.errorhandler(Unauthorized)
# def redirect_unauthorized(e):
#     return redirect(url_for("login"))


##Run the app
if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False, port=5001)