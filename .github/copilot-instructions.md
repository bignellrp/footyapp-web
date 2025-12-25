# Copilot Instructions for footyapp-web

## Project Overview
This is a Flask-based web application for managing a 5-a-side football team. The app helps select balanced teams from available players using a scoring system and integrates with Discord for notifications.

## Tech Stack
- **Backend**: Python 3.9 with Flask
- **Frontend**: HTML templates with Jinja2, Bootstrap (Grayscale theme)
- **Authentication**: Flask-Login with Discord OAuth2
- **Deployment**: Docker, Gunicorn
- **API Integration**: Communicates with a separate REST API (footyapp-api)

## Project Structure
- `main.py` - Main Flask application entry point
- `routes/` - Blueprint modules for different pages (index, player, stats, etc.)
- `services/` - Business logic and data handling functions
- `templates/` - Jinja2 HTML templates
- `static/` - Static assets (CSS, JS, images)
- `requirements.txt` - Python dependencies
- `Dockerfile` and `docker-compose.yml` - Container configuration

## Code Organization and Conventions

### Flask Blueprints
- Each route is organized as a separate blueprint in the `routes/` directory
- Blueprint naming convention: `{module_name}_blueprint` (e.g., `index_blueprint`, `player_blueprint`)
- Blueprints are auto-registered in `main.py` by iterating through the routes folder
- Always use the `@login_required` decorator for protected routes

### Services Layer
- Business logic is separated into the `services/` directory
- Service files use descriptive names (e.g., `get_player_data.py`, `post_games_data.py`)
- Functions should be focused and single-purpose

### Code Style
- Use double hash (`##`) for section comments
- Use single quotes for strings unless double quotes are needed
- Follow PEP 8 naming conventions:
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
- Use descriptive variable names (e.g., `get_all_players`, `team_a_total`)
- Include docstrings for route handlers explaining their purpose

### Error Handling
- Use try-except blocks for operations that may fail (database calls, Discord webhooks)
- Print error messages for debugging (e.g., `print(f"Error: {err}")`)
- Redirect with error messages using URL parameters and urlencode
- Use Flask's session flash messages for user feedback where appropriate

### Input Validation
- Use regex patterns for validating user input (see `player.py` for examples)
- Player names must match pattern: `^[A-Z][a-zA-Z]*$` (capitalized, letters only)
- Numeric values use pattern: `^(?:100|[1-9]?[0-9])$` (0-100)
- Always validate form data before processing

### Session Management
- Use Flask sessions to pass data between routes
- Session is configured to be permanent with 30-day lifetime
- Store temporary data like selected teams, player counts in session

### Environment Configuration
- All configuration uses environment variables loaded from `.env` via `python-dotenv`
- Never commit sensitive data (tokens, secrets, passwords) to the repository
- Environment variables include:
  - Discord OAuth credentials (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
  - Discord webhook URLs for notifications
  - API tokens and URLs
  - Session secret key
  - Branch indicator (GIT_BRANCH) for dev/main environments

### Discord Integration
- Discord webhooks send team notifications before saving
- Separate webhooks for main and dev environments
- Use embeds for formatted Discord messages
- Handle `discord.DiscordException` gracefully

### Authentication
- Uses Flask-Login for session management
- Discord OAuth2 for user authentication
- Login manager configured with `login_view = 'login.login'`
- Sessions persist for 30 days with remember cookie

### Template Rendering
- Context processor injects `env_suffix` to all templates (shows "Dev" for dev branch)
- Use `render_template()` with keyword arguments for passing data
- Error/success messages passed via URL parameters

## Development Workflow

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env file with required variables
# Run the application
python main.py
```

### Docker Deployment
```bash
# Build and run with docker-compose
docker-compose up -d
```

### Branches
- `main` - Production environment
- `dev` - Development environment
- Different Discord webhooks and configurations per branch

## API Integration
- The app communicates with a separate REST API (footyapp-api)
- API URL configured via `API_URL` environment variable
- API authentication uses `API_TOKEN` environment variable
- Functions in `services/` handle GET, POST, UPDATE, DELETE operations

## Form Handling
- Use `request.form['submit_button']` to differentiate between multiple submit buttons
- Use `request.form.getlist()` for checkbox arrays
- Validate required fields before processing
- Redirect with success/error messages using `urlencode()`

## Best Practices
1. **Security**: Never expose secrets, validate all user input, use parameterized queries
2. **Error Handling**: Always handle exceptions gracefully and provide user feedback
3. **Session Data**: Clean up session data when no longer needed
4. **Comments**: Add comments for complex logic, especially in team balancing algorithms
5. **Dependencies**: Keep `requirements.txt` updated when adding new packages
6. **Separation of Concerns**: Keep routes thin, move business logic to services
7. **Environment Awareness**: Use GIT_BRANCH to distinguish between dev and production behavior

## Common Patterns

### Route Structure
```python
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

module_blueprint = Blueprint('module', __name__, 
                            template_folder='templates', 
                            static_folder='static')

@module_blueprint.route('/path', methods=['GET', 'POST'])
@login_required
def handler():
    '''Docstring describing the function'''
    if request.method == 'POST':
        # Handle form submission
        pass
    return render_template('template.html', data=data)
```

### Error Redirect Pattern
```python
from urllib.parse import urlencode

params = urlencode({'error': 'Error message'})
return redirect(url_for('module.handler') + '?' + params)
```

### Discord Webhook Pattern
```python
try:
    url = os.getenv("DISCORD_WEBHOOK")
    webhook = discord.Webhook.from_url(url, 
                                     adapter=discord.RequestsWebhookAdapter())
    # Send message
except discord.DiscordException as e:
    print("Discord Webhook Error!", e)
```

## Testing
- Currently no automated tests in the repository
- Manual testing should focus on:
  - Team balancing algorithm accuracy
  - Form validation
  - Session persistence
  - Discord notifications
  - Authentication flow

## Deployment
- CI/CD configured via `.github/workflows/docker-build.yml`
- Automatic Docker builds on push to `main` or `dev`
- Images pushed to GitHub Container Registry (GHCR)
- Portainer webhook triggers deployment after build
