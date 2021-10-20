#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

""""""

# ----------------------------------------------------------------------------

from celery import Celery

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


celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task()
def registrar_log(usuario,fecha):
    """"""

    with open('log_sigin.txt','a+') as file:
        file.write(f'{usuario} - inicio de sessión: {fecha}\n')
