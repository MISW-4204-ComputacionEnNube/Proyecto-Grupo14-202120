#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definicion de la funcion que se ejecuta al inicio de la aplicacion."""

# ----------------------------------------------------------------------------

from flask import request, flash
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, \
    get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from operator import contains
from werkzeug.utils import secure_filename
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy

from ..tareas import registrar_log
from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema
from ..tareas.convert import CronConvert

# ----------------------------------------------------------------------------

# creditos
__author__ = "Jose Lopez"
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
formatos = ['aac', 'mp3', 'ogg', 'wav', 'wma']


# ----------------------------------------------------------------------------


def ValidarEmail(email: str) -> tuple:
    """Funcion que valida el email."""

    if email not in None:
        try:
            # Valida el email
            valid = validate_email(email)
            # Obtiene el valor normalizado del email.
            email = valid.email
            return 0, email
        except EmailNotValidError as e:
            # email no es vlaido
            return -2, str(e)

    else:
        return -1, "Email vacio" 



# ----------------------------------------------------------------------------


def ValidarPassword(password1: str, password2: str) -> tuple:
    """Funcion que valida el password."""

    # valida los passwords
    if password1 is None:
        return -1, "Error password1 inexistente"
    if password1 is None:
        return -2, "Error password2 inexistente"
    if password1 != password2:
        return -3, "Error de validación en comparación del password"

    # define la complejidad mínima del password
    policy = PasswordPolicy.from_names(
        length=8,  # min length: 8
        uppercase=2,  # need min. 2 uppercase letters
        numbers=2,  # need min. 2 digits
        special=2,  # need min. 2 special characters
        nonletters=2,  # need min. 2 non-letter characters 
                       # (digits, specials, anything)
    )

    # evalua la calidad del password
    result = policy.test(password1)
    if len(result) > 0:
        # tiene errores de validación el password
        return -4, f"El password tiene {len(result)} errores de " + \
                   f"validación en complejidad : {str(result)}. " + \
                   f"Debe tener mínimo: 8 carácteres, 2 mayúsculas, " + \
                   f"2 dígitos, 2 carácteres especiales."
    
    return 0, password1


# ----------------------------------------------------------------------------


# end point: /api/auth/signup
class VistaSignUp(Resource):
    """clase relacionada con la creación de usuario."""

    def post(self):
        """Crea un nuevo usuario."""

        usuario = request.json["username"]
        password1 = request.json["password1"]
        password2 = request.json["password2"]
        email = request.json["email"]
        
        # valida el password
        err, password = ValidarPassword(password1, password2)
        if err != 0:
            return {"mensaje": f"Error en el password : {password}"}

        # valida el email
        err, email = ValidarEmail(email)
        if err != 0:
            return {"mensaje": f"Error en el email : {email}"}

        nuevo_usuario = Usuario(
            usuario=usuario,
            email=email,
            contrasena=password
            )

        db.session.add(nuevo_usuario)
        db.session.commit()

        token_de_acceso = create_access_token(identity = nuevo_usuario.id)

        return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso}


# ----------------------------------------------------------------------------


# end point: /api/auth/login
class VistaLogIn(Resource):
    """Clase relacionada con login."""

    def post(self):
        """Inicio de sesion."""

        username = request.json["username"]
        password = request.json["password"]

        if username is not None:
            # verifica que el usuario y password existan en la base de datos
            if db.session.query(
                Usuario.query.filter(
                Usuario.usuario == username, 
                Usuario.contrasena == password
                ).exists()).scalar():

                # obtiene el objeto usuario
                usuario = Usuario.query.filter(
                    Usuario.usuario == username, 
                    Usuario.contrasena == password
                    ).first()
                # crea el token para el usuario
                token_de_acceso = create_access_token(identity = usuario.id)
                
                return {"mensaje":"Inicio de sesion exitoso", "token": token_de_acceso}

            # verifica que el email y password existan en la base de datos
            if db.session.query(
                Usuario.query.filter(
                Usuario.email == username, 
                Usuario.contrasena == password
                ).exists()).scalar():

                # obtiene el objeto usuario
                usuario = Usuario.query.filter(
                    Usuario.email == username, 
                    Usuario.contrasena == password
                    ).first()
                # crea el token para el usuario
                token_de_acceso = create_access_token(identity = usuario.id)
                
                return {"mensaje":"Inicio de sesion exitoso", "token": token_de_acceso}

        return "El usuario no existe", 404


# ----------------------------------------------------------------------------


# end point: /api/tasks
class VistaTareas(Resource):
    """"""

    def post(self):
        """Se crea una nueva tarea.
        
        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             -F "file=@/home/estudiante/music/tina-guo.mp3;type=audio/mpeg"  
             -F "destino=wav" 
             -F "usuario_id=1" http://localhost:5000/api/tasks
        """


        # obtiene el archivo enviado
        try:
            f = request.files['file']
        except:
            # no se envio el archivo, por ende no se crea la tarea
            msg = "No se cargo el archivo"
            flash(msg)
            return msg, 402

        # obtiene el tipo de archivo al que se transformara
        try:
            extension_destino = request.form['destino']
        except:
            # no se envio la extension de destino, por ende no se crea la tarea
            msg = "No se definio la extension de destino"
            flash(msg)
            return msg, 402

        # obtiene el identificador del usuario
        try:
            usuario_id = request.form["usuario_id"]
        except:
            # no se envio la extension de destino, por ende no se crea la tarea
            msg = "No se reporto el id del usuario"
            flash(msg)
            return msg, 402

        if f is None:
            # no se envio el archivo, por ende no se crea la tarea
            msg = "No se cargo el archivo"
            flash(msg)
            return msg, 402

        if extension_destino is None:
            # no se envio la extension de destino, por ende no se crea la tarea
            msg = "No se definio la extension de destino"
            flash(msg)
            return msg, 402

        if usuario_id is None:
            # no se envio la extension de destino, por ende no se crea la tarea
            msg = "No se reporto el id del usuario"
            flash(msg)
            return msg, 402

        # obtiene el nombre del archivo
        archivo = secure_filename(f.filename)
        # obtiene la extension del archivo en minuscula
        extension_origen = archivo.split('.')[-1].lower()
        # obtiene la base del nombre del archivo
        base_archivo = archivo[:(len(archivo)-len(extension_origen)-1)]
        # pasa la extension de destino a minuscula
        extension_destino = extension_destino.lower()

        # valida que el nombre de archivo tenga base
        if len(base_archivo) == 0:
            # nombre de archivo sin base
            msg = "Nombre de archivo sin base"
            flash(msg)
            return msg, 402

        # valida la extension del archivo de origen
        if extension_origen not in formatos:
            # el formato del archivo no es admitido
            msg = "El formato del archivo no es admitido"
            flash(msg)
            return msg, 402

        # valida la extension de destino
        if extension_destino not in formatos:
            # el formato de destino no es admitido
            msg = "El formato de destino no es admitido"
            flash(msg)
            return msg, 402

        # obtiene la fecha actual
        fecha = datetime.now()
        tfecha = fecha.strftime('%Y%m%d%H%M%S')

        # genera el nombre del archivo con el que se almacenara el archivo
        archivo_origen = f"{tfecha}_{archivo}".replace(' ', '_')

        # genera el nombre del archivo con el que se almacenara el archivo 
        # transformado
        archivo_destino = f"{tfecha}_{base_archivo}.{extension_destino}".\
            replace(' ', '_')

        # construye la ruta donde se almaceno el archivo
        ruta_archivo_origen = f"{ruta}/{archivo_origen}"
        # construye la ruta donde se almacenara el archivo transformado
        ruta_archivo_destino = f"{ruta}/{archivo_destino}"

        try:
            # almacena el archivo
            f.save(ruta_archivo_origen)
        except:
            msg = "Error al almacenar el archivo"
            flash(msg)
            return msg, 402

        # crea el registro en la base de datos
        nueva_tarea = Tarea(
            archivo = archivo,
            formato_origen = extension_origen,
            ruta_archivo_origen = ruta_archivo_origen,
            formato_destino = extension_destino,
            ruta_archivo_destino = ruta_archivo_destino,
            fecha = fecha,
            estado = 'uploaded',
            usuario_id = usuario_id)

        db.session.add(nueva_tarea)
        db.session.commit()

        return tarea_schema.dump(nueva_tarea)

    def get(self):
        """Retorna todas las tareas.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X GET -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/tasks
        """

        return [tarea_schema.dump(ta) for ta in Tarea.query.all()]


# end point: /api/run_tasks
class VistaEjecutarTareas(Resource):
    """"""

    def post(self):
        """Se dispara la tarea de conversion.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X POST -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/run_tasks
        """

        return CronConvert()


# end point: /api/tasks/<int:id_task>
class VistaTarea(Resource):
    """"""

    def get(self, id_task):
        """Se obtiene una tarea con base en el id.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X GET -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/tasks/1
        """

        return tarea_schema.dump(Tarea.query.get_or_404(id_task))


    def delete(self, id_task):
        """Se elimina el archivo.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X DELETE -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/tasks/1
        """


        if db.session.query(Tarea.query.filter(Tarea.id==id_task).exists()).scalar():

            tarea = Tarea.query.get(id_task)
            db.session.delete(tarea)
            db.session.commit()

            msg = "La tarea fue eliminada"
            flash(msg)
            return msg, 204

        else:
            msg = "No existe la tarea a eliminar"
            flash(msg)
            return msg, 402




# end point: /api/files/<string:filename>
class VistaUsuariosTarea(Resource):
    """"""

    def get(self, filename):
        """Retorna la tarea relacionada a un archivo."""

        tarea = Tarea.query.filter(Tarea.archivo.contains(filename))
        print(tarea, filename)
        return tarea_schema.dump(tarea)