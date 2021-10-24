#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definición de la función que se ejecuta al inicio de la aplicación."""

# ----------------------------------------------------------------------------

from api import create_app
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from api.modelos import db
from api.vistas import VistaSignUp, VistaTarea, VistaTareas, \
    VistaUsuariosTarea, VistaLogIn, VistaEjecutarTareas

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
__date__ = "2021-10-19 15:38"

# ----------------------------------------------------------------------------


app = create_app()
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignUp, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaTareas, '/api/tasks')
api.add_resource(VistaTarea, '/api/tasks/<int:id_task>')
api.add_resource(VistaUsuariosTarea, '/api/files/<string:filename>')
api.add_resource(VistaEjecutarTareas, '/api/run_tasks')

jwt = JWTManager(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
