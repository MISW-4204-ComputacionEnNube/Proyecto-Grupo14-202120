#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Definicion de la funcion que se ejecuta al inicio de la aplicacion."""

# ----------------------------------------------------------------------------

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, \
    get_jwt_identity
from flask import send_file

from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from datetime import datetime
from operator import contains
from werkzeug.utils import secure_filename
from email_validator import validate_email, EmailNotValidError
from password_strength import PasswordPolicy
import subprocess

from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema
from ..tareas import CronConvert, SendEmail

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

    if email is not None:
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
        return -3, "Error de validacion en comparacion del password"

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
        # tiene errores de validacion el password
        return -4, f"El password tiene {len(result)} errores de " + \
                   f"validacion en complejidad : {str(result)}. " + \
                   f"Debe tener mínimo: 8 caracteres, 2 mayusculas, " + \
                   f"2 dígitos, 2 caracteres especiales."
    
    return 0, password1


# ----------------------------------------------------------------------------


# end point: /api/auth/signup
class VistaSignUp(Resource):
    """clase relacionada con la creacion de usuario."""

    def post(self):
        """Crea un nuevo usuario.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X POST
             -H "Content-Type: multipart/form-data" 
             -F "username=s.salinasv" 
             -F "email=s.salinasv@uniandes.edu.co" 
             -F "password1=ABC123+-.#$%" 
             -F "password2=ABC123+-.#$%" 
             http://localhost:5000/api/auth/signup
        """

        usuario = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        email = request.form["email"]
        
        # valida el password
        err, password = ValidarPassword(password1, password2)
        if err != 0:
            return f"Error en el password : {password}", 400

        # valida el email
        err, email = ValidarEmail(email)
        if err != 0:
            return f"Error en el email : {email}", 400

        # evalua si ya existe un usuario con igual usuario
        if db.session.query(
            Usuario.query.filter(
            Usuario.usuario == usuario
            ).exists()).scalar():

            # usuario ya existente en la base de datos
            return f"Usuario {usuario} ya existente. " \
                "Cambielo e intente de nuevo", 400

        # evalua si ya existe un usuario con igual email
        if db.session.query(
            Usuario.query.filter(
            Usuario.email == email
            ).exists()).scalar():

            # email ya existente en la base de datos
            return f"Email {email} ya existente. " \
                "Cambielo e intente de nuevo", 400

        nuevo_usuario = Usuario(
            usuario=usuario,
            email=email,
            contrasena=password
            )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return "Usuario creado exitosamente", 200


# ----------------------------------------------------------------------------


# end point: /api/auth/login
class VistaLogIn(Resource):
    """Clase relacionada con login."""

    def post(self):
        """inicio de sesion.
    
        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X POST
             -H "Content-Type: multipart/form-data" 
             -F "username=s.salinasv" 
             -F "password=ABC123+-.#$%" 
             http://localhost:5000/api/auth/login

        o tambien:
        curl -X POST
             -H "Content-Type: multipart/form-data" 
             -F "username=s.salinasv@uniandes.edu.co" 
             -F "password=ABC123+-.#$%" 
             http://localhost:5000/api/auth/login
        """

        username = request.form["username"]
        password = request.form["password"]

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
                
                return {"mensaje":"inicio de sesion exitoso", "token": token_de_acceso}

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
                
                return {"mensaje":"inicio de sesion exitoso", "token": token_de_acceso}

        return "El usuario no existe", 404


# ----------------------------------------------------------------------------


# end point: /api/tasks
class VistaTareas(Resource):
    """"""

    # @jwt_required((optional=True)
    def get(self):
        """Retorna todas las tareas.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X GET 
             -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}"
             "http://localhost:5000/api/tasks?user_id=1&max=100&order=0"
        """

        # obtiene los datos como parametros de la solicitud
        user_id = request.args.get('user_id', default = 0, type = int)
        max = request.args.get('max', default = 100, type = int)
        order = request.args.get('order', default = 0, type = int)

        # valida el dato entregado
        if max < 1:
            return "El valor pasado en 'max' debe ser un numero " \
                "entero positivo.", 400

        # valida el dato entregado
        if order not in (0, 1):
            return "El valor numerico pasado en 'order' debe ser " \
                "0 o 1.", 400

        # valida que se haya pasado el id del usuario
        if user_id > 0:

            if db.session.query(Tarea.query.filter(Tarea.usuario_id==user_id).exists()).scalar():

                # obtiene las tareas asociadas al usuario
                tareas = Tarea.query.filter(Tarea.usuario_id==user_id)

                if order == 1:
                    # ordena las tareas de forma descendente
                    tareas = tareas.order_by(desc(Tarea.id))

                count = 0
                lista = []
                for ta in tareas:
                    lista.append({'id': ta.id, 'nombre': ta.archivo, 
                        'extension_origen': ta.formato_origen,
                        'extension_destino': ta.formato_destino,
                        'estado': ta.estado})

                    if count >= max:
                        break
                    else:
                        count += 1

                return lista
            else:
                return f"El usuario {user_id} no tiene tareas registradas.", 400
        else:
            return "No se suministro el iD del usuario a consultar.", 400


    # @jwt_required((optional=True)
    def post(self):
        """Se crea una nueva tarea.
        
        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             -F "fileName=@/home/estudiante/music/tina-guo.mp3;type=audio/mpeg"  
             -F "newFormat=wav" 
             -F "user_id=1" 
             http://localhost:5000/api/tasks
        """

        # obtiene el identificador del usuario
        try:
            usuario_id = request.form["user_id"]
        except:
            # no se envio la extension de destino, por ende no se crea la tarea
            return "No se reporto el id del usuario.", 400

        # valida que el usuario exista
        if db.session.query(Usuario.query.filter(Usuario.id==usuario_id).exists()).scalar():

            # obtiene el archivo enviado
            try:
                f = request.files['fileName']
            except:
                # no se envio el archivo, por ende no se crea la tarea
                return "No se cargo el archivo.", 400

            # obtiene el tipo de archivo al que se transformara
            try:
                extension_destino = request.form['newFormat']
            except:
                # no se envio la extension de destino, por ende no se crea la tarea
                return "No se definio la extension de destino.", 400

            if f is None:
                # no se envio el archivo, por ende no se crea la tarea
                return "No se cargo el archivo.", 400

            if extension_destino is None:
                # no se envio la extension de destino, por ende no se crea la tarea
                return "No se definio la extension de destino.", 400

            if usuario_id is None:
                # no se envio la extension de destino, por ende no se crea la tarea
                return "No se reporto el id del usuario.", 400

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
                return "Nombre de archivo sin base.", 400

            # valida la extension del archivo de origen
            if extension_origen not in formatos:
                # el formato del archivo no es admitido
                return "El formato del archivo no es admitido.", 400

            # valida la extension de destino
            if extension_destino not in formatos:
                # el formato de destino no es admitido
                return "El formato de destino no es admitido.", 400

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
                return "Error al almacenar el archivo.", 400

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

        else:
            return f"Usuario {usuario_id} no existe.", 400

# ----------------------------------------------------------------------------


# end point: /api/tasks/<int:id_task>
class VistaTarea(Resource):
    """"""

    # @jwt_required((optional=True)
    def get(self, id_task):
        """Se obtiene una tarea con base en el id de la tarea.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X GET -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/tasks/1
        """

        # determina si existe una tarea con ese id
        if db.session.query(Tarea.query.filter(Tarea.id==id_task).exists()).\
            scalar():
            return tarea_schema.dump(Tarea.query.get_or_404(id_task))
        else:
            return f"No existe la tarea {id_task}."

    # @jwt_required((optional=True)
    def put(self, id_task):
        """Se actualiza una tarea.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X DELETE -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}"
             -F "newFormat=aac"
             http://localhost:5000/api/tasks/1
        """

        # obtiene los datos como parametros de la solicitud
        newFormat = request.form['newFormat']

        # obtiene el tipo de archivo al que se transformara
        try:
            extension_destino = newFormat
        except:
            # no se envio la extension de destino, por ende no se crea la tarea
            return "No se definio la extension de destino.", 400

        if extension_destino is None:
            # no se envio la extension de destino, por ende no se crea la tarea
            return "No se definio la extension de destino.", 400

        # pasa la extension de destino a minuscula
        extension_destino = extension_destino.lower()

        # valida la extension de destino
        if extension_destino not in formatos:
            # el formato de destino no es admitido
            return "El formato de destino no es admitido.", 400

        # determina si existe una tarea con ese id
        if db.session.query(Tarea.query.filter(Tarea.id==id_task).exists()).\
            scalar():

            # obtiene la tarea con el id
            tarea = Tarea.query.get(id_task)

            if extension_destino == tarea.formato_destino:
                return "No hay cambio en el formato de destino. " \
                    "Tarea no actualizada.", 200

            # obtiene la fecha actual
            fecha = datetime.now()
            tfecha = fecha.strftime('%Y%m%d%H%M%S')
            archivo = tarea.archivo

            # obtiene la extension del archivo en minuscula
            extension_origen = archivo.split('.')[-1].lower()
            # obtiene la base del nombre del archivo
            base_archivo = archivo[:(len(archivo)-len(extension_origen)-1)]
            # genera el nombre del archivo con el que se almacenara el archivo 
            # transformado
            archivo_destino = f"{tfecha}_{base_archivo}.{extension_destino}".\
                replace(' ', '_')
            # construye la ruta donde se almacenara el archivo transformado
            ruta_archivo_destino = f"{ruta}/{archivo_destino}"

            # elimina el archivo previamente convertido
            if tarea.estado == "processed":
                subprocess.call(['rm', '-f', tarea.ruta_archivo_destino])

            # actualiza la tarea
            tarea.formato_destino = extension_destino
            tarea.ruta_archivo_destino = ruta_archivo_destino
            tarea.estado = 'uploaded'
            db.session.commit()

            # envia el mensaje al usuario informando de la actualizacion
            mensaje = f"Se actualizo exitosamente la tarea {id_task}."
            SendEmail(tarea.usuario.email, mensaje)

            return "La tarea fue actualizada", 200

        else:
            return "No existe la tarea a actualizar.", 400


    # @jwt_required((optional=True)
    def delete(self, id_task):
        """Se elimina el archivo.

        Esta funcion se llama usando CURL desde la linea de comandos asi:
        curl -X DELETE -H "Content-Type: multipart/form-data" 
             -H "Authorization: Bearer {..token..}" 
             http://localhost:5000/api/tasks/1
        """


        if db.session.query(Tarea.query.filter(Tarea.id==id_task).exists()).scalar():

            # obtiene la tarea
            tarea = Tarea.query.get(id_task)

            # elimina el archivo original
            subprocess.call(['rm', '-f', tarea.ruta_archivo_origen])

            # elimina el archivo convertido
            if tarea.estado == "processed":
                subprocess.call(['rm', '-f', tarea.ruta_archivo_destino])

            # elimina el registro en la base de datos
            db.session.delete(tarea)
            db.session.commit()

            return "La tarea fue eliminada", 200

        else:
            return "No existe la tarea a eliminar", 400


# ----------------------------------------------------------------------------


# end point: /api/files/<string:filename>
class VistaUsuariosTarea(Resource):
    """"""

    # @jwt_required((optional=True)
    def get(self, filename):
        """Retorna el archivo relacionada a un nombre de archivo."""

        # obtiene la ultima tarea cargada que tiene como nombre de archivo el
        # pasado como parametro de la funcion
        if db.session.query(Tarea.query.\
            filter(Tarea.archivo.contains(filename)).exists()).scalar():

            tarea = Tarea.query.filter(Tarea.archivo.contains(filename)).\
                order_by(Tarea.id.desc()).first()

            # si la tarea ya fue procesada retorna el archivo convertido
            if tarea.estado == "processed":
                try:
                    return send_file(tarea.ruta_archivo_destino, 
                        attachment_filename=str(tarea.ruta_archivo_destino).\
                            split('/')[-1])
                except Exception as e:
            	    return str(e)

            else:
                try:
                    return send_file(tarea.ruta_archivo_origen, 
                        attachment_filename=str(tarea.ruta_archivo_origen).\
                            split('/')[-1])
                except Exception as e:
            	    return str(e)

        else:
            return f"No existe una tarea sobre el archivo {filename}."            

# ----------------------------------------------------------------------------


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


