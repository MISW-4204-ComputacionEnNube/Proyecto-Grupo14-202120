#!/usr/bin/python
import psycopg2
import os, sys, json

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
