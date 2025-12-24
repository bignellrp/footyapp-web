# Reset Season Feature - Pull Request

## 🎯 Feature Overview

This PR adds a "Reset Season" button to the stats page, allowing authenticated users to reset the season by deleting all games and resetting player statistics.

![Reset Season Button Preview](https://github.com/user-attachments/assets/65a2822e-48d4-4939-af0b-890889ec02e9)

## ✨ What's New

### Frontend Implementation (footyapp-web)

1. **New "Reset Season" Button**
   - Location: Stats page, below the Player Stats table
   - Styling: Bootstrap danger button (red) to indicate destructive action
   - Visibility: Only shown to authenticated users

2. **Confirmation Dialog**
   - Warning message: *"Are you sure you want to reset the season? This will permanently delete all games for the season and reset player stats except for Name and Total."*
   - Prevents accidental data deletion

3. **Backend Integration**
   - New service: `services/reset_season.py`
   - New endpoint: `POST /stats/reset_season`
   - Protected with `@login_required` decorator

## 📋 Functional Requirements (Completed)

- ✅ Button only visible to authenticated users
- ✅ Confirmation dialog with clear warning message
- ✅ Delete all games for the season
- ✅ Reset player stats (preserve only `name` and `total`)
- ✅ Success/error feedback to user
- ✅ Auto-reload page after successful reset

## 🔒 Security Features

- ✅ Authentication required (`@login_required`)
- ✅ Confirmation dialog prevents accidental resets
- ✅ Request timeout protection (30 seconds)
- ✅ Clear warning about permanent data deletion
- ✅ No security vulnerabilities (CodeQL scan passed)

## 📁 Files Changed

### New Files
- `services/reset_season.py` - Service layer for season reset logic
- `API_CHANGES_NEEDED.md` - Documentation for required API changes
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation documentation
- `PR_README.md` - This file

### Modified Files
- `routes/stats.py` - Added reset season endpoint
- `templates/stats.html` - Added button and JavaScript handler

## ⚠️ Important: API Changes Required

**This feature requires two new endpoints in the `footyapp-api` repository:**

### 1. `DELETE /games` - Delete All Games
```python
@games_bp.route('/games', methods=['DELETE'])
def delete_all_games():
    result = games_collection.delete_many({})
    return jsonify({"message": f"{result.deleted_count} games deleted"}), 200
```

### 2. `PUT /players/reset_season` - Reset Player Stats
```python
@players_bp.route('/players/reset_season', methods=['PUT'])
def reset_season_players():
    reset_data = request.json
    allowed_fields = ['wins', 'draws', 'losses', 'score', 'playing', 'played', 'percent', 'winpercent', 'goals']
    filtered_data = {k: v for k, v in reset_data.items() if k in allowed_fields}
    result = players_collection.update_many({}, {"$set": filtered_data})
    return jsonify({"message": f"{result.modified_count} players updated"}), 200
```

See `API_CHANGES_NEEDED.md` for complete implementation details.

## 🧪 Testing

### Code Quality Checks ✅
- [x] Python files compile without errors
- [x] Template validates correctly (Jinja2)
- [x] Code review completed and feedback addressed
- [x] Security scan passed (CodeQL - 0 vulnerabilities)

### Integration Testing (After API Implementation)
- [ ] Button appears for authenticated users
- [ ] Button hidden from unauthenticated users
- [ ] Confirmation dialog works correctly
- [ ] All games deleted after reset
- [ ] Player stats reset correctly (name and total preserved)
- [ ] Success/error messages display properly
- [ ] Page reloads after successful reset

## 🎨 User Flow

1. **Navigate to Stats Page** → User must be logged in
2. **See Reset Season Button** → Red button below player stats table
3. **Click Button** → Confirmation dialog appears
4. **Confirm Action** → Season reset executes
5. **View Results** → Success message, page reloads with reset data

## 📊 Example Data

### Before Reset
```json
{
  "name": "Aaron",
  "total": 85,
  "wins": 5,
  "draws": 2,
  "losses": 3,
  "score": 17,
  "playing": false,
  "played": 10,
  "percent": 50,
  "winpercent": 50,
  "goals": 3
}
```

### After Reset
```json
{
  "name": "Aaron",
  "total": 85,  // ✅ Preserved
  "wins": 0,    // ✅ Reset
  "draws": 0,   // ✅ Reset
  "losses": 0,  // ✅ Reset
  "score": 0,   // ✅ Reset
  "playing": false,
  "played": 0,
  "percent": 0,
  "winpercent": 0,
  "goals": 0
}
```

## 🚀 Deployment Steps

1. **Deploy API Changes First**
   - Implement the two required endpoints in `footyapp-api`
   - Test endpoints independently
   - Deploy to API server

2. **Deploy Web Changes**
   - Merge this PR to dev branch
   - Test in dev environment
   - Verify integration works correctly
   - Merge to main when approved

## 📚 Documentation

- `API_CHANGES_NEEDED.md` - Detailed API endpoint specifications
- `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `PR_README.md` - This pull request overview

## 💡 Notes

- Implementation follows existing codebase patterns
- Minimal changes made (surgical approach)
- No existing functionality broken or removed
- CSRF protection not added (consistent with existing app patterns)
- All player fields reset except `name` and `total` as specified

## 🔗 Related

- API Repository: [bignellrp/footyapp-api](https://github.com/bignellrp/footyapp-api)
- Issue: Add "Reset Season" button to stats page

## ✅ Ready for Review

This PR is complete and ready for review. All code quality checks have passed. The feature is fully functional pending the implementation of the required API endpoints.
