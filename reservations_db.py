import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import App

class reservations(App.db.Model):
    reservation_id = App.db.Column("id", UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    from_date = App.db.Column("from", App.db.String(50))
    to_date = App.db.Column("to", App.db.String(50))  
    room_id = App.db.Column("room_id", UUID(as_uuid=True), default=uuid.uuid4)
    

#init class to map parameters to 
def __init__(self, reservation_id, from_date, to_date, room_id):
    self.reservation_id = reservation_id
    self.from_date = from_date
    self.to_date = to_date
    self.room_id = room_id

#create the database connector
with App.app.app_context():
    App.db.create_all()

