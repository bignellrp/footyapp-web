# from routes.compare import compare_blueprint
# from routes.index import index_blueprint
# from routes.leaderboard import leaderboard_blueprint
# from routes.stats import stats_blueprint
# from routes.result import result_blueprint
# from routes.score import score_blueprint
# from routes.login import login_blueprint
# from routes.logout import logout_blueprint
# from routes.player import player_blueprint
# from routes.swap import swap_blueprint

import os
from flask import Blueprint

# Get the directory of the current file (assuming __init__.py is in the same directory)
current_dir = os.path.dirname(__file__)

# Create an empty list to store the blueprints
blueprints = []

# Loop through the files in the current directory
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        # Import the blueprint module using the package name 'routes'
        module_name = filename[:-3]  # Remove the .py extension
        blueprint_module = __import__(f"routes.{module_name}", fromlist=["*"])

        # Get the blueprint object from the module
        blueprint = getattr(blueprint_module, f"{module_name}_blueprint", None)

        # Append the blueprint to the list if it exists
        if blueprint and isinstance(blueprint, Blueprint):
            blueprints.append(blueprint)

# You can now use the 'blueprints' list to register the blueprints in the main.py file.
