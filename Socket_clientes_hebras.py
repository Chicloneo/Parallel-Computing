"""Este archivo es válido para Socket_servidor_con_hebras.py y Socket_servidor_mensajeria.py"""

import socket
import threading
import time

def cliente_test(id_cliente):
    try:
        sckt = socket.socket()
        sckt.connect(("localhost", 54324))

        # Enviar una petición
        peticion = f"UPPER:Cliente {id_cliente} dice hola"
        sckt.send(peticion.encode())
        respuesta = sckt.recv(1024).decode()
        print(f"Cliente {id_cliente}: Envié '{peticion}', recibí '{respuesta}'")

        time.sleep(0.5)  # Pequeña pausa

        # Otra petición
        peticion2 = f"LOWER:Cliente {id_cliente} DICE ADIÓS"
        sckt.send(peticion2.encode())
        respuesta2 = sckt.recv(1024).decode()
        print(f"Cliente {id_cliente}: Envié '{peticion2}', recibí '{respuesta2}'")

        time.sleep(0.5)  # Pequeña pausa

        peticion3 = f"ALMACENAR:Mensaje del cliente {id_cliente}"
        sckt.send(peticion3.encode())
        respuesta3 = sckt.recv(1024).decode()
        print(f"Cliente {id_cliente}: Envié '{peticion3}', recibí '{respuesta3}'")

        time.sleep(0.5)  # Pequeña pausa

        sckt.close()
    except Exception as e:
        print(f"Cliente {id_cliente}: Error - {e}")

# Crear y lanzar 5 clientes simultáneamente
hilos = []
for i in range(1, 6):
    hilo = threading.Thread(target=cliente_test, args=(i,))
    hilos.append(hilo)
    hilo.start()

# Esperar a que todos terminen
for hilo in hilos:
    hilo.join()

def cliente_test2(id_cliente):
    try:
        sckt = socket.socket()
        sckt.connect(("localhost", 54324))

        peticion4 = "LISTA:"
        sckt.send(peticion4.encode())
        respuesta4 = sckt.recv(1024).decode()
        print(f"Cliente {id_cliente}: Envié '{peticion4}', recibí '{respuesta4}'")

        sckt.close()
    except Exception as e:
        print(f"Cliente {id_cliente}: Error - {e}")

print('\n' + '-'*50 + '\n')

hilos = []
for i in range(1, 6):
    hilo = threading.Thread(target=cliente_test2, args=(i,))
    hilos.append(hilo)
    hilo.start()

# Esperar a que todos terminen
for hilo in hilos:
    hilo.join()

print("Prueba completada: 5 clientes atendidos concurrentemente.")