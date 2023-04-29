import threading
import time
from flask import Flask
from models import db, User, LoginManager, Bcrypt, Listing, ListingTransaction, pytz
from routes.authentication import auth
from routes.home import home
from routes.listings import listing
from datetime import timedelta, datetime

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

# listing update functions
def update_auction_status():
    with app.app_context():
      latvia_timezone = pytz.timezone('Europe/Riga')
      now = datetime.now(latvia_timezone)
      listings = Listing.query.filter(Listing.auctionStatus.in_([0, 1])).all()
      for listing in listings:
          auctionTime = pytz.timezone('UTC').localize(listing.auctionTime).astimezone(latvia_timezone)
          delta = timedelta(minutes=2)

          auctionTimeOffset = timedelta(hours=3)
          auctionTime = auctionTime - auctionTimeOffset
          if auctionTime <= now:
              listing.auctionStatus = 2
          elif auctionTime - now <= delta:
              listing.auctionStatus = 1
          db.session.commit()

def end_auctions():
    with app.app_context():
        listings = Listing.query.filter_by(auctionStatus=2).all()
        for listing in listings:
            listingTransactions = ListingTransaction.query.filter_by(listingID=listing.id, participating=True).all()
            if not listingTransactions:
              listing.auctionStatus = 3
            else:
              listing.price = listing.price + listing.priceIncrease
            db.session.commit()



# listing updater
def listing_update_thread():
    while True:
        update_auction_status()
        end_auctions()
        time.sleep(1)


with app.app_context():
  db.create_all()


# authentication routes
app.register_blueprint(auth, url_prefix="")

# item view and main routes 
app.register_blueprint(home, url_prefix="")

# listing CRUD routes
app.register_blueprint(listing, url_prefix="/prece")





if __name__ == "__main__":
    listingUpdateThread = threading.Thread(target=listing_update_thread)
    listingUpdateThread.start()
    app.run(debug=True, host='0.0.0.0', port=81)