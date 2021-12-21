import TPLC
import pandas as pd

'''AFA Cust # = 1081'''

orders = TPLC.get_orders(rql='readOnly.customerIdentifier.id==1081', detail='Packages,OrderItems,SmallParcel,ParcelOptions',itemdetail='All')

def get_sku(order_number, order_item_id):
    for item in orders[order_number].get("_embedded").get('http://api.3plCentral.com/rels/orders/item'):
        if item["readOnly"].get("orderItemId") == order_item_id:
            return item["itemIdentifier"].get('sku')
    return ''

cleaned_orders = []
for order_number, order_details in orders.items():
    for package in order_details["readOnly"]["packages"]:
        for package_content in package["packageContents"]:
            d = {
                "Order ID"              : order_number,
                "Order Process Date"    : order_details["readOnly"]["processDate"],
                "Reference Number"      : order_details["referenceNum"],
                "Carrier"               : order_details["routingInfo"].get("carrier"),
                "Order Tracking Number" : order_details["routingInfo"].get("trackingNumber"),
                "Package Number"        : package.get("packageId"),
                "Package Description"   : package.get("packageDefIdentifier").get("name") if package.get("packageDefIdentifier") else '',
                "Package Length"        : package.get("length"),
                "Package Width"         : package.get("width"),
                "Package Height"        : package.get("height"),
                "Package Weight"        : package.get("weight"),
                "Package Tracking Num"  : package.get("trackingNumber"),
                "Order Item ID"         : package_content.get("orderItemId"),
                "SKU"                   : get_sku(order_number, package_content.get("orderItemId")),
                "Qty"                   : package_content["qty"],
                "Fulfill S&H"           : order_details.get('fulfillInvInfo').get('fulfillInvShippingAndHandling')
            }
            cleaned_orders.append(d)

df = pd.DataFrame(cleaned_orders)
df.to_excel('output.xlsx')