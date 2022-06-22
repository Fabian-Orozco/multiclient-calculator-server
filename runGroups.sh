#!/bin/bash 
# Para la demostración entre grupos.

cd src
screen -dmS "Server" python3 Server.py server $1 $2
sleep 0.3 # delay

screen -dmS "Client" python3 Client.py -u admin -p admin1234 $1 $2
cd ..

# Realiza el proceso de levantar los nodos.
# [nombre archivo] [IP] [PORT]
./config_routers.sh topologia.csv $1 $2
