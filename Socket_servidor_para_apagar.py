from socket import socket
import threading
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
    def __init__(self, cl_socket, almacen: Almacen, parar_event: threading.Event):
        Thread.__init__(self)
        self.cl_socket = cl_socket
        self.almacen = almacen
        self.parar_event = parar_event

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
            elif comando == 'SHUTDOWN':
                respuesta = 'Servidor apagándose...'
                self.parar_event.set()
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
    
hay_que_parar = threading.Event()
almacen_compartido = Almacen()  

IP_ADDR = "localhost"
PUERTO = 54325 
srvr_socket = socket()
srvr_socket.settimeout(5) # Espera 5 segs como maximo
srvr_socket.bind((IP_ADDR, PUERTO))
srvr_socket.listen()

while not hay_que_parar.is_set():
    try:
        cl_socket, _ = srvr_socket.accept()
        cl_socket.settimeout(5)
        cl_thread = AtiendeCliente(cl_socket, almacen_compartido, hay_que_parar)
        cl_thread.start()
    except TimeoutError:
        print("No se han recibido conexiones en los últimos 5 segundos. Cerrando el servidor.")
srvr_socket.close()