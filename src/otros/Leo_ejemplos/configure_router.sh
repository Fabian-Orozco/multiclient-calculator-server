#!/bin/bash
#echo -n Numero de routers inter-provinciales: 
#read inter_provincial_count
inter_provincial_count=3

#echo -n Numero de routers intra-provinciales: 
#read intra_provincial_count
intra_provincial_count=3

#echo -n Numero de areas de salud: 
#read health_area_count
health_area_count=1

cd src

# Crea una topologia random
python3 generate_topology.py $inter_provincial_count $intra_provincial_count $health_area_count

# Crea inter_provincial_count terminales de routers inter-provinciales 
for inter_id in $(seq 1 $inter_provincial_count); do
  gnome-terminal -e "bash -c \"python3 Inter_provincial_router.py $inter_id; exec bash\""
done

# Crea intra_provincial_count terminales de routers intra-provinciales para cada router inter provincial
for inter_id in $(seq 1 $inter_provincial_count); do
  for intra_id in $(seq 1 $intra_provincial_count); do
    gnome-terminal -e "bash -c \"python3 Intra_provincial_router.py $inter_id $intra_id; exec bash\""
  done
done

# Crea health_area_count terminales de areas de salud
for inter_id in $(seq 1 $inter_provincial_count); do
  for intra_id in $(seq 1 $intra_provincial_count); do
    for area_id in $(seq 1 $health_area_count); do
      gnome-terminal -e "bash -c \"python3 Server.py $inter_id $intra_id $area_id; exec bash\""
    done
  done
done
clear

# Abre server de verificacion en 4001
gnome-terminal -e "bash -c \"python3 VerificationServer.py; exec bash\""

# Talvez abra un cliente

echo Done 
