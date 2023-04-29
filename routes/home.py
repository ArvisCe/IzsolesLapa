from flask import Blueprint, render_template
from models import Listing, pytz
home = Blueprint("home", __name__, static_folder="static", template_folder="templates")

@home.route("/home")
@home.route("/")
def index():
    return render_template('pages/home.html', listings=Listing.query.filter(Listing.auctionStatus.notin_([3])).order_by(Listing.auctionTime.asc()).all())

@home.route("/vesture")
def history():
    return render_template('pages/history.html', listings=Listing.query.filter(Listing.auctionStatus.notin_([0, 1, 2])).order_by(Listing.auctionTime.asc()).all())


@home.route("/noteikumi")
def rules():
    return render_template('pages/rules.html')