#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definición de la función que se ejecuta al inicio de la aplicación."""

# ----------------------------------------------------------------------------

from operator import contains
from flask import request
from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from ..tareas import registrar_log

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
__date__ = "2021-10-19 15:46"

# ----------------------------------------------------------------------------


usuario_schema = UsuarioSchema()
tarea_schema = TareaSchema()

# end point: /api/tasks
class VistaTareas(Resource):
    """"""

    def post(self):
        """Se crea una nueva tarea."""

        nueva_tarea = Tarea(archivo = request.json["archivo"],
            formato = request.json["formato"],
            fecha = datetime.today(),
            estado = 1,
            usuario_id = request.json["usuario_id"])

        db.session.add(nueva_tarea)
        db.session.commit()

        return tarea_schema.dump(nueva_tarea)

    def get(self):
        """Retorna todas las tareas."""

        return [tarea_schema.dump(ta) for ta in Tarea.query.all()]


# end point: /api/tasks/<int:id_task>
class VistaTarea(Resource):
    """"""

    def get(self, id_task):
        """Se obtiene una tarea con base en el id."""

        return tarea_schema.dump(Tarea.query.get_or_404(id_task))

    def put(self, id_task):
        """Se actualiza el archivo."""

        tarea = Tarea.query.get_or_404(id_task)

        if Tarea.query.filter(Tarea.id==id_task).exists():
            tarea.archivo = request.json.get("archivo", tarea.archivo)
            db.session.commit()
            return tarea_schema.dump(tarea)
        
        else:
            return tarea

    def delete(self, id_task):
        """Se elimina el archivo."""

        tarea = Tarea.query.get_or_404(id_task)

        if Tarea.query.filter(Tarea.id==id_task).exists():
            db.session.delete(tarea)
            db.session.commit()
            return {"mensaje":"La tarea fue eliminada"}, 204

        else:
            return {"mensaje":"No existe la tarea a eliminar"}, 404


# end point: /api/auth/signup
class VistaSignUp(Resource):
    """"""

    def post(self):
        """Crea un nuevo usuario."""

        nuevo_usuario = Usuario(usuario=request.json["usuario"],
            email=request.json["email"],
            contrasena=request.json["contrasena"])

        db.session.add(nuevo_usuario)
        db.session.commit()

        token_de_acceso = create_access_token(identity = nuevo_usuario.id)

        return {"mensaje":"usuario creado exitosamente", "token":token_de_acceso}

    def put(self, id_usuario):
        """Cambia la contraseña."""

        usuario = Usuario.query.get_or_404(id_usuario)

        if Usuario.query.filter(Usuario.id==id_usuario).exists():
            usuario.contrasena = request.json.get("contrasena",usuario.contrasena)
            db.session.commit()
            return usuario_schema.dump(usuario)
        else:
            return usuario

    def delete(self, id_usuario):
        """Elimina el usuario."""

        usuario = Usuario.query.get_or_404(id_usuario)

        if Usuario.query.filter(Usuario.id==id_usuario).exists():
            db.session.delete(usuario)
            db.session.commit()
            return {"mensaje":"El usuario fue eliminado"}, 204

        else:
            return {"mensaje":"No existe el usuario a eliminar"}, 404


# end point: /api/auth/login
class VistaLogIn(Resource):
    """"""

    def post(self):
        """Inicio de sesión."""

        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"], 
            Usuario.contrasena == request.json["contrasena"]).first()

        db.session.commit()

        if usuario is None:
            return "El usuario no existe", 404

        else:
            token_de_acceso = create_access_token(identity = usuario.id)
            return {"mensaje":"Inicio de sesión exitoso", "token": token_de_acceso}


# end point: /api/files/<string:filename>
class VistaUsuariosTarea(Resource):
    """"""

    def get(self, filename):
        """Retorna la tarea relacionada a un archivo."""

        tarea = Tarea.query.filter(Tarea.archivo.contains(filename))
        print(tarea, filename)
        return tarea_schema.dump(tarea)