#!/bin/bash 
echo -n [Configurando routers...]

cd src

# args: topologyFilename IP Port_server
# python3 router_mapper.py topologia.csv 172.16.202.167 8081

python3 router_mapper.py $1 $2 $3

# for local tests
# python3 router_mapper.py topologia.csv 127.0.0.1 8081

chmod +x start_router.sh
./start_router.sh


echo
echo -n [Configuración finalizada]