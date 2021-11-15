#!/usr/bin/bash
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------

# Definición del script quep rueba la conversion de archivos.

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
# __date__ = "2021-10-31 10:10"

# ----------------------------------------------------------------------------

# crea el contador de tareas
counter=$1

# bandera que define se se procesarán los archivos desde unaorigen AWS S3
s3=$2

# Obtiene las credenciales de conexion a la base de datos
credenciales="/home/ubuntu/Proyecto-Grupo14-202120/Backend/api/credenciales.json"
host=`grep '"host"' $credenciales | cut -d '"' -f 4`
database=`grep '"database"' $credenciales | cut -d '"' -f 4`
user=`grep '"user"' $credenciales | cut -d '"' -f 4`
password=`grep '"password"' $credenciales | cut -d '"' -f 4`
port=`grep '"port"' $credenciales | cut -d ':' -f 2`

# elimina las tareas en la base de datos
consulta="delete from tarea;"
PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"
# elimina los archivos procesados
rm /home/ubuntu/Proyecto-Grupo14-202120/Backend/files/*.wma
# recrea la base de datos
PGPASSWORD=$password psql -A -t -U $user -h $host -p $port $database < /home/ubuntu/test_log/tarea.sql
# elimina las tareas en la base de datos
consulta="delete from tarea where id>$counter;"
PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"

# ----------------------------------------------------------------------------

# Obtiene las credenciales de conexion a la base de datos
credenciales="/home/ubuntu/Proyecto-Grupo14-202120/Backend/api/credenciales.json"
host=`grep '"host"' $credenciales | cut -d '"' -f 4`
database=`grep '"database"' $credenciales | cut -d '"' -f 4`
user=`grep '"user"' $credenciales | cut -d '"' -f 4`
password=`grep '"password"' $credenciales | cut -d '"' -f 4`
port=`grep '"port"' $credenciales | cut -d ':' -f 2`

# obtiene la ruta del software conversor
conversor="/bin/bash /home/ubuntu/Proyecto-Grupo14-202120/Backend/scripts/convert_pararell.sh "

# hace ciclo por las tareas que estan pendientes por convertir
consulta="select tarea.id, tarea.ruta_archivo_origen, tarea.ruta_archivo_destino, usuario.email, tarea.archivo, tarea.formato_origen, tarea.formato_destino, to_char(tarea.fecha, 'YYYY-MM-DD_HH24:MI:SS'), usuario.usuario from tarea, usuario where tarea.usuario_id=usuario.id and tarea.estado='uploaded';"

for item in `PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"`
do
    echo -e "\n==============================\n"
    echo -e "Procesando la tarea:\n"
    echo -e "$item\n"

    inicio=`date '+%s'`

    # divide la informacion del item
    id=`echo $item | cut -d '|' -f 1`
    ruta_archivo_origen=`echo $item | cut -d '|' -f 2`
    ruta_archivo_destino=`echo $item | cut -d '|' -f 3`

    # convierte el archivo
    $conversor $id $counter $ruta_archivo_origen $ruta_archivo_destino $s3 &

done

echo "Done"
