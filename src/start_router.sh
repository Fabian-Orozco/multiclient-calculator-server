#order: ID_router IP Port_server Port_router
python3 Router2.py router J 172.16.202.167 8081 50010 &
python3 Router2.py router C 172.16.202.167 8081 50060 &
python3 Router2.py router C 172.16.202.167 8081 50080 &
python3 Router2.py router J 172.16.202.167 8081 50230 &
python3 Router2.py router J 172.16.202.167 8081 50250 &
python3 Router2.py router J 172.16.202.167 8081 50300 &
