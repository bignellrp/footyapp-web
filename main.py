from flask import Flask
from routes import *
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

##Create the Flask App
app = Flask(__name__)

##Import Secret Key for Session Pop
app.secret_key = os.getenv("SESSION")

##Register the blueprint for each route
app.register_blueprint(index_blueprint)
app.register_blueprint(compare_blueprint)
app.register_blueprint(leaderboard_blueprint)
app.register_blueprint(stats_blueprint)
app.register_blueprint(result_blueprint)
app.register_blueprint(score_blueprint)

##Run the app
if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False, port=5000)