from random import gauss
import time
from multiprocessing import Process, Queue
import os

"""
c_0 es el capital inicial
c_i capital que tengo en el año i
c_n capital que tengo en el último año
Queremos ver si c_n <= o > 0

Con este programa se ve mucha diferencia entre secuencial y paralelo

¿Cuánto dinero necesito tener ahorrado para dejar de trabajar?

Esta versión alternativa es sin archivos. Vamos a hacerlo con put, get, queue, ...
"""

def una_simulacion(capital_inicial: float, esperanza_de_vida: int, gasto_anual: float, mu: float, sigma: float) -> bool:
        capital_actual = capital_inicial
        anyos_restantes = esperanza_de_vida

        while capital_actual > 0 and anyos_restantes > 0:
            variacion_inversion = gauss(mu, sigma)
            capital_actual = capital_actual * (1 + variacion_inversion) - gasto_anual
            anyos_restantes -= 1

        return capital_actual > 0


class Simulacion(Process):
    def __init__(self, capital_inicial, esperanza_de_vida, gasto_anual, mu, sigma, num_simulaciones, nombre_archivo):
        super().__init__() #estoy creando una subclase de Process
        self.capital_inicial   = capital_inicial
        self.esperanza_de_vida = esperanza_de_vida
        self.gasto_anual       = gasto_anual
        self.mu                = mu
        self.sigma             = sigma
        self.num_simulaciones  = num_simulaciones
        self.nombre_archivo    = nombre_archivo

        self.result_queue      = None

    def una_simulacion(capital_inicial: float, esperanza_de_vida: int, gasto_anual: float, mu: float, sigma: float) -> bool:
        capital_actual = capital_inicial
        anyos_restantes = esperanza_de_vida

        while capital_actual > 0 and anyos_restantes > 0:
            variacion_inversion = gauss(mu, sigma)
            capital_actual = capital_actual * (1 + variacion_inversion) - gasto_anual
            anyos_restantes -= 1

        return capital_actual > 0

    def run(self):
        num_sies = 0
        for i in range(self.num_simulaciones):
            if una_simulacion(self.capital_inicial, self.esperanza_de_vida, self.gasto_anual, self.mu, self.sigma):
                num_sies += 1

        if self.result_queue is not None:
            self.result_queue.put(num_sies) #escribimos el resultado en la cola

        # No será None porque antes de llamar a start() creamos la cola 
        # q = Queue()
        # proceso.result_queue = q
        


if __name__ == '__main__':

    print('\n')
    print('Nuevo Montecarlo Alternativo')
    print('\n')

    capital_inicial = 900_000
    esperanza_de_vida = 60
    gasto_anual = 3_000 * 12
    mu = 0.06
    sigma = 0.15
    num_simulaciones = 1_000_000

    num_sies = 0
    t0 = time.perf_counter()
    for i in range(num_simulaciones):
        if una_simulacion(capital_inicial, esperanza_de_vida, gasto_anual, mu, sigma):
            num_sies += 1
    t1 = time.perf_counter()

    print('Número de éxitos: ' f'{num_sies}', 'Número de simulaciones: ' f'{num_simulaciones}')
    print('Porcentaje de éxito: ' f'{(num_sies/num_simulaciones)*100}%')
    print(f'Tiempo secuencial: {t1 - t0:.4f} segundos')

    print('\n')
    print('--------------------------------------------')
    print('\n')

    t0 = time.perf_counter()

    q = Queue() #creamos una cola

    lista_simulaciones = [Simulacion(capital_inicial, esperanza_de_vida, gasto_anual, mu, sigma, num_simulaciones//8, f'Montecarlo_{i}') for i in range(8)]
    #Dividimos entre 8 las simulaciones totales porque hacemos 8 procesos paralelos

    for proceso in lista_simulaciones:
            proceso.result_queue = q
            proceso.start()
    for proceso in lista_simulaciones:
            proceso.join()

    num_sies = 0
    for proceso in lista_simulaciones:
            num_sies += q.get() #el resultado está guardado en la cola y lo vamos sacando (ya no está en la cola)

    t1 = time.perf_counter()

    print('Número de éxitos: ' f'{num_sies}', 'Número de simulaciones: ' f'{num_simulaciones}')
    print('Porcentaje de éxito: ' f'{(num_sies/num_simulaciones)*100}%')
    print(f'Tiempo con paralelismo: {t1 - t0:.4f} segundos')
    print('\n')

    """
    get() es bloqueante pero 
    """
