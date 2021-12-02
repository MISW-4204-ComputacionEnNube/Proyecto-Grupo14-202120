#!/usr/bin/python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------------------


"""Definicion de la funcion que se crea datos para las pruebas de estres."""


# ----------------------------------------------------------------------------


from datetime import datetime
import os
import boto3

from ..modelos import db, Tarea


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
__date__ = "2021-12-02 09:09"


# ----------------------------------------------------------------------------


ruta_base = "/home/ubuntu/Proyecto-Grupo14-202120/Backend"
ruta = f"{ruta_base}/files"
ruta_scripts = f"{ruta_base}/scripts"
script_conversion = f"{ruta_scripts}/convert_pararell.sh"
formatos = ['aac', 'mp3', 'ogg', 'wav', 'wma']
s3 = 1
# URL de la cola
queue_url = 'https://sqs.us-east-1.amazonaws.com/733817334377/cola-grupo14.fifo'
# maximas conversiones simultaneas
max_num_proc = 50


# ----------------------------------------------------------------------------


def make _data_proof():
    """Se crea una nueva tarea."""

    # obtiene los datos del usuario
    user_id = 1
    extension_destino = "wav"
    # obtiene el nombre del archivo
    archivo = "Brandenburg-Concerto-no.-3-BWV-1048-Complete-Performance.mp3"
    # obtiene la extension del archivo en minuscula
    extension_origen = "mp3"
    # obtiene la base del nombre del archivo
    base_archivo = "Brandenburg-Concerto-no.-3-BWV-1048-Complete-Performance"

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

    os.system(f"aws s3 cp {ruta}/{archivo} s3://bucket-grupo14{ruta_archivo_origen}")

    # crea el registro en la base de datos
    nueva_tarea = Tarea(
        archivo = archivo,
        formato_origen = extension_origen,
        ruta_archivo_origen = ruta_archivo_origen,
        formato_destino = extension_destino,
        ruta_archivo_destino = ruta_archivo_destino,
        fecha = fecha,
        estado = 'uploaded',
        usuario_id = user_id)

    db.session.add(nueva_tarea)
    db.session.commit()

    # crea el mensaje en la cola de aws
    # Create SQS client
    sqs = boto3.client('sqs')

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageGroupId='1',
        MessageDeduplicationId='A',
        MessageAttributes={
            'Title': {
                'DataType': 'String',
                'StringValue': 'conversion'
            },
            'Date': {
                'DataType': 'String',
                'StringValue': str(tfecha)
            },
            'UserId': {
                'DataType': 'Number',
                'StringValue': str(user_id)
            },
            'TaskId': {
                'DataType': 'Number',
                'StringValue': str(nueva_tarea.id)
            },
            'Archivo': {
                'DataType': 'String',
                'StringValue': str(archivo)
            },
            'FormatoOrigen': {
                'DataType': 'String',
                'StringValue': str(extension_origen)
            },
            'RutaArchivoOrigen': {
                'DataType': 'String',
                'StringValue': str(ruta_archivo_origen)
            },
            'FormatoDestino': {
                'DataType': 'String',
                'StringValue': str(extension_destino)
            },
            'RutaArchivoDestino': {
                'DataType': 'String',
                'StringValue': str(ruta_archivo_destino)
            },
        },
        MessageBody=(
            'Carga de conversion de archivo.'
        )
    )

    return "Done!"


# ----------------------------------------------------------------------------
