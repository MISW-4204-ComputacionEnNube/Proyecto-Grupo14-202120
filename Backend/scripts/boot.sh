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
# __date__ = "2021-11-10 18:00"
​
# ----------------------------------------------------------------------------
​
# Preparar el sistema para la instalación de los servicios.
​
sudo apt update
sudo apt upgrade
sudo apt install git
git config --global user.name "J3LopezL"
git config --global user.email jl.lopez77@uniandes.edu.co
sudo apt install python3.8-venv
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install nginx
sudo usermod "$(whoami)" -a -G www-data
​
function servicioApi(){
  echo "[Unit]" | sudo tee -a /etc/systemd/system/apig14.service
  echo "Description=Gunicorn instance to serve Gunicorn apig14" | sudo tee -a /etc/systemd/system/apig14.service
  echo "After=network.target" | sudo tee -a /etc/systemd/system/apig14.service
  echo -e | sudo tee -a /etc/systemd/system/apig14.service
  echo "[Service]" | sudo tee -a /etc/systemd/system/apig14.service
  echo "User=$(whoami)" | sudo tee -a /etc/systemd/system/apig14.service
  echo "Group=www-data" | sudo tee -a /etc/systemd/system/apig14.service
  echo "WorkingDirectory=/home/"$(whoami)"/Proyecto-Grupo14-202120/Backend" | sudo tee -a /etc/systemd/system/apig14.service
  echo "Environment="PATH=/home/"$(whoami)"/Proyecto-Grupo14-202120/Backend/venv/bin"" | sudo tee -a /etc/systemd/system/apig14.service
  echo "ExecStart=/home/"$(whoami)"/Proyecto-Grupo14-202120/Backend/venv/bin/gunicorn --workers 4 --bind unix:apig14.sock -m 007 wsgi:app" | sudo tee -a /etc/systemd/system/apig14.service
  echo -e | sudo tee -a /etc/systemd/system/apig14.service
  echo "[Install]" | sudo tee -a /etc/systemd/system/apig14.service
  echo "WantedBy=multi-user.target" | sudo tee -a /etc/systemd/system/apig14.service
}
​
function servicioNginx(){
  echo "server {" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "    listen 8080;" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "    server_name 172.16.1.251;" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "    client_max_body_size 100M;" | sudo tee -a /etc/nginx/sites-available/apig14
  echo -e | sudo tee -a /etc/nginx/sites-available/apig14
  echo "    location / {" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "        include proxy_params;" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "        proxy_pass http://unix:/home/"$(whoami)"/Proyecto-Grupo14-202120/Backend/apig14.sock;" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "    }" | sudo tee -a /etc/nginx/sites-available/apig14
  echo "}" | sudo tee -a /etc/nginx/sites-available/apig14
}
​
echo "Inicia configuración instancia web "`date '+%Y%m%d%H%M%S'`
Proyecto="/home/"$(whoami)"/Proyecto-Grupo14-202120"
​
# Verificar la existencia de la carpeta del proyecto.
if [ ! -d $Proyecto ]; then
  cd /home/"$(whoami)"/
  # Descarga del repositorio los archivos requeridos
  git clone -b releasev2 git@github.com:MISW-4204-ComputacionEnNube/Proyecto-Grupo14-202120.git
  Api="/home/"$(whoami)"/Proyecto-Grupo14-202120/Backend"
  # Verifica que se haya descargado la carpeta principal del proyecto
  if [ -d $Api ]; then
    cd $Proyecto
    # Borra directorios no requeridos
    rm -rf Docs_Postman
    rm -rf images
    cd $Api
    # rm -rf files
    rm -rf scripts
    # Instalación del ambiente virtual
    python3 -m venv venv
    # Activa el ambiente virtual
    source venv/bin/activate
    # Instala los paquetes requeridos para el proyecto 
    pip install -r requirements.txt
    # Desactiva el ambiente virtual
    deactivate
    # Crear el servicio de Gunicorn con el nombre apig14 en el sistema.
    servicioApi
    # Habilitar el servicio de Nginx por el puerto 8080 sock apig14.
    sudo rm -rf /etc/nginx/sites-available/*
    sudo rm -rf /etc/nginx/sites-enabled/*
    servicioNginx
    # Iniciar los servicios instalados.
    sudo systemctl start apig14
    sudo systemctl enable apig14
    sudo ln -s /etc/nginx/sites-available/apig14 /etc/nginx/sites-enabled
    sudo systemctl restart nginx
    sudo ufw allow 'Nginx Full'
  else
    echo "Se presento un error en la descarga del repositorio"
  fi
echo "Instalación terminada "`date '+%Y%m%d%H%M%S'`
fi