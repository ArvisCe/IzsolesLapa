from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import pytz
from datetime import timedelta, datetime




session = session
db = SQLAlchemy()
bcrypt = Bcrypt()
class User(db.Model, UserMixin):
    __tablename__ = 'User'
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
    isAdmin = db.Column(db.Boolean)
    isVerified = db.Column(db.Boolean)
    isDeleted = db.Column(db.Boolean)
    createdOn = db.Column(db.DateTime, unique=False, nullable=False)
    deletedOn = db.Column(db.DateTime, unique=False, nullable=True)
    Listings = db.relationship('Listing', backref='User', lazy=True)
    ListingTransactions = db.relationship('ListingTransaction', backref='User', lazy=True)
    bankAccount = db.Column(db.String, nullable=True)
    bankName = db.Column(db.String, nullable=True)
    bankSurname = db.Column(db.String, nullable=True)
    

class Listing(db.Model):
    __tablename__ = "Listing"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    startPrice = db.Column(db.Float, nullable=False)
    priceIncrease = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    auctionTime = db.Column(db.DateTime, nullable=False)
    auctionStatus = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String, nullable=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.id'))
    creationDate = db.Column(db.DateTime, nullable=True)
    ListingTransactions = db.relationship('ListingTransaction', backref='Listing', lazy=True)

class ListingTransaction(db.Model):
    __tablename__ = "ListingTransactions"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    participating = db.Column(db.Boolean, nullable=False)
    winner = db.Column(db.Boolean, nullable=False)
    buyerID = db.Column(db.Integer, db.ForeignKey('User.id'))
    listingID =  db.Column(db.Integer, db.ForeignKey('Listing.id'))
    date = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String, nullable=True)
    
    paid = db.Column(db.Boolean, nullable=False)
    
    buyerShaked = db.Column(db.Boolean, nullable=False)
    
    bankDescription = db.Column(db.String, nullable=True)
    
    moneyReceived = db.Column(db.Boolean, nullable=False)