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


def SendEmail(email: str):
    """Función que envía un mensaje por email."""

    return "Done"


def CronConvert() ->str:
    """Funcion que se dispara por un cron y convierte los archivos pendientes."""

    # hace un ciclo por las tareas donde el estado es 'uploaded'
    for task in Tarea.query.filter(Tarea.estado=='uploaded').order_by(Tarea.fecha):

        # utiliza ffmpeg para la conversión siempre y cuando sea de formato
        # 'aac', 'mp3', 'ogg', 'wav', 'wma'.
        formato_ffmpeg = ['aac', 'mp3', 'ogg', 'wav', 'wma']
        if task.formato_origen in formato_ffmpeg and \
            task.formato_destino in formato_ffmpeg:

            print(">>> Procesando archivo : ", task.archivo, " | ",
                task.formato_origen, " -> ", task.formato_destino)

            # ejecuta un subproceso que hace la conversión
            subprocess.call(['ffmpeg', '-i', Tarea.ruta_archivo_origen,
                Tarea.ruta_archivo_destino])

            task.estado = "processed"
            db.session.commit()

            # envia el mensaje al usuario
            SendEmail(task.usuario.email)

        else:
            print("Formato no admitido")

    return "Done"
