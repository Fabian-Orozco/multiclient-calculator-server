#!/bin/bash 
# Ejecuta el script de python que carga la topologia de nuestros nodos.
# Corre el archivo sh que generó python.

echo
echo -n [Configurando routers...]

cd src

# args: [topologyFilename] [IP] [Port_server]
python3 Router_mapper.py $1 $2 $3

# Da permisos de ejecución
chmod +x start_router.sh

# Script generado por python. Corre cada nodo del equipo.
./start_router.sh

# Muestra el estado de las terminales generadas
screen -ls

echo
echo -n [Configuración finalizada]
echo
