from flask import jsonify, Blueprint, render_template, request, redirect, flash, url_for
from datetime import timedelta, datetime
from models import Listing, db, current_user, ListingTransaction, pytz
import os
import uuid

listing = Blueprint("listing", __name__, static_folder="static", template_folder="templates")

@listing.route("/jauna", methods=["GET","POST"])
def new():
    if request.method == "GET":
        return render_template("listings/new.html")
        
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    priceIncrease = request.form['priceIncrease']
    auctionTime = request.form['auctionTime']
    image = request.files['image']
    errors = 0
    if image:
        image = request.files['image']
        # generate a unique ID for the image filename
        image_id = str(uuid.uuid4())

        # get the file extension from the original filename
        ext = os.path.splitext(image.filename)[1]

        # construct the new filename using the image ID and extension
        new_filename = image_id + ext
        extension = new_filename.split(".")[1]
        if not extension in ["png","jpeg","jpg",""]:
            flash("bildei jābūt png vai jpeg formātā",'error')
            print(extension)
            errors += 1
        # save the image in the static folder with the new filename
        image.save(os.path.join('static', 'images', new_filename))
        imageLocation = "/static/images/" + new_filename
    else:
        imageLocation = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"

    if not isinstance(price, str):
        flash("Nemaini datu tipus, dauni!",'error')
        errors += 1
    if not isinstance(priceIncrease, str):
        flash("Nemaini datu tipus, dauni!",'error')
        errors += 1
    if len(name) < 5 or len(name) > 64:
        errors += 1
        flash('Nosaukumam jābūt starp 5 un 64 simboliem!','error')
    if float(price) < 0.01 or float(price) > 100000:
        errors += 1
        flash('Cenai jābūt starp 0.01 EUR un 100,000 EUR','error')
    if float(price) < 0.01 or float(priceIncrease) > 100:
        errors += 1
        flash('Cenas jābūt starp 0.01 EUR un 100 EUR','error')
    if len(description) > 1024:
        errors += 1
        flash('Apraksts nedrīkst pārsniegt 1024 simbolus!', 'error') 
    latvia_timezone = pytz.timezone('Europe/Riga')
    current_time = datetime.now(latvia_timezone)

    try:
        auctionTime = datetime.strptime(request.form['auctionTime'], '%Y-%m-%dT%H:%M')
        if auctionTime.replace(tzinfo=None) - current_time.replace(tzinfo=None) < timedelta(days=1):
            flash('Izsole nedrīkst notikt ātrāk par 24 stundām nākotnē!','error')
            errors += 1
    except ValueError:
        flash("Tu nedrīksti vienkārši rakstīt ko tu gribi datetime. ip grabbed.",'error')
        errors += 1
        

        
    if errors > 0:
        return redirect(url_for('listing.new'))
    new_listing = Listing(
        name = name,
        description = description,
        startPrice = price,
        priceIncrease = priceIncrease,
        price = price,
        auctionTime = auctionTime,
        image=imageLocation,
        auctionStatus = 0,
        userID = current_user.id,
        creationDate = current_time,
    )
    db.session.add(new_listing)
    db.session.commit()
    flash('veiksmīgi ievietota prece!','success')
    return redirect(url_for('home.index'))

@listing.route("/rediget/<id>", methods=["GET","POST"])
def edit(id):
    listing = Listing.query.filter_by(id=id).first()
    if not current_user != listing.userID and current_user.isAdmin == False:
        return redirect(url_for("home.index")) 
    if request.method == "GET":
        return render_template("listings/edit.html", listing=listing)

    name = request.form['name']
    description = request.form['description']
    image = request.files['image']
    if image:
        image = request.files['image']
        image_id = str(uuid.uuid4())
        ext = os.path.splitext(image.filename)[1]
        new_filename = image_id + ext
        image.save(os.path.join('static', 'images', new_filename))
        imageLocation = "static/images/" + new_filename
        listing.image = imageLocation
    errors = 0
    if 5 > len(name) < 64:
        errors += 1
        flash('Nosaukumam jābūt starp 8 un 64 simboliem!','error')

    if len(description) > 1024:
        errors += 1
        flash('apraksts nedrīkst pārsniegt 1024 simbolus!', 'error') 

    if errors > 0:
        return redirect(url_for('listing.new'))

    listing.name = name
    listing.description = description
    db.session.commit()
    flash('veiksmīgi nomainīta preces informācija','success')
    return redirect("/prece/apskatit/"+id)
    



@listing.route("/apskatit/<int:id>")
def view(id):
    listing = Listing.query.filter_by(id=id).first()
    if listing:
        return render_template("listings/view.html", listing = listing)
    else:
        return render_template("pages/404.html")

@listing.route("/apskatit")
def view_none():
    return redirect(url_for("home.index"))


@listing.route("/dzest/<int:id>")
def dzest(id):
    listing = Listing.query.filter_by(id=id).first()
    if not current_user.id == listing.userID and not current_user.isAdmin:
        flash('Tev nav peieja izdzēst šo preci!', 'error')
        return redirect(url_for("home.index"))
    db.session.delete(listing)
    db.session.commit()
    flash('veiksmīgi izdzēsta prece!','success')
    return redirect(url_for("home.index"))


@listing.route("/pievienoties/<int:id>")
def join(id):
    listing = Listing.query.filter_by(id=id).first()
    if listing.auctionStatus != 1:
        flash('Izsolei vairs nevar pievienoties!','error')
        return redirect("/prece/apskatit/"+str(listing.id))
    if listing.userID == current_user.id:
        flash('Savai izsolei nevar pievienoties!','error')
        return redirect("/prece/apskatit/"+str(listing.id))
    if ListingTransaction.query.filter_by(buyerID=current_user.id,listingID=id).first():
        redirect(url_for("listing.auction",id=id))
    if not current_user:
        flash('lai pievienotos izsolei jābūt reģistrētam lietotājam!','error')
    else:
        latvia_timezone = pytz.timezone('Europe/Riga')
        current_time = datetime.now(latvia_timezone)
        newTransaction = ListingTransaction(
            price = listing.price,
            participating = True,
            buyerID = current_user.id,
            listingID = id,
            date = current_time,
            winner = False,
        )
        db.session.add(newTransaction)
        db.session.commit()
        return redirect(url_for("listing.auction",id=id))

@listing.route("/iziet/<int:id>")
def exit(id):
    listing = Listing.query.filter_by(id=id).first()
    userTransaction = ListingTransaction.query.filter_by(buyerID=current_user.id, listingID=id).first()
    if not userTransaction:
        return redirect(url_for("home.index"))
    if listing.auctionStatus == 1:
        db.session.delete(userTransaction)
    else:
        latvia_timezone = pytz.timezone('Europe/Riga')
        current_time = datetime.now(latvia_timezone)

        userTransaction.participating = False
        userTransaction.price = listing.price
        userTransaction.date = current_time
    db.session.commit()
    flash("veiksmīgi esi izstājies no izsoles!","success")
    return redirect(url_for("home.index"))

@listing.route("/izsole/<int:id>")
def auction(id):
    listing = Listing.query.filter_by(id=id).first()
    userTransactions = ListingTransaction.query.filter_by(buyerID=current_user.id).all()
    joinedAuction = False
    for userTransaction in userTransactions:
        if userTransaction.listingID == id:
            joinedAuction = True

    if not joinedAuction:
        if listing.auctionStatus == 1:
            return redirect("/prece/pievienoties/"+id)
        else:
            flash("izsolei vairs nevar pievienoties!","error")
            return redirect(url_for("home.index"))
    
    return redirect(url_for("listing.participatingIn"))

@listing.route("/manas")
def myListings():
    if not current_user:
        flash('Tev jāreģistrējas, lai redzētu savas izsoles!','error')
        return redirect(url_for("home.index"))
    
    return render_template("listings/myListings.html", listings = Listing.query.filter_by(userID=current_user.id).all())


@listing.route("/piedalos")
def participatingIn():
    if not current_user:
        flash('Tev jāreģistrējas, lai pievienotos izsolei!','error')
        return redirect(url_for("home.index"))
    
    listings = []
    userTransactions = ListingTransaction.query.filter_by(buyerID=current_user.id).all()
    for transaction in userTransactions:
        if transaction.participating:
            listings += Listing.query.filter_by(id=transaction.listingID)
    return render_template("pages/participatingIn.html", listings = listings)

@listing.route("/db/refresh/get/<int:page>", methods=["GET"])
def dbUpdate(page):
    listings = Listing.query.filter(Listing.auctionStatus.notin_([3])).order_by(Listing.auctionTime.asc()).offset(page*6).limit(10).all()
    data = []
    for listing in listings:
        data.append({
            "ident": listing.id,
            "name": listing.name,
            "description": listing.description,
            "image": listing.image,
            "auctionStatus": listing.auctionStatus,
            "price": listing.price,
        })
    return jsonify(data)