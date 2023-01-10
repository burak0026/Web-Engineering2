import datetime
import uuid

#function to check JSON parameters
def checkJSONValues(content):
    #validate id
    if content.get('id') is not None:  
        try:
            uuid.UUID(str(content['id']))
        except ValueError:
            #app.logger.error("JSON ValueError 'id'")
            return False
    #validate from
    if content.get('from') is not None:
        try:
            datetime.datetime.strptime(content['from'], '%Y-%m-%d')
        except ValueError:
            #app.logger.error("JSON ValueError 'from'")
            return False
    #validate to
    if content.get('to') is not None:
        try:
            datetime.datetime.strptime(content['to'], '%Y-%m-%d')
        except ValueError:
            #app.logger.error("JSON ValueError 'to'")
            return False
    #validate room_id
    if content.get('room_id') is not None:
        try:
            uuid.UUID(str(content['room_id']))
        except ValueError:
            #app.logger.error("JSON ValueError 'room_id'")
            return False
    #if no error, return true
    return True

#function to check JSON parameters
def checkQueryValues(before, after, room_id):
    #validate before
    if before is not None:
        try:
            datetime.datetime.strptime(before, '%Y-%m-%d')
        except ValueError:
            #app.logger.error("Query ValueError 'from'")
            return False
    #validate after
    if after is not None:
        try:
            datetime.datetime.strptime(after, '%Y-%m-%d')
        except ValueError:
            #app.logger.error("Query ValueError 'after'")
            return False
    #validate room_id
    if room_id is not None:
        try:
            uuid.UUID(str(room_id))
        except ValueError:
            #app.logger.error("Query ValueError 'room_id'")
            return False
    #if no error, return true
    return True