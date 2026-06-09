from flask import Flask, session
from routes import *
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from services.get_user import User
from datetime import timedelta, datetime
import subprocess

##Load the .env file
load_dotenv()

##Create the Flask App
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
##Redirect to login page if user is not logged in
login_manager.login_view = 'login.login'

# Get the values of AUTH_USERNAME and AUTH_PASSWORD from the environment variables
auth_username = os.getenv("AUTH_USERNAME")
auth_password = os.getenv("AUTH_PASSWORD")

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

def format_build_timestamp(iso_timestamp):
    """Convert an ISO timestamp to D-DD-MM-YYYY-T-HH:MM:SS format"""
    try:
        # Parse ISO format timestamp (e.g. 2026-06-09T15:12:12+00:00)
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('D-%d-%m-%Y-T-%H:%M:%S')
    except (ValueError, TypeError):
        return iso_timestamp

def get_build_info():
    """Get git commit hash and timestamp for the current build"""
    env_hash = os.getenv('APP_BUILD_SHA')
    env_timestamp = os.getenv('APP_BUILD_TIMESTAMP')
    if env_hash and env_timestamp and env_hash != 'unknown' and env_timestamp != 'unknown':
        return env_hash[:7], format_build_timestamp(env_timestamp)

    try:
        # Try to get the short commit hash
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        # Try to get the commit timestamp in ISO format
        commit_timestamp = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI'],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        return commit_hash, format_build_timestamp(commit_timestamp)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback if git is not available
        now = datetime.utcnow()
        return "unknown", now.strftime('D-%d-%m-%Y-T-%H:%M:%S')

@app.context_processor
def inject_env_indicator():
    """Make environment indicator and build info available to all templates"""
    git_branch = os.getenv("GIT_BRANCH", "main").lower()
    is_dev = git_branch == "dev"
    env_suffix = " Dev" if is_dev else ""
    
    build_hash, build_timestamp = get_build_info()
    
    return dict(
        env_suffix=env_suffix,
        build_hash=build_hash,
        build_timestamp=build_timestamp
    )

@app.template_filter('format_date')
def format_date(date_string):
    """Convert date from YYYY-MM-DD to DD-MM-YYYY format"""
    if date_string is None:
        return None
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        return date_string

@app.template_filter('format_custom_date')
def format_custom_date(date_string):
    """Convert date from YYYY-MM-DD or DD-MM-YYYY to 'Day Month' format (e.g. 10th June)"""
    if date_string is None:
        return None
    date_obj = None
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y'):
        try:
            date_obj = datetime.strptime(date_string, fmt)
            break
        except (ValueError, TypeError):
            continue
            
    if date_obj is None:
        return date_string
        
    day = date_obj.day
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
    return f"{day}{suffix} {date_obj.strftime('%B')}"

##Import Secret Key for Session Pop
app.secret_key = os.getenv("SESSION")
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

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