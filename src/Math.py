from math import *

# @brief calculates operations with eval
# @param operation string with the operation to calculate
# @return tuple with a boolean indicating if there was any error, and the result
# @details returns True if there was no error calculating the operation
def calculateOperation(operation : str):
  operations = {"sqrt": sqrt} 
  try:
    result = eval(operation,operations)
    return (True, result)
  except:
    return (False, operation)
