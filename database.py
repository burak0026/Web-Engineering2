import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import db

#create model class with database scheme
class reservations(db.Model):
    reservation_id = db.Column("id", UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    from_date = db.Column("from", db.String(50))
    to_date = db.Column("to", db.String(50))  
    room_id = db.Column("room_id", UUID(as_uuid=True), default=uuid.uuid4)

#init class to map parameters to 
def __init__(self, reservation_id, from_date, to_date, room_id):
    self.reservation_id = reservation_id
    self.from_date = from_date
    self.to_date = to_date
    self.room_id = room_id