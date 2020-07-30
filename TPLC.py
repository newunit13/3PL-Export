import base64
import requests
import json
import time
from urllib.parse import urlencode
from credentials import tpl_id, tpl_secret, tpl_guid, tpl_user_id



#----------------------------------------------------------------------------------------------

def GetAccessToken(tpl_id, tpl_secret, tpl_guid, tpl_user_id):

    print(f"GetAccessToken() called.")
    clock_start = time.time()

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
    print(f"GetAccessToken() took {time.time() - clock_start:2.2f} seconds.\tStatus Code: {response.status_code}")

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

global access_token
access_token = GetAccessToken(tpl_id, tpl_secret, tpl_guid, tpl_user_id)


# testing code below
if __name__ == '__main__':

    item, etag = GetItem(1, 8504)
    item["sku"] = "04719-test"
    UpdateItem(1, item["itemId"], etag, item)

    print("")
    
