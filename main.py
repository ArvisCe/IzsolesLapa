from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from routes.authentication import auth
from routes.home import home

app = Flask(__name__)
app.secret_key = 'DevelopmentKey123'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///IzsoleLV.db"

db = SQLAlchemy()
db.init_app(app)

# create  databases

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, unique=False, nullable=False)
  bio = db.Column(db.String, unique=False, nullable=True)
  gender = db.Column(db.String, unique=False, nullable=True)
  profileImage = db.Column(db.String, unique=False, nullable=True)
  role = db.Column(db.String, unique=False, nullable=True)
  createdOn = db.Column(db.String, unique=False, nullable=False)


with app.app_context():
  db.create_all()


# authentication routes
app.register_blueprint(auth, url_prefix="")

# item view and main routes 
app.register_blueprint(home, url_prefix="")


if __name__ == "__main__":
    app.run(debug=True)