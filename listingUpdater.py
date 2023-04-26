import datetime
from models import db, Listing, ListingTransaction
from apscheduler.schedulers.background import BackgroundScheduler



# auction statusses

# 0 - waiting
# 1 - able to join
# 2 - ongoing
# 3 - ended

def update_auction_status():
    now = datetime.datetime.now()
    listings = Listing.query.filter_by(auctionStatus=0).all()
    for listing in listings:
        if listing.auctionTime - now <= datetime.timedelta(minutes=2):
            listing.auctionStatus = 1
        elif listing.auctionTime <= now:
            listing.auctionStatus = 2
        db.session.commit()

def end_auctions():
    listings = Listing.query.filter_by(auctionStatus=2)
    for listing in listings:
        listingTransactions = ListingTransaction.query.filter_by(listingID=listing.id, participating=True).all()
        if not listingTransactions:
            listing.auctionStatus = 3
            db.session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(update_auction_status, 'interval', minutes=1)
scheduler.add_job(end_auctions, 'interval', minutes=1)
scheduler.start()