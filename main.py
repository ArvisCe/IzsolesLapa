import time
from flask import Flask
from models import db, User, LoginManager, Bcrypt, Listing, ListingTransaction, pytz, current_user
from datetime import timedelta, datetime
from routes.authentication import auth
from routes.home import home
from routes.listings import listing
from routes.admin import admin
from routes.user import user
from app import app
from apscheduler.schedulers.background import BackgroundScheduler



# authentication routes
app.register_blueprint(auth, url_prefix="")

# item view and main routes 
app.register_blueprint(home, url_prefix="")

# listing CRUD routes
app.register_blueprint(listing, url_prefix="/prece")

# listing admin routes
app.register_blueprint(admin, url_prefix="/admin")

# listing user routes
app.register_blueprint(user, url_prefix="/lietotajs")

# give admins to specific users
def makeAdmins():
    with app.app_context():
        ids=[]
        if ids:
            for id in ids:
                user  = User.query.filter_by(id=id).first()
                user.isAdmin = True
            db.session.commit()
        removeAdmins()
# remove admin from specific users
def removeAdmins():
    with app.app_context():
        ids=[]
        if ids:
            for id in ids:
                user  = User.query.filter_by(id=id).first()
                user.isAdmin = False
            db.session.commit()

with app.app_context():
  db.create_all()
  def update_auction_status():
    with app.app_context():
        latvia_timezone = pytz.timezone('Europe/Riga')
        now = datetime.now(latvia_timezone)
        listings = Listing.query.filter(Listing.auctionStatus.in_([0, 1])).all()
        for listing in listings:
            auctionTime = pytz.timezone('UTC').localize(listing.auctionTime).astimezone(latvia_timezone)
            #print("latvia time: "+str(now))
            #print("auction time: "+str(auctionTime))
            delta = timedelta(minutes=2)

            auctionTimeOffset = timedelta(hours=3)
            auctionTime = auctionTime - auctionTimeOffset
            if auctionTime <= now:
                listing.auctionStatus = 2
            elif auctionTime - now <= delta:
                listing.auctionStatus = 1
            db.session.commit()
        end_auctions()

  def end_auctions():
    with app.app_context():
      listings = Listing.query.filter_by(auctionStatus=2).all()
      for listing in listings:
          listingTransactions = ListingTransaction.query.filter_by(listingID=listing.id, participating=True).all()
          if not listingTransactions:
              listing.auctionStatus = 3
              db.session.commit()
          else:
              listing.price = listing.price + listing.priceIncrease / 10
          db.session.commit()
          
  scheduler = BackgroundScheduler()
  scheduler.add_job(update_auction_status,'interval',seconds=0.1)
  makeAdmins()
  print("scheduler start")
  scheduler.start()
  

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port="8000")
