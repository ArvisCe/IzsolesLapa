from flask import Flask
from database import db
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from routes.authentication import auth
from routes.home import home

app = Flask(__name__)
app.secret_key = 'DevelopmentKey123'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///IzsoleLV.db"

db.init_app(app)

with app.app_context():
  db.create_all()


# authentication routes
app.register_blueprint(auth, url_prefix="")

# item view and main routes 
app.register_blueprint(home, url_prefix="")


if __name__ == "__main__":
    app.run(debug=True)