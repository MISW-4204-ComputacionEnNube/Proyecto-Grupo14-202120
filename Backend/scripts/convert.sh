#!/usr/bin/bash
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

# Definición del script que dispara de manera remota la conversion de archivos.

# ----------------------------------------------------------------------------

# creditos
# __author__ = "Santiago Alejandro Salinas Vargas"
# __review__ = "Santiago Alejandro Salinas Vargas"
# __copyright__ = "Grupo 14"
# __credits__ = ["Grupo 14"]
# __license__ = "GPLv3"
# __version__ = "1.0.0"
# __email__ = "s.salinas@uniandes.edu.co"
# __status__ = "Dev"
# __date__ = "2021-10-29 05:33"

# ----------------------------------------------------------------------------

# Obtiene las credenciales de conexion a la base de datos
credenciales="/home/ubuntu/Proyecto-Grupo14-202120/Backend/api/credenciales.json"
host=`grep '"host"' $credenciales | cut -d '"' -f 4`
database=`grep '"database"' $credenciales | cut -d '"' -f 4`
user=`grep '"user"' $credenciales | cut -d '"' -f 4`
password=`grep '"password"' $credenciales | cut -d '"' -f 4`
port=`grep '"port"' $credenciales | cut -d ':' -f 2`

# obtiene la ruta del software conversor
conversor="/usr/bin/ffmpeg -i "

# hace ciclo por las tareas que estan pendientes por convertir
consulta="select id, ruta_archivo_origen, ruta_archivo_destino, usuario_id from tarea where estado='uploaded';"

for item in `PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"`
do
    echo -e "\n==============================\n"
    echo -e "Procesando la tarea:\n"
    echo -e "$item\n"

    # divide la informacion del item
    id=`echo $item | cut -d '|' -f 1`
    ruta_archivo_origen=`echo $item | cut -d '|' -f 2`
    ruta_archivo_destino=`echo $item | cut -d '|' -f 3`
    usuario_id=`echo $item | cut -d '|' -f 4`

    # convierte el archivo
    $conversor $ruta_archivo_origen $ruta_archivo_destino

    # obtiene el estado final de ejecución del comando de conversion
    status=$?

    # determina si fue exitosa la conversion
    if test $status -eq 0
    then
        if test -s $ruta_archivo_destino
        then

            # actualiza el estado de la tarea
            consulta="update tarea set estado='processed' where id=$id;"
            PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"

            # envia un mensaje al usuario
            # TODO
            
        fi
    fi
done

echo "Done"