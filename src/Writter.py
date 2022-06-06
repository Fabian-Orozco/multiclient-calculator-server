import json
route = "./json/BD.json"

# @param newOperation ejemplo: 
# "{\"index\": 1, \"operation\": \"2+2\", \"result\": \"4\"}"
def addOperation(newOperation):
    # abre archivo y lo almacena como string
    with open(route) as BDFile: 
        bd_str = json.dumps(json.load(BDFile))
    
    # busca en orden inverso del json el primer '}'. No contempla el último chr.
    offset = bd_str.rindex("}", 0, len(bd_str)-1) + 1
    # sobreescribe string de 0 a } y agrega coma
    bd_str = bd_str[:offset:] + ","
    
    # concatena otra operacion al string
    bd_str = bd_str + newOperation + "]}"

    # sobreescribe el archivo
    with open(route, "w") as BDFile:
        BDFile.write(bd_str)

# test code. To run: python Writter.py
if __name__ == "__main__":
    print("\nstart\n")

    for k in range(1,5):
        operation = f"{{\"index\": {k}, \"operation\": \"{k+1}+{k+2}\", \"result\": \"{k+1+k+2}\"}}"
        addOperation(operation)

    print("\nend\n")
