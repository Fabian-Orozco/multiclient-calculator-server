## Class Validator
# This class verifies if the input operation is valid or not
class Validator:
    VALID_ENTRIES = {"(", ")", "+", "-", "*", "/", "sqrt", "^", "1","2","3","4","5","6","7","8","9","0"}
    VALID_SYMBOLS = {"(", ")","+", "*", "/", "sqrt", "^",}
    VALID_NUMBERS = {"1","2","3","4","5","6","7","8","9","0"}

    ## Validates if the sqrt function is well typed
    # @param input the string to verify the sqrt function
    # @return True if the syntax of the sqrt function is valid, False if not
    def __validateSquare(self, i, input):

        if((i + 6) <= len(input)):      # The string has to follow the next structure: "sqrt(" and has to have at least one number before closing the parenthesis
            if(input[i + 1] == "q"):
                if(input[i + 2] == "r"):
                    if(input[i + 3] == "t"):
                        if(input[i + 4] == "("):
                            if ((input[i + 5] in self.VALID_NUMBERS) or (input[i + 5] == "s") or (input[i + 5] == "(")):
                                return True
        return False


    ## Validates the end and the beggining of the input to see if its valid
    # @param input The input string
    # @param length The length of the string
    # @return: True on valid borders, False if not
    def __checkBorders(self, input, length):
        i = 0
        char = input[i]
        if ((char != "(") and (char != "-") and (char in self.VALID_SYMBOLS) and (char != "s")):  
            return False                          # If the beginning is a symbol except "(" or "-" or "s" return False
        elif((char == "-") and (i + 1) < length):
            if(input[i + 1] == "-"):              # If the beginning is -- return False
                return False

        char = input[length - 1]
        if (((char != ")") and (char in self.VALID_SYMBOLS)) or (char == "-")):
            return False                          # If the end is a symbol except ")" return False
        
        return True


    ## When a minus operator appears this function validates it
    # @param input The input string
    # @param i The index of where the minus is in the string
    # @return True on valid borders, False if not
    def __checkMinus(self, input, i):
        if ((i - 1) >= 0):     # There is space before the minus
            if(((input[i - 1] in self.VALID_SYMBOLS) or (input[i - 1] == "-")) 
            and ((input[i + 1] in self.VALID_SYMBOLS) or (input[i + 1] == "-"))):    # In front and behind are symbols
                if((input[i + 1] == "-") and (input[i - 1] == ")")):                                            # ")--" is valid
                    return True
                elif(((input[i - 1] in self.VALID_SYMBOLS) or (input[i - 1] == "-"))and (input[i + 1] == "(")): # "symbol-(" is valid
                    return True
                else:
                    return False
            elif((input[i + 1] in self.VALID_SYMBOLS) and (input[i + 1] != "(") and (input[i + 1] != "-")):# "-symbol" is invalid except "-(" and "--"
                return False
            else:
                return True

        elif((input[i + 1] != "(") and (input[i + 1] in self.VALID_NUMBERS == False)):      # At the beggining of the string
            return False

    
    def __checkParenthesis(self, input, length, i):
        char = input[i]
        if ((i + 1) < length):          # Verifies that there is space after the currect parenthesis
            if ((char == "(") and (input[i + 1] in self.VALID_SYMBOLS)):                # Only numbers after "("
                if (input[i + 1] != "("):
                    return False
            elif((char == ")") and ((input[i + 1] in self.VALID_SYMBOLS) == False)):    # Only symbols after ")"
                if (input[i + 1] != "-"):
                    return False
            if((i - 1) >= 0):   # Verifies that there is space before the currect parenthesis
                if(((char == "(") and ((input[i - 1] in self.VALID_SYMBOLS) == False))):# Only symbols before "("
                    if (input[i - 1] != "-"):
                        return False
                if((char == ")") and (input[i - 1] in self.VALID_SYMBOLS)):             # Only numbers before ")"
                    if (input[i - 1] != ")"):
                        return False


    ## Verifies the input operation string
    # @param input: The input operation string 
    def validateInput(self, input):

        i = 0                   # While iterator
        length = len(input)     # Length of the input
        openParenthesis = 0     # Amount of open parenthesis in the string
        closeParenthesis = 0    # Amount of close parenthesis in the string
        operationFound = False  # Validates if there is at least one operation
        
        # Cicle that goes through the input string
        while i < length:
            char = input[i]

            if (self.__checkBorders(input, length)):           # Continues if the first and last character are right
                if (char == "s"):                               # Verifies if there is a sqrt function and that is well typed
                    operationFound = True  
                    if (self.__validateSquare(i, input)):
                        openParenthesis = openParenthesis + 1   # If is well typed jumps to the space after the open parenthesis
                        i = i + 5
                    else:
                        print("La funcion sqrt() no fue escrita correctamente")
                        return False                            # If the sqrt function is wrong typed returns false
                else:
                    found = char in self.VALID_ENTRIES          # Validates that the current character is a valid one
                    
                    if (found):         # The current character is valid
                        
                        # Is not a parenthesis
                        if ((char != "(") and (char != ")")):      
                            if (((i + 1) < len(input)) and ((char in self.VALID_SYMBOLS) or char == "-")): # There is something after a symbol
                                operationFound = True
                                if(char == "-"):
                                    if (self.__checkMinus(input, i) == False):
                                        return False
                                else:
                                    if ((char == input[i + 1])):  #Verifies that there's not duplicated symbols such as ++
                                        return False
                                    if ((input[i + 1] in self.VALID_SYMBOLS) and (input[i + 1] != "(") and (input[i + 1] != "-")):  
                                        return False       # After a symbol only can be a number or "(" or "-" 

                        # Is a parenthesis
                        else:      
                            if(char == "("):
                                openParenthesis = openParenthesis + 1
                            else:
                                closeParenthesis = closeParenthesis + 1

                            if(self.__checkParenthesis(input, length, i) == False):
                                return False

                        i = i + 1
                    else:                           # If the currect character is invalid return False
                        print("Se encontro caracteres invalidos en la operacion.\nLos caracteres validos son: +, -, *, /, a^b y sqrt(a)")
                        return False
            else:
                return False

        if (i < 2):
            print("Por favor, ingrese una operacion")
            return False
        else:
            if(operationFound == False):               # There is at least one valid operation
                print("No se encontraron operaciones.")       
                return False

            if(openParenthesis == closeParenthesis):   # Verifies that the number of open and close parenthesis are equal and return true if they are
                return True
            else:
                print("La cantidad de parentesis abiertos y cerrados no coinciden")
                return False


# To run python Validator.py
def main():

    validator = Validator()

    input = "sqrt(1)"

    res = validator.validateInput(input)

    if (res == True):
        print("Valido")
    else:
        print("Invalido")

if __name__ == "__main__":
  	main()
