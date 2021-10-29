#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definición de la función que crea y configura la aplicación."""

# ----------------------------------------------------------------------------

from flask import Flask
import json

# ----------------------------------------------------------------------------

# creditos
__author__ = "José López"
__review__ = "Santiago Alejandro Salinas Vargas"
__copyright__ = "Grupo 14"
__credits__ = ["Grupo 14"]
__license__ = "GPLv3"
__version__ = "1.0.0"
__email__ = "s.salinas@uniandes.edu.co"
__status__ = "Dev"
__date__ = "2021-10-29 05:23"

# ----------------------------------------------------------------------------

def create_app():
    """"""
    app = Flask(__name__)

    # abre el archivo de credenciales con la información de conexión a la 
    # base de datos
    with open('api/credenciales.json') as arch:
        config = json.load(arch)

    # crea la cadena de conexión
    conexion = 'postgresql://' + config['user']+ ':' + config['password'] + '@' + config['host'] + ':' + str(config['port']) + '/' + config['database']

    # establece los paámetros de la aplicación
    app.config['SQLALCHEMY_DATABASE_URI'] = conexion
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fa'
    app.config['JWT_SECRET_KEY']='Maestría-en-Ingeniería-de-Software-Miso2021'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['UPLOAD_FOLDER'] = "/home/ubuntu/Proyecto-Grupo14-202120/Backend/files"

    return app
