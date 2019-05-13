import requests
from datetime import datetime, timedelta, date
import csv
import json

wb_name = 'homedepot'
today = date.today()
week_ago = today - timedelta(days=7)

endpoint = 'http://rolodex.prod.us-east-1.nexus.bazaarvoice.com/' + wb_name + '/correspondences?passkey=8PtY8M33nu7r1I18sEXBlUn3XoF&startdate=' + str(week_ago)
r = requests.get(endpoint)
all_sends = list(json.loads(r.text))


def sends():
    if len(all_sends) <= 10:
        return ["fail", {'sent':len(allsends)}]