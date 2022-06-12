#!/bin/bash

#order: IP Port_server ID_router
screen -dmS "J-router" python3 Router2.py router 172.16.202.167 8081 J
screen -dmS "C-router" python3 Router2.py router - - C
