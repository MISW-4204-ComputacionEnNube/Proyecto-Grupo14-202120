## Proyecto de Computación en la Nube. Grupo 14.

### 1. Instalación en maquina virtual.

* Este proyecto es la realización de una API en python3 con flask y utiliza para su despliegue en producción el servidor de aplicaciones gunicorn y el nginx como servidor proxy. <br>

* Esta aplicación esta diseñada para ser instalada en forma manual y se puede hacer descargando este repsoitorio o el archivo cromprimido [realease](https://github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo14-202120/releases/tag/V1.0.0). <br>

* El detalle de las intrucciones para su intalación, en máquinas virtuales se encuentra [Aquí](https://github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo14-202120/wiki/instalacion)

### 2. Instalación en AWS.

* El proyecto se adecuo para su instalación y despliegue en Amazon Web Service "AWS", utilizando python3, gunicorn y nginx en una instancia EC2 "Web Server". <br>

* Además se desplegaron instancias EC2 para el Worker y NFS y se configuraron los servicios de "RDS" con la base de datos PostgreSQL y Simple Email Service "SES". <br>

* El detalle de la configuración, instalación y despliegue se puede consultar en la [Wiki](https://github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo14-202120/wiki) del proyecto, sección "Sistema conversión Cloud - AWS".
