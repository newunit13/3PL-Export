from mongoengine import connect, Document, DynamicDocument, StringField, IntField, DateField, BooleanField, ReferenceField, DictField
from credentials import db_id, db_pw

connect(
    db='B4BWMS', 
    username=db_id,
    password=db_pw,
    authentication_source='admin',
    host="mongodb+srv://b4b-mongocluster-7bwmj.gcp.mongodb.net"
)

#### Document Schemas

class Warehouse(Document):
    pass

class Location(Document):
    pass

class Customer(DynamicDocument):
    id      = IntField(unique=True, required=True)
    name    = StringField(required=True)

class Item(DynamicDocument):
    id              = IntField(unique=True, required=True)
    sku             = StringField()
    upc             = StringField()
    description     = StringField()

class PurchaseOrder(DynamicDocument):
    id              = IntField(unique=True, required=True),
    reference       = DictField()
 
class Inventory(Document):
    receiverId      = IntField()
    receivedDate    = DateField()
    customerId      = ReferenceField(Customer)
    itemId          = ReferenceField(Item)
    purchaseOrderId = ReferenceField(PurchaseOrder)



c1 = Customer(
    custId = 0,
    custName = "Test Customer"
).save()

i1 = Item(
    itemId = 0,
    itemDescription = "Test Item"
).save()


print("done")