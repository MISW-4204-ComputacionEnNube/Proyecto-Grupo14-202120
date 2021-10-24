#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Convierte entre los diferentes formatos de audio."""

# ----------------------------------------------------------------------------

import subprocess

from ..modelos import Tarea, db, Usuario

# ----------------------------------------------------------------------------

# creditos
__author__ = "Santiago Alejandro Salinas Vargas"
__review__ = "Santiago Alejandro Salinas Vargas"
__copyright__ = "Grupo 14"
__credits__ = ["Grupo 14"]
__license__ = "GPLv3"
__version__ = "1.0.0"
__email__ = "s.salinas@uniandes.edu.co"
__status__ = "Dev"
__date__ = "2021-10-22 05:39"

# ----------------------------------------------------------------------------


def SendEmail(email: str, mensaje: str) -> str:
    """Función que envía un mensaje por email."""

    asunto = "Notificacion de Cloud Conversion Tool"

    print(f"EMAIL: Destinatario -> {email}; Asunto -> {asunto}; Mensaje -> {mensaje}")
    return "Done"


# ----------------------------------------------------------------------------


def Convert(id_task: int) ->str:
    """Funcion que convierte el archivo de la tarea."""

    print(">>> id_task : ", id_task)
    
    # obtiene la tarea correspondiente
    task = Tarea.query.get(id_task)

    # utiliza ffmpeg para la conversión siempre y cuando sea de formato
    # 'aac', 'mp3', 'ogg', 'wav', 'wma'.
    formato_ffmpeg = ['aac', 'mp3', 'ogg', 'wav', 'wma']

    if task.formato_origen in formato_ffmpeg and \
        task.formato_destino in formato_ffmpeg:

        print(">>> Procesando archivo : ", task.archivo, " | ",
            task.formato_origen, " -> ", task.formato_destino)

        # ejecuta un subproceso que hace la conversión
        subprocess.call(['ffmpeg', '-i', task.ruta_archivo_origen,
            task.ruta_archivo_destino])

        task.estado = "processed"
        db.session.commit()

        # envia el mensaje al usuario
        mensaje = f"La tarea {task.id} fue procesada correctamente."
        SendEmail(task.usuario.email, mensaje)

    else:
        return "Formato no admitido"

    return "Done"
