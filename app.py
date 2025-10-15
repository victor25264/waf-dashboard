from src.model.user import db, User
from src.dashboard.dash_app import DashAppFactory
from flask import Flask, app, redirect, render_template, request, session, url_for
import os
from dotenv import load_dotenv
from src.waf_data.waf_data_getter import WAFDataGetter
from src.waf_data.health_checker import  HealthChecker
from src.data_processor.data_statistics import DataStatistics
import requests


load_dotenv()

server = Flask(__name__)
server.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
server.config['MAX_LOGIN_ATTEMPTS'] = 3

data_statistics = DataStatistics()

waf_data_getter = WAFDataGetter(
    data_location=os.getenv("WAF_LOGS"),
    secret=os.getenv("WAF_TOKEN"),
    http_client=requests
)

health_checker = HealthChecker(
    url=os.getenv("WAF_HEALTH_CHECK_URL"),
    token=os.getenv("WAF_TOKEN"),
    http_client=requests
)


basedir = os.path.abspath(os.path.dirname(__file__))
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dashboard.db')
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(server)

with server.app_context():
    db.create_all() # Create tables if they don't exist

    # Add default admin user if no users exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        admin_user.set_password('password123') # username: admin, password: password123
        db.session.add(admin_user)
        db.session.commit()
    

dash_factory = DashAppFactory(server, data_statistics, health_checker, waf_data_getter )
   
@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if 'login_attempts' in session and session['login_attempts'] >= server.config['MAX_LOGIN_ATTEMPTS']:
            return 'Account locked. Please try again later.'


        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for(dash_app_instance.config["url_base_pathname"])) # Redirect to Dash app
        else:
            session['login_attempts'] = session.get('login_attempts', 0) + 1
            return render_template('login.html', error='Invalid credentials'), 401
    return render_template('login.html')

@server.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

dash_app_instance = dash_factory.create_dashboard_main()

@server.before_request
def restrict_dash_access():
    if request.path.startswith(dash_app_instance.config["url_base_pathname"]) and not session.get('logged_in'):
        return redirect(url_for('login'))

if __name__ == "__main__":
    server.run(debug=True, port=8050)