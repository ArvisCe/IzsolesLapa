import time
from flask import Flask
from models import db, User, LoginManager, Bcrypt, Listing, ListingTransaction, pytz
from datetime import timedelta, datetime
from routes.authentication import auth
from routes.home import home
from routes.listings import listing

app = Flask(__name__)
app.secret_key = 'DevelopmentKey123'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///IzsoleLV.db"
app.config['SESSION_PERMANENT'] = True

db.init_app(app)

app.permanent_session_lifetime = timedelta(days=2)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))




