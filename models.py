from flask_login import UserMixin
from database import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    surname = db.Column(db.String, unique=False, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String, unique=False, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    bio = db.Column(db.String, unique=False, nullable=True)
    gender = db.Column(db.String, unique=False, nullable=True)
    profileImage = db.Column(db.String, unique=False, nullable=True)
  
    verificationCode = db.Column(db.String, unique=False, nullable=False)

    isVerified = db.Column(db.Boolean)
    isDeleted = db.Column(db.Boolean)

    createdOn = db.Column(db.DateTime, unique=False, nullable=False)
    deletedOn = db.Column(db.DateTime, unique=False, nullable=True)
