import base64
import requests
import json
import re
from urllib.parse import urlencode
from credentials import tpl_id, tpl_secret, tpl_guid, tpl_user_id



#----------------------------------------------------------------------------------------------
def Billboard():
    url = "https://secure-wms.com/billboard"
    response = requests.get(url=url)
    top_level = response.json()

    billboard = {'root': "https://secure-wms.com", 'billboard': 'https://secure-wms.com/billboard'}
    for level in top_level.get("_links"):
        service = level["Rel"].split("/")[-1]
        href = level["Href"][1:]
        
        url = billboard["billboard"] + href
        response = requests.get(url=url)
        data = response.json()

        items = {'root': data.get("RootUri")}
        for link in data.get("_links"):
            item = link["Rel"].split("/")[-1]
            matches = re.match(r'(.*){\?(.*)}', link["Href"])
            if matches:
                endpoint = matches[1]
                options = matches[2].split(',')
            else:
                endpoint = link["Href"]
                options = None

            items[item] = {'url': billboard.get("root") + endpoint, 'endpoint': endpoint, 'options': options}

        billboard[service] = items

    return billboard

def GetAccessToken(tpl_id, tpl_secret, tpl_guid, tpl_user_id):

    secret_key = f'{tpl_id}:{tpl_secret}'.encode('utf-8')
    secret_key = base64.b64encode(secret_key).decode('utf-8')

    url = "https://secure-wms.com/AuthServer/api/Token"

    headers = {
        "Authorization": f"Basic {secret_key}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    data = json.dumps({
        "grant_type" : "client_credentials",
        "tpl" : f"{tpl_guid}",
        "user_login_id" : f"{tpl_user_id}"
    })

    response = requests.post(url=url, headers=headers, data=data)
    print(f"GetAccessToken() called.\tStatus Code: {response.status_code}")

    return response.json()["access_token"]

def GetReceipts(detail="All",rql=""):
    options = {
        "detail": detail,
        "rql": rql
    }
    options = {k:v for k,v in options.items() if v}
    options = urlencode(options)
    base_url = f"https://secure-wms.com"
    url = f'{base_url}/inventory/receivers?{options}'
    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()
    receipts = data["_embedded"]["http://api.3plCentral.com/rels/inventory/receiver"] if data.get("_embedded") else []
    while data.get("_links").get("next"):

        url = f'{base_url}{data.get("_links").get("next").get("href")}'
        response = requests.get(url=url, headers=headers)
        data = response.json()
        receipts += data["_embedded"]["http://api.3plCentral.com/rels/inventory/receiver"]

    receipts = {r["readOnly"]["receiverId"]:r for r in receipts}
    return receipts

def GetStockStatus(customer_id):
    base_url = "https://secure-wms.com"
    url = f"{base_url}/inventory/stockdetails?customerid={customer_id}&facilityid=2&pgsiz=100"
    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    } 

    response = requests.get(url=url, headers=headers)

    while True:
        data_dict = response.json()
        if data_dict.get("_embedded"):
            inventory = {item["receiveItemId"]:item for item in data_dict["_embedded"]["item"]}

        next_page = data_dict["_links"].get("next").get("href") if data_dict["_links"].get("next") else None
        if next_page:
            response = requests.get(url=f"{base_url}{next_page}", headers=headers)
        else:
            break
         
    return inventory

def GetInventory(pgsiz=100, pgnum=1, rql="", sort="", senameorvaluecontains="" ):
    options = {
        "pgsiz": pgsiz,
        "pgnum": pgnum,
        "rql": rql,
        "sort": sort,
        "senameorvaluecontains": senameorvaluecontains
    }
    options = {k:v for k,v in options.items() if v}
    options = urlencode(options)
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/inventory?{options}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()

    total_results = data["totalResults"]
    current_progress = 0
    items = []

    while True:

        print(f'Gathering page {pgnum}.\t{current_progress} out of {total_results} [{current_progress/total_results:2.2%}]')

        response = requests.get(url=url, headers=headers)
        
        if response.status_code != 200:
            raise Exception

        data = response.json()
        items += data['_embedded']['item']

        current_progress += pgsiz
        pgnum += 1
    
        if data.get("_links").get("next"):
            url = f'{base_url}{data.get("_links").get("next").get("href")}'
        else:
            break

    return items

def GetItems(customer_id, pgsiz=100, pgnum=1, rql="", sort=""):
    options = {
        "pgsiz": pgsiz,
        "pgnum": pgnum,
        "rql": rql,
        "sort": sort,
    }
    options = {k:v for k,v in options.items() if v}
    options = urlencode(options)
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/customers/{customer_id}/items?{options}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()

    total_results = data["totalResults"]
    current_progress = 0
    items = []

    while True:

        print(f'Gathering page {pgnum}.\t{current_progress} out of {total_results} [{current_progress/total_results:2.2%}]')

        response = requests.get(url=url, headers=headers)
        
        if response.status_code != 200:
            raise Exception

        data = response.json()
        items += data['_embedded']['http://api.3plCentral.com/rels/customers/item']

        current_progress += pgsiz
        pgnum += 1
    
        if data.get("_links").get("next"):
            url = f'{base_url}{data.get("_links").get("next").get("href")}'
        else:
            break

    return items

def GetItem(customer_id, item_id):
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/customers/{customer_id}/items/{item_id}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        raise Exception

    item = response.json()

    return (item, response.headers["ETag"])

def UpdateItem(customer_id, item_id, etag, payload):
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/customers/{customer_id}/items/{item_id}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}",
        "If-Match"          : f"{etag}"
    }

    try:
        del payload["_links"]
        del payload["_embedded"]
    except:
        pass

    response = requests.put(url=url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise Exception


    return True

def GetCustomers(pgsiz=100, pgnum=1, rql="", sort="", facilityId=""):
    options = {
        "pgsiz": pgsiz,
        "pgnum": pgnum,
        "rql": rql,
        "sort": sort,
        "facilityId": facilityId
    }
    options = {k:v for k,v in options.items() if v}
    options = urlencode(options)
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/customers?{options}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)
    data = response.json()

    total_results = data["totalResults"]
    current_progress = 0
    customers = []

    while True:

        print(f'Gathering page {pgnum}.\t{current_progress} out of {total_results} [{current_progress/total_results:2.2%}]')

        response = requests.get(url=url, headers=headers)
        
        if response.status_code != 200:
            raise Exception

        data = response.json()
        customers += data['_embedded']['http://api.3plCentral.com/rels/customers/customer']

        current_progress += pgsiz
        pgnum += 1
    
        if data.get("_links").get("next"):
            url = f'{base_url}{data.get("_links").get("next").get("href")}'
        else:
            break

    return customers

def GetLocations(pgsiz=100, pgnum=1, rql="", sort="", beginlocationid="", endlocationid=""):
    options = {
        "pgsiz": pgsiz,
        "pgnum": pgnum,
        "rql": rql,
        "sort": sort,
        "beginlocationid": beginlocationid,
        "endlocationid": endlocationid
    }
    options = {k:v for k,v in options.items() if v}
    options = urlencode(options)
    base_url = f"https://secure-wms.com"
    url = f"{base_url}/properties/facilities/locations?{options}"

    headers = {
        "Host"              : "secure-wms.com",
        "Content-Type"      : "application/hal+json; charset=utf-8",
        "Accept"            : "application/hal+json",
        "Authorization"     : f"Bearer {access_token}"
    }


    current_progress = 0
    locations = []

    while True:

        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            raise Exception

        data = response.json()
        total_results = data["totalResults"]
        locations += data['_embedded']['http://api.3plCentral.com/rels/properties/location']

        print(f'Gathering page {pgnum}.\t{current_progress} out of {total_results} [{current_progress/total_results:2.2%}]')

        current_progress += pgsiz
        pgnum += 1
    
        if data.get("_links").get("next"):
            url = f'{base_url}{data.get("_links").get("next").get("href")}'
        else:
            break

    return locations

global access_token
access_token = GetAccessToken(tpl_id, tpl_secret, tpl_guid, tpl_user_id)


# testing code below
if __name__ == '__main__':

    #a = Billboard()

    locations = GetLocations(pgsiz=100, rql="facilityIdentifier.id==2;deactivated==False")
    with open('output.tsv', 'w') as f:
        for location in locations:
            f.write(f'{location["name"]}\t{location["hasInventory"]}\n')
    print()

