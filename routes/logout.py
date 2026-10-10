# Flask password authentication disabled; NPM/Authentik handles login.
# Uncomment this module and the Flask-Login setup to restore it.
# from flask import render_template, Blueprint, redirect, url_for, request
# from flask_login import LoginManager, logout_user, login_required, current_user, UserMixin

# logout_blueprint = Blueprint('logout',
#                                   __name__,
#                                   template_folder='templates',
#                                   static_folder='static')

# @logout_blueprint.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login.login'))
