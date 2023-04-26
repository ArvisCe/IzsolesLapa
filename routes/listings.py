from flask import Blueprint, jsonify, render_template, request, redirect, flash, url_for
from datetime import datetime
from models import Listing, db, current_user
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
    auctionTime = datetime.strptime(request.form['auctionTime'], '%Y-%m-%dT%H:%M')
    image = request.files['image']
    if image:
        image = request.files['image']
        # generate a unique ID for the image filename
        image_id = str(uuid.uuid4())

        # get the file extension from the original filename
        ext = os.path.splitext(image.filename)[1]

        # construct the new filename using the image ID and extension
        new_filename = image_id + ext

        # save the image in the static folder with the new filename
        image.save(os.path.join('static', 'images', new_filename))
        imageLocation = "static/images/" + new_filename
    else:
        imageLocation = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
    errors = 0
    if 5 > len(name) < 64:
        errors += 1
        flash('Nosaukumam jābūt starp 8 un 64 simboliem!','error')
    if 0.01 > float(price) < 100000:
        errors += 1
        flash('Cenai jābūt starp 0.01 EUR un 100,000 EUR','error')
    if len(description) > 1024:
        errors += 1
        flash('apraksts nedrīkst pārsniegt 1024 simbolus!', 'error') 

    if errors > 0:
        return redirect(url_for('listing.new'))
    else:
        new_listing = Listing(
            name = name,
            description = description,
            startPrice = price,
            priceIncrease = priceIncrease,
            auctionTime = auctionTime,
            image=imageLocation,
            auctionStatus = 0,
            userID = current_user.id,
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
    else:
        imageLocation = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
    
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
    listing.image = imageLocation
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




@listing.route("/check_updates", methods=["GET"])
def check_updates():
    listings = Listing.query.all()
    data = []
    for listing in listings:
        data.append({
            "id": listing.id,
            "name": listing.name,
            "description": listing.description,
            "startPrice": listing.startPrice,
            "priceIncrease": listing.priceIncrease,
            "auctionTime": listing.auctionTime.strftime("%Y-%m-%d %H:%M:%S"),
            "image": listing.image,
            "auctionStatus": listing.auctionStatus
        })
    return jsonify(data)