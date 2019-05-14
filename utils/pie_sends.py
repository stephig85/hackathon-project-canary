import requests
from datetime import datetime, timedelta, date
import csv
import json


def get_pie_status(client):
    wb_name = client
    today = date.today()
    week_ago = today - timedelta(days=7)
    endpoint = 'http://rolodex.prod.us-east-1.nexus.bazaarvoice.com/' + wb_name + '/correspondences?passkey=8PtY8M33nu7r1I18sEXBlUn3XoF&startdate=' + str(week_ago) 
    
    r = requests.get(endpoint)
    
    # Gets around 0 length rolodex responses
    all_sends = 0
    if r.text is not '[]':
        # print(r.text)
        all_sends = len(list(json.loads(r.text)))

    if all_sends <= 10:
        return ["fail", {'sent': all_sends}]
    else:
        return ["pass", {'sent': all_sends}]
