# project-canary

To run locally 

1. Run flask

```
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

2. Run Mongo

```
brew install mongodb
sudo mkdir -p /data/db
sudo chown -R `id -un` /data/db
mongod
mongo
use canary
db.users.insert({id: 'greg.garcia',email: 'greg.garcia@bazaarvoice.com',subscriptions: ['csttires', 'hasbro']})
```