from flask import Flask
from dotenv import load_dotenv
from connectors.mysql_connector import connection

from flask_session import Session

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.users import Users

from controllers.users import users_routes
from controllers.accounts import accounts_routes
from controllers.transactions import transaction_routes

from flask_login import LoginManager
from flasgger import Swagger
from datetime import timedelta

import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Konfigurasi Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Inisialisasi Flask-Session
Session(app)


app.register_blueprint(users_routes)
app.register_blueprint(accounts_routes)
app.register_blueprint(transaction_routes)

swagger = Swagger(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(users_id):
    Session = sessionmaker(connection)
    s = Session()
    try:
        return s.query(Users).get(int(users_id))
    finally: 
        s.close()

@app.route("/")
def home():
    return "Welcome to MY APP for assignment MILESTONE 3"