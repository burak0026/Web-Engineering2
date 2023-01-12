import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# create flask api class and configure
class Flask_API:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+os.getenv('POSTGRES_RESERVATIONS_USER')+':'+os.getenv('POSTGRES_RESERVATIONS_PASSWORD')+'@'+os.getenv('POSTGRES_RESERVATIONS_HOST')+':'+os.getenv('POSTGRES_RESERVATIONS_PORT')+'/'+os.getenv('POSTGRES_RESERVATIONS_DBNAME')+''
    db = SQLAlchemy(app)
    logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')  

