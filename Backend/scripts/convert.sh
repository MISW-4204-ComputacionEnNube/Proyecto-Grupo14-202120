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

# imprime la fecha actual, para calcular el tiempo de ejcución del script
echo "FECHA INICIO : "`date '+%Y%m%d%H%M%S'`

# credenciales para el envio del email
from="s.salinasv@uniandes.edu.co"
from_name="Santiago Alejandro Salinas Vargas"
smtp_username="AKIA2VWXL5JUYXVHHU65"
smtp_password="BGK3EwVotaGornWSAYLBtr23lbOzKRo+r+fYaO944RcI"
smtp_endpoint="email-smtp.us-east-1.amazonaws.com"
smtp_port=587

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
consulta="select tarea.id, tarea.ruta_archivo_origen, tarea.ruta_archivo_destino, usuario.email, tarea.archivo, tarea.formato_origen, tarea.formato_destino, to_char(tarea.fecha, 'YYYY-MM-DD_HH24:MI:SS'), usuario.usuario from tarea, usuario where tarea.usuario_id=usuario.id and tarea.estado='uploaded';"

for item in `PGPASSWORD=$password psql -A -t -U $user -h $host -p $port -d $database -c "$consulta"`
do
    echo -e "\n==============================\n"
    echo -e "Procesando la tarea:\n"
    echo -e "$item\n"

    # divide la informacion del item
    id=`echo $item | cut -d '|' -f 1`
    ruta_archivo_origen=`echo $item | cut -d '|' -f 2`
    ruta_archivo_destino=`echo $item | cut -d '|' -f 3`
    email=`echo $item | cut -d '|' -f 4`
    archivo=`echo $item | cut -d '|' -f 5`
    formato_origen=`echo $item | cut -d '|' -f 6`
    formato_destino=`echo $item | cut -d '|' -f 7`
    fecha=`echo $item | cut -d '|' -f 8`
    usuario=`echo $item | cut -d '|' -f 9`


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
            # encripta el nombre de usuario
            esmtp_username=`echo -n $smtp_username | openssl enc -base64`
            esmtp_password=`echo -n $smtp_password | openssl enc -base64`
            # crea el archivo con el mensaje
            tmp=`mktemp`
            echo "EHLO example.com" > $tmp
            echo "AUTH LOGIN" >> $tmp
            echo "$esmtp_username" >> $tmp
            echo "$esmtp_password" >> $tmp
            echo "MAIL FROM: $from" >> $tmp
            echo "RCPT TO: $email" >> $tmp
            echo "DATA" >> $tmp
            #echo "X-SES-CONFIGURATION-SET: ConfigSet" >> $tmp
            echo "From: $from_name <$from>" >> $tmp
            echo "To: $email" >> $tmp
            echo "Subject: Notificacion de Cloud Conversion Tool" >> $tmp
            echo "" >> $tmp
            echo "Hola $usuario" >> $tmp
            echo "" >> $tmp
            echo "" >> $tmp
            echo "La tarea, que consistia en convertir el archivo $archivo del formato $formato_origen al formato $formato_destino y que fue activada la fecha $fecha, fue ejecutada correctamente y la conversion del archivo curso exitosamente." >> $tmp
            echo "" >> $tmp
            echo "" >> $tmp
            echo "Cordialmente," >> $tmp
            echo "" >> $tmp
            echo "Cloud Conversion Tool" >> $tmp
            echo "" >> $tmp
            echo "." >> $tmp
            echo "QUIT" >> $tmp
            
            # envia el correo
            openssl s_client -crlf -quiet -starttls smtp -connect $smtp_endpoint:$smtp_port < $tmp &

        fi
    fi
done

echo "FECHA FIN : "`date '+%Y%m%d%H%M%S'`