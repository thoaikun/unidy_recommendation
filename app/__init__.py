from flask import Flask
from flask_mysqldb import MySQL
import csv
import json
import time
from pathlib import Path

app = Flask(__name__)

# app.config.from_object('app.config')
app.config['MYSQL_HOST'] = 'unidy-dev-db.cqkog3b87pvl.ap-southeast-1.rds.amazonaws.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'unidyteam'
app.config['MYSQL_DB'] = 'unidy_database'

mysql = MySQL(app)

from app.routes import recommend_routes
app.register_blueprint(recommend_routes)


        
