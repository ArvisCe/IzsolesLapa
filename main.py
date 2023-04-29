import multiprocessing
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

with app.app_context():
  db.create_all()

app.register_blueprint(auth, url_prefix="")
app.register_blueprint(home, url_prefix="")
app.register_blueprint(listing, url_prefix="/prece")

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
          print(f"Auction time: {auctionTime}")
          print(f"Now: {now}")
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

def run_flask_app():
    app.run(debug=True, host='0.0.0.0', port=5000)


def run_while_loop():
    while True:
        update_auction_status()
        end_auctions()
        time.sleep(1)

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', True)
    flask_process = multiprocessing.Process(target=run_flask_app)
    while_process = multiprocessing.Process(target=run_while_loop)

    flask_process.start()
    while_process.start()

    flask_process.join()
    while_process.join()