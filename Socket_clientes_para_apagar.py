import socket
import threading
import time

HOST = 'localhost'
PORT = 54325

def cliente(i, comando, texto=None):
    with socket.socket() as s:
        s.connect((HOST, PORT))
        if comando == 'ALMACENAR':
            msg = f'ALMACENAR:{texto}'
        elif comando == 'LISTA':
            msg = 'LISTA'
        elif comando == 'SHUTDOWN':
            msg = 'SHUTDOWN'
        else:
            return

        s.send(msg.encode('utf-8'))
        resp = s.recv(1024).decode('utf-8')
        print(f'Cliente {i} -> {msg} => {resp}')

# Cliente 1 almacena:
t1 = threading.Thread(target=cliente, args=(1, 'ALMACENAR', 'Hola desde 1'))
# Cliente 2 almacena:
t2 = threading.Thread(target=cliente, args=(2, 'ALMACENAR', 'Hola desde 2'))
# Cliente 3 pide lista y apaga:
def cliente_shutdown():
    time.sleep(0.2)
    cliente(3, 'SHUTDOWN')

t3 = threading.Thread(target=cliente_shutdown)

t1.start(); t2.start(); t3.start()
t1.join(); t2.join(); t3.join()
print('Prueba 3 clientes finalizada.')