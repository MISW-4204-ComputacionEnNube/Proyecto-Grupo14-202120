#!/usr/bin/python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------

"""Definición de los modelos."""

# -----------------------------------------------------------------------------

from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from datetime import datetime
import enum

# -----------------------------------------------------------------------------

# creditos
__author__ = "José López"
__review__ = "Santiago Alejandro Salinas Vargas"
__copyright__ = "Grupo 14"
__credits__ = ["Grupo 14"]
__license__ = "GPLv3"
__version__ = "1.0.0"
__email__ = "s.salinas@uniandes.edu.co"
__status__ = "Dev"
__date__ = "2021-10-19 10:24"

# -----------------------------------------------------------------------------

db = SQLAlchemy()


class Usuario(db.Model):
    """Modelo de los usuarios."""

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), )
    contrasena = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        """"""
        return f'<User {self.usuario}>'


class Tarea(db.Model):
    """Modelo de las tareas a ejecutar."""

    id = db.Column(db.Integer, primary_key=True)
    archivo = db.Column(db.String(512), nullable=False)
    formato_origen = db.Column(db.String(3), nullable=False)
    ruta_archivo_origen = db.Column(db.String(1024), nullable=False)
    formato_destino = db.Column(db.String(3), nullable=False)
    ruta_archivo_destino = db.Column(db.String(1024), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.today())
    estado = db.Column(db.String(16), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"),
        nullable=False)
    usuario = db.relationship('Usuario',
        backref=db.backref('tarea', lazy=True))


    def __repr__(self):
        """"""
        return f'<Task {self.id}>'


class EnumADiccionario(fields.Field):
    """"""

    def _serialize(self, value, attr, obj, **kwargs):
        """"""
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}


class UsuarioSchema(SQLAlchemyAutoSchema):
    """"""

    class Meta:
        """"""

        model = Usuario
        include_relationships = True
        load_instance = True


class TareaSchema(SQLAlchemyAutoSchema):
    """"""

    formato = EnumADiccionario(attribute=("formato"))


    class Meta:
        """"""

        model = Tarea
        include_relationships = True
        load_instance = True
