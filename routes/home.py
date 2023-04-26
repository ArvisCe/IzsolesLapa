from flask import Blueprint, render_template
from models import Listing
home = Blueprint("home", __name__, static_folder="static", template_folder="templates")

@home.route("/home")
@home.route("/")
def index():
    return render_template('pages/home.html', listings=Listing.query.filter(Listing.auctionStatus.notin_([2, 3])).order_by(Listing.auctionTime.asc()).all())