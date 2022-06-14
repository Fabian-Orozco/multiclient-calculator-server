# ejecutar con
# python router_mapper.py topologyFilename IP Port_server

import csv
import sys

# valores por defecto
topology_filename = "topologia.csv"
IP_7r = "172.16.202.167"	                #IP de 7raspado - Orozco
Port_server = "8081"                        # Puerto del server 7raspado

# "enum" para csv
NodeOne = 0
IPs_columnOne = 1
PortOne = 2
NodeTwo = 3
IPs_columnTwo = 4
PortTwo = 5
Weight = 6

# lee el archivo csv y carga las líneas que corresponden a la IP_7r en una lista
# en la lista, nuestros nodos siempre van escritos del lado izquierdo.
# retorna la lista con dichos valores
def getNodesInfo():
    conns = []
    with open(topology_filename) as topology:
        file = csv.reader(topology)
        for r in file:  # r is row
            if (r[IPs_columnOne] == IP_7r):
                # me, weight, neighbor
                conns.append([r[NodeOne], r[PortOne], r[NodeTwo], r[IPs_columnTwo], r[PortTwo], r[Weight]])
            elif (r[IPs_columnTwo] == IP_7r):
                # me, weight, neighbor
                conns.append([r[NodeTwo], r[PortTwo], r[NodeOne], r[IPs_columnOne], r[PortOne], r[Weight]])
    return conns

# Crea el archivo .sh ejecutable de bash
# el archivo sh contiene comandos para correr otros programas (routers)
# les envía su puerto y su letra que lo caracteriza
# al primer router que abre le envía la IP del servidor para montar la comunicación: server-nodos
def createSh(conns):
    with open("start_router.sh", "w") as configRouter_sh:
        counter = 0
        configRouter_sh.write("#!/bin/bash\n\n#order: IP Port_server ID_router\n")  # header of file
        IDs_registers = ""  # lleva el registro para no reescribir un nodo.
        while (counter < len(conns)):
            nodeID = conns[counter][0]
            if (nodeID not in IDs_registers): # no repite nodos, para no abrir mas de uno
                if (counter == 0):  # solo el primer nodo se conecta al server
                    temp = f"\"screen -dmS \"{nodeID}-router\" python3 Router2.py router {IP_7r} {Port_server} {nodeID}\""
                else:
                    temp = f"\"screen -dmS \"{nodeID}-router\" python3 Router2.py router - - {conns[counter][0]}\""
                temp = temp[1:len(temp)-1:]  # quita comillas
                configRouter_sh.write(f"{temp}\n")
                IDs_registers = IDs_registers + conns[counter][0]  # registra la letra del nodo
            counter = counter + 1
    return IDs_registers # nodos abiertos

# crea un archivo con los vecinos que tienen nuestros nodos.
# el objetivo es que cada nodo lea el archivo y cree los sockets que le correspondan
# en el archivo, nuestros nodos siempre van escritos del lado izquierdo.
def createNeighborsCsv(conns):
    with open("neighbors.csv", "w") as neighborsFile:
        counter = 0
        while (counter < len(conns)):  # recorre filas
            counter2 = 0
            while (counter2 < len(conns[counter])):  # recorre columnas
                if(not counter2 == 5): # weight, to delete ,
                    neighborsFile.write(conns[counter][counter2] + ",")
                else:
                    neighborsFile.write(conns[counter][counter2])
                counter2 = counter2 + 1  # avanza columna
            neighborsFile.write("\n")
            counter = counter + 1 # avanza fila

# Imprime el estado de la creación
# Invoca el cargar del archivo de topología para generar la lista.
# Crea el archivo que correrá los nodos
# Crea el archivo de vecinos de nuestros nodos
def main():
    print("\n\nRouter mapper Info:\ntopology_filename: " + topology_filename + "\nIP_7r: " + IP_7r + "\nPort_server: " + Port_server + "\n")

    conns = getNodesInfo()
    runningNodes = createSh(conns)
    print(len(runningNodes) , "online routers of 7raspado: " + runningNodes)
    createNeighborsCsv(conns)
    print("neighbors are ready to read for each router")


if __name__ == "__main__":
    # args: [fileTopology.csv] [IP] [Port_server]
    if (len(sys.argv) > 1):
        topology_filename = sys.argv[1]     # [fileTopology.csv]
    if (len(sys.argv) > 2):
        IP_7r = sys.argv[2]                 # [IP] 
    if (len(sys.argv) > 3):
        Port_server = sys.argv[3]           # Port_server
    main()