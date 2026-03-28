import Panaderia
import threading
import time

"""Tomamos esta clase, que encapsula un contador para que pueda ser usado concurrentemente de forma segura
EL Lock() normal puede ser usado. Creo que el Lamport (Bakery) es para fines didácticos"""

class ContadorSeguro:
    def __init__(self, inicial: int, n_procesos:int) -> None:
        self.contador = inicial
        self.lock = Panaderia.LockPanaderia(n_procesos)

    def incrementar(self, i:int) -> None:
        self.lock.acquire(i)
        self.contador += 1
        self.lock.release(i)

    def decrementar(self, i:int) -> None:
        self.lock.acquire(i)
        self.contador -= 1
        self.lock.release(i)

    def valor(self) -> int:
        return self.contador
    
def trabajador_estresante(contador: ContadorSeguro, id_hebra: int, iteraciones: int) -> None:
    """
    Suma y resta repetidamente. El balance neto final de esta hebra será 0.
    """
    for _ in range(iteraciones):
        contador.incrementar(id_hebra)
        contador.decrementar(id_hebra)
    
"""
Tu tarea es sustituir el uso del lock en esta clase por el algoritmo de la panadería [Lamport, 1974], de forma que la exclusión mutua siga estando garantizada.
Puedes implementar los await usando while ...: pass. No es ideal, pero estamos suponiendo que trabajamos al nivel más básico y no tenemos ninguna de las herramientas habituales.
Intenta implementar el protocolo en una clase, con métodos que sustituyan exactamente a los acquire y los release.
"""

if __name__ == "__main__":

    print("--- INICIANDO TEST 1: PRUEBA BÁSICA ---")
    N_HEBRAS_BASICO = 5
    
    # Arrancamos en 0, para 5 hebras
    contador_basico = ContadorSeguro(0, N_HEBRAS_BASICO)
    lista_hebras_basico = []

    # Cada hebra simplemente llama a incrementar una vez
    for i in range(N_HEBRAS_BASICO):
        hebra = threading.Thread(target=contador_basico.incrementar, args=(i,))
        lista_hebras_basico.append(hebra)
        hebra.start()

    for hebra in lista_hebras_basico:
        hebra.join()

    print(f"Esperado: {N_HEBRAS_BASICO}")
    print(f"Obtenido: {contador_basico.valor()}")
    if contador_basico.valor() == N_HEBRAS_BASICO:
        print("Test 1: SUPERADO \n")
    else:
        print("Test 1: FALLIDO \n")


    print("--- INICIANDO TEST 2: PRUEBA DE ESTRÉS ---")
    N_HEBRAS_ESTRES = 8
    ITERACIONES = 10_000  # 10,000 operaciones por hebra
    
    # Arrancamos en 0, para 8 hebras
    contador_estres = ContadorSeguro(0, N_HEBRAS_ESTRES)
    lista_hebras_estres = []

    inicio_tiempo = time.time()

    for i in range(N_HEBRAS_ESTRES):
        # Usamos nuestra función diseñada para el estrés
        hebra = threading.Thread(target=trabajador_estresante, args=(contador_estres, i, ITERACIONES))
        lista_hebras_estres.append(hebra)
        hebra.start()

    # Esperamos a que la tormenta de hebras termine
    for hebra in lista_hebras_estres:
        hebra.join()

    fin_tiempo = time.time()

    print(f"Operaciones totales: {N_HEBRAS_ESTRES * ITERACIONES * 2} (incrementos y decrementos)")
    print(f"Tiempo de ejecución: {fin_tiempo - inicio_tiempo:.2f} segundos")
    print("Esperado: 0")
    print(f"Obtenido: {contador_estres.valor()}")
    
    if contador_estres.valor() == 0:
        print("Test 2: SUPERADO ¡Tu candado resiste!")
    else:
        print("Test 2: FALLIDO Hay condiciones de carrera.")
