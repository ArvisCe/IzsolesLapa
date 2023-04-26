from flask import Flask
from models import db, User, UserMixin, login_user, LoginManager, login_required, logout_user, current_user, Bcrypt, session
from routes.authentication import auth
from routes.home import home
from routes.listings import listing
import listingUpdater
from datetime import date, timedelta, datetime

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


with app.app_context():
  db.create_all()
  if listingUpdater.scheduler.running:
    listingUpdater.scheduler.shutdown()
  listingUpdater.scheduler.start()


# authentication routes
app.register_blueprint(auth, url_prefix="")

# item view and main routes 
app.register_blueprint(home, url_prefix="")

# listing CRUD routes
app.register_blueprint(listing, url_prefix="/prece")


if __name__ == "__main__":
    app.run(debug=True)