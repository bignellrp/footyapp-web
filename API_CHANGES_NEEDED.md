# API Changes Required for Reset Season Feature

This document outlines the changes needed in the `footyapp-api` repository to support the Reset Season feature.

## Required API Endpoints

### 1. DELETE /games - Bulk Delete All Games

**Purpose:** Delete all games from the database to reset the season.

**Implementation in `/tmp/footyapp-api/routes/games.py`:**

Add this endpoint after the existing DELETE endpoint (around line 293):

```python
@games_bp.route('/games', methods=['DELETE'])
#@jwt_required()
def delete_all_games():
    """Delete all games from the database"""
    try:
        result = games_collection.delete_many({})
        return jsonify({
            "message": f"All games deleted successfully. {result.deleted_count} games removed."
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 2. PUT /players/reset_season - Reset Player Stats

**Purpose:** Reset all player statistics while preserving `name` and `total` fields.

**Implementation in `/tmp/footyapp-api/routes/players.py`:**

Add this endpoint after the existing update endpoints (around line 262):

```python
@players_bp.route('/players/reset_season', methods=['PUT'])
#@jwt_required()
def reset_season_players():
    """
    Reset all player stats for a new season.
    Preserves: name, total
    Resets: wins, draws, losses, score, playing, played, percent, winpercent, goals
    """
    try:
        reset_data = request.json
        
        # Ensure we're only resetting the allowed fields
        allowed_fields = ['wins', 'draws', 'losses', 'score', 'playing', 'played', 'percent', 'winpercent', 'goals']
        filtered_data = {k: v for k, v in reset_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return jsonify({"message": "No valid fields to reset"}), 400
        
        # Update all players with the reset data
        result = players_collection.update_many({}, {"$set": filtered_data})
        
        if result.modified_count > 0:
            return jsonify({
                "message": f"Season reset successfully. {result.modified_count} players updated."
            }), 200
        else:
            return jsonify({"message": "No players were updated"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Summary

These two endpoints are required to enable the Reset Season functionality:
- `DELETE /games` - Removes all game records
- `PUT /players/reset_season` - Resets player statistics while preserving name and total

Both endpoints should be protected with JWT authentication when enabled in production.
