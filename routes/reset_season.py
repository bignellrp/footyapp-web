from flask import Blueprint, send_file, jsonify, render_template, redirect, url_for
from flask_login import login_required
from services.backup_stats import create_backup_zip, reset_season_data
from datetime import datetime
import os

reset_season_blueprint = Blueprint('reset_season', 
                                    __name__, 
                                    template_folder='templates', 
                                    static_folder='static')

@reset_season_blueprint.route('/reset_season', methods=['POST'])
@login_required
def reset_season():
    """
    Handle the Reset Season button press.
    1. Create a backup ZIP of game and player stats
    2. Send the ZIP file as a download
    3. Reset the database
    """
    # Check if we're in dev environment
    git_branch = os.getenv("GIT_BRANCH", "main").lower()
    if git_branch != "dev":
        return jsonify({"error": "Reset Season is only available in dev environment"}), 403
    
    # Create backup ZIP
    zip_buffer = create_backup_zip()
    
    if zip_buffer is None:
        return jsonify({"error": "Failed to create backup. Aborting reset to prevent data loss."}), 500
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"footyapp-seasondump_{timestamp}.zip"
    
    # Send the ZIP file as a download
    # Note: We need to reset AFTER the download completes
    # For now, we'll send the file and the client will trigger the reset
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

@reset_season_blueprint.route('/reset_season_confirm', methods=['POST'])
@login_required
def reset_season_confirm():
    """
    Confirm and execute the database reset after backup download.
    This is called by the client after the download completes.
    """
    # Check if we're in dev environment
    git_branch = os.getenv("GIT_BRANCH", "main").lower()
    if git_branch != "dev":
        return jsonify({"error": "Reset Season is only available in dev environment"}), 403
    
    # Reset the database
    success = reset_season_data()
    
    if success:
        return jsonify({"success": True, "message": "Season data has been reset successfully"}), 200
    else:
        return jsonify({"success": False, "error": "Failed to reset season data"}), 500
