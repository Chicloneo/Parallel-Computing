"""Esquema de uso en el cliente"""

from socket import socket

sckt = socket()                      #crea un socket
srvr_ip = "localhost"                #es la dirección IP del servidor con el que se quiere conectar
srvr_puerto = 54323                  #es el puerto por el que el servidor está escuchando
sckt.connect((srvr_ip, srvr_puerto)) #solicita la conexión al servidor a través de la IP y el puerto especificados. Falla si el servidor no está preparado.

# Comienza el envío y recepción de mensajes
comando = ""
while comando != 'QUIT':
    comando = input("¿Qué comando deseas ejecutar, transformar a mayúsculas (UPPER) o a minúsculas (LOWER)? QUIT para salir: ")

    if comando == 'QUIT':
        print('¡Hasta pronto!')
        break

    texto = input("Introduce el texto que deseas transformar: ")
    peticion = f"{comando}:{texto}" #También se podría escribir como peticion = comando + ':' + texto
    msj_env = peticion.encode()
    sckt.send(msj_env)
    msj_rec = sckt.recv(1024)           #1024 es el tamaño máximo del mensaje que se va a recibir.
    respuesta = msj_rec.decode()

    if comando == 'UPPER':
        cmd = 'mayúsculas'
    elif comando == 'LOWER':
        cmd = 'minúsculas'
    else:
        cmd = 'desconocido'

    print(f"Según el servidor, '{texto}' en {cmd} es '{respuesta}'.")


# Termina el envío y recepción de mensajes

sckt.close()                        #acaba la conexión y cierra el socket.
