#!/usr/bin/python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------

"""Definición de la función que obtiene los archivos a procesar."""

# -----------------------------------------------------------------------------

import os, json
import psycopg2

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

def conectar():
    conexion = None
    try:
        with open('../api/credenciales.json') as arch:
            config = json.load(arch)
        conexion = psycopg2.connect(host=config['host'], port=config['port'], dbname=config['database'], user=config['user'], password=config['password'])
        cur = conexion.cursor()
        salida = open("tareas.txt", "w")
        cur.execute("SELECT archivo, formato FROM tarea WHERE estado = 'uploaded'")
        for tarea in cur:
            salida.write(','.join(tarea) + os.linesep)
        salida.close()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conexion is not None:
            conexion.close()

if __name__ == '__main__':
    conectar()
