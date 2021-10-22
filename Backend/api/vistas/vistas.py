#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definición de la función que se ejecuta al inicio de la aplicación."""

# ----------------------------------------------------------------------------

from flask import request, flash
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, \
    get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from operator import contains
from werkzeug.utils import secure_filename

from ..tareas import registrar_log
from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema

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
ruta = "/home/estudiante/Proyecto-Grupo14-202120/Backend/files"
formatos = ['acc', 'mp3', 'ogg', 'wav', 'wma']


# end point: /api/tasks
class VistaTareas(Resource):
    """"""

    def post(self):
        """Se crea una nueva tarea."""

        # obtiene el archivo enviado
        f = request.files['file']
        # obtiene el tipo de archivo al que se transformará
        extension_destino = request.form['destino']

        if f is None:
            # no se envio el archivo, por ende no se crea la tarea
            msg = "No se cargo el archivo"
            flash(msg)
            return msg, 402

        if extension_destino is None:
            # no se envio la extensión de destino, por ende no se crea la tarea
            msg = "No se definió la extensión de destino"
            flash(msg)
            return msg, 402

        # obtiene el nombre del archivo
        archivo = secure_filename(f.filename)
        # obtiene la extensión del archivo en minúscula
        extension_origen = archivo.split('.')[-1].lower()
        # obtiene la base del nombre del archivo
        base_archivo = archivo[:(len(archivo)-len(extension_origen)-1)]
        # pasa la extensión de destino a minúscula
        extension_destino = extension_destino.lower()

        # valida que el nombre de archivo tenga base
        if len(base_archivo) == 0:
            # nombre de archivo sin base
            msg = "Nombre de archivo sin base"
            flash(msg)
            return msg, 402

        # valida la extensión del archivo de origen
        if extension_origen not in formatos:
            # el formato del archivo no es admitido
            msg = "El formato del archivo no es admitido"
            flash(msg)
            return msg, 402

        # valida la extensión de destino
        if extension_destino not in formatos:
            # el formato de destino no es admitido
            msg = "El formato de destino no es admitido"
            flash(msg)
            return msg, 402

        # obtiene la fecha actual
        fecha = datetime.now()
        tfecha = fecha.strftime('%Y%m%d%H%M%S')

        # genera el nombre del archivo con el que se almacenará el archivo
        archivo_origen = f"{tfecha}_{archivo}".replace(' ', '_')

        # genera el nombre del archivo con el que se almacenará el archivo 
        # transformado
        archivo_destino = f"{tfecha}_{base_archivo}.{extension_destino}".\
            replace(' ', '_')

        try:
            # almacena el archivo
            f.save(archivo_origen)
        except:
            msg = "Error al almacenar el archivo"
            flash(msg)
            return msg, 402

        # construye la ruta donde se almacenó el archivo
        ruta_archivo_origen = f"{ruta}/{archivo_origen}"
        # construye la ruta donde se almacenará el archivo transformado
        ruta_archivo_destino = f"{ruta}/{archivo_destino}"


        # crea el registro en la base de datos
        nueva_tarea = Tarea(
            archivo = archivo,
            formato_origen = extension_origen,
            ruta_archivo_origen = ruta_archivo_origen,
            formato_destino = extension_destino,
            ruta_archivo_destino = ruta_archivo_destino,
            fecha = fecha,
            estado = 'uploaded',
            usuario_id = request.form["usuario_id"])

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