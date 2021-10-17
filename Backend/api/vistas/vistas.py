from operator import contains
from flask import request
from marshmallow.fields import String
from ..modelos import db, Usuario, UsuarioSchema, Tarea, TareaSchema
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from ..tareas import registrar_log


usuario_schema = UsuarioSchema()
tarea_schema = TareaSchema()

class VistaTareas(Resource):

    def post(self):
        nueva_tarea = Tarea(archivo = request.json["archivo"], \
            formato = request.json["formato"], \
            fecha = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S"), \
            estado = "uploaded", \
            usuario_id = request.json["usuario_id"])
        db.session.add(nueva_tarea)
        db.session.commit()
        return tarea_schema.dump(nueva_tarea)

    def get(self):
        return [tarea_schema.dump(ta) for ta in Tarea.query.all()]

class VistaTarea(Resource):

    def get(self, id_task):
        return tarea_schema.dump(Tarea.query.get_or_404(id_task))

    def put(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        tarea.archivo = request.json.get("archivo",tarea.archivo)
        db.session.commit()
        return tarea_schema.dump(tarea)

    def delete(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        db.session.delete(tarea)
        db.session.commit()
        return {"mensaje":"La tarea fue eliminada"},204

class VistaSignUp(Resource):
    
    def post(self):
        nuevo_usuario = Usuario(usuario=request.json["usuario"], email=request.json["email"] ,contrasena=request.json["contrasena"])
        db.session.add(nuevo_usuario)
        db.session.commit()
        token_de_acceso = create_access_token(identity = nuevo_usuario.id)
        return {"mensaje":"usuario creado exitosamente", "token":token_de_acceso}

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena",usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '',204

class VistaLogIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"], Usuario.contrasena == request.json["contrasena"]).first()
        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity = usuario.id)
            return {"mensaje":"Inicio de sesión exitoso", "token": token_de_acceso}

class VistaUsuariosTarea(Resource):

    def get(self, filename):
        tarea = Tarea.query.filter(Tarea.archivo.contains(filename))
        print(tarea, filename)
        return tarea_schema.dump(tarea)