# project-canary

## To Run Locally

1. Install AWS CLI
* https://bits.bazaarvoice.com/confluence/display/DEV/Day+2+-+Get+access+to+Nexus#Day2-GetaccesstoNexus-Exercise3-InstallAWSCLI

2. Run flask

```
python3 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

3. Run Mongo

```
brew install mongodb
sudo mkdir -p /data/db
sudo chown -R `id -un` /data/db
mongod
mongo
use canary
db.users.insert({id: 'greg.garcia',email: 'greg.garcia@bazaarvoice.com',subscriptions: ['csttires', 'hasbro']})
```