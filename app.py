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
@app.route('/subscriber', methods=["GET"])
@app.route("/subscriber/<subscriber>", methods=["GET"])
def subscriber(subscriber=None):
    if subscriber is not None:
        user = mongo.db.subscribers.find_one({"id": subscriber})
        if user == None:
            return render_template("subscriber.html")
        else:
            # Find all clients in user list
            clients = user['subscriptions']
            all_clients_data = []
            for client in clients:
                client_data = mongo.db.clients.find_one({"id": client})
                print(client_data)
                all_clients_data.append(client_data)
            user['client_data'] = all_clients_data
            return render_template("subscriber.html", subscriber=user)
    else:
        return render_template("subscriber.html")


# Update Data we have for a client
@app.route("/create_subscriber/<subscriber>", methods=["GET"])
def create_subscriber(subscriber):
    mongo.db.subscribers.insert({'id': subscriber})
    return jsonify({'status' : 'success'})


# Add subscription to an existing subscriber
@app.route("/subscriber/add_subscription/<subscriber>/<client>", methods=["GET"])
def add_subscription(subscriber, client):
    mongo.db.subscribers.update(
        {"id": subscriber},
        {"$addToSet": {"subscriptions": client}}
    )
    return jsonify({'status' : 'success'})

# Update Data we have for a client
@app.route("/run/<client>", methods=["GET"])
def run_checks(client):
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

    return client



if __name__ == "__main__":
    app.run(debug=True)