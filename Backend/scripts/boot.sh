#!/usr/bin/bash
# -*- coding: utf-8 -*-
​
# ----------------------------------------------------------------------------
​
# Definición del script para descargar el proyecto e instalar los servicios en el Web Server.
​
# ----------------------------------------------------------------------------
​
# creditos
# __author__ = "José López Lesmes"
# __review__ = "Santiago Salinas Vargas"
# __copyright__ = "Grupo 14"
# __credits__ = ["Grupo 14"]
# __license__ = "GPLv3"
# __version__ = "1.0.0"
# __email__ = "jl.lopez77.edu.co"
# __status__ = "Dev"
# __date__ = "2021-11-13 05:56"
​
# ----------------------------------------------------------------------------

# define las constantes usadas en el script
user="ubuntu"
group="www-data"
pro_name="Proyecto-Grupo14-202120"
proyecto="/home/$user/$pro_name"
api="/home/$user/$pro_name/Backend"
url="https://github.com/MISW-4204-ComputacionEnNube/$pro_name.git"
api_service="apig14"
port="8080"
ip=`ip addr | grep "inet " | grep "eth0" | cut -d ' ' -f 6 | cut -d '/' -f 1`

# ----------------------------------------------------------------------------

echo "Inicia la configuración instancia web "`date '+%Y%m%d%H%M%S'`

# +++++++++++++++++++++++++++++++++++​

# Preparar el sistema para la instalación de los servicios.
# actualiza la lista de paquetes en el manejador de paquetes del 
# sistema operativo​
apt update -y
# instala los paquetes básicos
apt install git python3-pip python3-dev python3-setuptools build-essential -y 
apt install libssl-dev libffi-dev nginx -y

# +++++++++++++++++++++++++++++++++++​

# Descarga del repositorio los archivos requeridos
cd /home/$user
git clone $url

# Verificar la existencia de la carpeta del proyecto.
if [ ! -d $proyecto ]; 
then
  # no existe el directorio del repositorio
  echo "Se presento un error en la descarga del repositorio"
  exit 1
fi
# Verifica que se haya descargado la carpeta principal del proyecto
if [ ! -d $Api ];
then
  echo "Se presento un error en la descarga del repositorio"
  exit 2
fi

# Ingresa al directorio donde estan el código de la aplicación
cd $api
# Instala los paquetes requeridos para el proyecto 
pip install -r requirements.txt

# +++++++++++++++++++++++++++++++++++​

# Crear el servicio de Gunicorn
echo -e "
[Unit]
Description=Gunicorn instance to serve Gunicorn $api_service
After=network.target

[Service]
User=$user
Group=$group
WorkingDirectory=$api
Environment='PATH=$api/venv/bin'
ExecStart=$api/venv/bin/gunicorn --workers 4 --bind unix:$api_service.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/$api_service.service

# +++++++++++++++++++++++++++++++++++​

# elimina el sitios por default habilitado en Nginx
rm -f /etc/nginx/sites-enabled/default
# crea el servicio de Nginx
echo -e "
server {
    listen $port;
    server_name $ip;
    client_max_body_size 100M;

    location / {
        include proxy_params;
        proxy_pass http://unix:$api/$api_service.sock;
    }
}" > /etc/nginx/sites-enabled/$api_service

# habilita en el firewall el trafico hacia Nginx
ufw allow 'Nginx Full'

# +++++++++++++++++++++++++++++++++++​

# Iniciar los servicios instalados.
systemctl enable apig14
systemctl start apig14
systemctl stop apig14
systemctl start apig14

systemctl stop nginx
systemctl start nginx

echo "Instalación terminada "`date '+%Y%m%d%H%M%S'`
