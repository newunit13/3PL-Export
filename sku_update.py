import TPLC
import csv

# Get all items from 3PL that are going to be updated
items = TPLC.GetItems(customer_id=1, pgsiz=100, pgnum=1, rql="readOnly.deactivated==False")

# Turn list into hash indexed on SKU
items = {item["sku"]:item for item in items}

with open('Compendium SKU Update.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for old_sku, new_sku, sku_desc, active_state in csvreader:

        # Check to make sure SKU exists in current 3PL items
        if items.get(old_sku) == None:
            print(f"Unable to find {old_sku}")
            continue

        print(f"Updating SKU: {old_sku} -> {new_sku}")
        
        # Get the itemId
        item_id = items[old_sku]["itemId"]

        # Get current item config from 3PLC
        item, etag = TPLC.GetItem(1, item_id)
        
        # Update the local copy's SKU
        item["sku"] = new_sku

        # Set the UPC to the old_sku
        item["upc"] = old_sku

        # Push updated config back to 3PLC
        TPLC.UpdateItem(customer_id=1, item_id=item_id, etag=etag, payload=item)
