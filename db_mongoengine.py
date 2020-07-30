from mongoengine import connect, Document, DynamicDocument, StringField, IntField, DateTimeField, BooleanField, ReferenceField, DictField, ListField
from credentials import db_id, db_pw
from datetime import datetime

connect(
    db='B4BWMS', 
    username=db_id,
    password=db_pw,
    authentication_source='admin',
    host="mongodb+srv://b4b-mongocluster-7bwmj.gcp.mongodb.net"
)

#### Document Schemas

class Warehouse(Document):
    name            = StringField(required=True)
    locations       = DictField()

    def addLocation(self, location):
        if not self.locations.get(location.id.__str__()):               # pylint: disable=no-member
            self.locations[location.id.__str__()] = location.name       # pylint: disable=unsupported-assignment-operation
        else:
            raise Exception("Location already exist.")

class Location(Document):
    warehouse       = ReferenceField(Warehouse, required=True) 
    name            = StringField(required=True)
    type            = StringField(choices=['Storage', 'Staging', 'Picking', 'Quarantine'], default='Storage')
    priority        = IntField()

class Customer(DynamicDocument):
    name            = StringField(required=True)
    reference       = DictField

class Item(DynamicDocument):
    sku             = StringField()
    upc             = StringField()
    description     = StringField()
    reference       = DictField()

class PurchaseOrder(DynamicDocument):
    reference       = DictField()

class Receiver(DynamicDocument):
    items           = ListField()
    reference       = DictField()

class Order(DynamicDocument):
    customer        = ReferenceField(Customer)
    items           = ListField()

class Inventory(Document):
    customer        = ReferenceField(Customer)
    item            = ReferenceField(Item)
    receivedQty     = IntField()
    onHand          = IntField()
    available       = IntField()
    location        = ReferenceField(Location)
    receiver        = ReferenceField(Receiver)
    receivedDate    = DateTimeField(default=datetime.utcnow)
    purchaseOrder   = ReferenceField(PurchaseOrder)
    reference       = DictField()


warehouse = Warehouse(
    name = "Progress Blvd"
).save()

location = Location(
    warehouse = warehouse,
    name = "N01A01"
).save()

warehouse.addLocation(location)
warehouse.save()

customer = Customer(
    name = "Test Customer"
).save()

item = Item(
    sku = "SKU12345",
    description = "Test Item",
).save()

receiver1 = Receiver().save()

receipt1 = Inventory(
    customer = customer,
    item = item,
    receivedQty = 100,
    onHand = 100,
    available = 100,
    location = location,
    receiver = receiver1
).save()

receiver1.items.append(receipt1)
receiver1.save()


print("done")