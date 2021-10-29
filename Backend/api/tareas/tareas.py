#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

"""Convierte entre los diferentes formatos de audio."""

# ----------------------------------------------------------------------------

import subprocess
from datetime import datetime
import requests

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
__date__ = "2021-10-29 05:30"

# ----------------------------------------------------------------------------

def SendSlack(mensaje: str) -> str:
    """Función que envía un mensaje por slack."""

    url_notificacion = "https://hooks.slack.com/services/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"

    asunto = "Notificacion de Cloud Conversion Tool"

    data = { "text": f"{mensaje}"}

    r = requests.post(url = url_notificacion, json=data )

    return "Done"


# ----------------------------------------------------------------------------


def SendEmail(mensaje: str, user_id: int) -> str:
    """Función que envía un mensaje por email."""

    asunto = "Notificacion de Cloud Conversion Tool"

    return "Done"

