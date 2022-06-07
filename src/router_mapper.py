# ejecutar con
# python router_mapper.py topologyFilename IP Port_server

import csv
import sys

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

def createSh(conns):
    with open("start_router.sh", "w") as configRouter_sh:
        counter = 0
        configRouter_sh.write("#order: IP Port_server ID_router\n")
        IDs_registers = ""
        while (counter < len(conns)):
            if (conns[counter][0] not in IDs_registers):
                if (counter == 0):  # solo el primer nodo se conecta al server
                    temp = f"\"python3 Router2.py router {IP_7r} {Port_server} {conns[counter][0]}\""
                else:
                    temp = f"\"python3 Router2.py router - - {conns[counter][0]}\""
                temp = temp[1:len(temp)-1:]  # quita comillas
                configRouter_sh.write(f"{temp} &\n")
                IDs_registers = IDs_registers + conns[counter][0]
            counter = counter + 1

def createNeighborsCsv(conns):
    with open("neighbors.csv", "w") as neighborsFile:
        counter = 0
        while (counter < len(conns)):
            counter2 = 0
            while (counter2 < len(conns[counter])):
                if(not counter2 == 5): # weight, to delete ,
                    neighborsFile.write(conns[counter][counter2] + ",")
                else:
                    neighborsFile.write(conns[counter][counter2])
                counter2 = counter2 + 1
            neighborsFile.write("\n")
            counter = counter + 1

def main():
    print("\n\nRouter mapper Info:\ntopology_filename: " + topology_filename + "\nIP_7r: " + IP_7r + "\nPort_server: " + Port_server + "\n")

    conns = getNodesInfo()
    createSh(conns)
    print(len(conns) , "online routers of 7raspado")
    createNeighborsCsv(conns)
    print("neighbors are ready to read for each router")


if __name__ == "__main__":
    # args: fileTopology.csv IP Port_server
    if (len(sys.argv) > 1):
        topology_filename = sys.argv[1]
    if (len(sys.argv) > 2):
        IP_7r = sys.argv[2]
    if (len(sys.argv) > 3):
        Port_server = sys.argv[3]
    main()