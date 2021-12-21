from credentials import db_id, db_pw
import TPLC
import pymongo
import time

client = pymongo.MongoClient(f"mongodb+srv://{db_id}:{db_pw}@b4b-mongocluster-7bwmj.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client["TPLC"]

inventory = db["inventory"]
customers = db["customers"]
orders = db["orders"]

clock_start = time.time()
tpl_inventory = TPLC.get_inventory(pgsiz=1000,rql="customeridentifier.id==1;facilityidentifier.id==2")
print(f"TPL inventory get took {time.time() - clock_start:2.2f} seconds.")

record_count = len(tpl_inventory)
clock_start = time.time()
for i, item in enumerate(tpl_inventory):
    receive_item_id = item["receiveItemId"]
    #print(f"Updating {i} of {record_count}\t{i/record_count:2.2%}")
    inventory.replace_one({"receiveItemId":receive_item_id}, item, upsert=True)
    if int((i/record_count)*100) % 10 == 0:
        print(f"{i/record_count:2.2%} done.")
print(f"MongoDB push took {time.time() - clock_start:2.2f} seconds.")





# for doc in inventory.find({"customerIdentifier.id": 1066}).sort([("receivedDate",-1)]).limit(100):
#     print(f'{doc["receivedDate"].split("T")[0]}\t{doc["receiverId"]}\t{doc["itemIdentifier"]["sku"]}')
