from socket import socket
from threading import Thread

class AtiendeCliente(Thread):
    def __init__(self, cl_socket):
        Thread.__init__(self)
        self.cl_socket = cl_socket

    def run(self):
        msj_rec = self.cl_socket.recv(1024) 
        while msj_rec:

            peticion = msj_rec.decode()

            lista_datos = peticion.split(':')
            comando = lista_datos[0]
            texto = lista_datos[1]

            if comando == 'UPPER':
                respuesta = texto.upper()
            elif comando == 'LOWER': #Es importante un elif y no un if, porque si el comando es UPPER, volvería a preguntar si es LOWER. Como no lo es, entra en el else y devuelve error
                respuesta = texto.lower()
            else:
                respuesta = ('ERROR: petición no reconocida.')

            self.cl_socket.send(respuesta.encode())
            msj_rec = self.cl_socket.recv(1024)

        self.cl_socket.close()

srvr_socket = socket()
ip_addr = "localhost"               #es la dirección IP del servidor. El servidor escucha en ella, y el cliente necesita conocerla
puerto = 54323                      #probar a cambiar si falla. No debe ser <= 1024
srvr_socket.bind((ip_addr, puerto)) #asocia el socket a una IP y un puerto
srvr_socket.listen()                #hace que el servidor empiece a escuchar

while True:
    cl_socket, _ = srvr_socket.accept()
    cl_thread = AtiendeCliente(cl_socket)
    cl_thread.start()

srvr_socket.close()