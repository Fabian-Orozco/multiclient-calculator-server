# **Etapa 2 : Servidor multicliente calculador**

## Descripción del problema

Un sistema cliente servidor que permite procesar cálculos y solicitar los datos de los resultados posteriormente.

Objetivo: trabajar en la capa de recolección de datos entre cliente-servidor, esos datos serán distribuidos por un segundo proceso.

## Manual de uso: compilación y ejecución

### Para ejecutar el servidor

Ubicándose en la carpeta `src` ingrese el siguiente comando: `python Server.py [IP] [PORT]`

Ejemplo:

~~~bash
[src] $ python Server.py 127.0.0.1 8080
[MM/DD/AA - HH:MI:SS] |======: Server started :======|
[MM/DD/AA - HH:MI:SS] Binded to ip:127.0.0.1 | port:8080
~~~

### Para ejecutar un cliente

Ubicándose en la carpeta `src` ingrese el siguiente comando: `python Client.py -u [username] -p [password] [IP] [PORT]`

Ejemplo:

~~~bash
[src] $ python Client.py -u validUser -p validPass 127.0.0.1 8080
[MM/DD/AA - HH:MI:SS] |======: START :======|
[MM/DD/AA - HH:MI:SS] Connecting to ip:127.0.0.1 | port:8080
[MM/DD/AA - HH:MI:SS] Connection established to ip:127.0.0.1 | port:8082
[MM/DD/AA - HH:MI:SS] Logging in as: validUser
[MM/DD/AA - HH:MI:SS] User validated. Welcome validUser

[05/16/22 - 22:02:59] Enter q to exit

> Enter the action to perform: 
~~~

---

## Créditos

**Autores:**

| Nombre                      | contacto                       |
| :---                        | :---                           |
| Fabián Orozco Chaves        | fabian.orozcochaves@ucr.ac.cr   |
| Daniel Escobar Giraldo      | daniel.escobargiraldo@ucr.ac.cr        |
| Fabián Calvo Alcazar        | elian.calvo@ucr.ac.cr  |
| Marco Rodríguez Espinoza    | marco.rodriguezespinoza@ucr.ac.cr     |

---

Otras rutas:

[Diagrama de flujo - etapa 1](img/FLOW1.png)
[Diagrama de flujo - etapa 2](img/FLOW2.png)
[Tabla de mensajes de red](img/FLOW2.png)
[Diseño UML](img/UML.png)
