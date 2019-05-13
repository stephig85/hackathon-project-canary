
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import csv
import json

wb_name = 'americanstandard-ca'

endpoint = 'http://sodexo.bazaar.us-east-1.nexus.bazaarvoice.com/api/v1/job?client=' + wb_name
username = ''
password = ''
r = requests.get(endpoint, auth=HTTPBasicAuth(username, password))

main_successful_imports = True
main_object = {}

latest_successful_import_index = None
latest_failed_import_index = None

all_imports = list(json.loads(r.text))

def thirty_day_notify(import_object):
    cutoff_date = datetime.today() - timedelta(days=30)
    try:
        complete_timestamp = import_object['completeTime']
        if complete_timestamp > cutoff_date:
            return true
    except Exception as e:
        pass

# remove all non-product feed imports
for index, single_import in enumerate(all_imports):
    try:
        import_type = single_import['type']
        if import_type != 'cis_xml_import':
            all_imports.pop()[index]
    except Exception as e:
        pass
        
# date last feed failed
# if passed, what was the latest successful import
# if passed, notify if longer than 30 days

for index, single_import in enumerate(all_imports):
    try:
        imp_status = single_import['status']
        last_update = single_import['completeTime']
        
        if imp_status == 'failed':
            if latest_failed_import_index == None:
                latest_failed_import_index = index
            else:
                compare_time = single_import['completeTime']
                current_time = all_import[latest_successful_import_index]['completeTime']
                if compare_time > current_time:
                    latest_failed_import_index 
                    
        if imp_status == 'completed':
            if latest_successful_import_index == None:
                latest_successful_import_index = index
            else:
                compare_time = single_import['completeTime']
                current_time = all_import[latest_successful_import_index]['completeTime']
                if compare_time > current_time:
                    latest_successful_import_index = index
        
    except Exception as e:
        pass

if thirty_day_notify(all_imports[latest_successful_import_index]):
    print('Notify client last import was 30 days ago')


print('Latest successful import object')
print(all_imports[latest_successful_import_index])

print('Latest failed import object')
print(all_imports[latest_failed_import_index])


# In[ ]:





        
