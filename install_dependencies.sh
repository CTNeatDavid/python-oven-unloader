#!/bin/bash

# Actualiza los repositorios y el sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instala pip para Python 3
sudo apt-get install -y python3-pip

# Instala los paquetes necesarios del sistema operativo
sudo apt-get install -y python3-dev libmysqlclient-dev

# Instala las dependencias de Python
pip3 install paho-mqtt RPi.GPIO mysqlclient
