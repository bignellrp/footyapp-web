from flask import render_template, Blueprint, redirect, url_for, request
from flask_login import login_user

from services.get_user import User

login_blueprint = Blueprint('login',
                             __name__,
                             template_folder='templates',
                             static_folder='static')

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == User("1").username and password == User("1").password:
            user = User("1")  # Create a User object
            remember = True   # Enable cookie-based authentication
            login_user(user, remember=remember)  # Log in the user with cookie-based authentication
            # Authentication successful, redirect to a protected page
            return redirect(url_for('index.index'))
        else:
            error = '*ERROR*: Invalid username or password!'
    return render_template('login.html', error=error)
