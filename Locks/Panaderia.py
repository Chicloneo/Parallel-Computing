"""Algoritmo de la Panadería [Lamport, 1974]"""

import time

class LockPanaderia:
    def __init__(self, N_procesos: int):
        # Aquí inicializaremos el estado compartido
        self.cogiendoNumero = [False] * N_procesos  # Su función es evitar condiciones de carrera mientras una hebra está calculando su turno
        self.numero = [0] * N_procesos  # Aquí se guardan los "tickets" de cada hebra.
        self.N = N_procesos

    def acquire(self, i: int):
        # Protocolo de entrada
        self.cogiendoNumero[i] = True # La hebra i está cogiendo un número
        self.numero[i] = 1 + max(self.numero) 
        self.cogiendoNumero[i] = False # La hebra i ya ha cogido su número

        for j in range(self.N):
            if j == i:
                continue #Nos saltamos esta iteración

            # Esperamos a que la hebra j termine de coger su número
            while self.cogiendoNumero[j]:
                time.sleep(0)

            # Esperamos a que la hebra j termine su turno si tiene prioridad sobre la hebra i
            while self.numero[j] != 0 and self.comparar(j, i):
                time.sleep(0)

    def release(self, i: int):
        # Protocolo de salida
        self.numero[i] = 0 # La hebra i libera el recurso, poniendo su número a 0

    def comparar(self, i: int, j: int) -> bool:
        # Devuelve True si la hebra i tiene prioridad sobre la hebra j
        # Estamos suponiendo que comparamos siempre hebras distintas
        if self.numero[i] < self.numero[j]:
            return True
        elif self.numero[i] == self.numero[j]:
            return i < j
        else:
            return False
