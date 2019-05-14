import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_pymongo import PyMongo
from utils.canary_productfeed import *
from utils.pie_sends import *
from utils.canary_magpie import *

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/canary"
mongo = PyMongo(app)

# Display home page with or without client grid
@app.route('/', methods=["GET"])
@app.route('/<client>', methods=["GET"])
def home(client=None):
    print(client)
    client_data = {
        'id': '',
        'pie_status': '',
        'feed_status': '',
        'display_status': '',
        'pixel_status': ''
    }
    if client is not None:
        client_data = mongo.db.clients.find_one({"id": client})
        return render_template("index.html", client=client_data)
    else:
        return render_template("index.html", client=client_data)

# Display subscriber page or create new subscriber
@app.route("/subscriber/<subscriber>", methods=["GET", "POST"])
def subscriber(subscriber):
    if request.method == 'GET':
        user = mongo.db.users.find_one({"id": subscriber})
        print(user)
        if user == None:
            return render_template("subscriber.html")
        else:
            return render_template("subscriber.html", subscriber=user)
    if request.method == 'POST':
        email = request.form["enterEmail"]
        client = request.form["chooseClient"]


# Add subscription to an existing subscriber
@app.route("/subscriber/add_subscription", methods=["POST"])
def add_subscription():
    client = request.form["chooseClient"]
    subscriber = request.form["chooseSubscriber"]
    mongo.db.users.update(
        {"id": subscriber},
        {"$addToSet": {"subscriptions": client}}
    )
    return jsonify({})

# Update Data we have for a client
@app.route("/run/<client>", methods=["GET"])
def run_checks(client):
    print(client)
    # Run Checks
    try:
        pie_status = get_pie_status(client)
    except Exception:
        pie_status = 'error'
        print(Exception)
    try:
        feed_status = get_product_feed_status(client)
    except Exception:
        feed_status = 'error'
        print(Exception)
    try:
        display_status, pixel_status = get_display_status(client)
    except Exception:
        display_status, pixel_status = 'error'
        print(Exception)

    # Build Response JSON
    results = {
        'id': client,
        'pie_status': pie_status,
        'feed_status': feed_status,
        'display_status': display_status,
        'pixel_status': pixel_status
    }

    # Register Updates
    print(results)
    if mongo.db.clients.find({'id': client}).count() > 0:
        x = mongo.db.clients.update({'id': client}, results)
        print(x)
    else:
        x = mongo.db.clients.insert(results)
        print(x)

    return jsonify(results)


@app.route("/", methods=["POST"])
def update_subscriber():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)