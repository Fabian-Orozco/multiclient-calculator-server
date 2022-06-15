#!/bin/bash 

cd src
# [cantidad de nodos] [IP]
python config_generate.py $1 $2 > topologia.csv
sleep 0.3

screen -dmS "Server" python Server.py server
sleep 0.3

screen -dmS "User" python Client.py -u admin -p admin1234
cd ..

# [nombre archivo] [IP] [PORT]
./config_routers.sh topologia.csv $2 $3
sleep 1
