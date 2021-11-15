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

# bandera que define se se procesarán los archivos desde un origen AWS S3
s3=1

# hace ciclo por los grupos de conversiones paralelos que se desean ejecutar
for item in $(seq 1 20)
do
    echo -e "\n==============================\n"
    echo -e "Grupos paralelos:\n"
    echo -e "$item\n"

    # dispara el procesamiento paralelo
    /bin/bash /home/ubuntu/Proyecto-Grupo14-202120/Backend/scripts/test_pararell.sh $((item*10)) $s3

    # 4spera un tiempo dependiendo del numero de items paralelos
    sleep $((item*5*10+120))

done

echo "Done"
