import json
route = "./json/results.json"


# @brief method to store a operation and its result in a file
# @param newOperation string with the operation
# @param result string with the result of the operation
def addOperation(newOperation : str, result : str):
    newOperation = f"{{\"operation\": \"{newOperation}\", \"result\": {result}}}"

    try:
        # abre archivo y lo almacena como string
        with open(route) as results: 
            fie_str = json.dumps(json.load(results))
    except:
        results = open(route, "w+")
        results.write("{\"operations\": []}")
        results.close()
        with open(route) as results: 
            fie_str = json.dumps(json.load(results))
    if (newOperation not in fie_str):
        original_str = fie_str
        # busca en orden inverso del json el primer '}'. No contempla el último chr.
        offset = fie_str.rindex("]", 0, len(fie_str)-1)
        # sobreescribe string de 0 a } y agrega coma
        fie_str = fie_str[:offset:]
        if ("[]" not in original_str):
            fie_str += ","
        # concatena otra operacion al string
        fie_str = fie_str + newOperation + "]}"

        # sobreescribe el archivo
        with open(route, "w") as results:
            results.write(fie_str)


# @brief method to search a operation stored in the result file
# @param newOperation string with the operation
# @return tuple with boolean to indicate if it was found, and the operatio if found 
def getOperation(operation : str):
    try:
        resultsFile = open(route, "r")
    except:
        return (False, operation)

    results_json= json.load(resultsFile)
    for operation_json in results_json["operations"]:
        if (operation_json["operation"] == operation):
            return (True, operation_json["result"])
    return (False, operation)


# test code. To run: python Writter.py
if __name__ == "__main__":
    print("\nstart\n")

    for k in range(1,5):
        operation = f"{k}+{k+1}"
        addOperation(operation, k)

    print("\nend\n")
