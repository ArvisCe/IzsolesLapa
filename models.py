from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    surname = db.Column(db.String, unique=False, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    bio = db.Column(db.String, unique=False, nullable=True)
    gender = db.Column(db.String, unique=False, nullable=True)
    profileImage = db.Column(db.String, unique=False, nullable=True)
  
    verificationCode = db.Column(db.String, unique=False, nullable=False)

    isVerified = db.Column(db.Boolean)
    isDeleted = db.Column(db.Boolean)

    createdOn = db.Column(db.DateTime, unique=False, nullable=False)
    deletedOn = db.Column(db.DateTime, unique=False, nullable=True)
