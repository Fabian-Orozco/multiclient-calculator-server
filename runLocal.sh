#!/bin/bash 
# Para pruebas internas (locales y en putty).

cd src
# [cantidad de nodos] [IP]
python3 config_generate.py $1 $2 > topologia.csv
sleep 0.3 # delay

screen -dmS "Server" python3 Server.py server $2 $3
sleep 0.3 # delay

screen -dmS "Client" python3 Client.py -u admin -p admin1234 $2 $3
cd ..

# Realiza el proceso de levantar los nodos.
# [nombre archivo] [IP] [PORT]
./config_routers.sh topologia.csv $2 $3
