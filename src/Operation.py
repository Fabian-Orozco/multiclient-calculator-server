class Package:

    ## Constructor de la parte de operacion
    def __init__(self, operation, id, part):
        self.operation = operation      # Parte de la operacion
        self.id = self.configure(id)    # id de la operacion completa
        self.part = part                # id de la parte de la operacion

    ## Configura el id para que no sea confundible con la operacion de algun otro grupo
    #  
    #  @param id el identificador de la operacion, la proporcionael dispatcher
    #  @return el id modificado, en nuestro caso se le agrega el numero 167 al inicio
    def configure(self, id):
        string = str(id)
        string = "167" + string
        res = int(string)

        return res

