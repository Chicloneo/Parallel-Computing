"""Ejercicio primera parte, segundo paso"""

from socket import socket

srvr_socket = socket()
ip_addr = "localhost"               #es la dirección IP del servidor. El servidor escucha en ella, y el cliente necesita conocerla
puerto = 54323                      #probar a cambiar si falla. No debe ser <= 1024
srvr_socket.bind((ip_addr, puerto)) #asocia el socket a una IP y un puerto
srvr_socket.listen()                #hace que el servidor empiece a escuchar

cl_socket, _ = srvr_socket.accept() #es bloqueante y queda esperando que un cliente solicite una conexión.
                                    #Como resultado de accept se crea un nuevo socket, que es el que se usa para la comunicación con el cliente 
                                    #(y otro resultado que no nos interesa). El primer socket solo sirve para escuchar y establecer la conexión.


# Comienza el envío y recepción de mensajes usando cl_socket
msj_rec = cl_socket.recv(1024) 
while msj_rec:

    peticion = msj_rec.decode()

    lista_datos = peticion.split(':')
    comando = lista_datos[0]
    texto = lista_datos[1]

    if comando == 'UPPER':
        respuesta = texto.upper()
    elif comando == 'LOWER':
        respuesta = texto.lower()
    #Es importante un elif y no un if, porque si el comando es UPPER, volvería a preguntar si es LOWER. Como no lo es, entra en el else y devuelve error
    else:
        respuesta = ('ERROR: petición no reconocida.')

    cl_socket.send(respuesta.encode())
    msj_rec = cl_socket.recv(1024)

# Termina el envío y recepción de mensajes usando cl_socket
cl_socket.close()

srvr_socket.close()