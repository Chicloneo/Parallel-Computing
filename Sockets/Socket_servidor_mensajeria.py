from socket import socket
from threading import Thread, Lock

class Almacen:
    def __init__(self):
        self.mensajes_almacenados = []
        self.lock = Lock()  # Lock para sincronizar acceso concurrente

    def anadir_mensaje(self, mensaje: str) -> None:
        with self.lock:
            self.mensajes_almacenados.append(mensaje)

    def devolver_lista(self) -> list:
        with self.lock:
            return self.mensajes_almacenados.copy()  # Devuelve copia para evitar modificaciones externas

class AtiendeCliente(Thread):
    def __init__(self, cl_socket, almacen: Almacen):
        Thread.__init__(self)
        self.cl_socket = cl_socket
        self.almacen = almacen

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
            elif comando == 'ALMACENAR':
                self.almacen.anadir_mensaje(texto)
                respuesta = f'Mensaje {texto} almacenado.'
            elif comando == 'LISTA':
                respuesta = 'Mensajes almacenados: ' + ', '.join(self.almacen.devolver_lista())
            else:
                respuesta = ('ERROR: petición no reconocida.')

            self.cl_socket.send(respuesta.encode())
            msj_rec = self.cl_socket.recv(1024)

        self.cl_socket.close()

class Almacen:
    def __init__(self):
        self.mensajes_almacenados = []

    def anadir_mensaje(self, mensaje: str) -> None:
        self.mensajes_almacenados.append(mensaje)

    def devolver_lista(self) -> list:
        return self.mensajes_almacenados

srvr_socket = socket()
ip_addr = "localhost"               #es la dirección IP del servidor. El servidor escucha en ella, y el cliente necesita conocerla
puerto = 54324                      #probar a cambiar si falla. No debe ser <= 1024
srvr_socket.bind((ip_addr, puerto)) #asocia el socket a una IP y un puerto
srvr_socket.listen()                #hace que el servidor empiece a escuchar
almacen_compartido = Almacen()      

while True:
    cl_socket, _ = srvr_socket.accept()
    cl_thread = AtiendeCliente(cl_socket, almacen_compartido)
    cl_thread.start()

srvr_socket.close()