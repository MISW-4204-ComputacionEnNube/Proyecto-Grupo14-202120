from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

def create_app(config_name):
    app = Flask(__name__)


    with open('credenciales.json') as arch:
        config = json.load(arch)
    conexion = 'postgresql://' + config['user']+ ':' + config['password'] + '@' + config['host'] + ':' + str(config['port']) + '/' + config['database']
    app.config['SQLALCHEMY_DATABASE_URI'] = conexion
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY']='Maestría-en-Ingeniería-de-Software-Miso2021'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    return app
